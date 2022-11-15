from flask import jsonify, request, abort, url_for
from config import connection
from math import ceil
from app import bp
from app.functions import *


@bp.route("/book/<int:book_id>", methods=['GET'])
def book_info(book_id):
    """
    Возвращает информацию о заданной книге включая автора (или авторов) этой книги
    Args:
        book_id: int, must_have == id книги
    Returns:
        JSON с данными об указанной книге и её авторах == в случае успешного выполнения запроса
        404 ошибка == если книга с указанным id не существует
    """
    with connection.cursor() as cursor:
        cursor.execute(is_exists('books', id=book_id))
        if not cursor.fetchone()[0]:
            return abort(404)

        cursor.execute(f"""SELECT * FROM books WHERE id = {book_id};""")
        temp = cursor.fetchall()[0]
        book = {'book_info': {'id': temp[0], 'name': temp[1], 'created_at': temp[2], 'updated_at': temp[3]}}

        cursor.execute(f"""SELECT authors.id, authors.name, authors.surname FROM authors
            INNER JOIN author_books ON authors.id = author_books.author_id
            INNER JOIN books ON books.id = author_books.book_id AND book_id = {book_id};""")
        book['authors_of_book'] = {row[0]: row[1] + ' ' + row[2] for row in cursor.fetchall()}

        return jsonify(book)


@bp.route("/book", methods=['GET'])
def list_of_book():
    """
    Возвращает информацию об имеющихся книгах, с возможностью пагинации
    Params:
        page: int, optional == номер страницы (по умолчанию = 1)
        per_page: int, optional == кол-во записей на странице (по умолчанию = 5)
    Returns:
        JSON с данными о книгах == в случае успешного выполнения запроса
    """
    with connection.cursor() as cursor:
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 5, type=int), 10)

        cursor.execute("SELECT count(id) FROM books;")
        data_count = cursor.fetchall()[0][0]
        info = {'books_count': data_count, 'total_pages': ceil(data_count / per_page), 'current_page': page}

        cursor.execute(f"SELECT id, name FROM books ORDER BY id LIMIT {per_page} OFFSET {(page*per_page)-per_page};")
        data = {row[0]: row[1] for row in cursor.fetchall()}

        result = {'pagination': info, 'data_info': data}
        return jsonify(result)


@bp.route("/book", methods=['POST'])
def add_book():
    """
    Создает новую книгу с возможностью сразу привязать её к автору (или авторам)
    Params:
        name: str, must_have == имя книги
        authors_id: list, must_have == id (id = int) авторов этой книги
    Returns:
        JSON с данными о созданной книге и её авторами == в случае успешного выполнения запроса
        404 ошибка == если name или author_id отсутствует
        400 ошибка == если список authors_id пуст или некорректно указан (например id автора не существует)
    """
    data = request.get_json()
    if 'name' not in data or 'authors_id' not in data:
        return abort(404)
    name = data['name']

    with connection.cursor() as cursor:
        cursor.execute(is_exists('books', name=name))
        if cursor.fetchone()[0]:
            return abort(400)

        authors_ids = {author_id for author_id in data['authors_id']}
        cursor.execute(f"""SELECT count(id) FROM authors WHERE id = any('{authors_ids}');""")
        if cursor.fetchone()[0] != len(authors_ids):
            return abort(403)

        cursor.execute(f"""WITH book AS (INSERT INTO books (name, created_at) VALUES ('{name}', NOW())
            RETURNING id, name, created_at, updated_at),
            authors_update AS (UPDATE authors SET updated_at = NOW() WHERE id = any('{authors_ids}'))
            SELECT id, name, created_at, updated_at FROM book;""")
        temp_2 = cursor.fetchall()[0]
        book = {'book_info': {'id': temp_2[0], 'name': temp_2[1], 'created_at': temp_2[2], 'updated_at': temp_2[3]}}

        cursor.executemany(f"""INSERT INTO author_books (book_id, author_id)
            VALUES ('{temp_2[0]}', %s);""", [str(i) for i in authors_ids])
        connection.commit()

        cursor.execute(f"""SELECT authors.id, authors.name, authors.surname FROM authors
                    INNER JOIN author_books ON authors.id = author_books.author_id
                    INNER JOIN books ON books.id = author_books.book_id AND book_id = {temp_2[0]};""")
        authors_of_book = {row[0]: row[1] + ' ' + row[2] for row in cursor.fetchall()}
        book['authors_of_book'] = authors_of_book

        response = jsonify(book)
        response.status_code = 201
        response.headers['Location'] = url_for('.book_info', book_id=book['book_info']['id'])
        return response


@bp.route("/book/<int:book_id>", methods=['PUT'])
def book_update(book_id):
    """
    Редактирует данные указанной книги с возможностью редактирования её автора(ов)
    Args:
        book_id: int, must_have == id книги
    Params:
        new_name: str, optional == новое имя, которое будет присвоено книге
        join_author_id: list, optional == список с id (id = int) авторов, которые будут связаны с книгой
        split_author_id: list, optional == список с id (id = int) авторов, которые перестанут числится авторами книги
    Returns:
        JSON с актуальной информацией об указанной книге и её авторами == в случае успешного выполнения запроса
        404 ошибка == если книга с указанным id не существует и если нет никаких данных на обновление
        403 ошибка == если автор в параметре join_book_id не существует или этот автор уже связан с книгой
        403 ошибка == если автор в параметре split_book_id не связан с указанной книгой
    """
    data = request.get_json()
    if len(data) == 0:
        return abort(404)

    with connection.cursor() as cursor:
        cursor.execute(is_exists('books', id=book_id))
        if not cursor.fetchone()[0]:
            return abort(404)

        sqlreq = " "
        if 'new_name' in data:
            sqlreq += f"name = '{data['new_name']}', "
        cursor.execute(f"""UPDATE books SET{sqlreq}updated_at = NOW() WHERE id = {book_id}
            RETURNING id, name, created_at, updated_at;""")
        temp = cursor.fetchall()[0]
        book = {'book_info': {'id': temp[0], 'name': temp[1], 'created_at': temp[2], 'updated_at': temp[3]}}

        if 'join_author_id' in data:
            authors_ids = {author_id for author_id in data['join_author_id']}
            cursor.execute(f"""SELECT count(*) FROM author_books
                WHERE book_id = {book_id} AND author_id = any('{authors_ids}');""")
            if cursor.fetchone()[0] == len(authors_ids):
                return abort(403)
            cursor.execute(f"""SELECT count(*) FROM authors WHERE id = any('{authors_ids}');""")
            if cursor.fetchone()[0] != len(authors_ids):
                return abort(403)
            authors_ids = [[i] for i in authors_ids]
            cursor.executemany(f"""INSERT INTO author_books (book_id, author_id)
                VALUES ('{book_id}', %s);""", authors_ids)

        if 'split_author_id' in data:
            authors_ids = {author_id for author_id in data['split_author_id']}
            cursor.execute(f"""SELECT count(*) FROM author_books
                WHERE book_id = {book_id} AND author_id = any('{authors_ids}');""")
            if cursor.fetchone()[0] == len(authors_ids):
                return abort(403)
            cursor.execute(f"""DELETE FROM author_books
                WHERE book_id = {book_id} AND author_id = any('{authors_ids}');""")
        connection.commit()

        cursor.execute(f"""SELECT authors.id, authors.name, authors.surname FROM authors
            INNER JOIN author_books ON authors.id = author_books.author_id
            INNER JOIN books ON books.id = author_books.book_id AND book_id = {book_id};""")
        authors_of_book = {row[0]: row[1] + ' ' + row[2] for row in cursor.fetchall()}

        book['authors_of_book'] = authors_of_book
        return jsonify(book)


@bp.route("/book/<int:book_id>", methods=['DELETE'])
def book_delete(book_id):
    """
    Удаляет указанную книгу
    Args:
        book_id: int, must_have == id книги, которая будет удалена
    Returns:
        JSON с информацией об удаленной книге == в случае успешного выполнения запроса
        404 ошибка == если книга с указанным id не существует
    """
    with connection.cursor() as cursor:
        cursor.execute(is_exists('books', id=book_id))
        if not cursor.fetchone()[0]:
            return abort(404)

        cursor.execute(f"""DELETE FROM books WHERE id = {book_id}
            RETURNING id, name, created_at;""")
        temp = cursor.fetchall()[0]
        deleted_book = {'deleted_book': {'id': temp[0], 'name': temp[1], 'created_at': temp[2]}}
        connection.commit()

        return jsonify(deleted_book)

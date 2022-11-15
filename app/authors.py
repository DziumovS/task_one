from flask import jsonify, request, abort, url_for
from config import connection
from math import ceil
from app import bp
from app.functions import *


@bp.route("/author/<int:author_id>", methods=['GET'])
def author_info(author_id):
    """
    Возвращает информацию о заданном авторе включая список его книг
    Args:
        author_id: int, must_have == id автора
    Returns:
        JSON с данными об авторе и его книгах == в случае успешного выполнения запроса
        404 ошибка == если автор с указанным id не существует
    """
    with connection.cursor() as cursor:
        cursor.execute(is_exists('authors', id=author_id))
        if not cursor.fetchone()[0]:
            return abort(404)

        cursor.execute(f"""SELECT * FROM authors WHERE id = {author_id};""")
        temp = cursor.fetchall()[0]
        author = {'id': temp[0], 'name': temp[1], 'surname': temp[2], 'created_at': temp[3], 'updated_at': temp[4]}

        cursor.execute(f"""SELECT books.id, books.name FROM books
            INNER JOIN author_books ON books.id = author_books.book_id
            INNER JOIN authors ON authors.id = author_books.author_id AND author_id = {author_id};""")
        author_books = {row[0]: row[1] for row in cursor.fetchall()}
        result = {'author_info': author, 'author_books': author_books}
        return jsonify(result)


@bp.route("/author/", methods=['GET'])
def list_of_authors():
    """
    Возвращает информацию об имеющихся авторах, с возможностью пагинации
    Params:
        page: int, optional == номер страницы (по умолчанию = 1)
        per_page: int, optional == кол-во записей на странице (по умолчанию = 5)
    Returns:
        JSON с данными об авторах == в случае успешного выполнения запроса
    """
    with connection.cursor() as cursor:
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 5, type=int), 10)

        cursor.execute("SELECT count(id) FROM authors;")
        data_count = cursor.fetchall()[0][0]
        info = {'authors_count': data_count, 'total_pages': ceil(data_count / per_page), 'current_page': page}

        cursor.execute(f"""SELECT id, name, surname FROM authors
            ORDER BY id LIMIT {per_page} OFFSET {(page*per_page)-per_page};""")
        data = {row[0]: row[1] + ' ' + row[2] for row in cursor.fetchall()}

        result = {'pagination': info, 'data_info': data}
        return jsonify(result)


@bp.route("/author", methods=['POST'])
def add_author():
    """
    Создает нового автора
    Params:
        name: str, must_have == имя, которое будет присвоено автору
        surname: str, must_have == фамилия, которая будет присвоена автору
    Returns:
        JSON с данными о созданном авторе == в случае успешного выполнения запроса
        404 ошибка == если автор с указанным именем и фамилией уже существует
        400 ошибка == если обязательные параметры не указаны
    """
    data = request.get_json()
    if 'name' not in data or 'surname' not in data:
        return abort(400)
    name, surname = data['name'].capitalize(), data['surname'].capitalize()

    with connection.cursor() as cursor:
        cursor.execute(is_exists('authors', name=name, surname=surname))
        if cursor.fetchone()[0]:
            return abort(404)

        cursor.execute(f"""INSERT INTO authors (name, surname, created_at)
            VALUES ('{name}', '{surname}', NOW()) RETURNING id, created_at;""")
        connection.commit()
        temp = cursor.fetchall()[0]
        author = {'added_author': {'id': temp[0], 'name': name, 'surname': surname, 'created_at': temp[1]}}

        response = jsonify(author)
        response.status_code = 201
        response.headers['Location'] = url_for('.author_info', author_id=author['added_author']['id'])
        return response


@bp.route("/author/<int:author_id>", methods=['PUT'])
def author_update(author_id):
    """
    Редактирует данные указанного автора с возможностью редактирования его книг
    Args:
        author_id: int, must_have == id автора
    Params:
        new_name: str, optional == новое имя, которое будет присвоено автору
        new_surname: str, optional == новая фамилия, которая будет присвоена автору
        join_book_id: list, optional == список с id (id = int) книг, автором которых будет числится указанный автор
        split_book_id: list, optional == список с id (id = int) книг, автором которых перестанет быть указанный автор
    Returns:
        JSON с актуальной информацией об авторе и список связанных с ним книг == в случае успешного выполнения запроса
        404 ошибка == если автора с author_id не существует и если нет никаких данных на обновление
        403 ошибка == если id книг в join_book_id не существует или одна из этих книг уже связана с автором ИЛИ;
                      если одна из id книг в split_book_id не связана с указанным автором
    """
    data = request.get_json()
    if len(data) == 0:
        return abort(404)

    with connection.cursor() as cursor:
        cursor.execute(is_exists('authors', id=author_id))
        if not cursor.fetchone()[0]:
            return abort(404)

        sqlreq = " "
        if 'new_name' in data:
            sqlreq += f"name = '{data['new_name'].capitalize()}', "
        if 'new_surname' in data:
            sqlreq += f"surname = '{data['new_surname'].capitalize()}', "
        cursor.execute(f"""UPDATE authors SET{sqlreq}updated_at = NOW() WHERE id = {author_id}
            RETURNING id, name, surname, created_at, updated_at;""")
        temp = cursor.fetchall()[0]
        author = {'author_info': {
            'id': temp[0], 'name': temp[1], 'surname': temp[2], 'created_at': temp[3], 'updated_at': temp[4]}}

        if 'join_book_id' in data:
            book_ids = {book_id for book_id in data['join_book_id']}
            cursor.execute(f"""SELECT count(*) FROM author_books
                WHERE author_id = {author_id} AND book_id = any('{book_ids}');""")
            if cursor.fetchone()[0] == len(book_ids):
                return abort(403)
            cursor.execute(f"""SELECT count(*) FROM books WHERE id = any('{book_ids}');""")
            if cursor.fetchone()[0] != len(book_ids):
                return abort(403)
            cursor.executemany(f"""INSERT INTO author_books (author_id, book_id)
                VALUES ('{author_id}', %s);""", [[i] for i in book_ids])

        if 'split_book_id' in data:
            book_ids = {book_id for book_id in data['split_book_id']}
            cursor.execute(f"""SELECT count(*) FROM author_books
                WHERE author_id = {author_id} AND book_id = any('{book_ids}');""")
            if cursor.fetchone()[0] != len(book_ids):
                return abort(403)
            cursor.execute(f"""DELETE FROM author_books
                WHERE author_id = {author_id} AND book_id = any('{book_ids}');""")
        connection.commit()

        cursor.execute(f"""SELECT books.id, books.name FROM books
            INNER JOIN author_books ON books.id = author_books.book_id
            INNER JOIN authors ON authors.id = author_books.author_id AND author_id = {author_id};""")
        author_books = {row[0]: row[1] for row in cursor.fetchall()}

        author['author_books'] = author_books
        return jsonify(author)


@bp.route("/author/<int:author_id>", methods=['DELETE'])
def author_delete(author_id):
    """
    Удаляет указанного автора и связанные с ним книги
    Args:
        author_id: int, must_have == id автора, которого нужно удалить
    Returns:
        JSON с данными об удаленном авторе и его удаленными книгами == в случае успешного выполнения запроса
        404 ошибка == если автор с указанным author_id не существует
    """
    with connection.cursor() as cursor:
        cursor.execute(is_exists('authors', id=author_id))
        if not cursor.fetchone()[0]:
            return abort(404)

        deleted_info = {'deleted_books {id: name}': {}}

        cursor.execute(f"""WITH books_to_delete AS (
            SELECT book_id FROM author_books WHERE book_id IN
                (SELECT book_id FROM author_books GROUP BY book_id HAVING COUNT(*) = 1) AND author_id = {author_id}
        ), author_delete AS (DELETE FROM authors WHERE id = {author_id} RETURNING id, name, surname
        ), books_delete AS (DELETE FROM books WHERE id IN (SELECT book_id FROM books_to_delete) RETURNING id, name
        ) SELECT id, name, surname AS table_1 FROM author_delete
            UNION SELECT id, name, NULL AS table_2 FROM books_delete ORDER BY table_1;""")
        for row in cursor.fetchall():
            if 'deleted_author' not in deleted_info:
                deleted_info['deleted_author'] = {'id': row[0], 'name': row[1], 'surname': row[2]}
                continue
            deleted_info['deleted_books {id: name}'][row[0]] = row[1]

        connection.commit()
        return jsonify(deleted_info)


@bp.route("/author/books/<int:author_id>/", methods=['GET'])
def authors_book_list(author_id):
    """
    Возвращает информацию о книгах указанного автора с возможностью пагинации
    Args:
        author_id: int, must_have == id автора, по которому будет получен список его книг
    Params:
        page: int, optional == номер страницы (по умолчанию = 1)
        per_page: int, optional == кол-во записей на странице (по умолчанию = 5)
    Returns:
        JSON с данными об авторе и его книгах с информацией о пагинации == в случае успешного выполнения запроса
        404 ошибка == если автор с указанным author_id не существует
    """
    with connection.cursor() as cursor:
        cursor.execute(is_exists('authors', id=author_id))
        if not cursor.fetchone()[0]:
            return abort(404)

        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 5, type=int), 10)

        cursor.execute(f"SELECT count(book_id) FROM author_books WHERE author_id = {author_id};")
        data_count = cursor.fetchall()[0][0]
        info = {'books_count': data_count, 'total_pages': ceil(data_count / per_page), 'current_page': page}

        cursor.execute(f"""SELECT books.id, books.name FROM books
            INNER JOIN author_books ON books.id = author_books.book_id
            INNER JOIN authors ON authors.id = author_books.author_id AND author_id = {author_id}
            ORDER BY id LIMIT {per_page} OFFSET {(page*per_page)-per_page};""")
        authors_book = {row[0]: row[1] for row in cursor.fetchall()}

        result = {'pagination': info, 'data_info': authors_book}
        return jsonify(result)

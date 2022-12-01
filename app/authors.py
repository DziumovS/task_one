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
        cursor.execute(is_exists(table='authors'), (str(author_id), ))
        if not cursor.fetchone()[0]:
            return abort(404)

        cursor.execute(count_or_select(table='authors', fields='*', _id='i'), (str(author_id), ))
        temp = cursor.fetchall()[0]
        author = {'id': temp[0], 'name': temp[1], 'surname': temp[2], 'created_at': temp[3], 'updated_at': temp[4]}

        cursor.execute(count_or_select(table='books', fields='books.id, books.name', inner_join='book'),
                       (str(author_id), ))
        author_books = {row[0]: row[1] for row in cursor.fetchall()}
        result = {'author_info': author, 'author_books': author_books}
        return jsonify(result)


@bp.route("/author", methods=['GET'])
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
        offset = page * per_page - per_page

        cursor.execute(count_or_select(table='authors', fields='count(id)'))
        data_count = cursor.fetchall()[0][0]
        info = {'authors_count': data_count, 'total_pages': ceil(data_count / per_page), 'current_page': page}

        cursor.execute(count_or_select(table='authors', fields='id, name, surname', limit=per_page, offset=offset))
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
        cursor.execute(is_exists(table='authors', _id=False, name=True, surname=True), [name, surname])
        if cursor.fetchone()[0]:
            return abort(404)

        cursor.execute(insert_into(table='authors'), (name, surname))
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
        403 ошибка == если id книг в join_book_id не существует или одна из этих книг уже связана с автором ЛИБО
                      если одна из id книг в split_book_id не связана с указанным автором
    """
    data = request.get_json()
    if len(data) == 0:
        return abort(404)

    with connection.cursor() as cursor:
        cursor.execute(is_exists(table='authors'), (str(author_id), ))
        if not cursor.fetchone()[0]:
            return abort(404)

        sql_req = " "
        if 'new_name' in data:
            sql_req += f"name = '{data['new_name'].capitalize()}', "
        if 'new_surname' in data:
            sql_req += f"surname = '{data['new_surname'].capitalize()}', "
        cursor.execute(update_data(table='authors', sql_req=sql_req), (str(author_id), ))
        temp = cursor.fetchall()[0]
        author = {'author_info': {
            'id': temp[0], 'name': temp[1], 'surname': temp[2], 'created_at': temp[3], 'updated_at': temp[4]}}

        if 'join_book_id' in data:
            book_ids = {book_id for book_id in data['join_book_id']}
            cursor.execute(count_or_select(table='author_books', fields='count(*)', _id='ab'),
                           (str(author_id), [b_id for b_id in book_ids]))
            if cursor.fetchone()[0] == len(book_ids):
                return abort(403)
            cursor.execute(count_or_select(table='books', fields='count(*)', _id='any'), ([b_id for b_id in book_ids],))
            if cursor.fetchone()[0] != len(book_ids):
                return abort(403)
            cursor.executemany(insert_into(table='author_books', route='a'), [(author_id, b_id) for b_id in book_ids])

        if 'split_book_id' in data:
            book_ids = {book_id for book_id in data['split_book_id']}
            cursor.execute(count_or_select(table='author_books', fields='count(*)', _id='ab'),
                           (str(author_id), [b_id for b_id in book_ids]))
            if cursor.fetchone()[0] != len(book_ids):
                return abort(403)
            cursor.execute(delete_from(table='author_books', route='a'), (str(author_id), [b_id for b_id in book_ids]))
        connection.commit()

        cursor.execute(count_or_select(table='books', fields='books.id, books.name', inner_join='book'),
                       (str(author_id), ))
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
        cursor.execute(is_exists(table='authors'), (str(author_id), ))
        if not cursor.fetchone()[0]:
            return abort(404)

        deleted_info = {'deleted_books {id: name}': {}}

        cursor.execute(with_as_authors_routes(), (str(author_id), str(author_id)))
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
        cursor.execute(is_exists(table='authors'), (str(author_id), ))
        if not cursor.fetchone()[0]:
            return abort(404)

        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 5, type=int), 10)
        offset = page * per_page - per_page

        cursor.execute(count_or_select(table='author_books', fields='count(book_id)', _id='a'), (str(author_id), ))
        data_count = cursor.fetchall()[0][0]
        info = {'books_count': data_count, 'total_pages': ceil(data_count / per_page), 'current_page': page}

        cursor.execute(count_or_select(table='books', fields='books.id, books.name', inner_join='book', limit=per_page,
                       offset=offset), (str(author_id), ))
        authors_book = {row[0]: row[1] for row in cursor.fetchall()}

        result = {'pagination': info, 'data_info': authors_book}
        return jsonify(result)

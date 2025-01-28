from flask import jsonify, request, abort, url_for
from settings.main import connection
from math import ceil
from app import bp
from app.functions import *


@bp.route("/book/<int:book_id>", methods=['GET'])
def book_info(book_id):
    """
    Returns information about a given book including the author (or authors) of that book
    Args:
        book_id: int, must_have == book id
    Returns:
        JSON with data about the specified book and its authors == in case of successful execution of the request
        404 error == if the book with the specified id does not exist
    """
    with connection.cursor() as cursor:
        cursor.execute(is_exists(table='books'), (str(book_id), ))
        if not cursor.fetchone()[0]:
            return abort(404)

        cursor.execute(count_or_select(table='books', fields='*', _id='i'), (str(book_id), ))
        temp = cursor.fetchall()[0]
        book = {'book_info': {'id': temp[0], 'name': temp[1], 'created_at': temp[2], 'updated_at': temp[3]}}

        cursor.execute(count_or_select(table='authors', fields='authors.id, authors.name, authors.surname',
                                       inner_join='author'), (str(book_id), ))
        book['authors_of_book'] = {row[0]: row[1] + ' ' + row[2] for row in cursor.fetchall()}

        return jsonify(book)


@bp.route("/book", methods=['GET'])
def list_of_book():
    """
    Returns information about available books, with pagination capability
    Params:
        page: int, optional == page number (default = 1)
        per_page: int, optional == number of records per page (default = 5)
    Returns:
        JSON with data about books == in case of successful execution of the request
    """
    with connection.cursor() as cursor:
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 5, type=int), 10)
        offset = page * per_page - per_page

        cursor.execute(count_or_select(table='books', fields='count(id)'))
        data_count = cursor.fetchall()[0][0]
        info = {'books_count': data_count, 'total_pages': ceil(data_count / per_page), 'current_page': page}

        cursor.execute(count_or_select(table='books', fields='id, name', limit=per_page, offset=offset))
        data = {row[0]: row[1] for row in cursor.fetchall()}

        result = {'pagination': info, 'data_info': data}
        return jsonify(result)


@bp.route("/book", methods=['POST'])
def add_book():
    """
    Creates a new book with the ability to immediately link it to an author (or authors)
    Params:
        name: str, must_have == book name
        authors_id: list, must_have == id (id = int) of the authors of this book
    Returns:
        JSON with data about the created book and its authors == in case of successful execution of the request
        404 error == if name or authors_id is missing
        400 error == if authors_id list is empty or incorrectly specified (e.g. author id does not exist)
    """
    data = request.get_json()
    if 'name' not in data or not data['name'] or 'authors_id' not in data or not data['authors_id']:
        return abort(404)
    name = data['name']

    with connection.cursor() as cursor:
        cursor.execute(is_exists(table='books', _id=False, name=True), (name, ))
        if cursor.fetchone()[0]:
            return abort(400)

        authors_ids = {author_id for author_id in data['authors_id']}
        cursor.execute(count_or_select(table='authors', fields='count(id)', _id='any'),
                       ([a_id for a_id in authors_ids], ))
        if cursor.fetchone()[0] != len(authors_ids):
            return abort(403)

        cursor.execute(with_as_books_routes(), (name, [a_id for a_id in authors_ids]))
        temp_2 = cursor.fetchall()[0]
        book = {'book_info': {'id': temp_2[0], 'name': temp_2[1], 'created_at': temp_2[2], 'updated_at': temp_2[3]}}

        cursor.executemany(insert_into(table='author_books', route='b'), [(temp_2[0], a_id) for a_id in authors_ids])
        connection.commit()

        cursor.execute(count_or_select(table='authors', fields='authors.id, authors.name, authors.surname',
                                       inner_join='author'), (str(temp_2[0]), ))
        authors_of_book = {row[0]: row[1] + ' ' + row[2] for row in cursor.fetchall()}
        book['authors_of_book'] = authors_of_book

        response = jsonify(book)
        response.status_code = 201
        response.headers['Location'] = url_for('.book_info', book_id=book['book_info']['id'])
        return response


@bp.route("/book/<int:book_id>", methods=['PUT'])
def book_update(book_id):
    """
    Edits the specified book data with the ability to edit its author(s)
    Args:
        book_id: int, must_have == book id
    Params:
        new_name: str, optional == a new name to be assigned to the book
        join_author_id: list, optional == list with id (id = int) of authors to be associated with the book
        split_author_id: list, optional == list with id (id = int) of authors who will no longer be listed as authors of the book
    Returns:
        JSON with up-to-date information about the specified book and its authors == in case of successful query execution
        404 error == if the book with the specified id does not exist and if there is no data to update.
        403 error == if the author in the join_book_id parameter does not exist or is already associated with the book OR
                     if the author in the split_book_id parameter is not associated with the specified book
        400 error == if a book with the specified name already exists
    """
    data = request.get_json()
    if len(data) == 0:
        return abort(404)

    with connection.cursor() as cursor:
        cursor.execute(is_exists(table='books'), (str(book_id), ))
        if not cursor.fetchone()[0]:
            return abort(404)

        book = dict()
        if 'new_name' in data:
            sqlreq = f" name = '{data['new_name']}', "
            cursor.execute(update_data(table='books', sql_req=sqlreq), (str(book_id), ))
            temp = cursor.fetchall()
            if temp:
                temp = temp[0]
                book['book_info'] = {'id': temp[0], 'name': temp[1], 'created_at': temp[2], 'updated_at': temp[3]}
            else:
                return abort(400)

        if 'join_author_id' in data:
            authors_ids = {author_id for author_id in data['join_author_id']}
            cursor.execute(count_or_select(table='author_books', fields='count(*)', _id='ba'),
                           (str(book_id), [a_id for a_id in authors_ids]))
            if 0 < cursor.fetchone()[0] <= len(authors_ids):
                return abort(403)
            cursor.execute(count_or_select(table='authors', fields='count(*)', _id='any'),
                           ([a_id for a_id in authors_ids], ))
            if cursor.fetchone()[0] != len(authors_ids):
                return abort(403)
            cursor.executemany(insert_into(table='author_books', route='b'), [(book_id, a_id) for a_id in authors_ids])

        if 'split_author_id' in data:
            authors_ids = {author_id for author_id in data['split_author_id']}
            cursor.execute(count_or_select(table='author_books', fields='count(*)', _id='ba'),
                           (str(book_id), [a_id for a_id in authors_ids]))
            if cursor.fetchone()[0] != len(authors_ids):
                return abort(403)
            cursor.execute(delete_from(table='author_books', route='b'), (str(book_id), [a_id for a_id in authors_ids]))
        connection.commit()

        cursor.execute(count_or_select(table='authors', fields='authors.id, authors.name, authors.surname',
                                       inner_join='author'), (str(book_id), ))
        authors_of_book = {row[0]: row[1] + ' ' + row[2] for row in cursor.fetchall()}

        book['authors_of_book'] = authors_of_book
        return jsonify(book)


@bp.route("/book/<int:book_id>", methods=['DELETE'])
def book_delete(book_id):
    """
    Deletes the specified book
    Args:
        book_id: int, must_have == id of the book to be deleted
    Returns:
        JSON with information about the deleted book == in case of successful request execution
        404 error == if the book with the specified id does not exist
    """
    with connection.cursor() as cursor:
        cursor.execute(is_exists(table='books'), (str(book_id), ))
        if not cursor.fetchone()[0]:
            return abort(404)

        cursor.execute(delete_from(table='books'), (str(book_id), ))
        temp = cursor.fetchall()[0]
        deleted_book = {'deleted_book': {'id': temp[0], 'name': temp[1], 'created_at': temp[2]}}
        connection.commit()

        return jsonify(deleted_book)

from flask import jsonify, request, abort, url_for
from settings.main import connection
from math import ceil
from app import bp
from app.functions import *


@bp.route("/author/<int:author_id>", methods=['GET'])
def author_info(author_id):
    """
    Returns information about a given author including a list of his books
    Args:
        author_id: int, must_have == author id
    Returns:
        JSON with data about the author and his books == in case of successful execution of the request
        404 error == if the author with the specified id does not exist
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
    Returns information about available authors, with pagination capability
    Params:
        page: int, optional == page number (default = 1)
        per_page: int, optional == number of records per page (default = 5)
    Returns:
        JSON with author data == in case of successful query execution
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
    Creates a new author
    Params:
        name: str, must_have == the name to be assigned to the author
        surname: str, must_have == the last name to be assigned to the author
    Returns:
        JSON with data about the created author == in case of successful execution of the request
        404 error == if an author with the specified first and last name already exists
        400 error == if no mandatory parameters are specified
    """
    data = request.get_json()
    if 'name' not in data or not data['name'] or 'surname' not in data or not data['surname']:
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
    Edits the specified author's data with the ability to edit their books
    Args:
        author_id: int, must_have == author id
    Params:
        new_name: str, optional == a new name to be assigned to the author
        new_surname: str, optional == the new surname to be assigned to the author
        join_book_id: list, optional == list with id (id = int) of books authored by the specified author
        split_book_id: list, optional == list with id (id = int) of books whose author will cease to be the specified author
    Returns:
        JSON with up-to-date information about the author and a list of related books == if the query is successful
        404 error == if author with author_id does not exist and if there is no data to update
        403 error == if the book id in join_book_id does not exist or one of these books is already linked to an author OR
                     if one of the book ids in split_book_id is not associated with the specified author
    """
    data = request.get_json()
    if len(data) == 0:
        return abort(404)

    with connection.cursor() as cursor:
        cursor.execute(is_exists(table='authors'), (str(author_id), ))
        if not cursor.fetchone()[0]:
            return abort(404)

        sql_req = " "
        if 'new_name' in data and data['new_name']:
            sql_req += f" name = '{data['new_name'].capitalize()}', "
        if 'new_surname' in data and data['new_surname']:
            sql_req += f"surname = '{data['new_surname'].capitalize()}', "
        cursor.execute(update_data(table='authors', sql_req=sql_req), (str(author_id), ))
        temp = cursor.fetchall()[0]
        author = {'author_info': {
            'id': temp[0], 'name': temp[1], 'surname': temp[2], 'created_at': temp[3], 'updated_at': temp[4]}}

        if 'join_book_id' in data:
            book_ids = {book_id for book_id in data['join_book_id']}
            cursor.execute(count_or_select(table='author_books', fields='count(*)', _id='ab'),
                           (str(author_id), [b_id for b_id in book_ids]))
            if 0 < cursor.fetchone()[0] <= len(book_ids):
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
    Deletes the specified author and associated books
    Args:
        author_id: int, must_have == id of the author to be deleted
    Returns:
        JSON with data about the deleted author and his deleted books == in case of successful query execution
        404 error == if author with specified author_id does not exist
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


@bp.route("/author/books/<int:author_id>", methods=['GET'])
def authors_book_list(author_id):
    """
    Returns information about books by the specified author with pagination capability
    Args:
        author_id: int, must_have == author id, by which the list of his books will be obtained
    Params:
        page: int, optional == page number (default = 1)
        per_page: int, optional == number of records per page (default = 5)
    Returns:
        JSON with data about the author and his books with pagination information == in case of successful query execution
        404 error == if author with specified author_id does not exist
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

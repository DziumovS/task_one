from lib_app import app
from flask import jsonify, request, abort, url_for
from config import connection
from math import ceil


@app.route("/api/author/<int:author_id>", methods=['GET'])
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
        cursor.execute(f"""SELECT EXISTS (SELECT 1 FROM authors WHERE id = {author_id});""")
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


@app.route("/api/author/", methods=['GET'])
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


@app.route("/api/author", methods=['POST'])
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
        cursor.execute(f"""SELECT EXISTS (SELECT 1 FROM authors
            WHERE name ILIKE '{name}' AND surname ILIKE '{surname}');""")
        if cursor.fetchone()[0]:
            return abort(404)

        cursor.execute(f"""INSERT INTO authors (name, surname, created_at)
            VALUES ('{name}', '{surname}', NOW()) RETURNING id, created_at;""")
        connection.commit()
        temp = cursor.fetchall()[0]
        author = {'added_author': {'id': temp[0], 'name': name, 'surname': surname, 'created_at': temp[1]}}

        response = jsonify(author)
        response.status_code = 201
        response.headers['Location'] = url_for('author_info', author_id=author['added_author']['id'])
        return response


@app.route("/api/author/<int:author_id>", methods=['PUT'])
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
        cursor.execute(f"""SELECT EXISTS (SELECT 1 FROM authors WHERE id = {author_id});""")
        if not cursor.fetchone()[0]:
            return abort(404)

        if 'new_name' in data:
            sqlreq = f"name = '{data['new_name'].capitalize()}', "
        if 'new_surname' in data:
            sqlreq += f"surname = '{data['new_surname'].capitalize()}', "
        cursor.execute(f"""UPDATE authors SET {sqlreq}updated_at = NOW() WHERE id = {author_id}
            RETURNING id, name, surname, created_at, updated_at;""")
        temp = cursor.fetchall()[0]
        author = {'id': temp[0], 'name': temp[1], 'surname': temp[2], 'created_at': temp[3], 'updated_at': temp[4]}

        if 'join_book_id' in data:
            for book in {book_id for book_id in data['join_book_id']}:
                cursor.execute(f"""SELECT EXISTS (SELECT 1 FROM books
                    INNER JOIN author_books ON books.id = author_books.book_id
                    INNER JOIN authors ON authors.id = author_books.author_id
                    AND author_id = {author_id} AND book_id = {book});""")
                if cursor.fetchone()[0]:
                    return abort(403)
                cursor.execute(f"""SELECT EXISTS (SELECT 1 FROM books WHERE id = {book});""")
                if not cursor.fetchone()[0]:
                    return abort(403)
                cursor.execute(f"""INSERT INTO author_books (author_id, book_id)
                    VALUES ('{author_id}', '{book}');""")
        connection.commit()

        if 'split_book_id' in data:
            for book in {book_id for book_id in data['split_book_id']}:
                cursor.execute(f"""SELECT EXISTS (SELECT 1 FROM books
                    INNER JOIN author_books ON books.id = author_books.book_id
                    INNER JOIN authors ON authors.id = author_books.author_id
                    AND author_id = {author_id} AND book_id = {book});""")
                if not cursor.fetchone()[0]:
                    return abort(403)
                cursor.execute(f"""DELETE FROM author_books
                    WHERE book_id = {book} AND author_id = {author_id};""")
        connection.commit()

        cursor.execute(f"""SELECT books.id, books.name FROM books
                INNER JOIN author_books ON books.id = author_books.book_id
                INNER JOIN authors ON authors.id = author_books.author_id AND author_id = {author_id};""")
        author_books = {row[0]: row[1] for row in cursor.fetchall()}

        result = {'author_info': author, 'author_books': author_books}
        return jsonify(result)


@app.route("/api/author/<int:author_id>", methods=['DELETE'])
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
        cursor.execute(f"""SELECT EXISTS (SELECT 1 FROM authors WHERE id = {author_id});""")
        if not cursor.fetchone()[0]:
            return abort(404)

        cursor.execute(f"""SELECT books.id FROM books
                    INNER JOIN author_books ON books.id = author_books.book_id
                    INNER JOIN authors ON authors.id = author_books.author_id AND author_id = {author_id};""")
        this_author_books = [row[0] for row in cursor.fetchall()]  # id книг автора

        books_to_delete = set()  # id книг автора где автор только он
        for book_id in this_author_books:
            cursor.execute(f"""SELECT authors.id FROM authors
                        INNER JOIN author_books ON authors.id = author_books.author_id
                        INNER JOIN books ON books.id = author_books.book_id AND book_id = {book_id};""")
            temp = [row[0] for row in cursor.fetchall()]
            if len(temp) == 1:
                books_to_delete.add(book_id)

        cursor.execute(f"""DELETE FROM authors WHERE id = {author_id} RETURNING id, name, surname, created_at;""")
        temp = cursor.fetchall()[0]
        deleted_author = {'id': temp[0], 'name': temp[1], 'surname': temp[2], 'created_at': temp[3]}

        deleted_info = {'deleted_author': deleted_author, 'deleted_books': {}}
        for book in books_to_delete:
            cursor.execute(f"""DELETE FROM books WHERE id = {book} RETURNING id, name;""")
            for row in cursor.fetchall():
                deleted_info['deleted_books'][row[0]] = row[1]
        connection.commit()
        return jsonify(deleted_info)


@app.route("/api/author/books/<int:author_id>/", methods=['GET'])
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
        cursor.execute(f"""SELECT EXISTS (SELECT 1 FROM authors WHERE id = {author_id});""")
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


@app.route("/api/book/<int:book_id>", methods=['GET'])
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
        cursor.execute(f"""SELECT EXISTS (SELECT 1 FROM books WHERE id = {book_id});""")
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


@app.route("/api/book", methods=['GET'])
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


@app.route("/api/book", methods=['POST'])
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
        cursor.execute(f"""SELECT EXISTS (SELECT 1 FROM books WHERE name ILIKE '{name}');""")
        if cursor.fetchone()[0]:
            return abort(400)

        authors_ids = set()
        for author_id in data['authors_id']:
            cursor.execute(f"""SELECT EXISTS (SELECT 1 FROM authors WHERE id = {author_id});""")
            if cursor.fetchone()[0]:
                authors_ids.add(author_id)
            else:
                return abort(400)

        cursor.execute(f"""INSERT INTO books (name, created_at) VALUES ('{name}', NOW())
            RETURNING id, name, created_at, updated_at;""")
        temp_2 = cursor.fetchall()[0]
        book = {'book_info': {
            'id': temp_2[0], 'name': temp_2[1], 'created_at': temp_2[2], 'updated_at': temp_2[3]},
            'author_info (id)': {}
        }

        for author_id in authors_ids:
            cursor.execute(f"""INSERT INTO author_books (author_id, book_id)
                VALUES ('{author_id}', {temp_2[0]});""")
            cursor.execute(f"""UPDATE authors SET updated_at = NOW() WHERE id = {author_id}
                RETURNING id, name, surname, updated_at;""")
            temp_3 = cursor.fetchall()[0]
            book['author_info (id)'].update(
                {temp_3[0]: {'name': temp_3[1], 'surname': temp_3[2], 'updated_at': temp_3[3]}}
            )
        connection.commit()

        response = jsonify(book)
        response.status_code = 201
        response.headers['Location'] = url_for('book_info', book_id=book['book_info']['id'])
        return response


@app.route("/api/book/<int:book_id>", methods=['PUT'])
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
        cursor.execute(f"""SELECT EXISTS (SELECT 1 FROM books WHERE id = {book_id});""")
        if not cursor.fetchone()[0]:
            return abort(404)

        cursor.execute(f"""SELECT * FROM books WHERE id = {book_id};""")
        temp = cursor.fetchall()[0]
        book = {'id': temp[0], 'name': temp[1], 'created_at': temp[2], 'updated_at': temp[3]}

        cursor.execute(f"""SELECT authors.id, authors.name, authors.surname FROM authors
            INNER JOIN author_books ON authors.id = author_books.author_id
            INNER JOIN books ON books.id = author_books.book_id AND book_id = {book_id};""")
        authors_of_book = {row[0]: row[1] + ' ' + row[2] for row in cursor.fetchall()}

        cursor.execute(f"""SELECT id FROM authors;""")
        all_authors = {row[0] for row in cursor.fetchall()}

        if 'new_name' in data and data['new_name'].lower() != book['name'].lower():
            cursor.execute(f"""UPDATE books SET name = '{data['new_name']}', updated_at = NOW()
                WHERE id = {book_id} RETURNING id, name, created_at, updated_at;""")
            temp = cursor.fetchall()[0]
            book = {'book_info': {'id': temp[0], 'name': temp[1], 'created_at': temp[2], 'updated_at': temp[3]}}

        if 'join_author_id' in data:
            for author in {author_id for author_id in data['join_author_id']}:
                if author not in authors_of_book and author in all_authors:
                    cursor.execute(f"""INSERT INTO author_books (author_id, book_id)
                        VALUES ('{author}', '{book_id}');""")
                    cursor.execute(f"""SELECT id, name, surname FROM authors WHERE id = '{author}';""")
                    authors_of_book.update(
                        {row[0]: row[1] + ' ' + row[2] for row in cursor.fetchall()})
                else:
                    return abort(403)
        if 'split_author_id' in data:
            for author in {author_id for author_id in data['split_author_id']}:
                if author in authors_of_book:
                    cursor.execute(f"""DELETE FROM author_books WHERE author_id = {author} AND book_id = {book_id};""")
                    del authors_of_book[author]
                else:
                    return abort(403)
        connection.commit()

        book['authors_of_book'] = authors_of_book
        return jsonify(book)


@app.route("/api/book/<int:book_id>", methods=['DELETE'])
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
        cursor.execute(f"""SELECT EXISTS (SELECT 1 FROM books WHERE id = {book_id});""")
        if not cursor.fetchone()[0]:
            return abort(404)

        cursor.execute(f"""DELETE FROM books WHERE id = {book_id}
            RETURNING id, name, created_at;""")
        temp = cursor.fetchall()[0]
        deleted_book = {'deleted_book': {'id': temp[0], 'name': temp[1], 'created_at': temp[2]}}
        connection.commit()
        return jsonify(deleted_book)

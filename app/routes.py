from lib_app import app
from flask import jsonify, request, abort, url_for
from config import connection
from math import ceil


# возвращает информацию о заданном авторе включая список его книг
# тело запроса может содержать:
#   ОБЯЗАТЕЛЬНО:
#      author_id (числовое значение) -- id автора
# если автор с заданным id не существует - вернет 400 ошибку.
@app.route("/api/author/<int:author_id>", methods=['GET'])
def author_info(author_id):
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM authors;")
        ids = [row[0] for row in cursor.fetchall()]
        if author_id not in ids:
            return abort(400)

        author = {}
        cursor.execute(f"""SELECT * FROM authors WHERE id = {author_id};""")
        for row in cursor.fetchall():
            author['id'] = row[0]
            author['name'] = row[1]
            author['surname'] = row[2]
            author['created_at'] = row[3]
            author['updated_at'] = row[4]

        cursor.execute(f"""SELECT books.id, books.name FROM books
            INNER JOIN author_books ON books.id = author_books.book_id
            INNER JOIN authors ON authors.id = author_books.author_id AND author_id = {author_id};""")
        temp = {row[0]: row[1] for row in cursor.fetchall()}

        author['authors_books'] = temp
        return jsonify(author)


# возвращает информацию об имеющихся авторах, с возможностью пагинации
# тело запроса может содержать:
#   ПО ЖЕЛАНИЮ:
#      page (числовое значение) -- номер страницы (по умолчанию 1)
#      per_page (числовое значение) - кол-во записей на странице (по умолчанию 5)
@app.route("/api/author/", methods=['GET'])
def list_of_authors():
    with connection.cursor() as cursor:
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 5, type=int), 10)

        result, info, data = {}, {}, {}
        cursor.execute("SELECT count(*) FROM authors;")
        data_count = cursor.fetchall()[0][0]
        info['authors_count'] = data_count
        info['total_pages'] = ceil(data_count/per_page)
        info['current_page'] = page

        cursor.execute(f"SELECT * FROM authors ORDER BY id LIMIT {per_page} OFFSET {(page*per_page)-per_page};")
        data = {row[0]: row[1] + ' ' + row[2] for row in cursor.fetchall()}

        result['support_info'], result['data_info'] = info, data
        return jsonify(result)


# добавляет (создает) нового автора;
# тело запроса может содержать:
#   ОБЯЗАТЕЛЬНО:
#      name (строковое значение) -- имя автора
#      surname (строковое значение) -- фамилия автора
# если обязательные параметры не указаны - вернет 400 ошибку
# если автор с указанным именем и фамилией уже существует - вернет 403 ошибку.
@app.route("/api/author", methods=['POST'])
def add_author():
    with connection.cursor() as cursor:
        data = request.get_json() or {}
        if 'name' not in data or 'surname' not in data:
            return abort(400)
        cursor.execute("SELECT * FROM authors;")
        for row in cursor.fetchall():
            if row[1] == data['name'].title() and row[2] == data['surname'].title():
                return abort(403)

        cursor.execute(f"""INSERT INTO authors (name, surname, created_at)
            VALUES ('{data['name']}', '{data['surname']}', NOW());""")
        connection.commit()

        author = {}
        cursor.execute(f"""SELECT * FROM authors WHERE name = '{data['name']}' AND surname = '{data['surname']}';""")
        for row in cursor.fetchall():
            author['id'] = row[0]
            author['name'] = row[1]
            author['surname'] = row[2]
            author['created_at'] = row[3]
        response = jsonify(author)
        response.status_code = 201
        response.headers['Location'] = url_for('author_info', author_id=author['id'])
        return response


# редактирует данные указанного автора с возможность редактирования его книг
# тело запроса может содержать:
#   ОБЯЗАТЕЛЬНО:
#      author_id (числовое значение) -- id автора,
#   ПО ЖЕЛАНИЮ НО НЕОБХОДИМО ХОТЯ БЫ ОДНО:
#      new_name (строковое значение) -- новое имя, которое будет присвоено автору
#      new_surname (строковое значение) -- новая фамилия, которая будет присвоена автору
#      join_book_id (числовое значение) - список [] с id книг, автором которых будет числится указанный автор
#      split_book_id (числовое значение) -- список [] id книг, автором которых перестанет числится указанный автор
#   если автор с заданным id не существует - вернет 400 ошибку,
#   если книги в параметре join_book_id не существует или эта книга уже связана с автором - вернет 403 ошибку,
#   если книга в параметре split_book_id не связана с указанным автором - вернет 403 ошибку,
#   в случае успешного выполнения запроса будет возвращен JSON с актуальной информацией об указанном авторе и
#       список связанных с ним книг.
@app.route("/api/author/<int:author_id>", methods=['PUT'])
def author_update(author_id):
    with connection.cursor() as cursor:
        data = request.get_json() or {}
        cursor.execute("SELECT * FROM authors;")
        ids = [row[0] for row in cursor.fetchall()]
        if author_id not in ids:
            return abort(400)

        temp_author = {}
        cursor.execute(f"""SELECT * FROM authors WHERE id = {author_id};""")
        for row in cursor.fetchall():
            temp_author['id'] = row[0]
            temp_author['name'] = row[1]
            temp_author['surname'] = row[2]
            temp_author['created_at'] = row[3]
            temp_author['updated_at'] = row[4]

        cursor.execute(f"""SELECT books.id, books.name FROM books
            INNER JOIN author_books ON books.id = author_books.book_id
            INNER JOIN authors ON authors.id = author_books.author_id AND author_id = {author_id};""")
        temp_book = {row[0]: row[1] for row in cursor.fetchall()}

        cursor.execute(f"""SELECT * FROM books;""")
        temp_books = {row[0]: row[1] for row in cursor.fetchall()}

        flag = False
        if 'new_name' in data and data['new_name'].title() != temp_author['name']:
            sqlreq = f"name = '{data['new_name'].title()}', "
            flag = True
        if 'new_surname' in data and data['new_surname'].title() != temp_author['surname']:
            sqlreq += f"surname = '{data['new_surname'].title()}', "
            flag = True
        if flag:
            cursor.execute(f"""UPDATE authors SET {sqlreq}updated_at = NOW() WHERE id = {author_id};""")

        if 'join_book_id' in data:
            book_to_add = {book_id for book_id in data['join_book_id']}
            for book in book_to_add:
                if book not in temp_book and book in temp_books:
                    cursor.execute(f"""INSERT INTO author_books (author_id, book_id)
                        VALUES ('{author_id}', '{book}');""")
                else:
                    return abort(403)
        if 'split_book_id' in data:
            book_to_remove = {book_id for book_id in data['split_book_id']}
            for book in book_to_remove:
                if book in temp_book:
                    cursor.execute(f"""DELETE FROM author_books
                        WHERE book_id = '{book}' AND author_id = {author_id};""")
                else:
                    return abort(403)
        connection.commit()

        author = {}
        cursor.execute(f"""SELECT * FROM authors WHERE id = {author_id};""")
        for row in cursor.fetchall():
            author['id'] = row[0]
            author['name'] = row[1]
            author['surname'] = row[2]
            author['created_at'] = row[3]
            author['updated_at'] = row[4]

        cursor.execute(f"""SELECT books.id, books.name FROM books
            INNER JOIN author_books ON books.id = author_books.book_id
            INNER JOIN authors ON authors.id = author_books.author_id AND author_id = {author_id};""")
        temp = {row[0]: row[1] for row in cursor.fetchall()}
        author['authors_books'] = temp
        return jsonify(author)


# удаляет указанного автора и связанные с ним книги;
# тело запроса может содержать:
#   ОБЯЗАТЕЛЬНО:
#      author_id (числовое значение) -- id автора,
#   если автор с заданным id не существует - вернет 400 ошибку,
#   удалены будут все книги, у которых указанный автор является единственным автором,
#   если у книги авторы: указанный автор и другие - книга удалена не будет,
#   в случае успешного выполнения запроса будет возвращен JSON с информацией об удаленном авторе:
#       данные самого удаленного автора и перечень удаленных вместе с ним книг.
@app.route("/api/author/<int:author_id>", methods=['DELETE'])
def author_delete(author_id):
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM authors;")
        ids = [row[0] for row in cursor.fetchall()]
        if author_id not in ids:
            return abort(400)

        deleted_info = {}

        cursor.execute(f"""SELECT * FROM authors WHERE id = {author_id};""")
        deleted_author = {}
        for row in cursor.fetchall():
            deleted_author['id'] = row[0]
            deleted_author['name'] = row[1]
            deleted_author['surname'] = row[2]
            deleted_author['created_at'] = row[3]
        deleted_info['deleted_author'] = deleted_author

        deleted_books = {}
        cursor.execute(f"""SELECT books.id FROM books
                    INNER JOIN author_books ON books.id = author_books.book_id
                    INNER JOIN authors ON authors.id = author_books.author_id AND author_id = {author_id};""")
        this_author_books = [row[0] for row in cursor.fetchall()]  # id книг автора

        books_to_delete = []  # id книг автора где автор только он
        for book_id in this_author_books:
            cursor.execute(f"""SELECT authors.id FROM authors
                        INNER JOIN author_books ON authors.id = author_books.author_id
                        INNER JOIN books ON books.id = author_books.book_id AND book_id = {book_id};""")
            temp = [row[0] for row in cursor.fetchall()]
            if len(temp) == 1:
                books_to_delete.append(book_id)

        for book in books_to_delete:
            cursor.execute(f"""SELECT * FROM books WHERE id = {book};""")
            for row in cursor.fetchall():
                deleted_books[row[0]] = row[1]
            cursor.execute(f"""DELETE FROM books WHERE id = {book};""")
        deleted_info['deleted_books'] = deleted_books
        cursor.execute(f"""DELETE FROM authors WHERE id = {author_id};""")
        connection.commit()
        return jsonify(deleted_info)


# возвращает информацию о книгах указанного автора с возможностью пагинации
# тело запроса может содержать:
#   ПО ЖЕЛАНИЮ:
#      author_id (числовое значение) -- id автора, по которому будет получен список его книг
#      page (числовое значение) -- номер страницы (по умолчанию 1)
#      per_page (числовое значение) -- кол-во записей на странице (по умолчанию 5)
# если автор с заданным id не существует - вернет 400 ошибку,
# в случае успеха вернется JSON с перечнем книг, где указанный автор является автором (или соавтором).
@app.route("/api/author/books/<int:author_id>/", methods=['GET'])
def authors_book_list(author_id):
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM authors;")
        ids = [row[0] for row in cursor.fetchall()]
        if author_id not in ids:
            return abort(400)

        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 5, type=int), 10)

        result = {}

        info = {}
        cursor.execute(f"SELECT count(book_id) FROM author_books WHERE author_id = {author_id};")
        data_count = cursor.fetchall()[0][0]
        info['books_count'] = data_count
        info['total_pages'] = ceil(data_count/per_page)
        info['current_page'] = page

        cursor.execute(f"""SELECT books.id, books.name FROM books
            INNER JOIN author_books ON books.id = author_books.book_id
            INNER JOIN authors ON authors.id = author_books.author_id AND author_id = {author_id}
            ORDER BY id LIMIT {per_page} OFFSET {(page*per_page)-per_page};""")
        authors_book_list = {row[0]: row[1] for row in cursor.fetchall()}

        result['support_info'], result['data_info'] = info, authors_book_list
        return jsonify(result)


# возвращает информацию о заданной книге включая автора (или авторов) этой книги
# тело запроса может содержать:
#   ОБЯЗАТЕЛЬНО:
#      book_id (числовое значение) -- id книги,
# если книги с заданным id не существует - вернет 400 ошибку.
@app.route("/api/book/<int:book_id>", methods=['GET'])
def book_info(book_id):
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM books;")
        ids = [row[0] for row in cursor.fetchall()]
        if book_id not in ids:
            return abort(400)

        book = {}
        cursor.execute(f"""SELECT * FROM books WHERE id = {book_id};""")
        for row in cursor.fetchall():
            book['id'] = row[0]
            book['name'] = row[1]
            book['created_at'] = row[2]
            book['updated_at'] = row[3]

        cursor.execute(f"""SELECT authors.id, authors.name, authors.surname FROM authors
            INNER JOIN author_books ON authors.id = author_books.author_id
            INNER JOIN books ON books.id = author_books.book_id AND book_id = {book_id};""")
        temp = {row[0]: row[1] + ' ' + row[2] for row in cursor.fetchall()}

        book['authors_of_book'] = temp
        return jsonify(book)


# возвращает информацию об имеющихся книгах, с возможностью пагинации;
# тело запроса может содержать:
#   ПО ЖЕЛАНИЮ:
#      page (числовое значение) -- номер страницы в числовом значении (по умолчанию 1)
#      per_page (числовое значение) -- кол-во записей на странице (по умолчанию 5)
@app.route("/api/book", methods=['GET'])
def list_of_book():
    with connection.cursor() as cursor:
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 5, type=int), 10)

        result, info, data = {}, {}, {}
        cursor.execute("SELECT count(*) FROM books;")
        data_count = cursor.fetchall()[0][0]
        info['books_count'] = data_count
        info['total_pages'] = ceil(data_count/per_page)
        info['current_page'] = page

        cursor.execute(f"SELECT * FROM books ORDER BY id LIMIT {per_page} OFFSET {(page*per_page)-per_page};")
        data = {row[0]: row[1] for row in cursor.fetchall()}

        result['support_info'], result['data_info'] = info, data
        return jsonify(result)


# создает новую книгу с возможностью сразу привязать её к автору (или авторам);
# тело запроса может содержать:
#   ОБЯЗАТЕЛЬНО:
#      name (строковое значение) -- имя книги,
#      authors_id (список с числовыми значениями [1, 2...]) -- id авторов этой книги
# если name или author_id отсутствует - вернет 400 ошибку,
# если название книги уже существует - вернет 403 ошибку,
# если список authors_id пуст или некорректно указан (например id автора не существует) - вернет 410 ошибку.
@app.route("/api/book", methods=['POST'])
def add_book():
    with connection.cursor() as cursor:
        data = request.get_json() or {}
        if 'name' not in data or 'authors_id' not in data:
            return abort(400)

        cursor.execute(f"""SELECT * FROM books WHERE name ILIKE '{data['name'][0]}%';""")
        for row in cursor.fetchall():
            if row[1].lower() == data['name'].lower():
                return abort(403)

        cursor.execute("SELECT * FROM authors;")
        temp = [row[0] for row in cursor.fetchall()]
        authors_ids = {author_id for author_id in data['authors_id'] if author_id in temp}
        if len(authors_ids) == 0:
            return abort(410)

        cursor.execute(f"""INSERT INTO books (name, created_at)
            VALUES ('{data['name']}', NOW());""")
        connection.commit()

        book = {}
        cursor.execute(f"""SELECT * FROM books WHERE name = '{data['name']}';""")
        for row in cursor.fetchall():
            book['id'] = row[0]
            book['name'] = row[1]
            book['created_at'] = row[2]
            book['updated_at'] = row[3]

        for author_id in authors_ids:
            cursor.execute(f"""INSERT INTO author_books (author_id, book_id) VALUES ('{author_id}', '{book['id']}');""")
        connection.commit()

        response = jsonify(book)
        response.status_code = 201
        response.headers['Location'] = url_for('book_info', book_id=book['id'])
        return response


# редактирует данные указанной книги с возможность редактирования её автора(ов)
# тело запроса может содержать:
#   ОБЯЗАТЕЛЬНО:
#      book_id (числовое значение) -- id книги,
#   ПО ЖЕЛАНИЮ НО НЕОБХОДИМО ХОТЯ БЫ ОДНО:
#      new_name (строковое значение) -- новое имя, которое будет присвоено книге
#      join_author_id (числовое значение) - список [] с id авторов, которые будут связаны с книгой
#      split_author_id (числовое значение) -- список [] с id авторов, которые перестанут числится авторами данной книги
#   если книга с заданным id не существует - вернет 400 ошибку,
#   если автор в параметре join_book_id не существует или этот автор уже связан с книгой - вернет 403 ошибку,
#   если автор в параметре split_book_id не связан с указанной книгой - вернет 403 ошибку,
#   в случае успешного выполнения запроса будет возвращен JSON с актуальной информацией об указанной книге и
#       список связанных с ней авторов.
@app.route("/api/book/<int:book_id>", methods=['PUT'])
def book_update(book_id):
    with connection.cursor() as cursor:
        data = request.get_json() or {}
        cursor.execute("SELECT * FROM books;")
        ids = [row[0] for row in cursor.fetchall()]
        if book_id not in ids:
            return abort(400)

        temp_book = {}
        cursor.execute(f"""SELECT * FROM books WHERE id = {book_id};""")
        for row in cursor.fetchall():
            temp_book['id'] = row[0]
            temp_book['name'] = row[1]
            temp_book['created_at'] = row[2]
            temp_book['updated_at'] = row[3]

        cursor.execute(f"""SELECT authors.id, authors.name, authors.surname FROM authors
            INNER JOIN author_books ON authors.id = author_books.author_id
            INNER JOIN books ON books.id = author_books.book_id AND book_id = {book_id};""")
        temp_authors = {row[0]: row[1] + ' ' + row[2] for row in cursor.fetchall()}

        cursor.execute(f"""SELECT * FROM authors;""")
        all_authors = {row[0]: row[1] + ' ' + row[2] for row in cursor.fetchall()}

        flag = False
        if 'new_name' in data and data['new_name'].lower() != temp_book['name'].lower():
            sqlreq = f"name = '{data['new_name']}', "
            flag = True
        if flag:
            cursor.execute(f"""UPDATE books SET {sqlreq}updated_at = NOW() WHERE id = {book_id};""")

        if 'join_author_id' in data:
            author_to_add = {author_id for author_id in data['join_author_id']}
            for author in author_to_add:
                if author not in temp_authors and author in all_authors:
                    cursor.execute(f"""INSERT INTO author_books (author_id, book_id)
                        VALUES ('{author}', '{book_id}');""")
                else:
                    return abort(403)
        if 'split_author_id' in data:
            author_to_remove = {author_id for author_id in data['split_author_id']}
            for author in author_to_remove:
                if author in temp_authors:
                    cursor.execute(f"""DELETE FROM author_books WHERE author_id = {author} AND book_id = {book_id};""")
                else:
                    return abort(403)
        connection.commit()

        book = {}
        cursor.execute(f"""SELECT * FROM books WHERE id = {book_id};""")
        for row in cursor.fetchall():
            book['id'] = row[0]
            book['name'] = row[1]
            book['created_at'] = row[2]
            book['updated_at'] = row[3]

        cursor.execute(f"""SELECT authors.id, authors.name, authors.surname FROM authors
            INNER JOIN author_books ON authors.id = author_books.author_id
            INNER JOIN books ON books.id = author_books.book_id AND book_id = {book_id};""")
        temp = {row[0]: row[1] + ' ' + row[2] for row in cursor.fetchall()}
        book['authors_of_book'] = temp
        return jsonify(book)


# удаляет указанную книгу;
# тело запроса может содержать:
#   ОБЯЗАТЕЛЬНО:
#      book_id (числовое значение) -- id книги, которая будет удалена
# в случае успешного выполнения запроса будет возвращен JSON с информацией об удаленной книге
@app.route("/api/book/<int:book_id>", methods=['DELETE'])
def book_delete(book_id):
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM books;")
        ids = [row[0] for row in cursor.fetchall()]
        if book_id not in ids:
            return abort(400)

        cursor.execute(f"""SELECT * FROM books WHERE id = {book_id};""")
        deleted_book = {}
        for row in cursor.fetchall():
            deleted_book['id'] = row[0]
            deleted_book['name'] = row[1]
            deleted_book['created_at'] = row[2]

        cursor.execute(f"""DELETE FROM books WHERE id = {book_id};""")
        connection.commit()
        return jsonify(deleted_book)

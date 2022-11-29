def is_exists(table: str = None, _id: bool = True, name: bool = False, surname: bool = False):
    sql_request = f"""SELECT EXISTS (SELECT 1 FROM {table} WHERE"""
    if _id:
        sql_request += """ id = %s"""
    if name:
        sql_request += """ name ILIKE %s """
        if surname:
            sql_request += """AND surname ILIKE %s"""
    sql_request += """);"""
    return sql_request


def count_or_select(table: str = None, inner_join: str = None, fields: str = None, limit: int = None,
                    offset: int = None, _id: str = None):
    sql_request = f"""SELECT {fields} FROM {table}"""
    if inner_join == 'author':
        sql_request += """ INNER JOIN author_books ON authors.id = author_books.author_id
                            INNER JOIN books ON books.id = author_books.book_id AND book_id = %s"""
    if inner_join == 'book':
        sql_request += """ INNER JOIN author_books ON books.id = author_books.book_id
                            INNER JOIN authors ON authors.id = author_books.author_id AND author_id = %s"""
    if limit or offset:
        sql_request += f""" ORDER BY id LIMIT {limit} OFFSET {offset}"""

    if _id == 'i':
        sql_request += """ WHERE id = %s"""
    if _id == 'a':
        sql_request += """ WHERE author_id = %s"""
    if _id == 'any':
        sql_request += """ WHERE id = any(%s)"""
    if _id == 'ab':
        sql_request += """ WHERE author_id = %s AND book_id = any(%s)"""
    if _id == 'ba':
        sql_request += """ WHERE book_id = %s AND author_id = any(%s)"""

    sql_request += """;"""
    return sql_request


def insert_into(table: str = None, route: str = None):
    sql_request = f"""INSERT INTO {table} ("""
    if route == 'a':
        sql_request += """author_id, book_id) VALUES ({}, %s);"""
    if route == 'b':
        sql_request += """book_id, author_id) VALUES ({}, %s);"""
    if table == 'authors':
        sql_request += """name, surname, created_at) VALUES (%s, %s, NOW()) RETURNING id, created_at;"""
    return sql_request


def delete_from(table: str = None, route: str = None):
    sql_request = f"""DELETE FROM {table} WHERE"""
    if route == 'a':
        sql_request += """ author_id = %s AND book_id = any(%s);"""
    if route == 'b':
        sql_request += """ book_id = %s AND author_id = any(%s);"""
    if table == "books":
        sql_request += """ id = %s RETURNING id, name, created_at;"""
    return sql_request


def update_data(table: str, sql_req: str = None):
    sql_request = f"""UPDATE {table} SET{sql_req}updated_at = NOW() WHERE id = %s RETURNING id, name,"""
    if table == 'authors':
        sql_request += """ surname,"""
    sql_request += """ created_at, updated_at;"""
    return sql_request


def with_as_authors_routes():
    sql_request = """WITH books_to_delete AS (
            SELECT book_id FROM author_books WHERE book_id IN
            (SELECT book_id FROM author_books GROUP BY book_id HAVING COUNT(*) = 1) AND author_id = %s
            ), author_delete AS (DELETE FROM authors WHERE id = %s RETURNING id, name, surname
            ), books_delete AS (DELETE FROM books WHERE id IN (SELECT book_id FROM books_to_delete) RETURNING id, name
            ) SELECT id, name, surname AS table_1 FROM author_delete
            UNION SELECT id, name, NULL AS table_2 FROM books_delete ORDER BY table_1;"""
    return sql_request


def with_as_books_routes():
    sql_request = """WITH book AS (INSERT INTO books (name, created_at) VALUES (%s, NOW())
            RETURNING id, name, created_at, updated_at),
            authors_update AS (UPDATE authors SET updated_at = NOW() WHERE id = any(%s))
            SELECT id, name, created_at, updated_at FROM book;"""
    return sql_request

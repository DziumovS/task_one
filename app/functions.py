def is_exists(table: str=None, id: bool=True, name: bool=False, surname: bool=False):
    sql_request = f"""SELECT EXISTS (SELECT 1 FROM {table} WHERE"""
    if id:
        sql_request += f""" id = %s"""
    if name:
        sql_request += f""" name ILIKE %s """
        if surname:
            sql_request += f"""AND surname ILIKE %s"""
    sql_request += """);"""
    return sql_request


def count_or_select(table: str, inner_join: str=None, fields: str=None, limit: int=None, offset: int=None,
                    conditions: str=None, id: int=None):
    sql_request = f"""SELECT {fields} FROM {table}"""
    if inner_join == 'author':
        sql_request += f""" INNER JOIN author_books ON authors.id = author_books.author_id
                            INNER JOIN books ON books.id = author_books.book_id AND book_id = {id}"""
    if inner_join == 'book':
        sql_request += f""" INNER JOIN author_books ON books.id = author_books.book_id
                            INNER JOIN authors ON authors.id = author_books.author_id AND author_id = {id}"""
    if limit or offset:
        sql_request += f""" ORDER BY id LIMIT {limit} OFFSET {offset}"""
    if conditions:
        sql_request += f""" WHERE {conditions}"""
    sql_request += """;"""
    return sql_request


def insert_into(table: str, fields: str=None, values: str=None, returning: str=None):
    sql_request = f"""INSERT INTO {table} ({fields}) VALUES {values}"""
    if returning:
        sql_request += f""" RETURNING {returning}"""
    sql_request += """;"""
    return sql_request


def delete_from(table: str, fields: str=None, returning: str=None):
    sql_request = f"""DELETE FROM {table} WHERE {fields}"""
    if returning:
        sql_request += f""" RETURNING {returning}"""
    sql_request += """;"""
    return sql_request


def update_data(table: str, sqlreq: str=None):
    sql_request = f"""UPDATE {table} SET{sqlreq}updated_at = NOW() WHERE id = %s RETURNING id, name,"""
    if table == 'authors':
        sql_request += """ surname,"""
    sql_request += """ created_at, updated_at;"""
    return sql_request


def with_as_authors_routes(author_id: int):
    sql_request = f"""WITH books_to_delete AS (
            SELECT book_id FROM author_books WHERE book_id IN
            (SELECT book_id FROM author_books GROUP BY book_id HAVING COUNT(*) = 1) AND author_id = {author_id}
            ), author_delete AS (DELETE FROM authors WHERE id = {author_id} RETURNING id, name, surname
            ), books_delete AS (DELETE FROM books WHERE id IN (SELECT book_id FROM books_to_delete) RETURNING id, name
            ) SELECT id, name, surname AS table_1 FROM author_delete
            UNION SELECT id, name, NULL AS table_2 FROM books_delete ORDER BY table_1;"""
    return sql_request


def with_as_books_routes(book_name: str=None, authors_ids_array: dict|set|tuple=None):
    sql_request = f"""WITH book AS (INSERT INTO books (name, created_at) VALUES ('{book_name}', NOW())
            RETURNING id, name, created_at, updated_at),
            authors_update AS (UPDATE authors SET updated_at = NOW() WHERE id = any('{authors_ids_array}'))
            SELECT id, name, created_at, updated_at FROM book;"""
    return sql_request

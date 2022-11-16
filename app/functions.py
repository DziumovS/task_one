def is_exists(table: str, id: int=None, name: str=None, surname: str=None):
    sql_request = f"""SELECT EXISTS (SELECT 1 FROM {table} WHERE"""
    if id:
        sql_request += f""" id = {id}"""
    if name:
        sql_request += f""" name ILIKE '{name}' """
        if surname:
            sql_request += f"""AND surname ILIKE '{surname}'"""
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


def update_data(table: str, sqlreq: str=None, id: int=None, returning: str=None):
    sql_request = f"""UPDATE {table} SET{sqlreq}updated_at = NOW() WHERE id = {id} RETURNING {returning};"""
    return sql_request



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





#
#
#
# def create_sql_statement(table, fields="*", conditions=None, skip=None, offset=None):
#     sql_statement = f"""SELECT {fields} FROM {table}"""
#     if conditions:
#         sql_statement += f""" {conditions}"""  # e.g.: WHERE x == 1, etc.
#     if skip:
#         sql_statement += f""" SKIP {skip}"""
#     if offset:
#         sql_statement += f""" OFFSET {offset}"""
#
#     sql_statement += ";"
#
#     return sql_statement
#
# sql_statement = create_sql_statement("authors", fields="author.id, author.books", conditions="WHERE id == 2",
#                                      skip=20, offset=20)
# # или
# sql_statement = create_sql_statement("authors")  # получить всех авторов
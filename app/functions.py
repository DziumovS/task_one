

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


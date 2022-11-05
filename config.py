import psycopg2


connection = psycopg2.connect(
    host="127.0.0.1",
    user="postgres",
    password="postgres",
    database="lib_api")
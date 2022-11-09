import psycopg2
from psycopg2 import pool


postgres_connection = psycopg2.pool.SimpleConnectionPool(1, 20,
                                                         host="127.0.0.1",
                                                         user="postgres",
                                                         password="postgres",
                                                         database="lib_api")

connection = postgres_connection.getconn()

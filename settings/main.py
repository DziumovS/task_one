import psycopg2
import os
from psycopg2 import pool
from dotenv import load_dotenv, find_dotenv


load_dotenv(find_dotenv())

host = os.getenv("POSTGRESQL_HOST")
user = os.getenv("POSTGRESQL_USER")
password = os.getenv("POSTGRESQL_PASSWORD")
db = os.getenv("POSTGRESQL_DB_NAME")

postgres_connection = psycopg2.pool.SimpleConnectionPool(1, 20, host=host, user=user, password=password, database=db)

connection = postgres_connection.getconn()

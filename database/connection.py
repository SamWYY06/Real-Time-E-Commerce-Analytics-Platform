from psycopg2 import pool
import os
from dotenv import load_dotenv

load_dotenv()

db_pool = pool.SimpleConnectionPool(
    1, 20,
    host=os.getenv("POSTGRES_HOST"),
    database=os.getenv("POSTGRES_DB"),
    user=os.getenv("POSTGRES_USER"),
    password=os.getenv("POSTGRES_PASSWORD"),
    port=os.getenv("POSTGRES_PORT")
)

def get_connection():
    return db_pool.getconn()

def return_connection(conn):
    db_pool.putconn(conn)
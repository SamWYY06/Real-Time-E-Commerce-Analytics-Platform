# POSTGRESQL CONNECTIONS
import psycopg2

def get_connection():
    conn = psycopg2.connect(
        host="localhost",
        database="ecommerce",
        user="postgres",
        password="postgres",
        port=5433
    )
    return conn
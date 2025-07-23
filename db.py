import os
from dotenv import load_dotenv
from urllib.parse import urlparse
import psycopg2

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")


def get_connection():
    result = urlparse(DATABASE_URL)
    return psycopg2.connect(
        dbname=result.path[1:],
        user=result.username,
        password=result.password,
        host=result.hostname,
        port=result.port
    )


def insert_face(employee_id, name, embedding):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO face_embeddings (employee_id, name, embedding)
                VALUES (%s, %s, %s)
                ON CONFLICT (employee_id) DO UPDATE
                SET name = EXCLUDED.name,
                    embedding = EXCLUDED.embedding
                """,
                (employee_id, name, embedding)
            )
            conn.commit()


def remove_face(employee_id):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM face_embeddings WHERE employee_id = %s", (employee_id,))
            conn.commit()

def get_all_embeddings():
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT employee_id, name, embedding FROM face_embeddings")
            rows = cur.fetchall()
            return [(employee_id, name, embedding) for (employee_id, name, embedding) in rows]

import os
import psycopg2
import psycopg2.extras
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.environ["DATABASE_URL"]


def get_connection():
    conn = psycopg2.connect(DATABASE_URL)
    conn.cursor_factory = psycopg2.extras.RealDictCursor
    return conn


class TaskRepository:
    def get_all(self):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM tasks")
        rows = cur.fetchall()
        conn.close()
        return [dict(row) for row in rows]

    def get_by_id(self, task_id):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM tasks WHERE id = %s", (task_id,))
        row = cur.fetchone()
        conn.close()
        return dict(row) if row else None

    def create(self, title):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO tasks (title, done) VALUES (%s, %s) RETURNING *",
            (title, False)
        )
        row = cur.fetchone()
        conn.commit()
        conn.close()
        return dict(row)

    def update(self, task_id, title, done):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            "UPDATE tasks SET title = %s, done = %s WHERE id = %s RETURNING *",
            (title, done, task_id)
        )
        row = cur.fetchone()
        conn.commit()
        conn.close()
        return dict(row) if row else None

    def delete(self, task_id):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("DELETE FROM tasks WHERE id = %s", (task_id,))
        deleted = cur.rowcount > 0
        conn.commit()
        conn.close()
        return deleted
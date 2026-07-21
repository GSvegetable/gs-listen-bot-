import os
import psycopg2

DATABASE_URL = os.getenv("DATABASE_URL")

def get_db_connection():
    return psycopg2.connect(DATABASE_URL)

def init_db():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS keywords (
            id SERIAL PRIMARY KEY,
            word TEXT UNIQUE NOT NULL
        )
    """)
    conn.commit()
    cur.close()
    conn.close()

def add_keyword(word):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("INSERT INTO keywords (word) VALUES (%s) ON CONFLICT DO NOTHING", (word,))
    conn.commit()
    cur.close()
    conn.close()

def remove_keyword(word):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM keywords WHERE word = %s", (word,))
    conn.commit()
    cur.close()
    conn.close()

def get_all_keywords():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT word FROM keywords")
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return [row[0] for row in rows]

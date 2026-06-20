# core/database.py

import psycopg2
import sqlite3
from sqlalchemy import create_engine
from core.config import DATABASE_URL, DB_TYPE, DB_PATH
from core.security import hash_password

from core.config import (
    DATABASE_URL,
    DB_TYPE
)




# -----------------------------
# SQLALCHEMY ENGINE
# -----------------------------
def get_engine():
    if DB_TYPE == "postgres":
        return create_engine(DATABASE_URL)
    return create_engine(f"sqlite:///{DB_PATH}")


# -----------------------------
# CONEXIÓN
# -----------------------------
def get_connection():
    if DB_TYPE == "postgres":
        return psycopg2.connect(DATABASE_URL)

    return sqlite3.connect(
        DB_PATH,
        timeout=30,
        check_same_thread=False
    )


# -----------------------------
# INIT DB (BASE + SEED)
# -----------------------------
def init_db():

    print("INIT_DB EJECUTANDOSE")

    conn = None
    cursor = None

    try:
        conn = get_connection()
        cursor = conn.cursor()

        # -----------------------------
        # TIPOS DE ID
        # -----------------------------
        if DB_TYPE == "postgres":
            id_type = "SERIAL PRIMARY KEY"
        else:
            id_type = "INTEGER PRIMARY KEY AUTOINCREMENT"

        # -----------------------------
        # TABLAS
        # -----------------------------
        cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS companies (
            id {id_type},
            name TEXT NOT NULL
        )
        """)

        cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS users (
            id {id_type},
            username TEXT UNIQUE,
            password TEXT,
            role TEXT,
            active INTEGER,
            company_id INTEGER
        )
        """)

        cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS sites (
            id {id_type},
            name TEXT NOT NULL,
            company_id INTEGER
        )
        """)

        cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS assets (
            id {id_type},
            name TEXT NOT NULL,
            type TEXT,
            site_id INTEGER
        )
        """)

        cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS readings (
            id {id_type},
            asset_id INTEGER,
            date TEXT,
            ph REAL,
            temperature REAL,
            tds REAL,
            calcium REAL,
            alkalinity REAL
        )
        """)

        # -----------------------------
        # PLACEHOLDER DINÁMICO
        # -----------------------------
        placeholder = "%s" if DB_TYPE == "postgres" else "?"

        # -----------------------------
        # COMPANY DEFAULT
        # -----------------------------
        try:
            cursor.execute("""
                INSERT INTO companies (id, name)
                VALUES (1, 'Default Company')
            """)
        except:
            pass  # ya existe

        # -----------------------------
        # ADMIN SEGURO (bcrypt)
        # -----------------------------
        cursor.execute(
            f"SELECT id FROM users WHERE username = {placeholder}",
            ("admin",)
        )
        existing_user = cursor.fetchone()

        if not existing_user:
            hashed = hash_password("admin123")

            cursor.execute(f"""
                INSERT INTO users (username, password, role, active, company_id)
                VALUES ({placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder})
            """, ("admin", hashed, "admin", 1, 1))

        conn.commit()

    except Exception as e:
        print("Error inicializando DB:", e)
        if conn:
            conn.rollback()

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

    print("INIT_DB TERMINADO")

# =========================================
# DB INFO
# =========================================
def get_db_info():

    return {

        "db": DATABASE_URL,

        "host": DB_TYPE,

        "user": "local"
    }
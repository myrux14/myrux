import uuid
from datetime import datetime, timedelta

import streamlit as st

from core.database import get_connection
from core.db_utils import p
from core.config import SESSION_TIMEOUT_MINUTES


def create_session(user_id):

    conn = None
    cursor = None

    try:

        conn = get_connection()
        cursor = conn.cursor()

        token = str(uuid.uuid4())

        expires_at = (
            datetime.utcnow()
            + timedelta(
                minutes=SESSION_TIMEOUT_MINUTES
            )
        ).strftime("%Y-%m-%d %H:%M:%S")

        cursor.execute(
            f"""
            INSERT INTO sessions (
                user_id,
                token,
                expires_at
            )
            VALUES (
                {p()},
                {p()},
                {p()}
            )
            """,
            (user_id, token, expires_at)
        )

        conn.commit()

        return token

    except Exception as e:

        print("Error create_session:", e)

        if conn:
            conn.rollback()

        return None

    finally:

        if cursor:
            cursor.close()

        if conn:
            conn.close()


def get_session(token):

    conn = None
    cursor = None

    try:

        conn = get_connection()
        cursor = conn.cursor()

        now = datetime.utcnow().strftime(
            "%Y-%m-%d %H:%M:%S"
        )

        cursor.execute(
            f"""
            SELECT
                u.id,
                u.username,
                u.role,
                u.active,
                u.company_id
            FROM sessions s
            JOIN users u
                ON u.id = s.user_id
            WHERE s.token = {p()}
            AND s.expires_at > {p()}
            """,
            (token, now)
        )

        row = cursor.fetchone()

        if not row:
            return None

        columns = [
            desc[0]
            for desc in cursor.description
        ]

        user = dict(zip(columns, row))

        if not user["active"]:
            return None

        return user

    except Exception as e:

        print("Error get_session:", e)
        return None

    finally:

        if cursor:
            cursor.close()

        if conn:
            conn.close()


def delete_session(token):

    conn = None
    cursor = None

    try:

        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            f"""
            DELETE FROM sessions
            WHERE token = {p()}
            """,
            (token,)
        )

        conn.commit()

    except Exception as e:

        print("Error delete_session:", e)

        if conn:
            conn.rollback()

    finally:

        if cursor:
            cursor.close()

        if conn:
            conn.close()


def cleanup_expired():

    conn = None
    cursor = None

    try:

        conn = get_connection()
        cursor = conn.cursor()

        now = datetime.utcnow().strftime(
            "%Y-%m-%d %H:%M:%S"
        )

        cursor.execute(
            f"""
            DELETE FROM sessions
            WHERE expires_at <= {p()}
            """,
            (now,)
        )

        conn.commit()

    except Exception as e:

        print("Error cleanup_expired:", e)

        if conn:
            conn.rollback()

    finally:

        if cursor:
            cursor.close()

        if conn:
            conn.close()


def _get_client_ip():

    try:
        headers = dict(st.context.headers)
    except Exception:
        return ""

    forwarded = headers.get(
        "x-forwarded-for", ""
    )

    if forwarded:
        return forwarded.split(",")[0].strip()

    return headers.get("x-real-ip", "")


def log_login(user_id, username):

    _log_action(
        user_id,
        username,
        "login"
    )


def log_logout(user_id, username):

    _log_action(
        user_id,
        username,
        "logout"
    )


def _log_action(user_id, username, action):

    conn = None
    cursor = None

    try:

        conn = get_connection()
        cursor = conn.cursor()

        ip = _get_client_ip()

        cursor.execute(
            f"""
            INSERT INTO login_history (
                user_id,
                username,
                action,
                ip
            )
            VALUES (
                {p()},
                {p()},
                {p()},
                {p()}
            )
            """,
            (user_id, username, action, ip)
        )

        conn.commit()

    except Exception as e:

        print("Error log_action:", e)

        if conn:
            conn.rollback()

    finally:

        if cursor:
            cursor.close()

        if conn:
            conn.close()

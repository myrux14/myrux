from core.database import get_connection
from core.config import DB_TYPE


def register_visit(page="public_lsi"):

    conn = None
    cursor = None

    try:

        conn = get_connection()
        cursor = conn.cursor()

        placeholder = (
            "%s"
            if DB_TYPE == "postgres"
            else "?"
        )

        cursor.execute(
            f"""
            INSERT INTO analytics_visits (
                page
            )
            VALUES (
                {placeholder}
            )
            """,
            (page,)
        )

        conn.commit()

    except Exception as e:

        print(
            "Error registrando visita:",
            e
        )

        if conn:
            conn.rollback()

    finally:

        if cursor:
            cursor.close()

        if conn:
            conn.close()
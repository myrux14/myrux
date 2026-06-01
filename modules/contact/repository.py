from core.database import get_connection
from core.config import DB_TYPE


def create_contact_request(
    name,
    email,
    message
):

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

        sql = f"""
        INSERT INTO contact_requests (

            name,
            email,
            message

        )
        VALUES (

            {placeholder},
            {placeholder},
            {placeholder}

        )
        """

        cursor.execute(
            sql,
            (
                name,
                email,
                message
            )
        )

        conn.commit()

        return True

    except Exception as e:

        print(
            "Error creando contacto:",
            e
        )

        return False

    finally:

        if cursor:
            cursor.close()

        if conn:
            conn.close()
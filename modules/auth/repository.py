# modules/auth/repository.py

from core.database import get_connection
from core.db_utils import p
from core.security import hash_password, verify_password
from core.config import DB_TYPE


# -----------------------------
# HELPERS
# -----------------------------
def row_to_dict(cursor, row):

    if not row:
        return None

    columns = [
        desc[0]
        for desc in cursor.description
    ]

    return dict(zip(columns, row))


# -----------------------------
# CONTAR ADMINS ACTIVOS
# -----------------------------
def count_active_admins():

    conn = None
    cursor = None

    try:

        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            f"""
            SELECT COUNT(*)
            FROM users
            WHERE role = {p()}
            AND active = 1
            """,
            ("admin",)
        )

        total = cursor.fetchone()[0]

        return total

    except Exception as e:
        print("Error count_active_admins:", e)
        return 0

    finally:

        if cursor:
            cursor.close()

        if conn:
            conn.close()


# -----------------------------
# LOGIN
# -----------------------------
def get_user(username, password):

    conn = None
    cursor = None

    try:

        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            f"""
            SELECT
                id,
                username,
                password,
                role,
                active,
                company_id
            FROM users
            WHERE username = {p()}
            """,
            (username,)
        )

        row = cursor.fetchone()

        if not row:
            return None

        user = row_to_dict(cursor, row)

        # 🔐 validar password
        if not verify_password(
            password,
            user["password"]
        ):
            return None

        return user

    except Exception as e:
        print("Error get_user:", e)
        return None

    finally:

        if cursor:
            cursor.close()

        if conn:
            conn.close()


# -----------------------------
# CREAR
# -----------------------------
def create_user(
    username,
    password,
    role,
    company_id
):

    conn = None
    cursor = None

    try:

        conn = get_connection()
        cursor = conn.cursor()

        # validar duplicado
        cursor.execute(
            f"""
            SELECT id
            FROM users
            WHERE username = {p()}
            """,
            (username,)
        )

        if cursor.fetchone():
            return False, "Usuario ya existe"

        # 🔐 hash
        hashed_password = hash_password(password)

        # insertar
        cursor.execute(
            f"""
            INSERT INTO users (
                username,
                password,
                role,
                active,
                company_id
            )
            VALUES (
                {p()},
                {p()},
                {p()},
                {p()},
                {p()}
            )
            """,
            (
                username,
                hashed_password,
                role,
                1,
                company_id
            )
        )

        conn.commit()

        return True, "Usuario creado"

    except Exception as e:

        if conn:
            conn.rollback()

        return False, str(e)

    finally:

        if cursor:
            cursor.close()

        if conn:
            conn.close()


# -----------------------------
# LISTAR
# -----------------------------
def get_all_users():

    conn = None
    cursor = None

    try:

        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT
                u.id,
                u.username,
                u.role,
                u.active,
                c.name as company

            FROM users u

            LEFT JOIN companies c
                ON c.id = u.company_id

            ORDER BY u.id DESC
        """)

        rows = cursor.fetchall()

        columns = [
            desc[0]
            for desc in cursor.description
        ]

        users = [
            dict(zip(columns, row))
            for row in rows
        ]

        return users

    except Exception as e:

        print(
            "Error get_all_users:",
            e
        )

        return []

    finally:

        if cursor:
            cursor.close()

        if conn:
            conn.close()


# -----------------------------
# LISTAR POR EMPRESA
# -----------------------------
def get_users_by_company(company_id):

    conn = None
    cursor = None

    try:

        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            f"""
            SELECT
                u.id,
                u.username,
                u.role,
                u.active,
                c.name as company

            FROM users u

            LEFT JOIN companies c
                ON c.id = u.company_id

            WHERE u.company_id = {p()}

            ORDER BY u.id DESC
            """,
            (company_id,)
        )

        rows = cursor.fetchall()

        columns = [
            desc[0]
            for desc in cursor.description
        ]

        users = [
            dict(zip(columns, row))
            for row in rows
        ]

        return users

    except Exception as e:

        print(
            "Error get_users_by_company:",
            e
        )

        return []

    finally:

        if cursor:
            cursor.close()

        if conn:
            conn.close()


# -----------------------------
# VERIFICAR USUARIO PERTENECE A EMPRESA
# -----------------------------
def user_belongs_to_company(user_id, company_id):

    conn = None
    cursor = None

    try:

        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            f"""
            SELECT id
            FROM users
            WHERE id = {p()}
            AND company_id = {p()}
            """,
            (user_id, company_id)
        )

        return cursor.fetchone() is not None

    except Exception as e:

        print(
            "Error user_belongs_to_company:",
            e
        )

        return False

    finally:

        if cursor:
            cursor.close()

        if conn:
            conn.close()


# -----------------------------
# ACTUALIZAR
# -----------------------------
def update_user(
    user_id,
    role,
    company_id
):

    conn = None
    cursor = None

    try:

        conn = get_connection()
        cursor = conn.cursor()

        # obtener usuario actual
        cursor.execute(
            f"""
            SELECT role, active
            FROM users
            WHERE id = {p()}
            """,
            (user_id,)
        )

        user = cursor.fetchone()

        if user:

            current_role = user[0]
            active = user[1]

            # proteger último admin
            if (
                current_role == "admin"
                and role != "admin"
                and active == 1
            ):

                total_admins = count_active_admins()

                if total_admins <= 1:
                    return (
                        False,
                        "Debe existir al menos "
                        "un administrador activo"
                    )

        # update
        cursor.execute(
            f"""
            UPDATE users
            SET
                role = {p()},
                company_id = {p()}
            WHERE id = {p()}
            """,
            (
                role,
                company_id,
                user_id
            )
        )

        conn.commit()

        return True, "Usuario actualizado"

    except Exception as e:

        if conn:
            conn.rollback()

        return False, str(e)

    finally:

        if cursor:
            cursor.close()

        if conn:
            conn.close()


# -----------------------------
# ACTIVAR / DESACTIVAR
# -----------------------------
def toggle_user(user_id, active):

    conn = None
    cursor = None

    try:

        conn = get_connection()
        cursor = conn.cursor()

        # obtener usuario actual
        cursor.execute(
            f"""
            SELECT role, active
            FROM users
            WHERE id = {p()}
            """,
            (user_id,)
        )

        user = cursor.fetchone()

        if user:

            role = user[0]
            current_active = user[1]

            # proteger último admin
            if (
                role == "admin"
                and current_active == 1
                and active == 0
            ):

                total_admins = count_active_admins()

                if total_admins <= 1:
                    return (
                        False,
                        "Debe existir al menos "
                        "un administrador activo"
                    )

        # update
        cursor.execute(
            f"""
            UPDATE users
            SET active = {p()}
            WHERE id = {p()}
            """,
            (
                active,
                user_id
            )
        )

        conn.commit()

        return True, "Estado actualizado"

    except Exception as e:

        if conn:
            conn.rollback()

        return False, str(e)

    finally:

        if cursor:
            cursor.close()

        if conn:
            conn.close()


# -----------------------------
# ELIMINAR
# -----------------------------
def delete_user(user_id):

    conn = None
    cursor = None

    try:

        conn = get_connection()
        cursor = conn.cursor()

        # obtener usuario
        cursor.execute(
            f"""
            SELECT role, active
            FROM users
            WHERE id = {p()}
            """,
            (user_id,)
        )

        user = cursor.fetchone()

        if user:

            role = user[0]
            active = user[1]

            # proteger último admin
            if (
                role == "admin"
                and active == 1
            ):

                total_admins = count_active_admins()

                if total_admins <= 1:
                    return (
                        False,
                        "No puedes eliminar "
                        "el último administrador"
                    )

        # delete
        cursor.execute(
            f"""
            DELETE FROM users
            WHERE id = {p()}
            """,
            (user_id,)
        )

        conn.commit()

        return True, "Usuario eliminado"

    except Exception as e:

        if conn:
            conn.rollback()

        return False, str(e)

    finally:

        if cursor:
            cursor.close()

        if conn:
            conn.close()


# -----------------------------
# RESET PASSWORD
# -----------------------------
def reset_password(
    user_id,
    new_password
):

    conn = None
    cursor = None

    try:

        conn = get_connection()
        cursor = conn.cursor()

        hashed = hash_password(
            new_password
        )

        cursor.execute(
            f"""
            UPDATE users
            SET password = {p()}
            WHERE id = {p()}
            """,
            (
                hashed,
                user_id
            )
        )

        conn.commit()

        return True, (
            "Contraseña actualizada"
        )

    except Exception as e:

        if conn:
            conn.rollback()

        return False, str(e)

    finally:

        if cursor:
            cursor.close()

        if conn:
            conn.close()

# =========================================
# INSERT USER
# =========================================
def insert_user(
    username,
    password,
    role,
    company_id
):

    import bcrypt

    conn = None
    cursor = None

    try:

        conn = get_connection()

        cursor = conn.cursor()

        hashed = bcrypt.hashpw(
            password.encode(),
            bcrypt.gensalt()
        ).decode()

        cursor.execute(
            f"""
            INSERT INTO users (
                username,
                password,
                role,
                active,
                company_id
            )
            VALUES (
                {p()},
                {p()},
                {p()},
                {p()},
                {p()}
            )
            """,
            (
                username,
                hashed,
                role,
                1,
                company_id
            )
        )

        conn.commit()

        return True

    except Exception as e:

        print(
            "Error insert_user:",
            e
        )

        if conn:
            conn.rollback()

        return False

    finally:

        if cursor:
            cursor.close()

        if conn:
            conn.close()
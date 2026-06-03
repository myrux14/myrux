from passlib.hash import bcrypt

from core.database import get_connection
from core.config import DB_TYPE
from core.db_utils import p, row_to_dict


# -----------------------------
# USERS
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

        print(e)
        return []

    finally:

        if cursor:
            cursor.close()

        if conn:
            conn.close()


# -----------------------------
# ACTUALIZAR ESTADO
# -----------------------------
def update_user_status(user_id, active):

    conn = None
    cursor = None

    try:
        conn = get_connection()
        cursor = conn.cursor()

        placeholder = p()

        cursor.execute(
            f"""
            UPDATE users
            SET active = {placeholder}
            WHERE id = {placeholder}
            """,
            (active, user_id)
        )

        conn.commit()

    except Exception as e:
        print("Error update_user_status:", e)

        if conn:
            conn.rollback()

    finally:
        if cursor:
            cursor.close()

        if conn:
            conn.close()


# -----------------------------
# CREAR COMPANY
# -----------------------------
# ==================================================
# CREATE COMPANY + INITIAL STRUCTURE
# ==================================================
def create_company(
    company_name,
    chemistry_model,
    asset_type_name,
    place_name
):

    conn = None
    cursor = None

    try:

        conn = get_connection()
        cursor = conn.cursor()

        # =========================================
        # COMPANY
        # =========================================
        cursor.execute(
            f"""
            INSERT INTO companies (
                name,
                chemistry_model
            )
            VALUES (
                {p()},
                {p()}
            )
            """,
            (
                company_name,
                chemistry_model
            )
        )

        # obtener company_id
        if DB_TYPE == "postgres":

            cursor.execute("""
                SELECT LASTVAL()
            """)

            company_id = cursor.fetchone()[0]

        else:

            company_id = cursor.lastrowid

        # =========================================
        # ASSET TYPE
        # =========================================
        cursor.execute(
            f"""
            INSERT INTO asset_types (
                name,
                company_id
            )
            VALUES (
                {p()},
                {p()}
            )
            """,
            (
                asset_type_name,
                company_id
            )
        )

        # obtener asset_type_id
        if DB_TYPE == "postgres":

            cursor.execute("""
                SELECT LASTVAL()
            """)

            asset_type_id = cursor.fetchone()[0]

        else:

            asset_type_id = cursor.lastrowid

        # =========================================
        # SYSTEM / PLACE
        # =========================================
        cursor.execute(
            f"""
            INSERT INTO systems (
                company_id,
                name,
                asset_type_id,
                chemistry_model
            )
            VALUES (
                {p()},
                {p()},
                {p()},
                {p()}
            )
            """,
            (
                company_id,
                place_name,
                asset_type_id,
                chemistry_model
            )
        )

        conn.commit()

        return True, "Empresa creada"

    except Exception as e:

        if conn:
            conn.rollback()

        return False, str(e)

    finally:

        if cursor:
            cursor.close()

        if conn:
            conn.close()

# ==================================================
# ACTIVATE / DEACTIVATE COMPANY
# ==================================================
def update_company_status(
    company_id,
    active
):

    conn = None
    cursor = None

    try:

        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            f"""
            UPDATE companies
            SET active = {p()}
            WHERE id = {p()}
            """,
            (
                active,
                company_id
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
# CREAR USER
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

        placeholder = p()

        hashed = bcrypt.hash(password)

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
                {placeholder},
                {placeholder},
                {placeholder},
                {placeholder},
                {placeholder}
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
        print("Error create_user:", e)

        if conn:
            conn.rollback()

        return False

    finally:
        if cursor:
            cursor.close()

        if conn:
            conn.close()

def get_companies():

    conn = None
    cursor = None

    try:

        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT
                c.id,
                c.name,
                c.chemistry_model,
                s.name as place_name,
                a.name as asset_type

            FROM companies c

            LEFT JOIN systems s
                ON s.company_id = c.id

            LEFT JOIN asset_types a
                ON a.id = s.asset_type_id

            ORDER BY c.id DESC
        """)

        rows = cursor.fetchall()

        result = [
            row_to_dict(cursor, row)
            for row in rows
        ]

        return result

    except Exception as e:

        print(e)
        return []

    finally:

        if cursor:
            cursor.close()

        if conn:
            conn.close()

def get_companies_grouped():

    conn = None
    cursor = None

    try:

        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT
                c.id as company_id,
                c.name as company_name,

                s.id as system_id,
                s.name as place_name,
                s.chemistry_model,

                a.name as asset_type

            FROM companies c

            LEFT JOIN systems s
                ON s.company_id = c.id

            LEFT JOIN asset_types a
                ON a.id = s.asset_type_id

            ORDER BY c.name
        """)

        rows = cursor.fetchall()

        companies = {}

        columns = [
            desc[0]
            for desc in cursor.description
        ]

        for row in rows:

            r = dict(zip(columns, row))

            cid = r["company_id"]

            if cid not in companies:

                companies[cid] = {
                    "id": cid,
                    "name": r["company_name"],
                    "chemistry_model": r["chemistry_model"],
                    "systems": []
                }

            if r["place_name"]:

                companies[cid]["systems"].append({

                    "id": r["system_id"],

                    "place_name": r["place_name"],

                    "asset_type": r["asset_type"],

                    "chemistry_model":
                        r["chemistry_model"]

                })

        return list(companies.values())

    except Exception as e:

        print(e)
        return []

    finally:

        if cursor:
            cursor.close()

        if conn:
            conn.close()

def create_asset_type(
    name,
    company_id
):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        f"""
        INSERT INTO asset_types (
            name,
            company_id
        )
        VALUES ({p()}, {p()})
        """,
        (name, company_id)
    )

    conn.commit()

    cursor.close()
    conn.close()

def get_asset_types(company_id):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        f"""
        SELECT *
        FROM asset_types
        WHERE company_id = {p()}
        ORDER BY name
        """,
        (company_id,)
    )

    rows = cursor.fetchall()

    result = [
        row_to_dict(cursor, row)
        for row in rows
    ]

    cursor.close()
    conn.close()

    return result

def create_system(
    company_id,
    name,
    asset_type_id,
    chemistry_model
):

    conn = None
    cursor = None

    try:

        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            f"""
            INSERT INTO systems (
                company_id,
                name,
                asset_type_id,
                chemistry_model
            )
            VALUES (
                {p()},
                {p()},
                {p()},
                {p()}
            )
            """,
            (
                company_id,
                name,
                asset_type_id,
                chemistry_model
            )
        )

        conn.commit()

        return True, "Sistema creado"

    except Exception as e:

        if conn:
            conn.rollback()

        return False, str(e)

    finally:

        if cursor:
            cursor.close()

        if conn:
            conn.close()

def get_systems(company_id):

    conn = None
    cursor = None

    try:

        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            f"""
            SELECT
                s.id,
                s.name,
                s.chemistry_model,
                a.name as type

            FROM systems s

            LEFT JOIN asset_types a
                ON s.asset_type_id = a.id

            WHERE s.company_id = {p()}

            ORDER BY s.name
            """,
            (company_id,)
        )

        rows = cursor.fetchall()

        result = [
            row_to_dict(cursor, row)
            for row in rows
        ]

        return result

    except Exception as e:

        print(e)
        return []

    finally:

        if cursor:
            cursor.close()

        if conn:
            conn.close()
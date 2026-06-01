from core.database import get_connection
from core.config import DB_TYPE
from core.db_utils import p


def run_migrations():

    conn = None
    cursor = None

    try:

        conn = get_connection()
        cursor = conn.cursor()

        # -----------------------------
        # ID dinámico
        # -----------------------------
        id_type = (
            "SERIAL PRIMARY KEY"
            if DB_TYPE == "postgres"
            else "INTEGER PRIMARY KEY AUTOINCREMENT"
        )

        # -----------------------------
        # TABLA MIGRATIONS
        # -----------------------------
        cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS migrations (
            id {id_type},
            name TEXT UNIQUE
        )
        """)

        # =====================================================
        # 001 - READINGS
        # =====================================================
        if not migration_applied(
            cursor,
            "001_create_readings"
        ):

            date_type = (
                "DATE"
                if DB_TYPE == "postgres"
                else "TEXT"
            )

            cursor.execute(f"""
            CREATE TABLE IF NOT EXISTS readings (
                id {id_type},
                asset_id INTEGER,
                date {date_type},
                ph REAL,
                temperature REAL,
                tds REAL,
                calcium REAL,
                alkalinity REAL
            )
            """)

            mark_migration(
                cursor,
                "001_create_readings"
            )

        # =====================================================
        # 002 - ASSET TYPES
        # =====================================================
        if not migration_applied(
            cursor,
            "002_create_asset_types"
        ):

            cursor.execute(f"""
            CREATE TABLE IF NOT EXISTS asset_types (
                id {id_type},
                name TEXT NOT NULL,
                company_id INTEGER
            )
            """)

            mark_migration(
                cursor,
                "002_create_asset_types"
            )

        # =====================================================
        # 003 - ALTER ASSETS
        # =====================================================
        if not migration_applied(
            cursor,
            "003_alter_assets"
        ):

            try:

                cursor.execute("""
                ALTER TABLE assets
                ADD COLUMN asset_type_id INTEGER
                """)

            except Exception as e:

                print(
                    "asset_type_id ya existe:",
                    e
                )

            try:

                cursor.execute("""
                ALTER TABLE assets
                ADD COLUMN company_id INTEGER
                """)

            except Exception as e:

                print(
                    "company_id ya existe:",
                    e
                )

            mark_migration(
                cursor,
                "003_alter_assets"
            )

        # =====================================================
        # 004 - COMPANY CHEMISTRY MODEL
        # =====================================================
        if not migration_applied(
            cursor,
            "004_company_chemistry_model"
        ):

            try:

                cursor.execute("""
                ALTER TABLE companies
                ADD COLUMN chemistry_model TEXT
                """)

            except Exception as e:

                print(
                    "chemistry_model ya existe:",
                    e
                )

            mark_migration(
                cursor,
                "004_company_chemistry_model"
            )
        # =====================================================
        # 005 - SYSTEMS
        # =====================================================
        if not migration_applied(
            cursor,
            "005_create_systems"
        ):

            cursor.execute(f"""
            CREATE TABLE IF NOT EXISTS systems (
                id {id_type},
                company_id INTEGER,
                name TEXT NOT NULL,
                asset_type_id INTEGER
            )
            """)

            mark_migration(
                cursor,
                "005_create_systems"
            )

        # =====================================================
        # 006 - COMPANY ACTIVE
        # =====================================================
        if not migration_applied(
            cursor,
            "006_company_active"
        ):

            try:

                cursor.execute("""
                ALTER TABLE companies
                ADD COLUMN active INTEGER DEFAULT 1
                """)

            except Exception as e:

                print(
                    "active ya existe:",
                    e
                )

            mark_migration(
                cursor,
                "006_company_active"
            )
        
        # =====================================================
        # 007 - SYSTEM CHEMISTRY MODEL
        # =====================================================
        if not migration_applied(
            cursor,
            "007_system_chemistry_model"
        ):

            try:

                cursor.execute("""
                ALTER TABLE systems
                ADD COLUMN chemistry_model TEXT
                """)

            except Exception as e:

                print(
                    "chemistry_model ya existe en systems:",
                    e
                )

            mark_migration(
                cursor,
                "007_system_chemistry_model"
            )

        # =====================================================
        # 008 - ANALYTICS VISITS
        # =====================================================
        if not migration_applied(
            cursor,
            "008_analytics_visits"
        ):

            cursor.execute(f"""
            CREATE TABLE IF NOT EXISTS analytics_visits (

                id {id_type},

                visit_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

                page TEXT

            )
            """)

            mark_migration(
                cursor,
                "008_analytics_visits"
            )

        # =====================================================
        # 009 - CONTACT REQUESTS
        # =====================================================
        if not migration_applied(
            cursor,
            "009_contact_requests"
        ):

            cursor.execute(f"""
            CREATE TABLE IF NOT EXISTS contact_requests (

                id {id_type},

                created_at TIMESTAMP
                DEFAULT CURRENT_TIMESTAMP,

                name TEXT,

                email TEXT,

                message TEXT,

                status TEXT
                DEFAULT 'new'

            )
            """)

            mark_migration(
                cursor,
                "009_contact_requests"
            )

        # -----------------------------
        # COMMIT FINAL
        # -----------------------------
        conn.commit()

    except Exception as e:

        print(
            "Error en migraciones:",
            e
        )

        if conn:
            conn.rollback()

    finally:

        if cursor:
            cursor.close()

        if conn:
            conn.close()


# =====================================================
# HELPERS
# =====================================================
def migration_applied(cursor, name):

    cursor.execute(
        f"""
        SELECT 1
        FROM migrations
        WHERE name = {p()}
        """,
        (name,)
    )

    return cursor.fetchone() is not None


def mark_migration(cursor, name):

    cursor.execute(
        f"""
        INSERT INTO migrations (name)
        VALUES ({p()})
        """,
        (name,)
    )
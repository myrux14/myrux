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

        # =====================================================
        # 010 - ANALYSIS TABLE
        # =====================================================
        if not migration_applied(
            cursor,
            "010_create_analysis"
        ):

            cursor.execute(f"""
            CREATE TABLE IF NOT EXISTS analysis (
                id {id_type},
                company_id INTEGER,
                company_name TEXT,
                system_id INTEGER,
                system_name TEXT,
                method TEXT,
                sample_date TEXT,
                ph REAL,
                temperature_c REAL,
                tds_ppm REAL,
                calcium_hardness REAL,
                alkalinity REAL,
                factor_a REAL,
                factor_b REAL,
                factor_c REAL,
                factor_d REAL,
                ph_s REAL,
                lsi REAL,
                lsi_tablas REAL,
                created_at TEXT
            )
            """)

            mark_migration(
                cursor,
                "010_create_analysis"
            )

        # =====================================================
        # 011 - ADD ID TO EXISTING ANALYSIS (Neon/Postgres)
        # =====================================================
        if not migration_applied(
            cursor,
            "011_add_id_to_analysis"
        ):

            if DB_TYPE == "postgres":

                try:

                    cursor.execute("""
                    ALTER TABLE analysis
                    ADD COLUMN id SERIAL PRIMARY KEY
                    """)

                except Exception as e:

                    print(
                        "id ya existe en analysis:",
                        e
                    )

            mark_migration(
                cursor,
                "011_add_id_to_analysis"
            )

        # =====================================================
        # 012 - ENRICH ANALYTICS VISITS
        # =====================================================
        if not migration_applied(cursor, "012_enrich_analytics_visits"):

            new_cols = [
                ("ip", "TEXT"),
                ("country", "TEXT"),
                ("city", "TEXT"),
                ("device_type", "TEXT"),
                ("browser", "TEXT"),
                ("os", "TEXT"),
                ("referrer", "TEXT"),
                ("language", "TEXT"),
            ]

            for col_name, col_type in new_cols:
                try:
                    cursor.execute(
                        f"ALTER TABLE analytics_visits ADD COLUMN {col_name} {col_type}"
                    )
                except Exception:
                    pass

            mark_migration(cursor, "012_enrich_analytics_visits")

        # =====================================================
        # 013 - SESSIONS
        # =====================================================
        if not migration_applied(
            cursor,
            "013_create_sessions"
        ):

            cursor.execute(f"""
            CREATE TABLE IF NOT EXISTS sessions (
                id {id_type},
                user_id INTEGER NOT NULL,
                token TEXT UNIQUE NOT NULL,
                created_at TIMESTAMP
                    DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP
            )
            """)

            mark_migration(
                cursor,
                "013_create_sessions"
            )

        # =====================================================
        # 014 - LOGIN HISTORY
        # =====================================================
        if not migration_applied(
            cursor,
            "014_create_login_history"
        ):

            cursor.execute(f"""
            CREATE TABLE IF NOT EXISTS login_history (
                id {id_type},
                user_id INTEGER NOT NULL,
                username TEXT,
                action TEXT NOT NULL,
                ip TEXT,
                created_at TIMESTAMP
                    DEFAULT CURRENT_TIMESTAMP
            )
            """)

            mark_migration(
                cursor,
                "014_create_login_history"
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
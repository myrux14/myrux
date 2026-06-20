from core.database import init_db, get_connection


def seed_data():
    conn = get_connection()
    cursor = conn.cursor()

    # 🔍 verificar si ya existe admin
    cursor.execute("SELECT * FROM users WHERE username='admin'")
    if cursor.fetchone():
        print("Usuario admin ya existe")
        conn.close()
        return

    # -----------------------------
    # CREAR EMPRESA
    # -----------------------------
    cursor.execute("""
    INSERT INTO companies (name)
    VALUES (?)
    """, ("Demo Company",))

    company_id = cursor.lastrowid

    # -----------------------------
    # CREAR USUARIO ADMIN
    # -----------------------------
    cursor.execute("""
    INSERT INTO users (username, password, role, active, company_id)
    VALUES (?, ?, ?, ?, ?)
    """, ("admin", "admin123", "admin", 1, company_id))

    conn.commit()
    conn.close()

    print("Usuario admin creado")
    print("usuario: admin")
    print("password: admin123")


if __name__ == "__main__":
    init_db()
    seed_data()
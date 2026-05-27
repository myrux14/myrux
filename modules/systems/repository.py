from core.database import (get_connection)

# ==========================================
# ELIMINAR SISTEMA
# ==========================================
def delete_system(system_id):

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute(
        """
        DELETE FROM systems
        WHERE id = ?
        """,
        (system_id,)
    )

    conn.commit()

    conn.close()
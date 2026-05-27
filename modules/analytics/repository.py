import pandas as pd

from core.database import (
    get_connection
)


# =========================================
# SAVE ANALYSIS
# =========================================
def save_analysis(df):

    conn = get_connection()

    try:

        df.to_sql(

            "analysis",

            conn,

            if_exists="append",

            index=False
        )

        conn.commit()

    except Exception as e:

        print(
            "Error save_analysis:",
            e
        )

    finally:

        conn.close()


# =========================================
# GET ANALYSIS BY SYSTEM
# =========================================
def get_analysis_by_system(

    company_id,
    system_id

):

    conn = get_connection()

    try:

        query = """
            SELECT *
            FROM analysis
            WHERE company_id = ?
            AND system_id = ?
            ORDER BY sample_date DESC
        """

        df = pd.read_sql_query(

            query,

            conn,

            params=(
                company_id,
                system_id
            )
        )

        return df

    except Exception as e:

        print(
            "Error get_analysis_by_system:",
            e
        )

        return pd.DataFrame()

    finally:

        conn.close()

# =========================================
# DELETE ANALYSIS
# =========================================
def delete_analysis(record_id):

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute(
        """
        DELETE FROM analysis
        WHERE id = ?
        """,
        (record_id,)
    )

    conn.commit()

    conn.close()
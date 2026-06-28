import pandas as pd

from core.database import (
    get_connection,
    get_engine
)

from core.db_utils import p


# =========================================
# SAVE ANALYSIS
# =========================================
def save_analysis(df):

    engine = get_engine()

    try:

        df.to_sql(

            "analysis",

            engine,

            if_exists="append",

            index=False
        )

    except Exception as e:

        print(
            "Error save_analysis:",
            e
        )


# =========================================
# GET ANALYSIS BY SYSTEM
# =========================================
def get_analysis_by_system(

    company_id,
    system_id

):

    conn = get_connection()

    try:

        query = f"""
            SELECT *
            FROM analysis
            WHERE company_id = {p()}
            AND system_id = {p()}
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
def delete_analysis(record_id, company_id):

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute(
        f"""
        DELETE FROM analysis
        WHERE id = {p()}
        AND company_id = {p()}
        """,
        (record_id, company_id)
    )

    conn.commit()

    conn.close()
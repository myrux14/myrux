import pandas as pd
import streamlit as st

from streamlit_analytics2 import (
    streamlit_analytics
)

# =========================================
# CONFIG STREAMLIT
# =========================================
st.set_page_config(
    page_title="Myrux",
    page_icon="📈",
    layout="wide"
)

with streamlit_analytics():

    from modules.public.lsi_simulator import (
        render_public_lsi
    )

    from modules.analytics.service import (
        calcular_lsi,
        clasificar_lsi
    )

    from modules.analytics.service import (
        calcular_lsi_dual
    )

    from modules.analytics.ui import (
        render_lsi_charts
    )

    from core.optimizer import (
        ajustar_parametros
    )






    from core.database import (
        init_db
    )

    from core.migrations import (
        run_migrations
    )


    from modules.auth.service import (
        create_user
    )

    # =========================================
    # IMPORTS
    # =========================================
    from core.config import (
        APP_NAME,
        ENV
    )

    from modules.auth.ui import (
        login
    )

    from core.env_check import (
        check_environment
    )

    from modules.analytics.tracking import (
        register_visit
    )


    # =========================================
    # INIT DB SOLO LOCAL
    # =========================================
    # =========================================
    # INIT DB + MIGRATIONS
    # =========================================
    if "db_initialized" not in st.session_state:

        print("🔥 LLAMANDO INIT_DB")

        init_db()

        print("🔥 LLAMANDO MIGRATIONS")

        run_migrations()

        st.session_state[
            "db_initialized"
        ] = True

    # =========================================
    # RESTAURAR SESIÓN
    # =========================================
    params = st.query_params

    if (

        "token" in params
        and "username" in params
        and "role" in params
        and "company_id" in params
        and "logged_in"
        not in st.session_state

    ):

        st.session_state[
            "logged_in"
        ] = True

        st.session_state[
            "token"
        ] = params.get("token")

        st.session_state[
            "role"
        ] = params.get("role")

        st.session_state[
            "company_id"
        ] = int(
            params.get("company_id")
        )

        # =====================================
        # RESTORE USER
        # =====================================
        st.session_state["user"] = {

            "username":
                params.get("username"),

            "role":
                params.get("role"),

            "company_id":
                int(
                    params.get(
                        "company_id"
                    )
                )
        }

    # =========================================
    # LOGIN
    # =========================================
    db_info = check_environment()

    logged = login()

    if not logged:

        if (
            "visit_registered"
            not in st.session_state
        ):

            register_visit(
                "public_lsi"
            )

            st.session_state[
                "visit_registered"
            ] = True

        render_public_lsi()

        st.stop()

        

    # =========================================
    # VALIDACIÓN SESIÓN
    # =========================================
    if "user" not in st.session_state:

        st.error(
            "Sesión inválida. "
            "Vuelve a iniciar sesión."
        )

        st.stop()

    # =========================================
    # ROLE
    # =========================================
    role = st.session_state.get(
        "role"
    )

    # =========================================
    # DEBUG SOLO ADMIN
    # =========================================
    if role == "admin":

        st.sidebar.divider()

        st.sidebar.subheader(
            "🌍 Entorno"
        )

        st.sidebar.info(
            f"""
    ENV: {db_info.get('env')}
    DB: {db_info.get('db')}
    HOST: {db_info.get('host')}
    USER: {db_info.get('user')}
    """
        )

        # =====================================
        # ALERTAS
        # =====================================
        alerts = db_info.get(
            "alerts",
            []
        )

        for alert_type, message in alerts:

            if alert_type == "error":

                st.sidebar.error(
                    message
                )

            elif alert_type == "warning":

                st.sidebar.warning(
                    message
                )

    # =========================================
    # ADMIN
    # =========================================
    if role == "admin":

        from modules.admin.ui import (
            admin_panel
        )

        admin_panel()

        st.stop()

    # =========================================
    # OPERATOR
    # =========================================
    elif role == "operator":

        from modules.operator.ui import (
            operator_dashboard
        )

        operator_dashboard()

        st.stop()

    # =========================================
    # VIEWER
    # =========================================
    elif role == "viewer":

        st.warning(
            "Dashboard viewer pendiente"
        )

        st.stop()

    # =========================================
    # INVALID ROLE
    # =========================================
    else:

        st.error(
            "Rol inválido"
        )

        st.stop()



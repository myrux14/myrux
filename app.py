import pandas as pd
import streamlit as st

# =========================================
# CONFIG STREAMLIT (debe ser lo primero)
# =========================================
st.set_page_config(
    page_title="Myrux | Análisis digital de la calidad del agua",
    page_icon="📈",
    layout="wide"
)

from extra_streamlit_components import CookieManager

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

from modules.auth.session import (
    get_session,
    cleanup_expired
)

# =========================================
# COOKIES
# =========================================
cookies = CookieManager()

# =========================================
# INIT DB + MIGRATIONS
# =========================================
if "db_initialized" not in st.session_state:

    print("LLAMANDO INIT_DB")

    init_db()

    print("LLAMANDO MIGRATIONS")

    run_migrations()

    cleanup_expired()

    st.session_state[
        "db_initialized"
    ] = True

# =========================================
# RESTAURAR SESIÓN DESDE COOKIE
# =========================================
if (

    "logged_in"
    not in st.session_state

):

    token = cookies.get("session_token")

    if token:

        session_user = get_session(token)

        if session_user:

            st.session_state[
                "logged_in"
            ] = True

            st.session_state[
                "token"
            ] = token

            st.session_state[
                "role"
            ] = session_user["role"]

            st.session_state[
                "company_id"
            ] = session_user["company_id"]

            st.session_state[
                "user"
            ] = session_user

        else:

            cookies["session_token"] = ""
            cookies.save()

# =========================================
# LOGIN
# =========================================
db_info = check_environment()

logged = login(cookies)

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
        f"ENV: {db_info.get('env')} | "
        f"DB: {db_info.get('host')}"
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
# COMPANY ADMIN
# =========================================
elif role == "company_admin":

    from modules.company_admin.ui import (
        company_admin_panel
    )

    company_admin_panel()

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

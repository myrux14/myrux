# modules/auth/ui.py

from datetime import datetime, timedelta

import streamlit as st
from modules.auth.service import login_user

MAX_LOGIN_ATTEMPTS = 5
LOCKOUT_MINUTES = 5

from modules.auth.session import (
    create_session,
    delete_session,
    log_login,
    log_logout
)

from modules.contact.repository import (
    create_contact_request
)


# =========================================
# LOGOUT
# =========================================
MYRUX_SESSION_KEYS = [
    "logged_in",
    "user",
    "role",
    "company_id",
    "token",
    "db_initialized",
    "visit_registered",
    "debug_login",
    "debug_login_type",
]


def logout(cookies):

    token = st.session_state.get("token")
    user = st.session_state.get("user")

    if token:
        delete_session(token)

    if isinstance(user, dict):
        log_logout(
            user.get("id"),
            user.get("username")
        )

    cookies["session_token"] = ""
    cookies.save()

    for key in MYRUX_SESSION_KEYS:
        if key in st.session_state:
            del st.session_state[key]


# =========================================
# LOGIN
# =========================================
def login(cookies):

    st.sidebar.markdown(
        "## 🔐 Cuenta Myrux"
    )

    # =====================================
    # INIT
    # =====================================
    if "logged_in" not in st.session_state:

        st.session_state.logged_in = False

    # =====================================
    # SESIÓN ACTIVA
    # =====================================
    if st.session_state.get("logged_in"):

        user = st.session_state.get("user")

        if isinstance(user, dict):

            st.sidebar.success(
                f"👤 {user['username']}"
            )

            if st.sidebar.button(
                "Cerrar sesión"
            ):

                logout(cookies)
                st.rerun()

            return True

    # =====================================
    # LOGIN FORM
    # =====================================
    username = st.sidebar.text_input(
        "Usuario"
    )

    password = st.sidebar.text_input(
        "Contraseña",
        type="password"
    )

    # =====================================
    # RATE LIMIT
    # =====================================
    attempts = st.session_state.get(
        "login_attempts", 0
    )

    locked_until = st.session_state.get(
        "login_locked_until"
    )

    if locked_until and datetime.utcnow() < locked_until:

        remaining = int(
            (locked_until - datetime.utcnow())
            .total_seconds() / 60
        ) + 1

        st.sidebar.error(
            f"Demasiados intentos. "
            f"Intenta en {remaining} min."
        )

        return False

    if locked_until and datetime.utcnow() >= locked_until:

        st.session_state["login_attempts"] = 0
        st.session_state["login_locked_until"] = None
        attempts = 0

    if st.sidebar.button("Entrar"):

        user = login_user(
            username,
            password
        )

        # =================================
        # USER INACTIVE
        # =================================
        if user == "inactive":

            st.sidebar.error(
                "Usuario desactivado"
            )

        # =================================
        # LOGIN OK
        # =================================
        elif isinstance(user, dict):

            st.session_state["login_attempts"] = 0
            st.session_state[
                "login_locked_until"
            ] = None

            token = create_session(
                user["id"]
            )

            if not token:
                st.sidebar.error(
                    "Error creando sesion"
                )
                return False

            st.session_state[
                "logged_in"
            ] = True

            st.session_state[
                "user"
            ] = user

            st.session_state[
                "role"
            ] = user["role"]

            st.session_state[
                "company_id"
            ] = user["company_id"]

            st.session_state[
                "token"
            ] = token

            cookies["session_token"] = token
            cookies.save()

            log_login(
                user["id"],
                user["username"]
            )

            st.rerun()

        # =================================
        # LOGIN ERROR
        # =================================
        else:

            attempts += 1

            st.session_state[
                "login_attempts"
            ] = attempts

            if attempts >= MAX_LOGIN_ATTEMPTS:

                st.session_state[
                    "login_locked_until"
                ] = (
                    datetime.utcnow()
                    + timedelta(
                        minutes=LOCKOUT_MINUTES
                    )
                )

                st.sidebar.error(
                    f"Demasiados intentos. "
                    f"Bloqueado {LOCKOUT_MINUTES} min."
                )

            else:

                remaining = (
                    MAX_LOGIN_ATTEMPTS - attempts
                )

                st.sidebar.error(
                    f"Credenciales incorrectas. "
                    f"{remaining} intentos restantes."
                )

    # =====================================
    # CONTACTO
    # =====================================
    st.sidebar.divider()

    st.sidebar.markdown(
        "## 📧 Contacto"
    )

    with st.sidebar.form(
        "contact_form",
        clear_on_submit=True
    ):

        nombre = st.text_input(
            "Nombre"
        )

        correo = st.text_input(
            "Correo electrónico"
        )

        mensaje = st.text_area(
            "Mensaje",
            height=100
        )

        enviar = st.form_submit_button(
            "Enviar consulta"
        )

    if enviar:

        if not nombre or not correo:

            st.sidebar.warning(
                "Completa nombre y correo."
            )

        else:

            ok = create_contact_request(
                nombre,
                correo,
                mensaje
            )

            if ok:

                st.sidebar.success(
                    "Consulta enviada."
                )

                st.rerun()

            else:

                st.sidebar.error(
                    "Error enviando consulta."
                )

    return False

# modules/auth/ui.py

import streamlit as st
from modules.auth.service import login_user
import uuid


# =========================================
# LOGOUT
# =========================================
def logout():

    st.query_params.clear()

    keys = list(
        st.session_state.keys()
    )

    for key in keys:
        del st.session_state[key]


# =========================================
# LOGIN
# =========================================
def login():

    st.sidebar.markdown(
        "### 🔐 Cuenta"
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

        # validar sesión
        if isinstance(user, dict):

            st.sidebar.success(
                f"👤 {user['username']}"
            )

            if st.sidebar.button(
                "Cerrar sesión"
            ):

                logout()
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

    if st.sidebar.button("Entrar"):

        user = login_user(
            username,
            password
        )

        # =========================================
        # DEBUG LOGIN PERSISTENTE
        # =========================================
        st.session_state[
            "debug_login"
        ] = user

        st.session_state[
            "debug_login_type"
        ] = str(type(user))

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

            token = str(
                uuid.uuid4()
            )

            # sesión
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

            # =================================
            # PERSISTENCIA URL
            # =================================
            st.query_params.update({

                "token": token,

                "username":
                    user["username"],

                "role":
                    user["role"],

                "company_id":
                    str(
                        user["company_id"]
                    )
            })

            st.rerun()

        # =================================
        # LOGIN ERROR
        # =================================
        else:

            st.sidebar.error(
                "Credenciales incorrectas"
            )


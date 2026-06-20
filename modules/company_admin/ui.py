import pandas as pd
import streamlit as st

from core.database import get_connection
from core.db_utils import p

from modules.auth.repository import (
    create_user,
    reset_password,
    get_users_by_company,
    user_belongs_to_company,
    update_user,
    toggle_user,
    delete_user
)

from modules.admin.repository import (
    create_asset_type,
    get_asset_types,
    create_system,
    get_systems
)

from modules.systems.repository import (
    delete_system
)


# =========================================
# ROLES PERMITIDOS
# =========================================
ALLOWED_ROLES = ["operator", "viewer"]


# =========================================
# PANEL COMPANY ADMIN
# =========================================
def company_admin_panel():

    role = st.session_state.get("role")

    if role != "company_admin":
        st.error("Acceso restringido")
        st.stop()

    company_id = st.session_state.get(
        "company_id"
    )

    if not company_id:
        st.error("Empresa no asignada")
        st.stop()

    # =========================================
    # OBTENER NOMBRE EMPRESA
    # =========================================
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        f"""
        SELECT name
        FROM companies
        WHERE id = {p()}
        """,
        (company_id,)
    )

    row = cursor.fetchone()
    company_name = row[0] if row else "—"

    cursor.close()
    conn.close()

    # =========================================
    # HEADER
    # =========================================
    st.title(
        f"🏭 {company_name}"
    )

    st.caption(
        "Panel de administración de empresa"
    )

    tab1, tab2, tab3 = st.tabs([
        "Usuarios",
        "Sistemas",
        "Tipos de activo"
    ])

    # ==================================================
    # TAB USUARIOS
    # ==================================================
    with tab1:

        _render_users_tab(company_id)

    # ==================================================
    # TAB SISTEMAS
    # ==================================================
    with tab2:

        _render_systems_tab(company_id)

    # ==================================================
    # TAB TIPOS
    # ==================================================
    with tab3:

        _render_asset_types_tab(company_id)


# ==================================================
# USUARIOS
# ==================================================
def _render_users_tab(company_id):

    # ==================================================
    # CREAR USUARIO
    # ==================================================
    st.subheader("➕ Crear usuario")

    with st.form("ca_create_user_form"):

        username = st.text_input("Usuario")

        password = st.text_input(
            "Contraseña",
            type="password"
        )

        role = st.selectbox(
            "Rol",
            ALLOWED_ROLES
        )

        submitted = st.form_submit_button(
            "Crear usuario"
        )

        if submitted:

            if not username or not password:

                st.warning(
                    "Completa usuario y contraseña"
                )

            else:

                ok, msg = create_user(
                    username,
                    password,
                    role,
                    company_id
                )

                if ok:
                    st.success(msg)
                    st.rerun()
                else:
                    st.error(msg)

    st.divider()

    # ==================================================
    # TABLA USUARIOS
    # ==================================================
    st.subheader("👥 Usuarios de la empresa")

    users = get_users_by_company(company_id)

    if not users:
        st.info("No hay usuarios")
        return

    df_users = pd.DataFrame(users)

    # ==================================================
    # ESTADO VISUAL
    # ==================================================
    if "active" in df_users.columns:

        df_users["Estado"] = df_users["active"].map({
            1: "Activo",
            0: "Inactivo"
        })

    df_display = df_users.drop(
        columns=["active"],
        errors="ignore"
    )

    df_display = df_display.rename(
        columns={
            "id": "ID",
            "username": "Usuario",
            "role": "Rol",
            "company": "Empresa"
        }
    )

    st.dataframe(df_display)

    st.divider()

    # ==================================================
    # EDITAR USUARIO
    # ==================================================
    st.subheader("✏️ Editar usuario")

    selected_user = st.selectbox(
        "Seleccionar usuario",
        users,
        format_func=lambda x:
            f"{x['username']} ({x['role']})",
        key="ca_select_user"
    )

    current_username = st.session_state[
        "user"
    ]["username"]

    is_self = (
        selected_user["username"]
        == current_username
    )

    col1, col2 = st.columns(2)

    # =========================================
    # DATOS
    # =========================================
    with col1:

        new_role = st.selectbox(
            "Rol",
            ALLOWED_ROLES,
            index=ALLOWED_ROLES.index(
                selected_user["role"]
            ) if selected_user["role"]
            in ALLOWED_ROLES else 0,
            key="ca_new_role"
        )

        if st.button(
            "Actualizar rol",
            key="ca_update_role"
        ):

            if not user_belongs_to_company(
                selected_user["id"],
                company_id
            ):
                st.error(
                    "Usuario no pertenece "
                    "a esta empresa"
                )

            else:

                ok, msg = update_user(
                    selected_user["id"],
                    new_role,
                    company_id
                )

                if ok:
                    st.success(msg)
                    st.rerun()
                else:
                    st.error(msg)

    # =========================================
    # ACCIONES
    # =========================================
    with col2:

        active_value = bool(
            selected_user["active"]
        )

        active_toggle = st.toggle(
            "Usuario activo",
            value=active_value,
            key="ca_active_toggle"
        )

        if is_self:

            st.warning(
                "No puedes desactivar "
                "tu propio usuario"
            )

        else:

            if st.button(
                "Actualizar estado",
                key="ca_update_status"
            ):

                if not user_belongs_to_company(
                    selected_user["id"],
                    company_id
                ):
                    st.error(
                        "Usuario no pertenece "
                        "a esta empresa"
                    )

                else:

                    ok, msg = toggle_user(
                        selected_user["id"],
                        1 if active_toggle else 0
                    )

                    if ok:
                        st.success(msg)
                        st.rerun()
                    else:
                        st.error(msg)

        st.divider()

        if is_self:

            st.warning(
                "No puedes eliminar "
                "tu propio usuario"
            )

        else:

            if st.button(
                "Eliminar usuario",
                key="ca_delete_user"
            ):

                if not user_belongs_to_company(
                    selected_user["id"],
                    company_id
                ):
                    st.error(
                        "Usuario no pertenece "
                        "a esta empresa"
                    )

                else:

                    ok, msg = delete_user(
                        selected_user["id"]
                    )

                    if ok:
                        st.warning(msg)
                        st.rerun()
                    else:
                        st.error(msg)

    st.divider()

    # ==================================================
    # RESET PASSWORD
    # ==================================================
    st.subheader("🔐 Reset contraseña")

    new_pass = st.text_input(
        "Nueva contraseña",
        type="password",
        key="ca_new_pass"
    )

    confirm_pass = st.text_input(
        "Confirmar contraseña",
        type="password",
        key="ca_confirm_pass"
    )

    if st.button(
        "Actualizar contraseña",
        key="ca_reset_pass"
    ):

        if not new_pass:

            st.warning(
                "Ingresa una contraseña"
            )

        elif new_pass != confirm_pass:

            st.error(
                "Las contraseñas no coinciden"
            )

        else:

            if not user_belongs_to_company(
                selected_user["id"],
                company_id
            ):
                st.error(
                    "Usuario no pertenece "
                    "a esta empresa"
                )

            else:

                ok, msg = reset_password(
                    selected_user["id"],
                    new_pass
                )

                if ok:
                    st.success(msg)
                    st.rerun()
                else:
                    st.error(msg)


# ==================================================
# SISTEMAS
# ==================================================
def _render_systems_tab(company_id):

    st.subheader("📍 Sistemas registrados")

    systems = get_systems(company_id)

    if systems:

        for system in systems:

            col_info, col_delete = st.columns(
                [5, 1]
            )

            with col_info:

                st.markdown(
                    f"""
                    📍 **{system['name']}**

                    ⚙️ Tipo: {system.get('type', '—')}

                    🧪 Método: {system.get('chemistry_model', '—')}
                    """
                )

            with col_delete:

                if st.button(
                    "🗑️",
                    key=f"ca_del_sys_{system['id']}"
                ):

                    st.session_state[
                        "ca_confirm_delete_system"
                    ] = system["id"]

            if (
                st.session_state.get(
                    "ca_confirm_delete_system"
                )
                == system["id"]
            ):

                st.warning(
                    f"¿Eliminar sistema "
                    f"**{system['name']}**?"
                )

                col_yes, col_no = st.columns(2)

                with col_yes:

                    if st.button(
                        "✅ Sí",
                        key=f"ca_yes_{system['id']}"
                    ):

                        delete_system(
                            system["id"]
                        )

                        st.session_state[
                            "ca_confirm_delete_system"
                        ] = None

                        st.success(
                            "Sistema eliminado"
                        )

                        st.rerun()

                with col_no:

                    if st.button(
                        "❌ No",
                        key=f"ca_no_{system['id']}"
                    ):

                        st.session_state[
                            "ca_confirm_delete_system"
                        ] = None

                        st.rerun()

            st.divider()

    else:

        st.info("Sin sistemas registrados")

    # ==================================================
    # AGREGAR SISTEMA
    # ==================================================
    st.subheader("➕ Nuevo sistema")

    asset_types = get_asset_types(company_id)

    if asset_types:

        new_system = st.text_input(
            "Nombre del sistema",
            key="ca_new_system"
        )

        type_options = {
            t["name"]: t["id"]
            for t in asset_types
        }

        selected_type = st.selectbox(
            "Tipo de sistema",
            list(type_options.keys()),
            key="ca_system_type"
        )

        selected_chemistry = st.selectbox(
            "Método químico",
            [
                "Índice de Saturación de Langelier (LSI)",
                "Índice de Estabilidad de Ryznar (RSI)"
            ],
            key="ca_chemistry"
        )

        if st.button(
            "Agregar sistema",
            key="ca_add_system"
        ):

            if new_system:

                ok, msg = create_system(
                    company_id,
                    new_system,
                    type_options[selected_type],
                    selected_chemistry
                )

                if ok:
                    st.success(msg)
                    st.rerun()
                else:
                    st.error(msg)

            else:

                st.warning(
                    "Ingresa nombre del sistema"
                )

    else:

        st.info(
            "Primero crea un tipo de activo "
            "en la pestaña 'Tipos de activo'"
        )


# ==================================================
# TIPOS DE ACTIVO
# ==================================================
def _render_asset_types_tab(company_id):

    st.subheader("⚙️ Tipos de activo")

    asset_types = get_asset_types(company_id)

    if asset_types:

        df_types = pd.DataFrame(asset_types)

        df_types = df_types.rename(
            columns={
                "id": "ID",
                "name": "Nombre"
            }
        )

        df_types = df_types.drop(
            columns=["company_id"],
            errors="ignore"
        )

        st.dataframe(df_types)

    else:

        st.info("Sin tipos registrados")

    st.divider()

    # ==================================================
    # CREAR TIPO
    # ==================================================
    st.subheader("➕ Nuevo tipo de activo")

    new_type = st.text_input(
        "Nombre (Cisterna, Chiller, Torre...)",
        key="ca_new_type"
    )

    if st.button(
        "Agregar tipo",
        key="ca_add_type"
    ):

        if new_type:

            create_asset_type(
                new_type,
                company_id
            )

            st.success("Tipo agregado")
            st.rerun()

        else:

            st.warning("Ingresa un nombre")

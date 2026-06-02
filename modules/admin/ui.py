import pandas as pd
import streamlit as st

from core.auth import is_admin
from core.database import get_connection

from modules.auth.repository import (
    create_user,
    reset_password,
    get_all_users,
    update_user,
    toggle_user,
    delete_user
)

from modules.admin.repository import (
    create_company,
    get_companies,
    create_asset_type,
    get_asset_types,
    create_system,
    get_systems,
    get_companies_grouped,
    update_company_status
)

from modules.systems.repository import (
    delete_system
)
# -----------------------------
# PANEL ADMIN
# -----------------------------
def admin_panel():

    if not is_admin():
        st.error("Acceso restringido")
        st.stop()

    st.title("⚙️ Panel de Administración")

    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "Usuarios",
        "Empresas",
        "Base de datos",
        "Visitas",
        "Contactos"
    ])

    # ==================================================
    # TAB USUARIOS
    # ==================================================
    with tab1:

        # -----------------------------
        # COMPANIES
        # -----------------------------
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT id, name
            FROM companies
            ORDER BY name
        """)

        companies = cursor.fetchall()

        cursor.close()
        conn.close()

        company_map = {
            c[1]: c[0]
            for c in companies
        }

        # ==================================================
        # CREAR USUARIO
        # ==================================================
        st.subheader("➕ Crear usuario")

        with st.form("create_user_form"):

            username = st.text_input("Usuario")

            password = st.text_input(
                "Contraseña",
                type="password"
            )

            role = st.selectbox(
                "Rol",
                [
                    "admin",
                    "operator",
                    "viewer"
                ]
            )

            company_name = st.selectbox(
                "Empresa",
                list(company_map.keys())
            )

            submitted = st.form_submit_button(
                "Crear usuario"
            )

            if submitted:

                ok, msg = create_user(
                    username,
                    password,
                    role,
                    company_map[company_name]
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
        st.subheader("👥 Usuarios")

        users = get_all_users()

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

        # ==================================================
        # ELIMINAR COLUMNAS TÉCNICAS
        # ==================================================
        df_users = df_users.drop(
            columns=["active"],
            errors="ignore"
        )


        
        # ==================================================
        # RENOMBRAR COLUMNAS
        # ==================================================
        df_users = df_users.rename(
            columns={
                "id": "ID",
                "username": "Usuario",
                "role": "Rol",
                "company_id": "Empresa"
            }
        )

        st.dataframe(df_users)

        st.divider()

        # ==================================================
        # EDITAR USUARIO
        # ==================================================
        st.subheader("✏️ Editar usuario")

        selected_user = st.selectbox(
            "Seleccionar usuario",
            users,
            format_func=lambda x:
                f"{x['username']} (ID {x['id']})"
        )

        current_username = st.session_state["user"]

        is_self = (
            selected_user["username"] == current_username
        )

        col1, col2 = st.columns(2)

        # -----------------------------
        # DATOS
        # -----------------------------
        with col1:

            new_role = st.selectbox(
                "Rol",
                [
                    "admin",
                    "operator",
                    "viewer"
                ],
                index=[
                    "admin",
                    "operator",
                    "viewer"
                ].index(selected_user["role"])
            )

            company_name_edit = st.selectbox(
                "Empresa",
                list(company_map.keys())
            )

            if st.button("Actualizar usuario"):

                ok, msg = update_user(
                    selected_user["id"],
                    new_role,
                    company_map[company_name_edit]
                )

                if ok:
                    st.success(msg)
                    st.rerun()
                else:
                    st.error(msg)

        # -----------------------------
        # ACCIONES
        # -----------------------------
        with col2:

            active_value = bool(
                selected_user["active"]
            )

            active_toggle = st.toggle(
                "Usuario activo",
                value=active_value
            )

            if is_self:

                st.warning(
                    "No puedes desactivar tu propio usuario"
                )

            else:

                if st.button("Actualizar estado"):

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
                    "No puedes eliminar tu propio usuario"
                )

            else:

                if st.button("Eliminar usuario"):

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
            type="password"
        )

        confirm_pass = st.text_input(
            "Confirmar contraseña",
            type="password"
        )

        if st.button("Actualizar contraseña"):

            if not new_pass:
                st.warning("Ingresa una contraseña")

            elif new_pass != confirm_pass:
                st.error("Las contraseñas no coinciden")

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
        # TAB EMPRESAS
        # ==================================================
        with tab2:

            # ==================================================
            # EMPRESAS REGISTRADAS
            # ==================================================

            # Título sección empresas
            st.subheader("📋 Empresas registradas")

            # ==============================================
            # OBTENER EMPRESAS DESDE DB
            # ==============================================
            # La función regresa una lista de empresas
            # junto con sus sistemas relacionados
            companies = get_companies_grouped()

            # ==============================================
            # RECORRER EMPRESAS
            # ==============================================
            for company in companies:

                # ==========================================
                # EXPANDER EMPRESA
                # ==========================================
                # Cada empresa se muestra en un panel
                # desplegable independiente
                with st.expander(
                    f"🏭 {company['name']}"
                ):

                    # ======================================
                    # SISTEMAS DE LA EMPRESA
                    # ======================================
                    st.subheader("📍 Sistemas")

                    # ======================================
                    # LISTA SISTEMAS
                    # ======================================
                    # Obtiene todos los sistemas
                    # asociados a la empresa
                    systems = company["systems"]

                    # ======================================
                    # VALIDAR SI EXISTEN SISTEMAS
                    # ======================================
                    if systems:

                        # ==================================
                        # RECORRER SISTEMAS
                        # ==================================
                        for system in systems:

                            # ==============================
                            # COLUMNAS
                            # ==============================
                            # Columna izquierda:
                            # información sistema
                            #
                            # Columna derecha:
                            # botón eliminar
                            col_info, col_delete = st.columns(
                                [5, 1]
                            )

                            # ==============================
                            # INFO SISTEMA
                            # ==============================
                            with col_info:

                                # ==========================
                                # MOSTRAR DATOS SISTEMA
                                # ==========================
                                st.markdown(
                                    f"""
                                    📍 **{system['place_name']}** 📍
                                    
                                    ⚙️ Tipo: {system['asset_type']}
                                    
                                    🧪 Método: {system['chemistry_model']}
                                    """
                                )

                            # ==============================
                            # ELIMINAR SISTEMA
                            # ==============================
                            with col_delete:

                                # ==========================
                                # BOTÓN ELIMINAR
                                # ==========================
                                if st.button(
                                    "🗑️ Eliminar",
                                    key=f"delete_system_{system['id']}"
                                ):

                                    st.session_state[
                                        "confirm_delete_system"
                                    ] = system["id"]

                            # ======================================
                            # CONFIRMACIÓN ELIMINAR
                            # ======================================
                            if (
                                st.session_state.get(
                                    "confirm_delete_system"
                                )
                                == system["id"]
                            ):

                                st.warning(
                                    f"""
                            ¿Seguro que deseas eliminar
                            el sistema:

                            {system['place_name']}?
                                    """
                                )

                                col_yes, col_no = st.columns(2)

                                # ==================================
                                # CONFIRMAR
                                # ==================================
                                with col_yes:

                                    if st.button(
                                        "✅ Sí eliminar",
                                        key=f"confirm_yes_{system['id']}"
                                    ):

                                        delete_system(
                                            system["id"]
                                        )

                                        st.session_state[
                                            "confirm_delete_system"
                                        ] = None

                                        st.success(
                                            "Sistema eliminado"
                                        )

                                        st.rerun()

                                # ==================================
                                # CANCELAR
                                # ==================================
                                with col_no:

                                    if st.button(
                                        "❌ Cancelar",
                                        key=f"cancel_delete_{system['id']}"
                                    ):

                                        st.session_state[
                                            "confirm_delete_system"
                                        ] = None

                                        st.rerun()

                            # ==============================
                            # SEPARADOR SISTEMAS
                            # ==============================
                            st.divider()

                    # ======================================
                    # SIN SISTEMAS
                    # ======================================
                    else:

                        # Mensaje si empresa no tiene sistemas
                        st.info(
                            "Sin sistemas"
                        )



                    # ==================================================
                    # AGREGAR SISTEMA
                    # ==================================================
                    st.subheader("📍 Nuevo sistema (Hotel, Torre...)")

                    asset_types = get_asset_types(
                        company["id"]
                    )

                    if asset_types:

                        new_system = st.text_input(
                            "Nombre sistema",
                            key=f"system_{company['id']}"
                        )

                        type_options = {
                            t["name"]: t["id"]
                            for t in asset_types
                        }

                        selected_type = st.selectbox(
                            "Tipo sistema",
                            list(type_options.keys()),
                            key=f"select_{company['id']}"
                        )

                        selected_chemistry = st.selectbox(
                        "Método químico",
                        [
                            "Índice de Saturación de Langelier (LSI)",
                            "Índice de Estabilidad de Ryznar (RSI)"
                        ],
                        key=f"chem_{company['id']}"
                    )

                        if st.button(
                            "Agregar sistema",
                            key=f"btn_system_{company['id']}"
                        ):

                            if new_system:

                                ok, msg = create_system(
                                            company["id"],
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
                                    "Ingresa nombre sistema"
                                )

                    else:

                        st.info(
                            "Primero crea tipos"
                        )

                    st.divider()

                    # ==================================================
                    # AGREGAR TIPO
                    # ==================================================
                    st.subheader("⚙️ Nuevo tipo (Cisterna, Chiller...)")

                    new_type = st.text_input(
                        "Nuevo tipo",
                        key=f"type_{company['id']}"
                    )

                    if st.button(
                        "Agregar tipo",
                        key=f"btn_type_{company['id']}"
                    ):

                        if new_type:

                            create_asset_type(
                                new_type,
                                company["id"]
                            )

                            st.success(
                                "Tipo agregado"
                            )

                            st.rerun()

                        else:

                            st.warning(
                                "Ingresa nombre"
                            )

                    st.divider()

                    # ==================================================
                    # ESTADO EMPRESA
                    # ==================================================
                    st.subheader("🛡️ Estado empresa")

                    company_active = st.toggle(
                        "Empresa activa",
                        value=company.get("active", True),
                        key=f"active_{company['id']}"
                    )

                    if st.button(
                        "Actualizar estado",
                        key=f"update_company_{company['id']}"
                    ):

                        ok, msg = update_company_status(
                            company["id"],
                            company_active
                        )

                        if ok:

                            st.success(msg)
                            st.rerun()

                        else:

                            st.error(msg)

            st.subheader("🏭 Nueva empresa")

            # ==================================================
            # CREAR EMPRESA
            # ==================================================
            company_name = st.text_input(
                "Nueva empresa"
            )

            # ==================================================
            # NOMBRE DEL LUGAR / SISTEMA
            # ==================================================
            place_name = st.text_input(
                "Nombre del lugar"
            )

            # ==================================================
            # TIPO DE ASSET
            # ==================================================
            asset_type_name = st.text_input(
                "Tipo del sistema"
            )

            # ==================================================
            # MÉTODO QUÍMICO
            # ==================================================
            chemistry_model = st.selectbox(
                "Método químico",
                [
                    "Índice de Saturación de Langelier (LSI)",
                    "Índice de Estabilidad de Ryznar (RSI)"
                ]
            )

            if st.button("Crear empresa"):

                if (
                    company_name
                    and place_name
                    and asset_type_name                    
                ):

                    ok, msg = create_company(
                        company_name,
                        chemistry_model,
                        asset_type_name,
                        place_name
                    )

                    if ok:

                        st.success(msg)

                        st.rerun()

                    else:

                        st.error(msg)

                    st.success("Empresa creada")

                    st.rerun()

                else:

                    st.warning(
                        "Completa todos los campos"
                    )

            st.divider()
        
            
        # ==================================================
        # TAB BASE DATOS
        # ==================================================
        with tab3:

            st.subheader("🗄️ Migraciones")

            conn = get_connection()
            cursor = conn.cursor()

            try:

                cursor.execute("""
                    SELECT *
                    FROM migrations
                """)

                data = cursor.fetchall()

                st.dataframe(data)

            except Exception as e:

                st.error(f"Error DB: {e}")

            finally:

                cursor.close()
                conn.close()

        # ==================================================
        # TAB VISITAS
        # ==================================================
        with tab4:

            st.subheader("📈 Analítica pública")

            conn = get_connection()
            cursor = conn.cursor()

            try:

                # =====================================
                # TOTAL VISITAS
                # =====================================
                cursor.execute("""
                    SELECT COUNT(*)
                    FROM analytics_visits
                """)

                total_visitas = cursor.fetchone()[0]

                # =====================================
                # VISITAS HOY
                # =====================================
                cursor.execute("""
                    SELECT COUNT(*)
                    FROM analytics_visits
                    WHERE DATE(visit_date) = CURRENT_DATE
                """)

                visitas_hoy = cursor.fetchone()[0]

                col1, col2 = st.columns(2)

                with col1:
                    st.metric(
                        "Visitas totales",
                        total_visitas
                    )

                with col2:
                    st.metric(
                        "Visitas hoy",
                        visitas_hoy
                    )

                # =====================================
                # ÚLTIMAS VISITAS
                # =====================================
                cursor.execute("""
                    SELECT *
                    FROM analytics_visits
                    ORDER BY id DESC
                    LIMIT 100
                """)

                data = cursor.fetchall()

                st.subheader(
                    "Últimas visitas"
                )

                st.dataframe(
                    data
                )

            except Exception as e:

                st.error(
                    f"Error: {e}"
                )

            finally:

                cursor.close()
                conn.close()

        # ==================================================
        # TAB CONTACTOS
        # ==================================================
        with tab5:

            st.subheader(
                "📧 Solicitudes de contacto"
            )

            conn = get_connection()
            cursor = conn.cursor()

            try:

                cursor.execute("""
                    SELECT
                        id,
                        created_at,
                        name,
                        email,
                        message,
                        status
                    FROM contact_requests
                    ORDER BY created_at DESC
                """)

                data = cursor.fetchall()

                if data:

                    df = pd.DataFrame(
                        data,
                        columns=[
                            "ID",
                            "Fecha",
                            "Nombre",
                            "Correo",
                            "Mensaje",
                            "Estado"
                        ]
                    )

                    st.dataframe(
                        df
                    )

                else:

                    st.info(
                        "No hay solicitudes de contacto."
                    )

            except Exception as e:

                st.error(
                    f"Error: {e}"
                )

            finally:

                cursor.close()
                conn.close()
import streamlit as st
import pandas as pd

from modules.operator.repository import (
    get_company_dashboard_data
)

from modules.analytics.service import (
    calcular_lsi,
    clasificar_lsi
)

from modules.analytics.service import (
    calcular_lsi_dual
)

from core.lsi_log import (
    componentes_log
)

from modules.analytics.repository import (
    save_analysis,
    get_analysis_by_system,
    delete_analysis
)

from core.lsi_table import (

    calcular_lsi as calcular_lsi_tablas,

    componentes_tabla

)

from core.lsi_table import calcular_lsi

from core.lsi_log import (
    calcular_lsi_log as calcular_lsi_log
)

from core.lsi_table import (
    calcular_lsi as calcular_lsi_tab
)

from modules.operator.graphs import (
    render_graphs
)

from modules.operator.optimization import (
    render_optimization
)


def operator_dashboard():

    # ======================================
    # OBTENER USUARIO EN SESIÓN
    # ======================================
    # Recupera el usuario guardado
    # después del login.
    user = st.session_state.get(
        "user"
    )

    # ======================================
    # VALIDAR SESIÓN
    # ======================================
    # Verifica que exista una sesión válida.
    # Si no existe, detiene el dashboard.
    if not isinstance(user, dict):

        st.error(
            "Sesión inválida. "
            "Vuelve a iniciar sesión."
        )

        return

    # ======================================
    # OBTENER COMPANY_ID
    # ======================================
    # Recupera el ID de empresa
    # asociado al usuario logueado.
    company_id = user.get(
        "company_id"
    )

    # ======================================
    # CARGAR DATOS DASHBOARD
    # ======================================
    # Consulta sistemas y datos
    # asociados a la empresa.
    data = get_company_dashboard_data(
        company_id
    )

    # ======================================
    # VALIDAR INFORMACIÓN
    # ======================================
    # Si no existen sistemas o datos
    # muestra advertencia.
    if not data:

        st.warning(
            "No hay información"
        )

        return

    # ======================================
    # OBTENER NOMBRE EMPRESA
    # ======================================
    # Toma el nombre de empresa
    # del primer registro.
    company_name = data[0][
        "company_name"
    ]

    # ======================================
    # SIDEBAR EMPRESA
    # ======================================
    # Muestra información general
    # de empresa en sidebar.
    st.sidebar.subheader(
        "🏭 Empresa"
    )

    st.sidebar.success(
        company_name
    )

    # ======================================
    # CREAR OPCIONES DE SISTEMA
    # ======================================
    # Convierte la lista de sistemas
    # en diccionario:
    #
    # {
    #   "Hotel A": row,
    #   "Hotel B": row
    # }
    system_options = {

        row["system_name"]: row

        for row in data
    }

    # ======================================
    # SEPARADOR VISUAL
    # ======================================
    st.divider()

    # ======================================
    # SELECTOR DE SISTEMA
    # ======================================
    # Permite seleccionar sistema
    # desde sidebar.
    selected_system = st.sidebar.selectbox(

        "--Selecciona un sistema para continuar--",

        list(system_options.keys())

    )

    # ======================================
    # OBTENER SISTEMA SELECCIONADO
    # ======================================
    # Recupera el diccionario completo
    # del sistema seleccionado.
    system = system_options[
        selected_system
    ]

    # ======================================
    # GUARDAR SISTEMA EN SESIÓN
    # ======================================
    # Guarda información para utilizarla
    # posteriormente en consultas SQL.
    st.session_state.system_id = (
        system["system_id"]
    )

    st.session_state.system_name = (
        system["system_name"]
    )

    # ======================================
    # INFO SISTEMA SIDEBAR
    # ======================================
    # Muestra:
    #
    # • tipo sistema
    # • método químico
    st.sidebar.markdown(
        f"""
        ### 
        ⚙️ **Tipo:**  
        {system['asset_type']}

        🧪 **Método químico:**  
        {system['chemistry_model']}
        """
    )

    # ======================================
    # COLUMNAS TÍTULO
    # ======================================
    # Layout superior:
    #
    # izquierda -> título dashboard
    # derecha   -> nombre sistema
    col_title_1, col_title_2 = st.columns(
        [3, 2]
    )

    # ======================================
    # TÍTULO PRINCIPAL
    # ======================================
    with col_title_1:

        st.title(
            "📊 Dashboard Operativo"
        )

    # ======================================
    # NOMBRE SISTEMA
    # ======================================
    with col_title_2:

        st.markdown(
            f"""
            <h2 style="
                margin-top:18px;
                font-size:24px;
                color:white;
                font-weight:700;
            ">
                📍{system['system_name']}📍
            </h2>
            """,
            unsafe_allow_html=True
        )

    # ======================================
    # DATAFRAME GLOBAL
    # ======================================
    # Variable principal utilizada
    # para guardar información cargada.
    df = None

    # ======================================
    # LAYOUT PRINCIPAL
    # ======================================
    # Divide dashboard en:
    #
    # • izquierda
    # • centro
    # • derecha
    col_left, col_center, col_right = st.columns(
        [1, 1.2, 1.5]
    )

    # ======================================
    # LEFT PANEL
    # ======================================
    with col_left:

        with st.container(border=True):

            # ==================================
            # MODELO QUÍMICO
            # ==================================
            chemistry_model = system[
                "chemistry_model"
            ]

            # ==================================
            # SISTEMAS LSI
            # ==================================
            if "LSI" in chemistry_model:

                st.info(
                    """
                    Sistema configurado
                    para índice Lengelier
                    """
                )

                # ==================================
                # MENÚ ANÁLISIS
                # ==================================
                analysis_option = st.selectbox(

                    "Selecciona análisis",

                    [

                        "📋 Datos campo",

                        "📈 Gráficas",

                        "🧠 Optimización",

                        "📊 KPI",
                                                
                        "⚠️ Alertas",

                        "📄 Reporte"


                    ]

                )
            
                # ==================================
                # INICIALIZAR KEYS
                # ==================================
                if "uploader_key" not in st.session_state:

                    st.session_state.uploader_key = 0

                if "upload_success" not in st.session_state:

                    st.session_state.upload_success = False

                # ==================================
                # FILE UPLOADER
                # ==================================
                uploaded_file = st.file_uploader(

                    "Selecciona archivo Excel",

                    type=["xlsx", "xls", "csv"],

                    key=f"uploader_{st.session_state.uploader_key}"

                )

                # ==================================
                # BOTÓN CARGAR
                # ==================================
                if uploaded_file is not None:

                    if st.button(
                        "📤 Cargar archivo"
                    ):

                        try:

                            # ==========================
                            # LEER EXCEL
                            # ==========================
                            if uploaded_file.name.endswith(
                                (".xlsx", ".xls")
                            ):

                                df = pd.read_excel(
                                    uploaded_file
                                )

                                

                            # ==========================
                            # LEER CSV
                            # ==========================
                            else:

                                df = pd.read_csv(
                                    uploaded_file
                                )
                                
                                                
                            # ==========================
                            # CALCULAR COMPONENTES LSI
                            # ==========================
                            results = df.apply(

                                lambda row:
                                componentes_log(

                                    ph=row["pH"],

                                    tds=row["tds_ppm"],

                                    temp=row["temperature_c"],

                                    calcium=row[
                                        "calcium_hardness"
                                    ],

                                    alkalinity=row[
                                        "alkalinity"
                                    ]

                                ),

                                axis=1

                            )

                            # ==========================
                            # RESULTADOS → DATAFRAME
                            # ==========================
                            results_df = pd.DataFrame(
                                results.tolist()
                            )

                            # ==========================
                            # CONCATENAR RESULTADOS
                            # ==========================
                            df = pd.concat(

                                [
                                    df,
                                    results_df
                                ],

                                axis=1
                            )

                            
                            # ==================================
                            # LSI TABLAS
                            # ==================================
                            lsi_tab_results = []

                            for _, row in df.iterrows():

                                try:

                                    result = calcular_lsi_tablas(

                                        ph=float(row["pH"]),

                                        temperature_c=float(
                                            row["temperature_c"]
                                        ),

                                        tds_ppm=float(
                                            row["tds_ppm"]
                                        ),

                                        calcium_hardness=float(
                                            row["calcium_hardness"]
                                        ),

                                        alkalinity=float(
                                            row["alkalinity"]
                                        )

                                    )

                                    lsi_tab_results.append(result)

                                except Exception as e:

                                    print("ERROR LSI TAB:", e)

                                    lsi_tab_results.append(None)

                            # ==================================
                            # GUARDAR RESULTADOS
                            # ==================================
                            df["lsi_tablas"] = lsi_tab_results

                            # ==========================
                            # IMPORTAR DATETIME
                            # ==========================
                            from datetime import datetime

                            # ==================================
                            # SISTEMA SELECCIONADO
                            # ==================================
                            selected_system_id = (
                                st.session_state.system_id
                            )

                            # ==================================
                            # COLUMNAS EMPRESA
                            # ==================================
                            df["company_id"] = (
                                st.session_state.company_id
                            )

                            df["company_name"] = (
                                company_name
                            )

                            # ==================================
                            # COLUMNAS SISTEMA
                            # ==================================
                            df["system_id"] = (
                                selected_system_id
                            )

                            df["system_name"] = (
                                system["system_name"]
                            )

                            # ==================================
                            # MÉTODO UTILIZADO
                            # ==================================
                            df["method"] = (
                                "LSI Logarítmico"
                            )

                            # ==================================
                            # FECHA CREACIÓN
                            # ==================================
                            df["created_at"] = (
                                datetime.now().isoformat()
                            )

                            # ==================================
                            # DATAFRAME PARA SQL
                            # ==================================
                            df_db = pd.DataFrame({

                                "company_id":
                                    df["company_id"],

                                "company_name":
                                    df["company_name"],

                                "system_id":
                                    df["system_id"],

                                "system_name":
                                    df["system_name"],

                                "method":
                                    df["method"],

                                "sample_date":
                                    df["date"],

                                "ph":
                                    df["pH"],

                                "temperature_c":
                                    df["temperature_c"],

                                "tds_ppm":
                                    df["tds_ppm"],

                                "calcium_hardness":
                                    df["calcium_hardness"],

                                "alkalinity":
                                    df["alkalinity"],

                                "factor_a":
                                    df["factor_A"],

                                "factor_b":
                                    df["factor_B"],

                                "factor_c":
                                    df["factor_C"],

                                "factor_d":
                                    df["factor_D"],

                                "ph_s":
                                    df["ph_saturacion"],

                                "lsi":
                                    df["lsi"],
                                
                                "lsi_tablas":
                                    df["lsi_tablas"],

                                "created_at":
                                    df["created_at"]
                            })

                            # ==================================
                            # GUARDAR EN DATABASE
                            # ==================================
                            save_analysis(df_db)

                            # ==================================
                            # MENSAJE SUCCESS
                            # ==================================
                            st.session_state[
                                "upload_success"
                            ] = True

                            # ==================================
                            # RESET FILE UPLOADER
                            # ==================================
                            st.session_state[
                                "uploader_key"
                            ] += 1

                            # ==================================
                            # RECARGAR APP
                            # ==================================
                            st.rerun()

                        # ==================================
                        # CAPTURA ERRORES
                        # ==================================
                        except Exception as e:

                            st.exception(e)

                # ==================================
                # MENSAJE ÉXITO
                # ==================================
                if st.session_state.upload_success:

                    st.success(
                        "Archivo cargado correctamente"
                    )


            # ==================================
            # RSI
            # ==================================
            elif "RSI" in chemistry_model:

                st.info(
                    """
                    Sistema configurado
                    para índice Ryznar
                    """
                )

    # ======================================
    # CENTER
    # ======================================
    with col_center:

        with st.container(border=True):

            # ======================================
            # RESULTADOS SESSION
            # ======================================
            lsi_result = st.session_state.get(

                "lsi_result",

                {
                    "log": "****",
                    "tab": "****"
                }
            )

            

            st.subheader(
                "🧮 Calculadora"
            )

           
            st.success(f"""

            LSI_log: {lsi_result['log']}

            LSI_tab: {lsi_result['tab']}

            """)

            # ==================================
            # INPUTS EN 2 COLUMNAS
            # ==================================
            input_col1, input_col2 = st.columns(
                2
            )

            # ==================================
            # INPUTS IZQUIERDA
            # ==================================
            with input_col1:

                ph = st.number_input(
                    "pH",
                    value=0.0
                )

                tds = st.number_input(
                    "TDS",
                    value=0.0
                )

                temperature = st.number_input(
                    "Temperatura °C",
                    value=0.0
                )

            # ==================================
            # INPUTS DERECHA
            # ==================================
            with input_col2:

                calcium = st.number_input(
                    "Calcio",
                    value=0.0
                )

                alkalinity = st.number_input(
                    "Alcalinidad",
                    value=0.0
                )

            # ==================================
            # BOTONES
            # ==================================
            btn_col1, btn_col2 = st.columns(2)

            # ==================================
            # CALCULAR LSI
            # ==================================
            with btn_col1:

                if st.button(
                    "🧮 Calcular"
                ):

                    # ==========================
                    # VALIDAR INPUTS
                    # ==========================
                    if (

                        ph == 0
                        or tds == 0
                        or temperature == 0
                        or calcium == 0
                        or alkalinity == 0
                    ):

                        st.warning(
                            "Completa todos los parámetros"
                        )

                    else:

                        # ==============================
                        # LSI LOGARÍTMICO
                        # ==============================
                        lsi_log = calcular_lsi_log(

                            ph=ph,

                            temp_c=temperature,

                            tds=tds,

                            calcium=calcium,

                            alkalinity=alkalinity

                        )

                        # ==============================
                        # LSI TABLAS
                        # ==============================
                        lsi_tab = calcular_lsi_tab(

                            ph=ph,

                            temperature_c=temperature,

                            tds_ppm=tds,

                            calcium_hardness=calcium,

                            alkalinity=alkalinity

                        )

                        # ==============================
                        # SAVE SESSION
                        # ==============================
                        st.session_state[
                            "lsi_result"
                        ] = {

                            "log": round(
                                lsi_log,
                                2
                            ),

                            "tab": round(
                                lsi_tab,
                                2
                            )

                        }

                        st.rerun()

            # ==================================
            # GUARDAR REGISTRO
            # ==================================
            with btn_col2:

                if st.button(
                    "💾 Agregar registro"
                ):

                    try:

                        from datetime import datetime

                        # ==========================
                        # CALCULAR LSI
                        # ==========================
                        lsi_log = calcular_lsi_log(

                            ph=ph,

                            temp_c=temperature,

                            tds=tds,

                            calcium=calcium,

                            alkalinity=alkalinity

                        )

                        lsi_tab = calcular_lsi_tab(

                            ph=ph,

                            temperature_c=temperature,

                            tds_ppm=tds,

                            calcium_hardness=calcium,

                            alkalinity=alkalinity

                        )

                        # ==========================
                        # COMPONENTES
                        # ==========================
                        result = componentes_log(

                            ph=ph,

                            tds=tds,

                            temp=temperature,

                            calcium=calcium,

                            alkalinity=alkalinity

                        )

                        # ==========================
                        # DATAFRAME
                        # ==========================
                        df_db = pd.DataFrame([{

                            "company_id":
                                st.session_state.company_id,

                            "company_name":
                                company_name,

                            "system_id":
                                st.session_state.system_id,

                            "system_name":
                                system["system_name"],

                            "method":
                                "LSI Manual",

                            "sample_date":
                                datetime.now().date(),

                            "ph":
                                ph,

                            "temperature_c":
                                temperature,

                            "tds_ppm":
                                tds,

                            "calcium_hardness":
                                calcium,

                            "alkalinity":
                                alkalinity,

                            "factor_a":
                                result["factor_A"],

                            "factor_b":
                                result["factor_B"],

                            "factor_c":
                                result["factor_C"],

                            "factor_d":
                                result["factor_D"],

                            "ph_s":
                                result["ph_saturacion"],

                            "lsi": round(lsi_log, 2),

                            "lsi_tablas": round(lsi_tab, 2),

                            "created_at":
                                datetime.now().isoformat()

                        }])

                        # ==========================
                        # GUARDAR DB
                        # ==========================
                        save_analysis(df_db)

                        st.success(
                            "Registro guardado"
                        )

                    except Exception as e:

                        st.exception(e)

        

    # ======================================
    # RIGHT
    # ======================================
    with col_right:
        with st.container(border=True):

            st.subheader(
                "📘 Información"
            )

            st.text_area(
                "Información técnica",
                value="""
        Aquí puedes agregar:

        • teoría química
        • interpretación
        • recomendaciones
        • límites operativos
        • criterios de corrosión
        • criterios de incrustación
                """,
                height=250
            )

            st.image(
                "https://upload.wikimedia.org/wikipedia/commons/3/3d/Cooling_tower.jpg",
                caption="Sistema de enfriamiento"
            )

    # ======================================
    # LOAD HISTORICAL DATA
    # ======================================
    from modules.analytics.repository import (
        get_analysis_by_system
    )

    df = get_analysis_by_system(

        company_id=st.session_state.company_id,

        system_id=st.session_state.system_id

    )

    # ======================================
    # DATOS DE CAMPO
    # ======================================
    from modules.operator.field_data_table import (
        render_field_data_table
    )

    if analysis_option == "📋 Datos campo":

        render_field_data_table(df)
    
    elif analysis_option == "📈 Gráficas":

        render_graphs(df)

    elif analysis_option == "🧠 Optimización":

        render_optimization()

    #elif analysis_option == "📄 Reporte":

        #render_report(df)
import streamlit as st
import pandas as pd

from core.lsi_log import (
    calcular_lsi_log
)

from core.lsi_table import (
    calcular_lsi
)



# ======================================
# OPTIMIZACIÓN
# ======================================
def render_optimization():

    
    st.divider()

    upload_col1, upload_col2 = st.columns(
        [3, 2]
    )

    with upload_col1:

        st.subheader(
            "🧠 Simulador de Optimización"
        )

        st.markdown(
            """
            Ajusta parámetros para observar
            cómo cambia el LSI en tiempo real.
            """
        )

        
    with upload_col2:

        uploaded_file = st.file_uploader(

            "📤 Subir Excel optimizado",

            type=[
                "xlsx",
                "xls",
                "csv"
            ],

            key="optimizer_upload"

        )

        # ==================================
        # BOTÓN SOLO SI HAY ARCHIVO
        # ==================================
        load_file = False

        if uploaded_file is not None:

            load_file = st.button(
                "📤 Cargar archivo"
            )

        df_opt = None

        # ==================================
        # LEER ARCHIVO
        # ==================================
        if uploaded_file is not None and load_file:

            if uploaded_file.name.endswith(
                ".csv"
            ):

                df_opt = pd.read_csv(
                    uploaded_file
                )

                # ==================================
                # NORMALIZAR COLUMNAS
                # ==================================
                df_opt.columns = (

                    df_opt.columns
                    .str.strip()
                    .str.lower()

                )

            else:

                df_opt = pd.read_excel(
                    uploaded_file
                )

                # ==================================
                # NORMALIZAR COLUMNAS
                # ==================================
                df_opt.columns = (

                    df_opt.columns
                    .str.strip()
                    .str.lower()

                )

                # ==================================
                # RENOMBRAR COLUMNAS
                # ==================================
                df_opt = df_opt.rename(

                    columns={

                        "sample_date": "date",

                        "ph": "ph",

                        "temperatura": "temperature_c",

                        "temperatura_c": "temperature_c",

                        "tds": "tds_ppm",

                        "calcio": "calcium_hardness",

                        "alcalinidad": "alkalinity"

                    }

                )

                

            # ==============================
            # CALCULAR LSI TABLAS
            # ==============================
            df_opt["lsi_tablas"] = df_opt.apply(

                lambda row: calcular_lsi(

                    ph=row["ph"],

                    temperature_c=row[
                        "temperature_c"
                    ],

                    tds_ppm=row[
                        "tds_ppm"
                    ],

                    calcium_hardness=row[
                        "calcium_hardness"
                    ],

                    alkalinity=row[
                        "alkalinity"
                    ]

                ),

                axis=1

            )

            # ==============================
            # FECHA
            # ==============================
            df_opt["date"] = pd.to_datetime(

                df_opt["date"]

            )

            # ==================================
            # COLUMNAS VISIBLES
            # ==================================
            visible_columns = [

                "date",

                "ph",

                "tds_ppm",

                "temperature_c",

                "calcium_hardness",

                "alkalinity",

                "lsi_tablas"

            ]

            # ==================================
            # FILTRAR COLUMNAS
            # ==================================
            existing_columns = [

                col for col in visible_columns

                if col in df_opt.columns

            ]

            df_opt = df_opt[
                existing_columns
            ]

   
    # ==================================
    # COLUMNAS
    # ==================================
    col1, col2 = st.columns(2)

    # ==================================
    # INPUTS
    # ==================================
    with col1:

        ph = st.slider(
            "pH",
            min_value=0.0,
            max_value=14.0,
            value=7.5,
            step=0.01
        )

        tds = st.slider(
            "TDS",
            min_value=0,
            max_value=5000,
            value=500,
            step=10
        )

        temp = st.slider(
            "Temperatura °C",
            min_value=0.0,
            max_value=80.0,
            value=25.0,
            step=0.1
        )

    with col2:

        calcium = st.slider(
            "Calcio",
            min_value=0,
            max_value=1000,
            value=100,
            step=1
        )

        alkalinity = st.slider(
            "Alcalinidad",
            min_value=0,
            max_value=1000,
            value=150,
            step=1
        )

    # ==================================
    # CÁLCULOS
    # ==================================
    lsi_log = calcular_lsi_log(

        ph=ph,

        tds=tds,

        temp_c=temp,

        calcium=calcium,

        alkalinity=alkalinity

    )

    lsi_tab = calcular_lsi(

        ph=ph,

        temperature_c=temp,

        tds_ppm=tds,

        calcium_hardness=calcium,

        alkalinity=alkalinity

    )

    # ==================================
    # RESULTADOS
    # ==================================
    result_col1, result_col2 = st.columns(2)

    with result_col1:

        st.metric(
            "LSI Log",
            round(lsi_log, 2)
            if lsi_log is not None
            else "Error"
        )

    with result_col2:

        st.metric(
            "LSI Tablas",
            round(lsi_tab, 2)
            if lsi_tab is not None
            else "Error"
        )

    # ==================================
    # ESTADO DEL AGUA
    # ==================================
    st.divider()

    if lsi_tab is not None:

        if lsi_tab < -0.5:

            st.error(
                "⚠️ Agua corrosiva"
            )

        elif lsi_tab > 0.5:

            st.warning(
                "⚠️ Agua incrustante"
            )

        else:

            st.success(
                "✅ Agua estable"
            )

    # ==============================
    # TABLA
    # ==============================

    if df_opt is not None:

        st.divider()

        st.subheader(
            "📋 Resultados optimizados"
        )

        st.dataframe(
            df_opt
        )

        # ==============================
        # GRÁFICA DINÁMICA PLOTLY
        # ==============================
        st.divider()

        st.subheader(
            "📈 LSI Optimizado"
        )

        import plotly.graph_objects as go

        # ==================================
        # ORDENAR DATOS
        # ==================================
        df_graph = df_opt.sort_values(
            "date"
        )

        # ==================================
        # FIGURA
        # ==================================
        fig = go.Figure()

        # ==================================
        # ÁREA ESTABLE
        # ==================================
        fig.add_hrect(

            y0=-0.5,
            y1=0.5,

            fillcolor="green",

            opacity=0.15,

            line_width=0

        )

        # ==================================
        # PUNTOS
        # ==================================
        fig.add_trace(

            go.Scatter(

                x=df_graph["date"],

                y=df_graph["lsi_tablas"],

                mode="markers",

                name="LSI Tablas",

                marker=dict(

                    size=10

                ),

                hovertemplate=(

                    "<b>Fecha:</b> %{x}<br>"
                    "<b>LSI:</b> %{y}<br><br>"

                    "<b>pH:</b> %{customdata[0]}<br>"
                    "<b>TDS:</b> %{customdata[1]}<br>"
                    "<b>Temp:</b> %{customdata[2]}<br>"
                    "<b>Calcio:</b> %{customdata[3]}<br>"
                    "<b>Alcalinidad:</b> %{customdata[4]}<br>"

                ),

                customdata=df_graph[
                    [
                        "ph",
                        "tds_ppm",
                        "temperature_c",
                        "calcium_hardness",
                        "alkalinity"
                    ]
                ]

            )

        )

        # ==================================
        # LAYOUT
        # ==================================
        fig.update_layout(

            template="plotly_dark",

            height=500,

            xaxis_title="Fecha",

            yaxis_title="LSI",

            showlegend=True

        )

        # ==================================
        # MOSTRAR
        # ==================================
        st.plotly_chart(

            fig
        )



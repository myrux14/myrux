import streamlit as st
import pandas as pd
import plotly.graph_objects as go

from core.rsi_log import calcular_rsi_log
from core.rsi_table import calcular_rsi

from core.config import (
    RSI_IDEAL_MIN,
    RSI_IDEAL_MAX,
    RSI_MUYINCRUSTANTE,
    RSI_MUYCORROSIVO
)

from modules.analytics.service import clasificar_rsi


def render_rsi_optimization():

    st.divider()

    upload_col1, upload_col2 = st.columns([3, 2])

    with upload_col1:

        st.subheader("🧠 Simulador de Optimización RSI")

        st.markdown(
            """
            Ajusta parámetros para observar
            cómo cambia el RSI en tiempo real.
            """
        )

    with upload_col2:

        uploaded_file = st.file_uploader(

            "📤 Subir Excel optimizado",

            type=["xlsx", "xls", "csv"],

            key="rsi_optimizer_upload"

        )

        load_file = False

        if uploaded_file is not None:

            load_file = st.button(
                "📤 Cargar archivo",
                key="rsi_opt_load_btn"
            )

        df_opt = None

        if uploaded_file is not None and load_file:

            if uploaded_file.name.endswith(".csv"):

                df_opt = pd.read_csv(uploaded_file)

                df_opt.columns = (
                    df_opt.columns
                    .str.strip()
                    .str.lower()
                )

            else:

                df_opt = pd.read_excel(uploaded_file)

                df_opt.columns = (
                    df_opt.columns
                    .str.strip()
                    .str.lower()
                )

                df_opt = df_opt.rename(columns={

                    "sample_date": "date",
                    "ph": "ph",
                    "temperatura": "temperature_c",
                    "temperatura_c": "temperature_c",
                    "tds": "tds_ppm",
                    "calcio": "calcium_hardness",
                    "alcalinidad": "alkalinity"

                })

            # ==============================
            # CALCULAR RSI TABLAS
            # ==============================
            df_opt["rsi_tablas"] = df_opt.apply(

                lambda row: calcular_rsi(

                    ph=row["ph"],

                    temperature_c=row["temperature_c"],

                    tds_ppm=row["tds_ppm"],

                    calcium_hardness=row["calcium_hardness"],

                    alkalinity=row["alkalinity"]

                ),

                axis=1

            )

            df_opt["date"] = pd.to_datetime(
                df_opt["date"],
                errors="coerce"
            )

            visible_columns = [
                "date", "ph", "tds_ppm",
                "temperature_c", "calcium_hardness",
                "alkalinity", "rsi_tablas"
            ]

            existing_columns = [
                col for col in visible_columns
                if col in df_opt.columns
            ]

            df_opt = df_opt[existing_columns]

    # ==================================
    # SLIDERS
    # ==================================
    col1, col2 = st.columns(2)

    with col1:

        ph = st.slider(
            "pH",
            min_value=0.0,
            max_value=14.0,
            value=7.5,
            step=0.01,
            key="rsi_opt_ph"
        )

        tds = st.slider(
            "TDS",
            min_value=0,
            max_value=5000,
            value=500,
            step=10,
            key="rsi_opt_tds"
        )

        temp = st.slider(
            "Temperatura °C",
            min_value=0.0,
            max_value=80.0,
            value=25.0,
            step=0.1,
            key="rsi_opt_temp"
        )

    with col2:

        calcium = st.slider(
            "Calcio",
            min_value=0,
            max_value=1000,
            value=100,
            step=1,
            key="rsi_opt_calcium"
        )

        alkalinity = st.slider(
            "Alcalinidad",
            min_value=0,
            max_value=1000,
            value=150,
            step=1,
            key="rsi_opt_alkalinity"
        )

    # ==================================
    # CÁLCULOS
    # ==================================
    rsi_log = calcular_rsi_log(
        ph=ph,
        temp_c=temp,
        tds=tds,
        calcium=calcium,
        alkalinity=alkalinity
    )

    rsi_tab = calcular_rsi(
        ph=ph,
        temperature_c=temp,
        tds_ppm=tds,
        calcium_hardness=calcium,
        alkalinity=alkalinity
    )

    # ==================================
    # MÉTRICAS
    # ==================================
    result_col1, result_col2 = st.columns(2)

    with result_col1:

        st.metric(
            "RSI Log",
            round(rsi_log, 2) if rsi_log is not None else "Error"
        )

    with result_col2:

        st.metric(
            "RSI Tablas",
            round(rsi_tab, 2) if rsi_tab is not None else "Error"
        )

    # ==================================
    # ESTADO DEL AGUA
    # ==================================
    st.divider()

    if rsi_tab is not None:

        clase = clasificar_rsi(rsi_tab)

        if clase == "Muy incrustante":

            st.error("⚠️ Agua muy incrustante")

        elif clase == "Incrustante":

            st.warning("⚠️ Agua incrustante")

        elif clase == "Equilibrada":

            st.success("✅ Agua estable")

        elif clase == "Corrosiva":

            st.warning("⚠️ Agua corrosiva")

        else:

            st.error("⚠️ Agua muy corrosiva")

    # ==================================
    # TABLA ARCHIVO OPTIMIZADO
    # ==================================
    if df_opt is not None:

        st.divider()

        st.subheader("📋 Resultados optimizados")

        st.dataframe(df_opt)

        # ==============================
        # GRÁFICA
        # ==============================
        st.divider()

        st.subheader("📈 RSI Optimizado")

        df_graph = df_opt.sort_values("date")

        fig = go.Figure()

        fig.add_hrect(

            y0=RSI_IDEAL_MIN,
            y1=RSI_IDEAL_MAX,
            fillcolor="green",
            opacity=0.15,
            line_width=0

        )

        fig.add_trace(

            go.Scatter(

                x=df_graph["date"],

                y=df_graph["rsi_tablas"],

                mode="markers",

                name="RSI Tablas",

                marker=dict(size=10),

                hovertemplate=(
                    "<b>Fecha:</b> %{x}<br>"
                    "<b>RSI:</b> %{y}<br>"
                )

            )

        )

        fig.update_layout(

            template="plotly_dark",

            height=500,

            xaxis_title="Fecha",

            yaxis_title="RSI",

            showlegend=True

        )

        st.plotly_chart(fig, use_container_width=True)

import streamlit as st

from modules.analytics.lsi_engine import (
    calcular_lsi_dual
)


def render_public_lsi():

    # =========================
    # CSS
    # =========================
    st.markdown(
        """
        <style>

        /* Menos espacio entre widgets */
        div[data-testid="stVerticalBlock"] > div {
            gap: 0.25rem !important;
        }

        /* Sliders compactos */
        .stSlider {
            padding-top: 0rem !important;
            padding-bottom: 0rem !important;
            margin-top: -18px !important;
            margin-bottom: -18px !important;
        }

        /* Etiquetas sliders */
        .stSlider label {
            font-size: 14px !important;
        }

        /* Métricas */
        [data-testid="stMetricLabel"] {
            font-size: 20px !important;
        }

        [data-testid="stMetricValue"] {
            font-size: 20px !important;
        }

        </style>
        """,
        unsafe_allow_html=True
    )


    st.title(
        "💧 Calculadora Índice de Saturación Langelier (LSI)"
    )

    st.divider()

    col_sim, col_log, col_tab = st.columns(
        [3, 1, 1]
    )

    # =========================
    # SIMULADOR
    # =========================
    with col_sim:

        st.subheader(
            "Simulador en tiempo real"
        )

        
        tds = st.slider(
            "TDS (ppm)",
            50,
            5000,
            500
        )

        temp = st.slider(
            "Temperatura °C",
            0.0,
            50.0,
            25.0,
            0.1
        )

        calcio = st.slider(
            "Calcio (ppm)",
            5,
            500,
            100
        )

        alcalinidad = st.slider(
            "Alcalinidad (ppm)",
            5,
            500,
            150
        )

        ph = st.slider(
            "pH",
            5.0,
            10.0,
            7.5,
            0.01
        )

    # =========================
    # CÁLCULO
    # =========================
    result = calcular_lsi_dual(
        ph=ph,
        tds=tds,
        temp=temp,
        calcium=calcio,
        alkalinity=alcalinidad
    )

    if not result:

        st.error(
            "No fue posible calcular el LSI."
        )

        return

    comp_log = result.get("log")
    comp_tab = result.get("tablas")

    if not comp_log or not comp_tab:

        st.error(
            "Error obteniendo componentes."
        )

        return

    # =========================
    # ETIQUETAS
    # =========================
    labels_log = {

        "ph_saturacion": "pHs",
        "factor_A": "Factor A",
        "factor_B": "Factor B",
        "factor_C": "Factor C",
        "factor_D": "Factor D",
        "lsi": "LSI Log"

    }

    labels_tab = {

        "ph_saturacion": "pHs",
        "A": "Factor A",
        "B": "Factor B",
        "HF": "HF (Calcio)",
        "AF": "AF (Alcalinidad)",
        "lsi": "LSI Tablas"

    }

    # =========================
    # MÉTODO LOG
    # =========================
    with col_log:

        st.subheader("Método Log")

        for k, v in comp_log.items():

            c1, c2 = st.columns([1.5, 0.8])

            c1.write(labels_log.get(k, k))
            c2.write(f"**{v:.2f}**")

    # =========================
    # MÉTODO TABLAS
    # =========================
    with col_tab:

        st.subheader("Método Tablas")

        for k, v in comp_tab.items():

            c1, c2 = st.columns([1.5, 0.8])

            c1.write(labels_tab.get(k, k))
            c2.write(f"**{v:.2f}**")
    

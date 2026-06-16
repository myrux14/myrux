import streamlit as st

from modules.analytics.lsi_engine import (
    calcular_lsi_dual
)


def render_public_lsi():

    # =========================
    # SEO META TAGS + NOSCRIPT
    # =========================
    st.markdown(
        """
        <meta name="description" content="Calculadora gratuita del Índice de Saturación de Langelier (LSI). Evalúa si el agua es corrosiva o incrustante. Ideal para cisternas, torres de enfriamiento, calderas y sistemas de agua potable en hotelería e industria.">
        <meta name="keywords" content="calculadora LSI, índice de Langelier, Langelier Saturation Index, corrosión agua, incrustación agua, pH agua, tratamiento agua, cisternas hotelería, torres enfriamiento, índice saturación Langelier, calidad agua potable, agua corrosiva, agua incrustante, TDS, alcalinidad, dureza cálcica">
        <meta name="robots" content="index, follow">
        <meta property="og:title" content="Calculadora LSI – Índice de Saturación de Langelier | Myrux">
        <meta property="og:description" content="Calcula el LSI en tiempo real: pH, temperatura, alcalinidad, dureza cálcica y TDS. Herramienta gratuita para operadores de agua potable e industrial.">
        <meta property="og:type" content="website">
        <meta property="og:url" content="https://myrux.app">
        <link rel="canonical" href="https://myrux.app">
        <noscript>
        <h1>Calculadora del Índice de Saturación de Langelier (LSI) — Gratis</h1>
        <p>
        Myrux ofrece una calculadora gratuita del Índice de Saturación de Langelier (LSI)
        para evaluar la tendencia del agua a formar incrustaciones de carbonato de calcio
        o a presentar corrosión en tuberías, cisternas, torres de enfriamiento, calderas
        y sistemas de agua potable en hotelería e industria.
        </p>
        <p>El LSI se calcula con: pH, temperatura, TDS (sólidos disueltos totales), dureza cálcica y alcalinidad.</p>
        <p>Aplicaciones: cisternas hoteleras, torres de enfriamiento, calderas, piscinas,
        sistemas de ósmosis inversa y plantas de tratamiento de agua potable.</p>
        <p>Interpretación: LSI negativo = agua corrosiva. LSI cercano a 0 = agua estable. LSI positivo = agua incrustante.</p>
        </noscript>
        """,
        unsafe_allow_html=True
    )

    # =========================
    # CSS
    # =========================
    st.markdown(
        """
        <style>

        /* Menos espacio entre widgets */
        div[data-testid="stVerticalBlock"] > div {
            gap: 0.30rem !important;
        }

        /* Sliders compactos */
        .stSlider {
            padding-top: 0rem !important;
            padding-bottom: 0rem !important;
            margin-top: -16px !important;
            margin-bottom: -16px !important;
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

    st.markdown("""
    ##  💧 Calculadora gratuita del Índice de Saturación de Langelier (LSI)

    Calcule el Índice de Saturación de Langelier (LSI) para evaluar
    el potencial de corrosión o incrustación del agua. La herramienta utiliza parámetros de: pH, TDS, Temperatura, Calcio, Alcalinidad e incluye cálculo mediante método logarítmico y método por tablas.
    """)

    col_sim, = st.columns(
        [4]
    )

    # =========================
    # SIMULADOR
    # =========================
    with col_sim:

        st.markdown("""
        ##### Simulador en tiempo real
        """)

        st.divider()

        sim_col1, sim_col2 = st.columns(2)

        with sim_col1:

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

            ph = st.slider(
                "pH",
                5.0,
                10.0,
                7.5,
                0.01
            )

        with sim_col2:

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

    st.divider()



    col_log, col_tab, col_info = st.columns(
        [0.8, 0.9, 1.3]
    )

    
    # =========================
    # MÉTODO LOG
    # =========================
    with col_log:

        with st.container(border=True):

            st.markdown(
                f"""
                <h2>
                    Método Log
                    <span style="
                        color:#22c55e;
                        font-size:30px;
                        margin-left:15px;
                    ">
                        {comp_log['lsi']:.2f}
                    </span>
                </h2>
                """,
                unsafe_allow_html=True
            )

            for k, v in comp_log.items():

                if k == "lsi":
                    continue

                c1, c2 = st.columns([2, 1])

                c1.write(labels_log.get(k, k))
                c2.write(f"**{v:.2f}**")

    # =========================
    # MÉTODO TABLAS
    # =========================
    with col_tab:

        with st.container(border=True):

            st.markdown(
                f"""
                <h2>
                    Método Tablas
                    <span style="
                        color:#22c55e;
                        font-size:30px;
                        margin-left:15px;
                    ">
                        {comp_tab['lsi']:.2f}
                    </span>
                </h2>
                """,
                unsafe_allow_html=True
            )

            for k, v in comp_tab.items():

                if k == "lsi":
                    continue

                c1, c2 = st.columns([2, 1])

                c1.write(labels_tab.get(k, k))
                c2.write(f"**{v:.2f}**")

    # =========================
    # INFORMACIÓN TEÓRICA
    # =========================
    with col_info:

        with st.container(border=True):

            st.markdown(
                "#### 📚 Interpretación"
            )

            lsi = comp_tab["lsi"]

            if lsi < -0.5:

                st.error(
                    "Agua corrosiva"
                )

                st.markdown(
                    """
                    - Alta tendencia a corrosión.
                    - Posible ataque a tuberías.
                    """
                )

            elif lsi > 0.5:

                st.warning(
                    "Agua incrustante"
                )

                st.markdown(
                    """
                    - Tendencia a precipitar CaCO₃.
                    - Posibles incrustaciones.
                    """
                )

            else:

                st.success(
                    "Agua estable"
                )

                st.markdown(
                    """
                    - Condición cercana al equilibrio.
                    - Bajo riesgo de corrosión.
                    - Bajo riesgo de incrustación.
                    """
                )

            st.markdown(
                """
                <h4>Rangos típicos</h4>

                <table style="
                    font-size:14px;
                    width:100%;
                    border-collapse:collapse;
                ">
                    <tr>
                        <th style="text-align:left;">LSI</th>
                        <th style="text-align:left;">Estado</th>
                    </tr>
                    <tr>
                        <td>&lt; -0.5</td>
                        <td>Corrosivo</td>
                    </tr>
                    <tr>
                        <td>-0.5 a 0.5</td>
                        <td>Estable</td>
                    </tr>
                    <tr>
                        <td>&gt; 0.5</td>
                        <td>Incrustante</td>
                    </tr>
                </table>
                """,
                unsafe_allow_html=True
            )

    st.divider()

    st.markdown("""
    <style>

    p, li {
        font-size: 18px !important;
        line-height: 1.8 !important;
    }

    </style>
    """, unsafe_allow_html=True)

    st.markdown(
        """       

        ## Calculadora del Índice de Saturación de Langelier

        El Índice de Saturación de Langelier, también conocido como LSI por sus siglas en inglés, es una herramienta utilizada para estimar la tendencia del agua a formar incrustaciones de carbonato de calcio o, por el contrario, a presentar un comportamiento corrosivo frente a superficies metálicas, tuberías, equipos hidráulicos, calderas, sistemas de enfriamiento, piscinas, pozos y redes de distribución.

        Nuestra calculadora gratuita permite simular en tiempo real el equilibrio del agua a partir de parámetros fisicoquímicos como pH, temperatura, alcalinidad, dureza cálcica, sólidos disueltos totales y otros factores relacionados. Al ingresar los datos, el sistema estima el LSI y muestra una interpretación práctica del resultado para apoyar la toma de decisiones en operación, tratamiento y control de calidad del agua.
        
        ## ¿Para qué sirve esta calculadora?

        Esta herramienta puede ayudarte a:

        - Estimar rápidamente la tendencia incrustante o corrosiva del agua.
        - Evaluar cambios de pH, temperatura, alcalinidad o dureza.
        - Simular ajustes químicos antes de aplicarlos en campo.
        - Apoyar decisiones de tratamiento, dosificación y control operativo.
        - Comparar diferentes muestras o escenarios de operación.
        - Facilitar la interpretación técnica de análisis de agua.

        ---
        
        ### ¿Qué es el Índice de Saturación de Langelier (LSI)?        

        El Índice de Saturación de Langelier (LSI) es una herramienta utilizada
        para estimar la tendencia del agua a formar incrustaciones de carbonato
        de calcio (CaCO₃) o a provocar corrosión en tuberías, intercambiadores,
        calderas y sistemas de enfriamiento.

        El índice compara el pH real del agua con el pH de saturación (pHs).

        **LSI = pH - pHs**

        Donde:

        - **LSI negativo:** tendencia corrosiva.
        - **LSI cercano a cero:** agua en equilibrio.
        - **LSI positivo:** tendencia incrustante.

        
        #### Variables consideradas

        El cálculo del LSI considera:

        - pH
        - Temperatura
        - Sólidos disueltos totales (TDS)
        - Dureza cálcica
        - Alcalinidad

        Estas variables determinan la estabilidad química del agua y su
        capacidad para disolver o precipitar carbonato de calcio.

        
        #### Aplicaciones

        El LSI se utiliza comúnmente en:

        - Torres de enfriamiento
        - Calderas
        - Sistemas de ósmosis inversa
        - Redes de distribución de agua
        - Piscinas y spas
        - Plantas de tratamiento de agua


        #### Interpretación general

        | LSI | Condición |
        |------|------------|
        | < -0.5 | Corrosiva |
        | -0.5 a 0.5 | Estable |
        | > 0.5 | Incrustante |

        El rango operativo más utilizado es:

        **-0.2 ≤ LSI ≤ 0.2**

        aunque puede variar dependiendo del tipo de sistema y los materiales de construcción.
        """
    )

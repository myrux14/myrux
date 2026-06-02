import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# ======================================
# RENDER GRÁFICAS
# ======================================
def render_graphs(df):

    st.subheader(
        "📈 Gráficas"
    )

    # ==================================
    # VALIDAR DATAFRAME
    # ==================================
    if df.empty:

        st.warning(
            "No hay datos disponibles"
        )

        return

    # ==================================
    # COPIA DATAFRAME
    # ==================================
    df_graph = df.copy()

    # ==================================
    # FECHA
    # ==================================
    df_graph["sample_date"] = pd.to_datetime(
        df_graph["sample_date"]
    )

    # ==================================
    # ORDENAR FECHA
    # ==================================
    df_graph = df_graph.sort_values(
        by="sample_date"
    )

    # ==================================
    # LSI LOGARÍTMICO
    # ==================================
    st.markdown(
        "### 📉 LSI Logarítmico"
    )

    fig = go.Figure()

    # ==============================
    # REGIÓN ESTABLE
    # ==============================
    fig.add_hrect(

        y0=-0.5,
        y1=0.5,

        fillcolor="green",

        opacity=0.15,

        line_width=0

    )

    # ==============================
    # PUNTOS
    # ==============================
    fig.add_trace(

        go.Scatter(

            x=df_graph["sample_date"],

            y=df_graph["lsi"],

            mode="markers",

            name="LSI Log"

        )

    )
    

    # ==============================
    # LAYOUT
    # ==============================
    fig.update_layout(

        xaxis_title="Fecha",

        yaxis_title="LSI",

        height=500

    )

    # ==============================
    # MOSTRAR
    # ==============================
    st.plotly_chart(
        fig,
        width="stretch"
    )

    # ==================================
    # LSI TABLAS
    # ==================================
    st.markdown(
        "### 📊 LSI Tablas"
    )

    fig_tab = go.Figure()

    # ==============================
    # ZONA ESTABLE
    # ==============================
    fig_tab.add_hrect(

        y0=-0.5,
        y1=0.5,

        fillcolor="green",

        opacity=0.15,

        line_width=0

    )

    # ==============================
    # PUNTOS
    # ==============================
    fig_tab.add_trace(

        go.Scatter(

            x=df_graph["sample_date"],

            y=df_graph["lsi_tablas"],

            mode="markers",

            name="LSI Tablas"

        )

    )

    # ==============================
    # LAYOUT
    # ==============================
    fig_tab.update_layout(

        xaxis_title="Fecha",

        yaxis_title="LSI",

        height=500

    )

    # ==============================
    # MOSTRAR
    # ==============================
    st.plotly_chart(

        fig_tab,

        width="stretch"

    )

    # ==================================
    # COMPARACIÓN
    # ==================================
    st.markdown(
        "### ⚖️ Comparación"
    )

    fig_compare = go.Figure()

    # ==============================
    # ZONA ESTABLE
    # ==============================
    fig_compare.add_hrect(

        y0=-0.5,
        y1=0.5,

        fillcolor="green",

        opacity=0.15,

        line_width=0

    )

    # ==============================
    # LÍNEA LSI LOG
    # ==============================
    fig_compare.add_trace(

        go.Scatter(

            x=df_graph["sample_date"],

            y=df_graph["lsi"],

            mode="lines+markers",

            name="LSI Log"

        )

    )

    # ==============================
    # LÍNEA LSI TABLAS
    # ==============================
    fig_compare.add_trace(

        go.Scatter(

            x=df_graph["sample_date"],

            y=df_graph["lsi_tablas"],

            mode="lines+markers",

            name="LSI Tablas"

        )

    )

    # ==============================
    # LAYOUT
    # ==============================
    fig_compare.update_layout(

        xaxis_title="Fecha",

        yaxis_title="LSI",

        height=600

    )

    # ==============================
    # MOSTRAR
    # ==============================
    st.plotly_chart(

        fig_compare,

        width="stretch"

    )
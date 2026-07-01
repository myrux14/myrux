import streamlit as st
import pandas as pd
import plotly.graph_objects as go

from core.config import (
    RSI_IDEAL_MIN,
    RSI_IDEAL_MAX
)


def render_rsi_graphs(df):

    st.subheader("📈 Gráficas RSI")

    if df is None or df.empty:

        st.warning("No hay datos disponibles")

        return

    df_graph = df.copy()

    df_graph["sample_date"] = pd.to_datetime(
        df_graph["sample_date"],
        errors="coerce"
    )

    df_graph = df_graph.sort_values(
        by="sample_date"
    )

    # ==================================
    # RSI LOGARÍTMICO
    # ==================================
    st.markdown("### 📉 RSI Logarítmico")

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

            x=df_graph["sample_date"],

            y=df_graph["rsi"],

            mode="markers",

            name="RSI Log",

            marker=dict(size=8)

        )

    )

    fig.update_layout(

        xaxis_title="Fecha",

        yaxis_title="RSI",

        height=500,

        template="plotly_dark"

    )

    st.plotly_chart(fig, use_container_width=True)

    # ==================================
    # RSI TABLAS
    # ==================================
    if "rsi_tablas" in df_graph.columns:

        st.markdown("### 📊 RSI Tablas")

        fig_tab = go.Figure()

        fig_tab.add_hrect(

            y0=RSI_IDEAL_MIN,
            y1=RSI_IDEAL_MAX,
            fillcolor="green",
            opacity=0.15,
            line_width=0

        )

        fig_tab.add_trace(

            go.Scatter(

                x=df_graph["sample_date"],

                y=df_graph["rsi_tablas"],

                mode="markers",

                name="RSI Tablas",

                marker=dict(size=8)

            )

        )

        fig_tab.update_layout(

            xaxis_title="Fecha",

            yaxis_title="RSI",

            height=500,

            template="plotly_dark"

        )

        st.plotly_chart(
            fig_tab,
            use_container_width=True
        )

    # ==================================
    # COMPARACIÓN
    # ==================================
    if "rsi_tablas" in df_graph.columns:

        st.markdown("### ⚖️ Comparación Log vs Tablas")

        fig_compare = go.Figure()

        fig_compare.add_hrect(

            y0=RSI_IDEAL_MIN,
            y1=RSI_IDEAL_MAX,
            fillcolor="green",
            opacity=0.15,
            line_width=0

        )

        fig_compare.add_trace(

            go.Scatter(

                x=df_graph["sample_date"],

                y=df_graph["rsi"],

                mode="lines+markers",

                name="RSI Log"

            )

        )

        fig_compare.add_trace(

            go.Scatter(

                x=df_graph["sample_date"],

                y=df_graph["rsi_tablas"],

                mode="lines+markers",

                name="RSI Tablas"

            )

        )

        fig_compare.update_layout(

            xaxis_title="Fecha",

            yaxis_title="RSI",

            height=600,

            template="plotly_dark"

        )

        st.plotly_chart(
            fig_compare,
            use_container_width=True
        )

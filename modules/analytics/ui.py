import streamlit as st
import plotly.graph_objects as go


def render_lsi_charts(df):

    if df is None or df.empty:
        st.info("No hay datos")
        return

    df = df.sort_values("date")

    # -----------------------------
    # COLORES POR ESTADO
    # -----------------------------
    colores = {
        "Incrustación alta": "red",
        "Incrustación ligera con corrosión": "orange",
        "Equilibrada": "green",
        "Corrosión ligera": "deepskyblue",
        "Corrosión alta": "red"
    }

    df["color"] = df["Estado"].map(colores).fillna("gray")

    # -----------------------------
    # FUNCIÓN BASE DE ESTILO
    # -----------------------------
    def estilo_base(fig, titulo):
        fig.add_hrect(
            y0=-0.3,
            y1=0.3,
            fillcolor="deepskyblue",
            opacity=0.08,
            line_width=0
        )

        fig.add_hline(y=0, line_dash="dash", line_color="black")

        fig.update_layout(
            template="plotly_dark",
            title=titulo,
            xaxis_title="Fecha",
            yaxis_title="LSI",
            hovermode="x unified"
        )



        return fig

    # -----------------------------
    # 1. LSI TABLA
    # -----------------------------
    fig_tabla = go.Figure()

    fig_tabla.add_trace(go.Scatter(
        x=df["date"],
        y=df["LSI_tabla"],
        mode='markers',
        name='LSI Tabla',
        marker=dict(
            size=9,
            color=df["color"],
            line=dict(width=1, color="black")
        )
    ))

    fig_tabla = estilo_base(fig_tabla, "LSI - Método Tablas")
    st.plotly_chart(fig_tabla, width="stretch")

    # -----------------------------
    # 2. LSI LOG
    # -----------------------------
    fig_log = go.Figure()

    fig_log.add_trace(go.Scatter(
        x=df["date"],
        y=df["LSI_log"],
        mode='markers',
        name='LSI Log',
        marker=dict(
            size=9,
            color=df["color"],
            symbol="diamond",
            line=dict(width=1, color="black")
        )
    ))

    fig_log = estilo_base(fig_log, "LSI - Método Logarítmico")
    st.plotly_chart(fig_log, width="stretch")

    # -----------------------------
    # 3. COMPARACIÓN PRO
    # -----------------------------
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=df["date"],
        y=df["LSI_tabla"],
        mode='markers',
        name='Tabla',
        marker=dict(
            size=9,
            color=df["color"],
            symbol="circle",
            line=dict(width=1, color="black")
        )
    ))

    fig.add_trace(go.Scatter(
        x=df["date"],
        y=df["LSI_log"],
        mode='markers',
        name='Log',
        marker=dict(
            size=9,
            color=df["color"],
            symbol="diamond",
            line=dict(width=1, color="black")
        )
    ))

    # alertas
    if "Error_abs" in df.columns:
        df_alert = df[df["Error_abs"] > 0.5]

        fig.add_trace(go.Scatter(
            x=df_alert["date"],
            y=df_alert["LSI_log"],
            mode='markers',
            name='⚠ Error alto',
            marker=dict(
                size=12,
                color="black",
                symbol="x"
            )
        ))

    fig = estilo_base(fig, "Comparación LSI (Tabla vs Log)")
    st.plotly_chart(fig, width="stretch")

def render_optimizacion_chart(df):

    if df is None or df.empty:
        st.info("No hay datos")
        return

    df = df.sort_values("date")

    fig = go.Figure()

    # -----------------------------
    # REAL
    # -----------------------------
    fig.add_trace(go.Scatter(
        x=df["date"],
        y=df["LSI_original"],
        mode='markers',
        name='LSI Real',
        marker=dict(
            size=10,
            symbol="circle",
            color="red",
            line=dict(width=1, color="white")
        )
    ))

    # -----------------------------
    # AJUSTADO
    # -----------------------------
    fig.add_trace(go.Scatter(
        x=df["date"],
        y=df["LSI_ajustado"],
        mode='markers',
        name='LSI Ajustado',
        marker=dict(
            size=10,
            symbol="diamond",
            color="green",
            line=dict(width=1, color="white")
        )
    ))

    # -----------------------------
    # ZONA ESTABLE
    # -----------------------------
    fig.add_hrect(
        y0=-0.3,
        y1=0.3,
        fillcolor="green",
        opacity=0.08,
        line_width=0
    )

    # línea equilibrio
    fig.add_hline(
        y=0,
        line_dash="dash",
        line_color="white"
    )

    # -----------------------------
    # ESTILO
    # -----------------------------
    fig.update_layout(
        template="plotly_dark",
        title="LSI Real vs LSI Ajustado",
        xaxis_title="Fecha",
        yaxis_title="LSI",
        hovermode="x unified"
    )

    st.plotly_chart(fig, width="stretch")
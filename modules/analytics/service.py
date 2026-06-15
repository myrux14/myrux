import math
import numpy as np
from core.lsi_table import calcular_lsi as calcular_lsi_tabla
from core.lsi_log import calcular_lsi_log
from core.lsi_table import A, B, HF, AF
from core.lsi_table import componentes_tabla
from core.lsi_log import componentes_log

# 🔥 FUNCIÓN QUE APP.py ESTÁ ESPERANDO
def calcular_lsi(ph, temperature, tds, calcium, alkalinity):
    return calcular_lsi_log(ph, tds, temperature, calcium, alkalinity)


# (opcional pero recomendado)
def calcular_lsi_dual(ph, temperature, tds, calcium, alkalinity):
    lsi_tabla = calcular_lsi_tabla(ph, temperature, tds, calcium, alkalinity)
    lsi_log = calcular_lsi_log(ph, tds, temperature, calcium, alkalinity)

    error = None
    if lsi_tabla is not None and lsi_log is not None:
        error = round(lsi_log - lsi_tabla, 3)

    return lsi_tabla, lsi_log, error


# -----------------------------
# CLASIFICACIÓN
# -----------------------------
def clasificar_lsi(lsi):
    if lsi is None:
        return "Sin datos"

    if lsi > 0.5:
        return "Incrustante"

    elif 0.3 < lsi <= 0.5:
        return "Tendencia incrustante"

    elif -0.5 <= lsi < -0.3:
        return "Tendencia Corrosiva"

    elif lsi < -0.5:
        return "Corrosiva"
    
    else:
        return "Equilibrada"
    
def color_lsi(clase):
    colores = {
        "Incrustante": "red",
        "Tendencia incrustante": "orange",
        "Equilibrada": "green",
        "Tendencia Corrosiva": "lightblue",
        "Corrosiva": "blue"
    }
    return colores.get(clase, "gray")


# -----------------------------
# RECOMENDACIONES
# -----------------------------
def recomendaciones_lsi(row):
    lsi = row["LSI"]
    ph = row["ph"]
    alkalinity = row["alkalinity"]
    calcium = row["calcium"]

    if lsi is None:
        return "Sin datos"

    if lsi > 0.5:
        acciones = []

        if ph and ph > 7.5:
            acciones.append("↓ Reducir pH")

        if alkalinity and alkalinity > 120:
            acciones.append("↓ Reducir alcalinidad")

        if calcium and calcium > 200:
            acciones.append("↓ Reducir calcio")

        return " | ".join(acciones) if acciones else "Control general de incrustación"

    elif lsi < -0.5:
        acciones = []

        if ph and ph < 7.0:
            acciones.append("↑ Aumentar pH")

        if alkalinity and alkalinity < 100:
            acciones.append("↑ Aumentar alcalinidad")

        return " | ".join(acciones) if acciones else "Control de corrosión"

    else:
        return "Sistema en equilibrio"


# -----------------------------
# TENDENCIA
# -----------------------------
def tendencia_lsi(df):
    if df is None or len(df) < 3:
        return "Sin datos suficientes", None

    df = df.sort_values("date")

    x = np.arange(len(df))
    y = df["LSI"].values

    slope, intercept = np.polyfit(x, y, 1)

    if slope > 0.1:
        estado = "Subiendo (hacia incrustación)"
    elif slope < -0.1:
        estado = "Bajando (hacia corrosión)"
    else:
        estado = "Estable"

    return estado, round(slope, 4)


# -----------------------------
# PROYECCIÓN
# -----------------------------
def proyectar_lsi(df, pasos=3):
    if df is None or len(df) < 3:
        return None

    df = df.sort_values("date")

    x = np.arange(len(df))
    y = df["LSI"].values

    slope, intercept = np.polyfit(x, y, 1)

    return [round(slope * (len(df) + i) + intercept, 2) for i in range(1, pasos + 1)]


def calcular_componentes(row):
    try:
        return (
            A(row["tds"]),
            B(row["temperature"]),
            HF(row["calcium"]),
            AF(row["alkalinity"]),
        )
    except:
        return None, None, None, None

def comparar_componentes(row):
    try:
        a_t, b_t, c_t, d_t, phs_t = componentes_tabla(
            row["tds"], row["temperature"], row["calcium"], row["alkalinity"]
        )

        a_l, b_l, c_l, d_l, phs_l = componentes_log(
            row["tds"], row["temperature"], row["calcium"], row["alkalinity"]
        )

        return (
            a_t, a_l,
            b_t, b_l,
            c_t, c_l,
            d_t, d_l,
            phs_t, phs_l
        )

    except:
        return (None,) * 10
    

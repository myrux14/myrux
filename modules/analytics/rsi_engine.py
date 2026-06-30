from core.rsi_log import componentes_rsi_log
from core.rsi_table import componentes_tabla_rsi


# =====================================
# MÉTODO DUAL
# =====================================
def calcular_rsi_dual(
    ph,
    tds,
    temp,
    calcium,
    alkalinity
):

    return {

        "log": componentes_rsi_log(
            ph,
            tds,
            temp,
            calcium,
            alkalinity
        ),

        "tablas": componentes_tabla_rsi(
            ph,
            tds,
            temp,
            calcium,
            alkalinity
        )

    }

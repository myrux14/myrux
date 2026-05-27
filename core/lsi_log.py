import math


# -----------------------------
# VALIDACIÓN
# -----------------------------
def safe_log10(x):
    if x is None or x <= 0:
        return None
    return math.log10(x)


# -----------------------------
# FACTORES
# -----------------------------
def factor_A(tds):
    log = safe_log10(tds)
    return (log - 1) / 10 if log is not None else None


def factor_B(temp_c):
    try:
        return -13.12 * math.log10(temp_c + 273) + 34.55
    except:
        return None


def factor_C(calcium):
    log = safe_log10(calcium)
    return log - 0.4 if log is not None else None


def factor_D(alkalinity):
    return safe_log10(alkalinity)


# -----------------------------
# pHs
# -----------------------------
def calcular_pHs_log(tds, temp_c, calcium, alkalinity):
    A = factor_A(tds)
    B = factor_B(temp_c)
    C = factor_C(calcium)
    D = factor_D(alkalinity)

    if None in [A, B, C, D]:
        return None

    return (9.3 + A + B) - (C + D)


# -----------------------------
# LSI LOG
# -----------------------------
def calcular_lsi_log(ph, tds, temp_c, calcium, alkalinity):
    try:
        if None in [ph, tds, temp_c, calcium, alkalinity]:
            return None

        pHs = calcular_pHs_log(tds, temp_c, calcium, alkalinity)

        if pHs is None:
            return None

        return round(ph - pHs, 2)

    except Exception as e:
        print("Error LSI log:", e)
        return None

def componentes_log(

    ph,
    tds,
    temp,
    calcium,
    alkalinity

):

    try:

        A = factor_A(tds)
        B = factor_B(temp)
        C = factor_C(calcium)
        D = factor_D(alkalinity)
        if None in [A, B, C, D]:

            return None

        # ======================
        # pHs
        # ======================
        pHs = (
            9.3 + A + B
        ) - (C + D)

        # ======================
        # LSI
        # ======================
        lsi = ph - pHs

        return {

            "factor_A": round(A, 2),
            "factor_B": round(B, 2),
            "factor_C": round(C, 2),
            "factor_D": round(D, 2),
            "ph_saturacion": round(pHs, 2),
            "lsi": round(lsi, 2)

        }

    except Exception as e:

        print(
            "Error componentes_log:",
            e
        )

        return None
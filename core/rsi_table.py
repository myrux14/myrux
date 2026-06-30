import math


# -----------------------------
# INTERPOLACIÓN
# -----------------------------
def interpolate(x, table):
    if x is None:
        return None

    if x <= table[0][0]:
        return table[0][1]
    if x >= table[-1][0]:
        return table[-1][1]

    for i in range(len(table) - 1):
        x0, y0 = table[i]
        x1, y1 = table[i + 1]

        if x0 <= x <= x1:
            return y0 + (y1 - y0) * (x - x0) / (x1 - x0)


# -----------------------------
# TABLAS
# -----------------------------
HF_TABLE = [
    (5,0.70),(25,1.40),(50,1.70),(75,1.90),(100,2.00),
    (150,2.20),(200,2.30),(250,2.40),(300,2.50),
    (400,2.60),(500,2.70),(1000,3.00)
]

AF_TABLE = HF_TABLE

A_TABLE = [
    (50,0.07),(100,0.10),(200,0.13),(300,0.15),(400,0.16),
    (500,0.17),(600,0.18),(800,0.19),(1000,0.20),
    (1500,0.22),(2000,0.23),(3000,0.25),
    (4000,0.26),(6000,0.28),(8000,0.29),(10000,0.30)
]


# -----------------------------
# FACTORES
# -----------------------------
def A(tds):
    return interpolate(tds, A_TABLE)

def B(temp):
    return -13.12 * math.log10(temp + 273) + 34.55

def HF(calcium):
    return interpolate(calcium, HF_TABLE)

def AF(alk):
    return interpolate(alk, AF_TABLE)


# -----------------------------
# RSI (TABLAS)
# -----------------------------
def calcular_rsi(ph, temperature_c, tds_ppm, calcium_hardness, alkalinity):
    try:
        if None in [ph, temperature_c, tds_ppm, calcium_hardness, alkalinity]:
            return None

        pHs = (9.3 + A(tds_ppm) + B(temperature_c)) - (
            HF(calcium_hardness) + AF(alkalinity)
        )

        return round(2 * pHs - ph, 2)

    except Exception as e:
        print("Error RSI:", e)
        return None


# -----------------------------
# COMPONENTES
# -----------------------------
def componentes_tabla_rsi(ph, tds, temp, calcium, alkalinity):
    try:
        a = A(tds)
        b = B(temp)
        hf = HF(calcium)
        af = AF(alkalinity)

        if None in [a, b, hf, af]:
            return None

        pHs = (9.3 + a + b) - (hf + af)
        rsi = 2 * pHs - ph

        return {

            "A": round(a, 2),
            "B": round(b, 2),
            "HF": round(hf, 2),
            "AF": round(af, 2),
            "ph_saturacion": round(pHs, 2),
            "rsi": round(rsi, 2)

        }

    except Exception as e:

        print("Error componentes_tabla_rsi:", e)
        return None

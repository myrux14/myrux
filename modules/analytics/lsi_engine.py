import math


# =====================================
# UTILIDADES
# =====================================
def safe_log10(x):

    if x is None or x <= 0:
        return None

    return math.log10(x)


# =====================================
# MÉTODO LOG
# =====================================
def factor_A_log(tds):

    log = safe_log10(tds)

    return (
        (log - 1) / 10
        if log is not None
        else None
    )


def factor_B_log(temp_c):

    try:

        return (
            -13.12
            * math.log10(temp_c + 273)
            + 34.55
        )

    except:

        return None


def factor_C_log(calcium):

    log = safe_log10(calcium)

    return (
        log - 0.4
        if log is not None
        else None
    )


def factor_D_log(alkalinity):

    return safe_log10(
        alkalinity
    )


def componentes_log(
    ph,
    tds,
    temp,
    calcium,
    alkalinity
):

    A = factor_A_log(tds)
    B = factor_B_log(temp)
    C = factor_C_log(calcium)
    D = factor_D_log(alkalinity)

    if None in [A, B, C, D]:

        return None

    pHs = (
        9.3 + A + B
    ) - (
        C + D
    )

    lsi = ph - pHs

    return {

        "factor_A": round(A, 2),

        "factor_B": round(B, 2),

        "factor_C": round(C, 2),

        "factor_D": round(D, 2),

        "ph_saturacion": round(
            pHs,
            2
        ),

        "lsi": round(
            lsi,
            2
        )

    }


# =====================================
# MÉTODO TABLAS
# =====================================
HF_TABLE = [

    (5,0.70),
    (25,1.40),
    (50,1.70),
    (75,1.90),
    (100,2.00),
    (150,2.20),
    (200,2.30),
    (250,2.40),
    (300,2.50),
    (400,2.60),
    (500,2.70),
    (1000,3.00)

]

AF_TABLE = HF_TABLE

A_TABLE = [

    (50,0.07),
    (100,0.10),
    (200,0.13),
    (300,0.15),
    (400,0.16),
    (500,0.17),
    (600,0.18),
    (800,0.19),
    (1000,0.20),
    (1500,0.22),
    (2000,0.23),
    (3000,0.25),
    (4000,0.26),
    (6000,0.28),
    (8000,0.29),
    (10000,0.30)

]

TEMP_TABLE = [

    (0, 2.10),
    (5, 2.00),
    (10, 1.90),
    (15, 1.80),
    (20, 1.70),
    (25, 1.60),
    (30, 1.53),
    (35, 1.46),
    (40, 1.40),
    (45, 1.34),
    (50, 1.28)

]


def interpolate(x, table):

    if x is None:

        return None

    if x <= table[0][0]:

        return table[0][1]

    if x >= table[-1][0]:

        return table[-1][1]

    for i in range(
        len(table) - 1
    ):

        x0, y0 = table[i]

        x1, y1 = table[i + 1]

        if x0 <= x <= x1:

            return y0 + (
                (y1 - y0)
                * (x - x0)
                / (x1 - x0)
            )


def A_tab(tds):

    return interpolate(
        tds,
        A_TABLE
    )


def B_tab(temp):

    return interpolate(
        temp,
        TEMP_TABLE
    )


def HF_tab(calcium):

    return interpolate(
        calcium,
        HF_TABLE
    )


def AF_tab(alk):

    return interpolate(
        alk,
        AF_TABLE
    )


def componentes_tabla(
    ph,
    tds,
    temp,
    calcium,
    alkalinity
):

    A = A_tab(tds)

    B = B_tab(temp)

    HF = HF_tab(calcium)

    AF = AF_tab(
        alkalinity
    )

    if None in [A, B, HF, AF]:

        return None

    pHs = (
        9.3 + A + B
    ) - (
        HF + AF
    )

    lsi = ph - pHs

    return {

        "A": round(A, 2),

        "B": round(B, 2),

        "HF": round(HF, 2),

        "AF": round(AF, 2),

        "ph_saturacion": round(
            pHs,
            2
        ),

        "lsi": round(
            lsi,
            2
        )

    }


# =====================================
# MÉTODO DUAL
# =====================================
def calcular_lsi_dual(
    ph,
    tds,
    temp,
    calcium,
    alkalinity
):

    return {

        "log": componentes_log(
            ph,
            tds,
            temp,
            calcium,
            alkalinity
        ),

        "tablas": componentes_tabla(
            ph,
            tds,
            temp,
            calcium,
            alkalinity
        )

    }
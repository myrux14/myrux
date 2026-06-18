"""
Patches Streamlit's index.html template to inject SEO meta tags in <head>
and replace the noscript content with keyword-rich text.
Run once after `pip install -r requirements.txt` in the build step.
"""
import os
import streamlit

template_path = os.path.join(
    os.path.dirname(streamlit.__file__),
    "static",
    "index.html"
)

with open(template_path, "r", encoding="utf-8") as f:
    html = f.read()

META_TAGS = """
<title>Myrux – Calculadora LSI | Índice de Saturación de Langelier</title>
<meta name="description" content="Calculadora gratuita del Índice de Saturación de Langelier (LSI). Evalúa si el agua es corrosiva o incrustante. Ideal para cisternas, torres de enfriamiento, calderas y agua potable en hotelería.">
<meta name="keywords" content="calculadora LSI, índice de Langelier, Langelier Saturation Index, corrosión agua, incrustación agua, pH agua, tratamiento agua, cisternas hotelería, torres enfriamiento, calidad agua potable, agua corrosiva, agua incrustante, TDS, alcalinidad, dureza cálcica">
<meta name="robots" content="index, follow">
<meta property="og:title" content="Calculadora LSI – Índice de Saturación de Langelier | Myrux">
<meta property="og:description" content="Calcula el LSI en tiempo real: pH, temperatura, alcalinidad, dureza cálcica y TDS. Herramienta gratuita para operadores de agua potable e industrial.">
<meta property="og:type" content="website">
<meta property="og:url" content="https://myrux.app">
<link rel="canonical" href="https://myrux.app">
"""

NOSCRIPT = """<noscript>
<h1>Calculadora del Índice de Saturación de Langelier (LSI) — Gratis | Myrux</h1>
<p>Myrux ofrece una calculadora gratuita del Índice de Saturación de Langelier (LSI) para evaluar la tendencia del agua a formar incrustaciones de carbonato de calcio o a presentar corrosión en tuberías, cisternas, torres de enfriamiento, calderas y sistemas de agua potable en hotelería e industria.</p>
<p>El LSI se calcula con: pH, temperatura, TDS (sólidos disueltos totales), dureza cálcica y alcalinidad.</p>
<p>Aplicaciones: cisternas hoteleras, torres de enfriamiento, calderas, piscinas, sistemas de ósmosis inversa y plantas de tratamiento de agua potable.</p>
<p>Interpretación: LSI negativo = agua corrosiva. LSI cercano a 0 = agua estable. LSI positivo = agua incrustante.</p>
</noscript>"""

# 1. Replace <title>Streamlit</title> + inject meta tags after <head>
if "<title>Streamlit</title>" in html:
    html = html.replace(
        "<title>Streamlit</title>",
        META_TAGS,
        1
    )
    print("[OK] Meta tags inyectados en <head>")
else:
    print("[WARN] No se encontró <title>Streamlit</title> — revisa manualmente")

# 2. Replace noscript content
old_noscript = "<noscript>You need to enable JavaScript to run this app.</noscript>"
if old_noscript in html:
    html = html.replace(old_noscript, NOSCRIPT, 1)
    print("[OK] Noscript reemplazado con contenido SEO")
else:
    print("[WARN] No se encontró el noscript original — puede que ya esté parcheado")

with open(template_path, "w", encoding="utf-8") as f:
    f.write(html)

print(f"[OK] Template guardado: {template_path}")

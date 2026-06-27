# core/config.py
from pathlib import Path
import os
from dotenv import load_dotenv
from urllib.parse import urlparse

# -----------------------------
# CARGAR VARIABLES DE ENTORNO
# -----------------------------
load_dotenv()

ENV = os.getenv("ENV", "local").lower()

# -----------------------------
# BASE DEL PROYECTO
# -----------------------------
BASE_DIR = Path(__file__).resolve().parent.parent

# -----------------------------
# DATABASE CONFIG
# -----------------------------
DATABASE_URL = os.getenv("DATABASE_URL")


# 🔥 DETECCIÓN ROBUSTA
def detect_db_type(url):
    if not url:
        return "sqlite"

    url = url.lower()

    if url.startswith("postgres://") or url.startswith("postgresql://"):
        return "postgres"

    raise ValueError(f"❌ DATABASE_URL no soportada: {url}")

DB_TYPE = detect_db_type(DATABASE_URL)

# -----------------------------
# SQLITE (LOCAL)
# -----------------------------
DB_PATH = BASE_DIR / "data" / "app.db"

if DB_TYPE == "sqlite":
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)

# -----------------------------
# VALIDACIÓN PRODUCCIÓN
# -----------------------------
if ENV == "production":
    if DB_TYPE != "postgres":
        raise ValueError("❌ En producción debes usar PostgreSQL (Neon)")

    if not DATABASE_URL:
        raise ValueError("❌ DATABASE_URL es obligatoria en producción")

# -----------------------------
# INFO DE CONEXIÓN
# -----------------------------
def get_db_info():
    if DB_TYPE == "sqlite":
        return {
            "engine": "sqlite",
            "host": "local",
            "db": str(DB_PATH),
            "user": None
        }

    parsed = urlparse(DATABASE_URL)

    return {
        "engine": "postgres",
        "host": parsed.hostname,
        "db": parsed.path.replace("/", ""),
        "user": parsed.username
    }

# -----------------------------
# APP
# -----------------------------
APP_NAME = "Calculadora Índice de Saturación Langelier (LSI)"
APP_VERSION = "1.0.0"

# -----------------------------
# SEGURIDAD
# -----------------------------
SESSION_TIMEOUT_MINUTES = 60

COOKIE_SECRET = os.getenv(
    "COOKIE_SECRET",
    "myrux-change-this-in-production"
)

# -----------------------------
# PARÁMETROS DE NEGOCIO (RSI)
# -----------------------------
RSI_IDEAL_MIN = 6.5
RSI_IDEAL_MAX = 7.5

RSI_MUYINCRUSTANTE = 6.0
RSI_MUYCORROSIVO = 8.5

# -----------------------------
# DEBUG
# -----------------------------
DEBUG = ENV == "local"
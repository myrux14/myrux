import streamlit as st
import requests

from core.database import get_connection
from core.config import DB_TYPE
from core.db_utils import p


_PRIVATE_PREFIXES = (
    "127.", "10.", "192.168.", "172.16.", "172.17.",
    "172.18.", "172.19.", "172.20.", "172.21.", "172.22.",
    "172.23.", "172.24.", "172.25.", "172.26.", "172.27.",
    "172.28.", "172.29.", "172.30.", "172.31.", "::1", ""
)


def _get_ip(headers: dict) -> str:
    h = {
        k.lower(): v
        for k, v in headers.items()
    }
    forwarded = h.get("x-forwarded-for", "")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return h.get("x-real-ip", "")


def _anonymize_ip(ip: str) -> str:
    if not ip:
        return ""

    if ":" in ip:
        # IPv6: cortar últimos 4 grupos
        parts = ip.split(":")
        if len(parts) > 4:
            return ":".join(parts[:4]) + "::"
        return ip

    # IPv4: reemplazar último octeto
    parts = ip.split(".")
    if len(parts) == 4:
        parts[3] = "0"
        return ".".join(parts)

    return ip


def _geo_from_ip(ip: str) -> dict:
    if not ip or ip.startswith(_PRIVATE_PREFIXES):
        return {"country": "local", "city": "local"}
    try:
        r = requests.get(
            f"https://ipapi.co/{ip}/json/",
            timeout=2
        )
        data = r.json()
        if not data.get("error"):
            return {"country": data.get("country_name", ""), "city": data.get("city", "")}
    except Exception:
        pass
    return {"country": "", "city": ""}


def _parse_ua(ua_string: str) -> dict:
    try:
        import user_agents
        ua = user_agents.parse(ua_string)
        if ua.is_bot:
            device_type = "bot"
        elif ua.is_mobile:
            device_type = "mobile"
        elif ua.is_tablet:
            device_type = "tablet"
        else:
            device_type = "desktop"
        return {
            "device_type": device_type,
            "browser": ua.browser.family or "",
            "os": ua.os.family or "",
        }
    except Exception:
        return {"device_type": "", "browser": "", "os": ""}


def register_visit(page: str = "public_lsi"):

    conn = None
    cursor = None

    try:
        headers = dict(st.context.headers)
    except Exception:
        headers = {}

    raw_ip = _get_ip(headers)
    geo = _geo_from_ip(raw_ip)
    anon_ip = _anonymize_ip(raw_ip)
    ua_info = _parse_ua(headers.get("user-agent", ""))
    referrer = headers.get("referer", "")
    language = headers.get("accept-language", "").split(",")[0].strip()

    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            f"""
            INSERT INTO analytics_visits (
                page, ip, country, city,
                device_type, browser, os,
                referrer, language
            )
            VALUES (
                {p()}, {p()}, {p()}, {p()},
                {p()}, {p()}, {p()},
                {p()}, {p()}
            )
            """,
            (
                page,
                anon_ip,
                geo["country"],
                geo["city"],
                ua_info["device_type"],
                ua_info["browser"],
                ua_info["os"],
                referrer,
                language,
            )
        )

        conn.commit()

    except Exception as e:
        print("Error registrando visita:", e)
        if conn:
            conn.rollback()

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
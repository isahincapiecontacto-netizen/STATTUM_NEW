"""Identidad visual y configuración compartida de STATTUM."""
from datetime import date
from hashlib import sha256

ACTIVOS_BASE = {
    "EXITO.CL": {"nombre": "Éxito", "sector": "Comercio", "color": "#E8B400", "moneda": "COP"},
    "ECOPETROL.CL": {"nombre": "Ecopetrol", "sector": "Energía", "color": "#1B8A3D", "moneda": "COP"},
    "PFCIBEST.CL": {"nombre": "Cibest", "sector": "Financiero", "color": "#1F4E9C", "moneda": "COP"},
    "ICOLCAP.CL": {"nombre": "ICOLCAP", "sector": "ETF de mercado", "color": "#6B7280", "moneda": "COP"},
}
PREDETERMINADOS = list(ACTIVOS_BASE)
PALETA_EXTRAS = ["#8B5CF6", "#ED6A2F", "#0D9488", "#D94696", "#A16207", "#4F46E5", "#0891B2"]
FECHA_INICIAL = date(2021, 11, 9)
FECHA_FINAL = date(2026, 11, 6)
TASA_LIBRE_RIESGO = 0.04
MAX_ACTIVOS = 8
# Mantiene la depuración usada por el código original; no se presenta como elemento visual.
APLICAR_DEPURACION_HISTORICA = True


def nombre_activo(ticker: str) -> str:
    return ACTIVOS_BASE.get(ticker, {}).get("nombre", ticker)


def color_activo(ticker: str) -> str:
    if ticker in ACTIVOS_BASE:
        return ACTIVOS_BASE[ticker]["color"]
    indice = int(sha256(ticker.encode("utf-8")).hexdigest()[:8], 16) % len(PALETA_EXTRAS)
    return PALETA_EXTRAS[indice]


def colores(tickers) -> dict:
    """Colores de activos predefinidos fijos; extras distintos entre sí siempre que sea posible."""
    salida = {t: color_activo(t) for t in tickers}
    extras = sorted(t for t in tickers if t not in ACTIVOS_BASE)
    for i, ticker in enumerate(extras):
        salida[ticker] = PALETA_EXTRAS[i % len(PALETA_EXTRAS)]
    return salida

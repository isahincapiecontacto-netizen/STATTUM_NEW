"""Descarga y validación de datos de mercado mediante Yahoo Finance."""
from __future__ import annotations
from datetime import date, timedelta
import re
import numpy as np
import pandas as pd
import yfinance as yf

PATRON_TICKER = re.compile(r"^[A-Z0-9^][A-Z0-9.=_^\-]{0,19}$")


def normalizar_ticker(texto: str) -> str:
    return texto.strip().upper()


def ticker_valido(ticker: str) -> bool:
    return bool(PATRON_TICKER.fullmatch(ticker))


def descargar_precios(tickers: tuple[str, ...], inicio: date, fin: date) -> pd.DataFrame:
    """Yahoo interpreta `end` como exclusivo: incluir último día sumando uno."""
    if not tickers:
        return pd.DataFrame()
    raw = yf.download(
        tickers=list(tickers), start=str(inicio), end=str(fin + timedelta(days=1)),
        auto_adjust=True, progress=False, threads=True, group_by="column",
    )
    if raw is None or raw.empty:
        return pd.DataFrame()
    if isinstance(raw.columns, pd.MultiIndex):
        if "Close" in raw.columns.get_level_values(0):
            precios = raw["Close"]
        elif "Close" in raw.columns.get_level_values(1):
            precios = raw.xs("Close", axis=1, level=1)
        else:
            raise ValueError("La fuente no devolvió una columna de precios de cierre.")
    else:
        if "Close" not in raw:
            raise ValueError("La fuente no devolvió precios de cierre.")
        precios = raw[["Close"]].rename(columns={"Close": tickers[0]})
    if isinstance(precios, pd.Series):
        precios = precios.to_frame(tickers[0])
    precios = precios.copy()
    precios.index = pd.to_datetime(precios.index).tz_localize(None)
    precios = precios.loc[~precios.index.duplicated(keep="last")].sort_index()
    precios = precios.reindex(columns=list(tickers))
    for ticker in tickers:
        precios[ticker] = pd.to_numeric(precios[ticker], errors="coerce")
    return precios.replace([np.inf, -np.inf, 0], np.nan)


def preparar_precios(crudo: pd.DataFrame, rellenar: int = 5) -> tuple[pd.DataFrame, list[str]]:
    """Conservar fechas comunes y pequeñas ausencias por falta de negociación."""
    if crudo.empty:
        return pd.DataFrame(), list(crudo.columns)
    ausentes = [c for c in crudo if crudo[c].dropna().empty]
    validos = crudo.drop(columns=ausentes)
    if validos.empty:
        return pd.DataFrame(), ausentes
    validos = validos.ffill(limit=rellenar).dropna(how="any")
    return validos, ausentes


def moneda_ticker(ticker: str) -> str | None:
    """Consulta no esencial: si falla, la app continúa sin afirmar una moneda."""
    try:
        info = yf.Ticker(ticker).fast_info
        mon = info.get("currency") if hasattr(info, "get") else info["currency"]
        return str(mon).upper() if mon else None
    except Exception:
        return None

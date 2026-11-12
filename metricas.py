"""Cálculos financieros de STATTUM, conservando los fundamentos del proyecto original.

No depende de Streamlit y puede comprobarse con pruebas automáticas.
"""
from __future__ import annotations
import numpy as np
import pandas as pd

DIAS_ANIO = 252


def retornos(precios: pd.DataFrame) -> pd.DataFrame:
    return precios.pct_change(fill_method=None).dropna(how="all")


def retorno_acumulado(precios: pd.DataFrame) -> pd.Series:
    return precios.iloc[-1] / precios.iloc[0] - 1


def retorno_anualizado(precios: pd.DataFrame) -> pd.Series:
    anios = (precios.index[-1] - precios.index[0]).days / 365.25
    if anios <= 0:
        return pd.Series(np.nan, index=precios.columns)
    return (precios.iloc[-1] / precios.iloc[0]) ** (1 / anios) - 1


def volatilidad_anual(rets: pd.DataFrame) -> pd.Series:
    return rets.std(ddof=1) * np.sqrt(DIAS_ANIO)


def sharpe(rets: pd.DataFrame, rf: float = 0.04) -> pd.Series:
    vol = volatilidad_anual(rets).replace(0, np.nan)
    return (rets.mean() * DIAS_ANIO - rf) / vol


def drawdown(precios: pd.DataFrame) -> pd.DataFrame:
    return precios / precios.cummax() - 1


def max_drawdown(precios: pd.DataFrame) -> pd.Series:
    return drawdown(precios).min()


def beta(rets: pd.DataFrame, benchmark: str) -> pd.Series:
    if benchmark not in rets.columns or pd.isna(rets[benchmark].var()) or rets[benchmark].var() == 0:
        return pd.Series(np.nan, index=rets.columns)
    return rets.apply(lambda s: s.cov(rets[benchmark])) / rets[benchmark].var()


def base_100(precios: pd.DataFrame) -> pd.DataFrame:
    return precios.div(precios.iloc[0]).mul(100)


def resumen(precios: pd.DataFrame, rets: pd.DataFrame, rf: float = 0.04,
            benchmark: str = "ICOLCAP.CL") -> pd.DataFrame:
    return pd.DataFrame({
        "Retorno acumulado": retorno_acumulado(precios),
        "Retorno anualizado": retorno_anualizado(precios),
        "Volatilidad anual": volatilidad_anual(rets),
        "Sharpe": sharpe(rets, rf),
        "Máx. drawdown": max_drawdown(precios),
        "Beta": beta(rets, benchmark),
    })


def limpiar_saltos(precios: pd.DataFrame, umbral: float = 0.15,
                   tolerancia: float = 0.10) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Heurística histórica original: detecta saltos grandes revertidos al día siguiente.

    No es garantía de error de origen; revisar su pertinencia cuando cambie la fuente.
    """
    p = precios.copy()
    r = precios.pct_change(fill_method=None)
    detalle = []
    for col in p.columns:
        hoy = r[col]
        siguiente = hoy.shift(-1)
        mascara = (
            (hoy.abs() > umbral)
            & (hoy * siguiente < 0)
            & ((((1 + hoy) * (1 + siguiente)) - 1).abs() < tolerancia)
        ).fillna(False)
        for fecha in hoy.index[mascara]:
            idx = p.index.get_loc(fecha)
            if idx == 0:
                continue
            detalle.append({"Fecha": fecha, "Ticker": col, "Precio original": float(precios.loc[fecha, col])})
            p.iloc[idx, p.columns.get_loc(col)] = p.iloc[idx - 1, p.columns.get_loc(col)]
    return p, pd.DataFrame(detalle)

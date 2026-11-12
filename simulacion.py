"""Simulación Monte Carlo por remuestreo (bootstrap) de rendimientos logarítmicos.

No presupone normalidad; toma muestras independientes de la distribución empírica
histórica. No incorpora costes, dividendos futuros ni cambios de divisa.
"""
from __future__ import annotations
import numpy as np
import pandas as pd


def monte_carlo(retornos_diarios: pd.Series, monto: float, horizonte_meses: int = 12,
                escenarios: int = 5000, confianza: float = 0.95, semilla: int = 2026) -> dict:
    if monto <= 0:
        raise ValueError("El monto debe ser mayor que cero.")
    if not (1 <= horizonte_meses <= 60):
        raise ValueError("El horizonte debe estar entre 1 y 60 meses.")
    if not (100 <= escenarios <= 20000):
        raise ValueError("El número de escenarios debe estar entre 100 y 20000.")
    if not (0.5 <= confianza <= 0.99):
        raise ValueError("La confianza debe estar entre 50 % y 99 %.")
    serie = pd.Series(retornos_diarios, dtype=float).replace([np.inf, -np.inf], np.nan).dropna()
    serie = serie[serie > -1]
    if len(serie) < 30:
        raise ValueError("Se requieren al menos 30 retornos diarios válidos.")

    dias = round(horizonte_meses * 252 / 12)
    retornos_log = np.log1p(serie.to_numpy())
    rng = np.random.default_rng(semilla)
    # `float32` evita consumo excesivo de memoria en Streamlit Community Cloud.
    variaciones = rng.choice(retornos_log, size=(dias, escenarios), replace=True).astype(np.float32)
    np.cumsum(variaciones, axis=0, out=variaciones)
    np.exp(variaciones, out=variaciones)
    variaciones *= np.float32(monto)

    inicio = np.full((1, escenarios), monto, dtype=np.float32)
    caminos = np.concatenate((inicio, variaciones), axis=0)
    q_inf = (1 - confianza) / 2
    q_sup = 1 - q_inf
    bandas = np.quantile(caminos, [q_inf, 0.5, q_sup], axis=1)
    finales = caminos[-1].astype(float)
    muestras = min(30, escenarios)
    ids = rng.choice(escenarios, size=muestras, replace=False)
    resultado = {
        "dias": dias,
        "monto": float(monto),
        "horizonte_meses": horizonte_meses,
        "escenarios": escenarios,
        "confianza": confianza,
        "media": float(finales.mean()),
        "mediana": float(np.median(finales)),
        "bajo": float(np.quantile(finales, q_inf)),
        "alto": float(np.quantile(finales, q_sup)),
        "prob_ganar": float((finales > monto).mean()),
        "banda_inferior": bandas[0],
        "banda_mediana": bandas[1],
        "banda_superior": bandas[2],
        "trayectorias": caminos[:, ids],
        "finales": finales,
    }
    return resultado

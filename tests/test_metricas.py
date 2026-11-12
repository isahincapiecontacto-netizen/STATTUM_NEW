import numpy as np
import pandas as pd
import metricas as m


def muestra():
    idx = pd.bdate_range("2024-01-01", periods=300)
    rng = np.random.default_rng(8)
    cambios = rng.normal(0.00035, 0.009, size=(300, 3))
    precios = pd.DataFrame(100 * np.cumprod(1 + cambios, axis=0), index=idx,
                           columns=["A", "B", "ICOLCAP.CL"])
    return precios


def test_resumen_y_correlacion():
    p = muestra()
    r = m.retornos(p)
    tabla = m.resumen(p, r, .04, "ICOLCAP.CL")
    assert tabla.shape == (3, 6)
    assert np.isclose(m.base_100(p).iloc[0].to_numpy(), 100).all()
    assert (tabla["Volatilidad anual"] >= 0).all()
    assert np.isclose(tabla.loc["ICOLCAP.CL", "Beta"], 1)
    assert (tabla["Máx. drawdown"] <= 0).all()


def test_salto_revertido_es_corregido():
    idx = pd.bdate_range("2026-01-01", periods=5)
    p = pd.DataFrame({"A": [100, 100, 130, 100, 101]}, index=idx)
    limpio, detalle = m.limpiar_saltos(p)
    assert limpio.iloc[2, 0] == 100
    assert not detalle.empty
    assert p.iloc[2, 0] == 130


def test_beta_sin_benchmark():
    p = muestra().drop(columns="ICOLCAP.CL")
    tabla = m.resumen(p, m.retornos(p), benchmark="")
    assert tabla["Beta"].isna().all()

import numpy as np
import pandas as pd
import pytest
from simulacion import monte_carlo
from figuras import grafica_monte_carlo, grafica_distribucion, grafica_precios, grafica_correlacion, grafica_riesgo
import metricas as m


def test_montecarlo_resultados_coherentes_y_reproducibles():
    serie = pd.Series(np.random.default_rng(4).normal(.0003, .008, 400))
    a = monte_carlo(serie, 1000000, 12, 1000, .95)
    b = monte_carlo(serie, 1000000, 12, 1000, .95)
    assert a["dias"] == 252
    assert a["trayectorias"].shape == (253, 30)
    assert a["bajo"] <= a["mediana"] <= a["alto"]
    assert 0 <= a["prob_ganar"] <= 1
    assert np.isclose(a["media"], b["media"])
    assert np.allclose(a["banda_mediana"][0], 1000000)
    assert len(grafica_monte_carlo(a).frames) >= 5
    assert len(grafica_distribucion(a).data) == 1


def test_montecarlo_rechaza_datos_insuficientes():
    with pytest.raises(ValueError):
        monte_carlo(pd.Series([.01] * 10), 1000)


def test_figuras_datos_sinteticos():
    idx = pd.bdate_range("2025-01-01", periods=140)
    p = pd.DataFrame({"EXITO.CL": np.linspace(90, 130, 140),
                      "ECOPETROL.CL": np.linspace(110, 93, 140)}, index=idx)
    r = m.retornos(p)
    tabla = m.resumen(p, r)
    assert len(grafica_precios(p).data) == 2
    assert len(grafica_riesgo(tabla).data) == 2
    assert len(grafica_correlacion(r).data) == 1

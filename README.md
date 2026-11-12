# STATTUM · Análisis financiero inteligente

**Una aplicación interactiva de análisis financiero desarrollada con Python y Streamlit.** Permite explorar el comportamiento histórico de activos bursátiles, comparar rentabilidad y riesgo, añadir nuevos tickers, simular escenarios de inversión mediante Monte Carlo y consultar conclusiones dinámicas.

## Pantallas

| Pestaña | Contenido |
|---|---|
| **Inicio** | Identidad original de STATTUM, presentación sencilla y los cuatro activos iniciales. |
| **Análisis** | Agregar otro ticker, seleccionar activos, precios normalizados, riesgo–rentabilidad, correlaciones e indicadores. |
| **Simulador** | Monto de inversión, horizonte, simulación Monte Carlo interactiva, escenarios y probabilidades. |
| **Conclusiones** | Interpretaciones automáticas, indicadores destacados y perspectivas según tres perfiles. |

**No incluye** una pestaña de Metodología ni un aviso inferior de «Importante». Los detalles técnicos se documentan aquí, sin recargar la interfaz.

## Identidad de activos

| Activo | Ticker original | Color que se conserva |
|---|---|---|
| Éxito | `EXITO.CL` | Amarillo `#E8B400` |
| Ecopetrol | `ECOPETROL.CL` | Verde `#1B8A3D` |
| Cibest | `PFCIBEST.CL` | Azul `#1F4E9C` |
| ICOLCAP | `ICOLCAP.CL` | Gris `#6B7280` |

Se respetan el logo aportado por el equipo y la identidad de cada activo. Los tickers adicionales reciben colores nuevos. Los símbolos iniciales se mantienen exactamente como están en el proyecto original y deben comprobarse con Yahoo Finance si la fuente modifica su nomenclatura.

## Empezar

Necesitas **Python 3.10 o posterior**.

```bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
# source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

La aplicación se abrirá en `http://localhost:8501`. Requiere conexión a internet para descargar precios y validar tickers de Yahoo Finance. Las descargas se almacenan temporalmente en caché para reducir solicitudes.

## Estructura del repositorio

```text
STATTUM_Concurso/
├── app.py                    # Navegación y las cuatro pantallas
├── config.py                 # Activos originales y colores
├── datos.py                  # Yahoo Finance, validación y fechas comunes
├── metricas.py               # Indicadores financieros
├── simulacion.py             # Monte Carlo por bootstrap
├── figuras.py                # Gráficas interactivas Plotly
├── estilos.py                # Identidad visual y CSS
├── assets/
│   ├── logo_stattum.png      # Logo original recortado para la interfaz
│   └── logo_original_completo.jpg
├── .streamlit/config.toml    # Tema visual
├── requirements.txt
├── tests/                    # Pruebas de cálculo
├── GUIA_GITHUB_Y_STREAMLIT.md
└── README.md
```

## Cómo funciona el análisis

- **Datos:** precios diarios ajustados descargados de Yahoo Finance con `yfinance`, inicialmente del 9 de noviembre de 2021 al 6 de noviembre de 2026 (fechas modificables).
- **Limpieza:** se rellenan pequeños faltantes de negociación (hasta cinco observaciones) y se alinean fechas entre activos; se mantiene como proceso interno la heurística de saltos reversados utilizada en el repositorio original, sin exponer mensajes sobre «precios sospechosos». Una heurística de este tipo puede corregir movimientos reales; se recomienda verificarla antes de usar los resultados en informes.
- **Rentabilidad anualizada:** CAGR calculado con el número de años calendario entre primera y última cotización común.
- **Volatilidad anualizada:** desviación típica de rendimientos diarios multiplicada por la raíz de 252.
- **Sharpe:** `(promedio diario × 252 − tasa de referencia) / volatilidad anual`. La tasa inicial es 4 % anual y se puede cambiar en Análisis.
- **Drawdown máximo:** caída máxima respecto a máximos históricos previos.
- **Beta:** sensibilidad de rendimientos frente al ETF ICOLCAP, cuando está incluido en la comparación.
- **Correlación:** correlación de rendimientos diarios de fechas alineadas.

### Monte Carlo

Se utiliza **remuestreo con reemplazo (bootstrap)** de rendimientos logarítmicos diarios históricos del activo; se acumulan para crear de 1.000 a 10.000 trayectorias. Se muestran la media de valores finales, un intervalo central (80 %, 90 % o 95 %), una distribución de resultados y la fracción de escenarios con resultado por encima de la inversión inicial.

**La simulación no equivale a una predicción:** supone que los rendimientos pasados son representativos y que se pueden remuestrear de manera independiente; no estima efectos cambiarios, comisiones, impuestos, liquidez futura ni cambios estructurales. El rango es un conjunto de escenarios del modelo, no una garantía.

Para tickers internacionales, los precios se analizan en su **moneda de cotización** y el monto simulado se expresa en esa misma unidad, sin conversión a COP. No se deben sumar directamente precios en monedas diferentes; la aplicación compara variaciones porcentuales y valores normalizados.

## Ejecutar pruebas

```bash
pip install pytest
python -m pytest -q
```

## Créditos y continuidad

STATTUM es una creación del equipo de estudiantes **Isabella Hincapié, Manuela Bohórquez y Yuliana Pineda**. Esta versión toma como base y reconoce el trabajo del [repositorio inicial STATTUM](https://github.com/valentinapineda434-lab/STATTUM): cálculos financieros, tickers originales, colores por empresa y posibilidad de añadir activos. El logo original se incluye tal como fue facilitado por el equipo.

## Publicación

La guía paso a paso está en **[`GUIA_GITHUB_Y_STREAMLIT.md`](GUIA_GITHUB_Y_STREAMLIT.md)**. En Streamlit Community Cloud selecciona `app.py` como archivo principal y utiliza la rama `main`.

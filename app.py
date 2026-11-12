"""STATTUM | Análisis financiero inteligente.

Para iniciar localmente: streamlit run app.py
Estructura final: Inicio · Análisis · Simulador · Conclusiones.
"""
from __future__ import annotations
from datetime import date
from html import escape
from pathlib import Path

import numpy as np
import pandas as pd
import streamlit as st

import datos
import metricas as m
from config import (
    ACTIVOS_BASE, PREDETERMINADOS, FECHA_INICIAL, FECHA_FINAL,
    TASA_LIBRE_RIESGO, MAX_ACTIVOS, APLICAR_DEPURACION_HISTORICA,
    nombre_activo, colores,
)
from estilos import (
    inyectar_css, encabezado, seccion, tarjetas_activos,
    tarjetas_kpi, panel_insight, pie_pagina,
)
from figuras import (
    grafica_precios, grafica_riesgo, grafica_correlacion,
    grafica_drawdown, grafica_monte_carlo, grafica_distribucion,
)
from simulacion import monte_carlo

ROOT = Path(__file__).resolve().parent
PAGINAS = ["Inicio", "Análisis", "Simulador", "Conclusiones"]

st.set_page_config(
    page_title="STATTUM | Análisis financiero inteligente",
    page_icon="📈", layout="wide", initial_sidebar_state="collapsed",
)
inyectar_css()


def iniciar_sesion() -> None:
    valores = {
        "pagina_actual": "Inicio",
        "activos": list(PREDETERMINADOS),
        "extras": [],
        "divisas": {ticker: meta["moneda"] for ticker, meta in ACTIVOS_BASE.items()},
        "fecha_inicio": FECHA_INICIAL,
        "fecha_fin": FECHA_FINAL,
        "tasa_rf": TASA_LIBRE_RIESGO,
        "ultima_simulacion": None,
        "selector_version": 0,
    }
    for llave, valor in valores.items():
        if llave not in st.session_state:
            st.session_state[llave] = valor


def ir_a(pagina: str) -> None:
    if pagina in PAGINAS:
        st.session_state["pagina_actual"] = pagina
        st.rerun()


def render_navegacion() -> None:
    with st.container(key="site_header"):
        cols = st.columns([1.62, 1.04, 1.10, 1.20, 1.33], vertical_alignment="center", gap="small")
        with cols[0]:
            st.image(str(ROOT / "assets" / "logo_stattum.png"), width=210)
        etiquetas = {"Inicio": "⌂  Inicio", "Análisis": "▥  Análisis", "Simulador": "▦  Simulador", "Conclusiones": "◎  Conclusiones"}
        for i, pagina in enumerate(PAGINAS, start=1):
            with cols[i]:
                if st.button(etiquetas[pagina], key=f"navegar_{pagina}",
                             type="primary" if pagina == st.session_state.pagina_actual else "secondary",
                             use_container_width=True):
                    ir_a(pagina)


def formato_dinero(valor: float, moneda: str = "COP") -> str:
    if moneda in {"COP", "CLP"}:
        numero = f"{valor:,.0f}".replace(",", ".")
    else:
        numero = f"{valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return f"{moneda} {numero}" if moneda and moneda != "N/D" else numero


def formato_pct(x: float) -> str:
    return f"{x:+.1%}" if np.isfinite(x) else "N/D"


def pagina_inicio() -> None:
    with st.container(key="home_hero"):
        izquierda, derecha = st.columns([1, 1.14], gap="large", vertical_alignment="center")
        with izquierda:
            st.image(str(ROOT / "assets" / "logo_stattum.png"), use_container_width=True)
        with derecha:
            st.markdown("""
            <div class="hero-kicker">Inteligencia financiera en tus manos</div>
            <div class="hero-title">Analiza, comprende y <span>decide mejor.</span></div>
            <p class="hero-sub">Conoce el comportamiento de activos del mercado colombiano,
            compara su rentabilidad y riesgo, y explora posibles escenarios de inversión
            con información que cualquier persona puede entender.</p>
            <svg class="hero-chart" viewBox="0 0 540 110" role="img" aria-label="Línea financiera que crece progresivamente">
              <path class="area" d="M0 104 L22 88 L70 95 L114 58 L160 77 L210 49 L260 63 L305 31 L352 48 L395 22 L445 38 L490 11 L530 7 L540 110 L0 110 Z"/>
              <path class="trace" d="M0 104 L22 88 L70 95 L114 58 L160 77 L210 49 L260 63 L305 31 L352 48 L395 22 L445 38 L490 11 L530 7"/>
            </svg>
            """, unsafe_allow_html=True)
            if st.button("Comenzar análisis   →", key="ir_analisis_hero", type="primary", use_container_width=True):
                ir_a("Análisis")

    seccion("¿Qué puedes hacer con STATTUM?")
    st.markdown("""
    <div class="feature-grid">
      <div class="feature-card"><span class="feature-icon">▥</span><b>Compara activos</b>
        <span class="description">Contrasta el desempeño de empresas y agrega nuevos tickers.</span></div>
      <div class="feature-card"><span class="feature-icon">◇</span><b>Entiende el riesgo</b>
        <span class="description">Explora volatilidad, caídas y correlaciones con gráficas claras.</span></div>
      <div class="feature-card"><span class="feature-icon">⌁</span><b>Simula escenarios</b>
        <span class="description">Ingresa un monto y visualiza resultados con Monte Carlo.</span></div>
      <div class="feature-card"><span class="feature-icon">◎</span><b>Recibe conclusiones</b>
        <span class="description">Convierte los indicadores en interpretaciones comprensibles.</span></div>
    </div>
    """, unsafe_allow_html=True)
    seccion("Nuestros cuatro activos de partida", "Cada activo conserva su color en todas las visualizaciones.")
    tarjetas_activos(PREDETERMINADOS)
    pie_pagina()


@st.cache_data(ttl=3600, show_spinner=False)
def cargar_crudo(tickers: tuple[str, ...], inicio: date, fin: date) -> pd.DataFrame:
    return datos.descargar_precios(tickers, inicio, fin)


@st.cache_data(ttl=86400, show_spinner=False)
def moneda_de_mercado(ticker: str) -> str | None:
    return datos.moneda_ticker(ticker)


def datos_activos() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame] | None:
    seleccion = list(dict.fromkeys(st.session_state.activos))
    if not seleccion:
        st.info("Selecciona al menos un activo en la pestaña Análisis.")
        return None
    if st.session_state.fecha_inicio >= st.session_state.fecha_fin:
        st.warning("La fecha inicial debe ser anterior a la fecha final.")
        return None
    try:
        with st.spinner("Consultando los datos históricos del mercado…"):
            bruto = cargar_crudo(tuple(seleccion), st.session_state.fecha_inicio, st.session_state.fecha_fin)
            precios, faltantes = datos.preparar_precios(bruto)
    except Exception:
        st.error("No fue posible conectarse con la fuente de precios. Comprueba la conexión y vuelve a intentarlo.")
        return None
    if faltantes:
        st.warning("Sin datos disponibles para: " + ", ".join(faltantes) + ". Puedes retirar esos tickers desde Análisis.")
    if precios.empty or len(precios) < 35:
        st.warning("No hay suficientes fechas comunes para analizar los activos elegidos. Ajusta el periodo o la selección en Análisis.")
        return None
    if APLICAR_DEPURACION_HISTORICA:
        precios, _ = m.limpiar_saltos(precios)
    rets = m.retornos(precios)
    if len(rets) < 30:
        st.warning("Se necesitan más datos diarios para calcular los indicadores.")
        return None
    benchmark = "ICOLCAP.CL" if "ICOLCAP.CL" in precios.columns else ""
    tabla = m.resumen(precios, rets, st.session_state.tasa_rf, benchmark)
    return precios, rets, tabla


def gestionar_ticker() -> None:
    with st.form("form_nuevo_ticker", clear_on_submit=True, border=False):
        nuevo = st.text_input("Agregar otra empresa", placeholder="Ticker: AAPL, MSFT, BOG…", max_chars=20,
                              help="Introduce el símbolo exacto de Yahoo Finance; puede incluir punto o guion.")
        pulsado = st.form_submit_button("＋ Agregar activo", type="primary", use_container_width=True)
    if not pulsado:
        return
    ticker = datos.normalizar_ticker(nuevo)
    if not datos.ticker_valido(ticker):
        st.error("Escribe un ticker válido; por ejemplo, AAPL o MSFT.")
        return
    disponibles = PREDETERMINADOS + st.session_state.extras
    if ticker in disponibles:
        if ticker not in st.session_state.activos:
            st.session_state.activos.append(ticker)
            st.session_state.selector_version += 1
            st.rerun()
        st.info("Ese ticker ya está disponible en el análisis.")
        return
    if len(disponibles) >= MAX_ACTIVOS:
        st.warning(f"Para mantener las gráficas legibles se admiten hasta {MAX_ACTIVOS} activos a la vez.")
        return
    try:
        with st.spinner("Validando el ticker en Yahoo Finance…"):
            verificacion = cargar_crudo((ticker,), st.session_state.fecha_inicio, st.session_state.fecha_fin)
            observaciones = int(verificacion[ticker].dropna().shape[0]) if ticker in verificacion else 0
    except Exception:
        observaciones = 0
    if observaciones < 35:
        st.error("No se encontraron suficientes precios para ese ticker y periodo. Revisa el símbolo o las fechas.")
        return
    with st.spinner("Consultando la moneda del nuevo activo…"):
        moneda = moneda_de_mercado(ticker)
    st.session_state.divisas[ticker] = moneda or "N/D"
    st.session_state.extras.append(ticker)
    st.session_state.activos.append(ticker)
    st.session_state.selector_version += 1
    st.rerun()


def pagina_analisis() -> None:
    encabezado("Análisis de activos", "Explora precios, riesgo y correlaciones; personaliza la comparación con tus propios tickers.", "▥")
    col_selector, col_agregar = st.columns([2.15, 1], gap="large")
    with col_selector:
        opciones = PREDETERMINADOS + st.session_state.extras
        seleccion = st.multiselect(
            "Activos para comparar", options=opciones,
            default=[a for a in st.session_state.activos if a in opciones],
            format_func=lambda t: f"{nombre_activo(t)} · {t}",
            help="Elige los activos que deseas visualizar. Tu selección también se utiliza en el Simulador y en Conclusiones.",
            key=f"seleccion_activos_{st.session_state.selector_version}",
        )
        st.session_state.activos = list(seleccion)
        with st.expander("Ajustar fechas y parámetros", expanded=False):
            f1, f2 = st.columns(2)
            with f1:
                st.session_state.fecha_inicio = st.date_input(
                    "Desde", value=st.session_state.fecha_inicio, max_value=date.today(),
                    key="control_fecha_inicio",
                )
            with f2:
                st.session_state.fecha_fin = st.date_input(
                    "Hasta", value=st.session_state.fecha_fin, max_value=date.today(),
                    key="control_fecha_fin",
                )
            st.session_state.tasa_rf = st.slider(
                "Tasa anual de referencia para el indicador Sharpe (%)", 0.0, 20.0,
                value=float(st.session_state.tasa_rf * 100), step=0.5,
                key="control_rf",
            ) / 100
        if st.session_state.extras:
            with st.expander("Administrar tickers añadidos", expanded=False):
                ticker_borrar = st.selectbox("Ticker que deseas retirar", options=st.session_state.extras,
                                             key="ticker_borrar")
                if st.button("Retirar del catálogo", key="btn_borrar_ticker"):
                    st.session_state.extras.remove(ticker_borrar)
                    st.session_state.activos = [t for t in st.session_state.activos if t != ticker_borrar]
                    st.session_state.divisas.pop(ticker_borrar, None)
                    st.session_state.selector_version += 1
                    st.rerun()
    with col_agregar:
        gestionar_ticker()

    resultado = datos_activos()
    if resultado is None:
        return
    precios, rets, tabla = resultado
    seccion("Activos en tu análisis")
    tarjetas_activos(precios.columns, tabla)
    if any((st.session_state.divisas.get(t, "COP") not in ("COP", "N/D")) for t in precios):
        st.caption("Los retornos se calculan en la moneda original de cada activo; la comparación no incluye cambios de divisa.")
    seccion("Explora el comportamiento del mercado")
    c1, c2 = st.columns([1.38, 1], gap="medium")
    with c1:
        st.markdown("#### Evolución de precios · base 100")
        st.caption("Todos comienzan en 100 para comparar trayectorias independientemente de su precio.")
        st.plotly_chart(grafica_precios(precios), use_container_width=True, config={"displaylogo": False})
    with c2:
        st.markdown("#### Riesgo frente a rentabilidad")
        st.caption("Arriba indica mayor rentabilidad histórica; a la izquierda, menor volatilidad.")
        st.plotly_chart(grafica_riesgo(tabla), use_container_width=True, config={"displaylogo": False})

    st.markdown("#### ¿Qué tan relacionados están los activos?")
    if len(precios.columns) >= 2:
        st.caption("La correlación muestra si tienden a moverse juntos; valores cercanos a cero sugieren menor relación lineal.")
        st.plotly_chart(grafica_correlacion(rets), use_container_width=True, config={"displaylogo": False})
    else:
        st.caption("Selecciona dos o más activos para calcular correlaciones.")

    with st.expander("Ver indicadores financieros en detalle", expanded=False):
        vista = tabla.copy().rename(index=nombre_activo)
        formato = {
            "Retorno acumulado": "{:.1%}", "Retorno anualizado": "{:.1%}",
            "Volatilidad anual": "{:.1%}", "Sharpe": "{:.2f}",
            "Máx. drawdown": "{:.1%}", "Beta": "{:.2f}",
        }
        st.dataframe(vista.style.format(formato, na_rep="—"), use_container_width=True)
        st.markdown("#### Caída desde el máximo previo")
        st.plotly_chart(grafica_drawdown(precios), use_container_width=True, config={"displaylogo": False})
    pie_pagina()


def pagina_simulador() -> None:
    encabezado("Simulador de inversión", "Introduce un monto y visualiza miles de escenarios posibles con Monte Carlo.", "▦")
    resultado = datos_activos()
    if resultado is None:
        return
    precios, rets, _ = resultado
    izquierda, derecha = st.columns([1, 2.25], gap="large")
    with izquierda:
        st.markdown("### Configura tu simulación")
        opciones = list(rets.columns)
        if st.session_state.get("activo_sim") not in opciones:
            st.session_state["activo_sim"] = opciones[0]
        ticker = st.selectbox("Activo para simular", options=opciones,
                              format_func=lambda t: f"{nombre_activo(t)} · {t}", key="activo_sim")
        moneda = st.session_state.divisas.get(ticker, "N/D")
        if moneda == "N/D":
            st.caption("No se pudo verificar la divisa del ticker: utiliza el importe en su moneda de cotización.")
        inicial = 1_000_000.0 if moneda == "COP" else 1_000.0
        monto = st.number_input(
            f"Monto a invertir ({moneda if moneda != 'N/D' else 'moneda del activo'})",
            min_value=1.0, value=inicial, step=50_000.0 if moneda == "COP" else 100.0,
            format="%.2f", key=f"monto_{ticker}",
        )
        meses = st.selectbox("Horizonte de inversión", [6, 12, 24, 36, 60],
                             index=1, format_func=lambda x: (f"{x} meses" if x < 12 else f"{x//12} año" + ("s" if x > 12 else "")),
                             key="sim_meses")
        with st.expander("Opciones de simulación", expanded=False):
            n_sim = st.select_slider("Cantidad de escenarios", [1000, 2500, 5000, 10000], value=5000,
                                     key="sim_n")
            confianza = st.select_slider("Intervalo central", [0.80, 0.90, 0.95], value=0.95,
                                         format_func=lambda x: f"{x:.0%}", key="sim_ci")
        # La firma evita reutilizar una simulación cuando cambian los datos o los parámetros.
        firma_datos = pd.util.hash_pandas_object(rets[ticker], index=True).sum()
        firma = (ticker, float(monto), int(meses), int(st.session_state.get("sim_n", 5000)),
                 float(st.session_state.get("sim_ci", 0.95)),
                 str(st.session_state.fecha_inicio), str(st.session_state.fecha_fin),
                 str(firma_datos))
        pulsado = st.button("▶   Simular inversión", type="primary", use_container_width=True)
        if pulsado:
            try:
                with st.spinner("Calculando posibles trayectorias de inversión…"):
                    sim = monte_carlo(rets[ticker], monto, meses, firma[3], firma[4])
                st.session_state.ultima_simulacion = {
                    "firma": firma, "datos": sim, "ticker": ticker, "moneda": moneda,
                    "fecha_inicio": st.session_state.fecha_inicio,
                    "fecha_fin": st.session_state.fecha_fin,
                }
            except ValueError as exc:
                st.error(str(exc))
        st.caption("Los escenarios se construyen remuestreando rendimientos históricos diarios del activo elegido.")

    anterior = st.session_state.get("ultima_simulacion")
    vigente = anterior is not None and anterior.get("firma") == firma
    with derecha:
        if not vigente:
            st.markdown("""
            <div class="info-card" style="min-height:270px;display:flex;flex-direction:column;justify-content:center">
              <span class="pill soft-plain" style="width:max-content;margin-bottom:15px">SIMULACIÓN MONTE CARLO</span>
              <h3 style="font-size:1.65rem">Tu inversión, miles de posibilidades.</h3>
              <p>Selecciona un activo, indica cuánto deseas invertir y presiona
              <b>«Simular inversión»</b> para descubrir el rango de resultados que genera el modelo.</p>
              <div style="margin-top:22px;height:8px;border-radius:8px;
                 background:linear-gradient(90deg,#D9EDFC,#0FA5E9,#86E2FB,#D9EDFC)"></div>
            </div>
            """, unsafe_allow_html=True)
        else:
            sim = anterior["datos"]
            tarjetas_kpi([
                ("Valor medio simulado", formato_dinero(sim["media"], moneda), "Promedio de escenarios", "#168E65"),
                ("Escenario inferior", formato_dinero(sim["bajo"], moneda), f"Percentil {(1-sim['confianza'])/2:.1%}", "#F1932B"),
                ("Escenario superior", formato_dinero(sim["alto"], moneda), f"Percentil {1-(1-sim['confianza'])/2:.1%}", "#087DD7"),
                ("Probabilidad de ganancia", f"{sim['prob_ganar']:.1%}", "Frecuencia en la simulación", "#8B5CF6"),
            ])
            st.markdown(f"#### Trayectorias posibles · {escape(nombre_activo(ticker))}")
            st.plotly_chart(grafica_monte_carlo(sim, colores([ticker])[ticker]),
                            use_container_width=True, config={"displaylogo": False})
            st.caption(f"La zona sombreada contiene el {sim['confianza']:.0%} central de los escenarios simulados en cada momento; cada línea fina es una trayectoria posible.")
    if vigente:
        seccion("Distribución de resultados", "Así se distribuyen los valores finales de los escenarios calculados.")
        st.plotly_chart(grafica_distribucion(anterior["datos"], colores([ticker])[ticker]),
                        use_container_width=True, config={"displaylogo": False})
        sim = anterior["datos"]
        variacion_media = sim["media"] / sim["monto"] - 1
        panel_insight(
            f"Para {nombre_activo(ticker)}, el valor medio simulado al cabo de {meses} meses equivale a "
            f"una variación de {variacion_media:+.1%} sobre el monto inicial. "
            f"El intervalo mostrado expresa variabilidad de escenarios, no una rentabilidad garantizada.",
            "Cómo interpretar la simulación",
        )
    pie_pagina()


def pagina_conclusiones() -> None:
    encabezado("Conclusiones", "Comprende los resultados del análisis y explora su significado para distintos perfiles.", "◎")
    resultado = datos_activos()
    if resultado is None:
        return
    precios, rets, tabla = resultado
    validas = tabla.dropna(subset=["Retorno anualizado", "Volatilidad anual"])
    if validas.empty:
        st.info("Todavía no hay indicadores suficientes para interpretar.")
        return
    mejor = validas["Retorno anualizado"].idxmax()
    estable = validas["Volatilidad anual"].idxmin()
    riesgoso = validas["Volatilidad anual"].idxmax()
    candidatos_sharpe = validas["Sharpe"].replace([np.inf, -np.inf], np.nan).dropna()
    equilibrado = candidatos_sharpe.idxmax() if not candidatos_sharpe.empty else estable

    seccion("Hallazgos del periodo analizado")
    tarjetas_kpi([
        ("Mayor retorno anualizado", nombre_activo(mejor), formato_pct(validas.loc[mejor,"Retorno anualizado"]), colores([mejor])[mejor]),
        ("Menor volatilidad", nombre_activo(estable), f"{validas.loc[estable,'Volatilidad anual']:.1%} anual", colores([estable])[estable]),
        ("Mayor volatilidad", nombre_activo(riesgoso), f"{validas.loc[riesgoso,'Volatilidad anual']:.1%} anual", "#E77A40"),
        ("Mejor índice de Sharpe", nombre_activo(equilibrado), f"Sharpe {validas.loc[equilibrado,'Sharpe']:.2f}" if np.isfinite(validas.loc[equilibrado,'Sharpe']) else "Sin dato", "#8B5CF6"),
    ])

    seccion("¿Qué nos dicen los resultados?")
    n_corr = len(rets.columns)
    if n_corr >= 2:
        corr = rets.corr().copy()
        np.fill_diagonal(corr.values, np.nan)
        pares = corr.stack().dropna()
        if not pares.empty:
            (t1, t2) = pares.idxmin()
            observacion_corr = (f"{nombre_activo(t1)} y {nombre_activo(t2)} registraron una de las relaciones "
                                 f"lineales más bajas del grupo ({pares.min():.2f}); conviene examinar ese vínculo al estudiar diversificación.")
        else:
            observacion_corr = "No hay suficientes datos conjuntos para interpretar correlaciones."
    else:
        observacion_corr = "Selecciona al menos dos activos para comparar su correlación."
    cards = [
        ("↗ Rentabilidad", f"{nombre_activo(mejor)} lideró la rentabilidad anualizada en el periodo observado "
                            f"({validas.loc[mejor, 'Retorno anualizado']:+.1%})."),
        ("◇ Riesgo", f"{nombre_activo(estable)} mostró menor volatilidad anual "
                       f"({validas.loc[estable, 'Volatilidad anual']:.1%}); "
                       f"{nombre_activo(riesgoso)} registró mayor variabilidad "
                       f"({validas.loc[riesgoso, 'Volatilidad anual']:.1%})."),
        ("▥ Diversificación", observacion_corr),
    ]
    c1,c2,c3 = st.columns(3, gap="medium")
    for col, (tit, cuerpo) in zip((c1,c2,c3), cards):
        with col:
            st.markdown(f'<div class="info-card"><h3>{escape(tit)}</h3><p>{escape(cuerpo)}</p></div>',
                        unsafe_allow_html=True)

    seccion("Explora los resultados según el perfil")
    perfiles = [
        ("Perfil conservador", "Prioriza observar menores oscilaciones históricas.", estable, "soft-green"),
        ("Perfil moderado", "Compara la rentabilidad con la volatilidad asumida.", equilibrado, "soft-plain"),
        ("Perfil dinámico", "Acepta mayor exposición al riesgo al evaluar retornos.", mejor, "soft-purple"),
    ]
    columnas = st.columns(3, gap="medium")
    for col, (titulo, descripcion, ticker, clase) in zip(columnas, perfiles):
        with col:
            st.markdown(
                '<div class="info-card">'
                f'<span class="pill {clase}">{escape(titulo)}</span>'
                f'<h3 style="margin:15px 0 8px">{escape(nombre_activo(ticker))}</h3>'
                f'<p>{escape(descripcion)} Este activo destaca dentro de la selección actual por '
                f'{"su menor volatilidad" if titulo == "Perfil conservador" else "su indicador de Sharpe" if titulo == "Perfil moderado" else "su rentabilidad anualizada"}.'
                '</p></div>', unsafe_allow_html=True)

    anterior = st.session_state.get("ultima_simulacion")
    if anterior and anterior.get("ticker") in precios.columns:
        sim = anterior["datos"]
        seccion("Tu última simulación")
        panel_insight(
            f"Para {nombre_activo(anterior['ticker'])}, con un monto de "
            f"{formato_dinero(sim['monto'], anterior['moneda'])} a {sim['horizonte_meses']} meses, "
            f"el modelo produjo un valor medio de {formato_dinero(sim['media'], anterior['moneda'])} "
            f"y una probabilidad simulada de ganancia de {sim['prob_ganar']:.1%}.",
            "Resultados Monte Carlo",
        )
    pie_pagina()


iniciar_sesion()
render_navegacion()
if st.session_state.pagina_actual == "Inicio":
    pagina_inicio()
elif st.session_state.pagina_actual == "Análisis":
    pagina_analisis()
elif st.session_state.pagina_actual == "Simulador":
    pagina_simulador()
else:
    pagina_conclusiones()

"""STATTUM | Versión visual para el concurso universitario.

Reemplaza app.py con este archivo. Mantiene compatibilidad con:
config.py, datos.py, metricas.py, simulacion.py, figuras.py y estilos.py.

Pantallas: Inicio · Análisis · Simulador · Conclusiones.
"""
from __future__ import annotations

import base64
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
from estilos import inyectar_css, encabezado, seccion, panel_insight
from figuras import (
    grafica_precios, grafica_riesgo, grafica_correlacion,
    grafica_drawdown, grafica_monte_carlo, grafica_distribucion,
)
from simulacion import monte_carlo

ROOT = Path(__file__).resolve().parent
PAGINAS = ("Inicio", "Análisis", "Simulador", "Conclusiones")

# Imágenes opcionales: si se suben estos archivos a assets/, se muestran sin
# depender de servidores externos. Los enlaces externos son un respaldo visual.
LOGOS_EXTERNOS = {
    "EXITO.CL": "https://commons.wikimedia.org/wiki/Special:Redirect/file/Almacenes_exito_logo.svg",
    "ECOPETROL.CL": "https://logowik.com/content/uploads/images/ecopetrol-empresa-colombiana-de-petroleos-sa6690.jpg",
    "PFCIBEST.CL": "https://www.sec.gov/Archives/edgar/data/2058897/000205889725000026/gc_logotipoxnegroxvertical.jpg",
    # ICOLCAP es un ETF: se representa mediante un distintivo textual propio,
    # en gris, sin atribuirle un logotipo corporativo que no le corresponde.
}
ARCHIVOS_LOGOS = {
    "EXITO.CL": "logo_exito.png",
    "ECOPETROL.CL": "logo_ecopetrol.png",
    "PFCIBEST.CL": "logo_cibest.png",
    "ICOLCAP.CL": "logo_icolcap.png",
}
FONDOS_ACTIVOS = {
    "EXITO.CL": "#FFF8D6", "ECOPETROL.CL": "#EAF7EF",
    "PFCIBEST.CL": "#EAF3FF", "ICOLCAP.CL": "#F1F3F6",
}

st.set_page_config(
    page_title="STATTUM | Análisis financiero inteligente",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="collapsed",
)
# Quita las opciones de desarrollador del menú de Streamlit. Los controles
# propios del administrador de Streamlit Community Cloud pueden seguir visibles
# en su cuenta, pero no deberían aparecer a visitantes sin permisos.
try:
    st.set_option("client.toolbarMode", "minimal")
except Exception:
    pass

inyectar_css()

# Se aplican después de estilos.py para modificar solo la experiencia visual.
st.markdown("""
<style>
  :root {--s-navy:#06264c;--s-blue:#067ac7;--s-cyan:#24cdf6;--s-ink:#0b2c56;--s-light:#f7fbff;}
  .stApp {background:linear-gradient(165deg,#f9fcff,#eef6ff 60%,#f8fbff) !important;}
  .block-container {max-width:1500px !important;padding-top:.55rem !important;padding-bottom:2.5rem !important;}
  #MainMenu, footer, [data-testid="stToolbar"], [data-testid="stDecoration"] {visibility:hidden !important;}
  header[data-testid="stHeader"] {background:transparent !important;height:0 !important;}
  .st-key-nav_stattum {background:linear-gradient(110deg,#032348,#06315f 60%,#042044) !important;
    border-radius:19px;padding:7px 16px 5px;margin:2px 0 19px;
    box-shadow:0 14px 32px rgba(4,39,83,.18);position:relative;z-index:2;}
  .s-nav-mark {height:69px;max-width:235px;display:flex;align-items:center;
    padding:4px 21px 4px 7px;margin:-7px 0 -5px -16px;background:#fcfaf6;
    border-radius:17px 10px 60px 17px;}
  .s-nav-mark img {max-width:100%;height:57px;object-fit:contain;mix-blend-mode:multiply;}
  .s-nav-mark .s-mini-fallback {font-size:1.5rem;color:#0759a7;font-weight:900;}
  .st-key-nav_stattum .stButton>button {min-height:45px !important;background:transparent !important;
    color:#eef9ff !important;border:1px solid transparent !important;
    border-radius:14px !important;font-weight:750 !important;font-size:.93rem !important;
    box-shadow:none !important;white-space:nowrap;}
  .st-key-nav_stattum button[kind="primary"] {background:#fff !important;color:#07386b !important;
    border:1px solid #fff !important;box-shadow:0 5px 13px rgba(0,0,0,.12) !important;}
  .st-key-nav_stattum .stButton>button:hover {background:rgba(255,255,255,.15) !important;
    color:#fff !important;transform:none;}
  .st-key-nav_stattum button[kind="primary"]:hover {background:#fff !important;color:#07386b !important;}
  .st-key-hero_stattum {position:relative;background:linear-gradient(112deg,#063160 0%,#053a74 58%,#06284e 100%);
    border-radius:26px;box-shadow:0 19px 45px rgba(3,41,86,.18);overflow:hidden;
    padding:20px 32px 27px;margin-bottom:16px;}
  .st-key-hero_stattum:before {content:"";position:absolute;inset:0;pointer-events:none;
    background:radial-gradient(ellipse at 90% 55%,rgba(16,179,245,.30),transparent 43%),
    radial-gradient(ellipse at 26% 90%,rgba(43,143,245,.17),transparent 52%);}
  .s-hero-identity {position:relative;min-height:266px;display:flex;align-items:center;justify-content:center;
    margin-left:-42px;margin-top:-20px;margin-bottom:-26px;padding:26px 22px 25px 29px;
    background:linear-gradient(150deg,#fffefa 0%,#f5faff 78%,#d5edff 100%);
    border-radius:0 51% 41% 0 / 0 52% 45% 0;isolation:isolate;overflow:hidden;}
  .s-hero-identity:after {content:"";position:absolute;inset:auto -5px 4px 0;height:30px;
    background:linear-gradient(90deg,transparent,#0695e5);filter:blur(14px);opacity:.16;z-index:-1;}
  .s-hero-identity img {width:100%;max-width:535px;object-fit:contain;mix-blend-mode:multiply;
    filter:contrast(1.025);}
  .s-hero-identity .s-brand-fallback {font-size:clamp(2.7rem,5.5vw,4.7rem);font-weight:900;color:#0869b7;}
  .s-hero-kicker {font-size:.76rem;letter-spacing:.18em;color:#82eafa;font-weight:800;text-transform:uppercase;}
  .s-hero-title {color:#fff;font-size:clamp(2.0rem,3.2vw,3.55rem);
    font-weight:850;letter-spacing:-.055em;line-height:1.1;margin:10px 0 15px;}
  .s-hero-title b {color:#4dd8ff;}
  .s-hero-sub {color:#e1f1ff !important;font-size:1.03rem;line-height:1.65;
    max-width:590px;margin:0 0 10px;}
  .s-hero-graphic {width:100%;max-height:88px;margin:9px 0 0;opacity:.94;overflow:visible;}
  .s-hero-graphic polyline {stroke-dasharray:810;stroke-dashoffset:810;animation:s-draw 2.6s ease-out forwards;}
  @keyframes s-draw {to{stroke-dashoffset:0}}
  .st-key-hero_stattum .stButton>button {max-width:410px;min-height:55px !important;
    border:1px solid #77e1ff !important;background:linear-gradient(95deg,#0871d2,#04b9e6) !important;
    color:white !important;border-radius:17px !important;box-shadow:0 8px 20px rgba(0,179,241,.18) !important;
    font-size:1rem !important;font-weight:800 !important;}
  .s-features {display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:14px;margin:15px 0 25px;}
  .s-feature {background:rgba(255,255,255,.93);border:1px solid #d9e9f8;border-radius:18px;
    padding:20px;box-shadow:0 6px 18px rgba(11,53,99,.04);min-height:157px;}
  .s-feature-icon {display:grid;place-items:center;background:#e8f5ff;color:#0676bf;
    width:43px;height:43px;border-radius:13px;font-size:1.3rem;font-weight:800;margin-bottom:12px;}
  .s-feature-title {font-weight:800;color:#082e59;margin-bottom:5px;font-size:.98rem;}
  .s-feature-desc {color:#61778c;font-size:.84rem;line-height:1.5;}
  .s-asset-grid {display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:15px;margin:14px 0 20px;}
  .s-asset {background:#fff;border:1px solid #dae8f5;border-top:5px solid var(--asset);
    border-radius:19px;box-shadow:0 8px 18px rgba(3,49,100,.06);overflow:hidden;
    transition:transform .18s ease,box-shadow .18s ease;}
  .s-asset:hover {transform:translateY(-3px);box-shadow:0 13px 26px rgba(5,50,99,.11);}
  .s-asset-top {background:var(--soft);display:flex;align-items:center;gap:11px;
    padding:14px 15px 11px;min-height:94px;}
  .s-asset-image {flex:0 0 78px;height:58px;display:flex;align-items:center;
    justify-content:center;overflow:hidden;background:#fff;border-radius:12px;padding:7px;}
  .s-asset-image img {max-width:100%;max-height:100%;object-fit:contain;}
  .s-asset-placeholder {font-size:1.3rem;font-weight:900;letter-spacing:-.04em;color:var(--asset);}
  .s-asset-title {font-weight:850;font-size:1.05rem;color:#0a2d54;}
  .s-asset-sector {color:#496883;font-size:.79rem;margin-top:2px;}
  .s-asset-bottom {padding:11px 16px 13px;font-size:.83rem;color:#516c84;}
  .s-asset-stat {display:flex;justify-content:space-between;gap:7px;padding:6px 0;
    border-bottom:1px solid #edf2f8;}
  .s-asset-stat:last-child {border:0;}.s-asset-stat b {color:#0c2f55;}
  .s-ticker {margin-top:7px;font-weight:700;font-size:.69rem;letter-spacing:.045em;color:#7890a4;}
  .s-brief {margin:8px 0 23px;border-radius:18px;padding:16px 20px;
    background:linear-gradient(102deg,#063262,#075a91);color:#eefaff;
    display:flex;align-items:center;gap:14px;line-height:1.5;font-size:.93rem;}
  .s-brief b {color:#64dffa;}
  .s-title-band {background:linear-gradient(103deg,#062549,#074a83 70%,#0674ae);
    color:white;border-radius:19px;padding:23px 26px;margin:8px 0 23px;position:relative;
    overflow:hidden;box-shadow:0 10px 22px rgba(4,43,84,.11);}
  .s-title-band:after {content:"";position:absolute;width:330px;height:175px;right:-40px;top:-60px;
    border:2px solid rgba(77,207,255,.17);border-radius:50%;transform:rotate(-20deg);}
  .s-title-band h1 {font-size:clamp(1.7rem,2.5vw,2.45rem);margin:0 0 5px;
    color:#fff !important;letter-spacing:-.045em;}
  .s-title-band p {color:#d3eafa !important;font-size:.95rem;margin:0;max-width:940px;}
  .s-panel {background:#fff;border:1px solid #deebf7;border-radius:17px;
    box-shadow:0 5px 16px rgba(13,56,104,.055);padding:16px 19px;}
  .s-kpis {display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:12px;margin:12px 0 20px;}
  .s-kpi {background:linear-gradient(180deg,#fff,var(--kpi-bg,#f8fbff));border:1px solid #dce9f6;
    border-radius:17px;padding:17px 14px 16px;border-top:4px solid var(--accent,#0988ca);
    box-shadow:0 5px 14px rgba(7,47,92,.04);min-height:133px;}
  .s-kpi-label {font-size:.80rem;font-weight:750;color:#4d6983;}
  .s-kpi-value {font-size:clamp(1.05rem,1.75vw,1.6rem);line-height:1.24;
    font-weight:850;color:#092c53;margin:12px 0 7px;overflow-wrap:anywhere;}
  .s-kpi-foot {font-size:.75rem;color:#657c92;line-height:1.35;}
  .s-chart-label {font-size:1.07rem;font-weight:800;color:#0a2c55;margin-top:10px;margin-bottom:6px;}
  .s-card-grid {display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:14px;margin:10px 0;}
  .s-conclusion {border:1px solid #e0eaf5;border-radius:16px;background:#fff;
    border-top:4px solid var(--accent);padding:18px;box-shadow:0 5px 16px rgba(7,47,92,.045);}
  .s-conclusion-title {color:#092a52;font-size:1rem;font-weight:850;margin-bottom:8px;}
  .s-conclusion-body {font-size:.89rem;line-height:1.62;color:#526c86;}
  .s-pill {border-radius:999px;padding:6px 12px;background:#ebf5fe;font-weight:800;
    color:#0c61a2;display:inline-block;margin-bottom:10px;font-size:.78rem;}
  .s-soft-note {color:#617991;font-size:.83rem;margin:8px 0 13px;line-height:1.6;}
  .s-foot {margin:31px 0 0;border-top:1px solid #d7e5f2;padding-top:17px;
    font-size:.77rem;color:#7b91a4;text-align:center;}
  div[data-testid="stPlotlyChart"] {border-radius:18px;border:1px solid #ddeaf6;background:#fff;
    box-shadow:0 5px 14px rgba(5,43,92,.04);}
  @media (max-width:1100px){.s-asset-grid,.s-features,.s-kpis{grid-template-columns:repeat(2,minmax(0,1fr))}}
  @media (max-width:750px){.s-card-grid{grid-template-columns:1fr}.s-hero-identity{min-height:195px;
    margin:0 0 17px;border-radius:20px;padding:12px;}.st-key-hero_stattum{padding:16px}}
  @media (max-width:560px){.s-asset-grid,.s-features,.s-kpis{grid-template-columns:1fr}
    .s-brief{display:block}.s-hero-title{font-size:2.0rem}.st-key-nav_stattum{padding:10px 9px}}
  @media (prefers-reduced-motion:reduce){.s-hero-graphic polyline{animation:none;stroke-dashoffset:0}
    .s-asset{transition:none}.s-asset:hover{transform:none}}
</style>
""", unsafe_allow_html=True)


def imagen_base64(ruta: Path) -> str | None:
    """Convierte una imagen local en data URI para evitar errores de MediaFileStorage."""
    if not ruta.is_file():
        return None
    ext = ruta.suffix.lower().lstrip(".")
    mime = {"png": "image/png", "jpg": "image/jpeg", "jpeg": "image/jpeg", "webp": "image/webp", "svg": "image/svg+xml"}.get(ext)
    if not mime:
        return None
    try:
        return f"data:{mime};base64," + base64.b64encode(ruta.read_bytes()).decode("ascii")
    except OSError:
        return None


LOGO_STATTUM = imagen_base64(ROOT / "assets" / "logo_stattum.png")


def img_empresa(ticker: str) -> str:
    """Logotipo si hay archivo local o referencia remota; distintivo textual para el ETF."""
    filename = ARCHIVOS_LOGOS.get(ticker)
    if filename:
        fuente = imagen_base64(ROOT / "assets" / filename)
        if fuente:
            return f'<img src="{fuente}" alt="Logo de {escape(nombre_activo(ticker))}">'
    remoto = LOGOS_EXTERNOS.get(ticker)
    if remoto:
        return f'<img src="{remoto}" loading="lazy" alt="Logo de {escape(nombre_activo(ticker))}">'
    if ticker == "ICOLCAP.CL":
        return '<span class="s-asset-placeholder" style="color:#64748b;font-size:1rem">▥ COLCAP</span>'
    return f'<span class="s-asset-placeholder">{escape(nombre_activo(ticker)[:7])}</span>'


def html_logo_principal(clase: str) -> str:
    if LOGO_STATTUM:
        return f'<div class="{clase}"><img src="{LOGO_STATTUM}" alt="STATTUM, Análisis Financiero Inteligente"></div>'
    return f'<div class="{clase}"><span class="s-brand-fallback">STATTUM</span></div>'


def bloque_titulo(titulo: str, descripcion: str) -> None:
    st.markdown(f'<div class="s-title-band"><h1>{escape(titulo)}</h1>'
                f'<p>{escape(descripcion)}</p></div>', unsafe_allow_html=True)


def pie() -> None:
    st.markdown('<div class="s-foot">STATTUM · Análisis financiero inteligente · Datos de Yahoo Finance</div>', unsafe_allow_html=True)


def indicadores(datos_kpi: list[tuple[str, str, str, str]]) -> None:
    bloques = ['<div class="s-kpis">']
    for titulo, valor, nota, color in datos_kpi:
        bloques.append(
            f'<div class="s-kpi" style="--accent:{color}">'
            f'<div class="s-kpi-label">{escape(titulo)}</div>'
            f'<div class="s-kpi-value">{escape(valor)}</div>'
            f'<div class="s-kpi-foot">{escape(nota)}</div></div>'
        )
    st.markdown(''.join(bloques) + '</div>', unsafe_allow_html=True)


def tarjeta_empresas(tickers, tabla: pd.DataFrame | None = None) -> None:
    paleta = colores(tickers)
    bloques = ['<div class="s-asset-grid">']
    for ticker in tickers:
        titulo = nombre_activo(ticker)
        color = paleta[ticker]
        fondo = FONDOS_ACTIVOS.get(ticker, "#f1f5ff")
        sector = ACTIVOS_BASE.get(ticker, {}).get("sector", "Activo personalizado")
        metrica = f'<div class="s-asset-bottom">{escape(sector)}</div>'
        if tabla is not None and ticker in tabla.index:
            ret = float(tabla.loc[ticker, "Retorno anualizado"])
            vol = float(tabla.loc[ticker, "Volatilidad anual"])
            ret_txt = f"{ret:+.1%}" if np.isfinite(ret) else "—"
            vol_txt = f"{vol:.1%}" if np.isfinite(vol) else "—"
            metrica = (f'<div class="s-asset-bottom">'
                       f'<div class="s-asset-stat"><span>Retorno anual</span><b>{ret_txt}</b></div>'
                       f'<div class="s-asset-stat"><span>Volatilidad</span><b>{vol_txt}</b></div>'
                       f'</div>')
        bloques.append(
            f'<div class="s-asset" style="--asset:{color};--soft:{fondo}">'
            f'<div class="s-asset-top"><div class="s-asset-image">{img_empresa(ticker)}</div>'
            f'<div><div class="s-asset-title">{escape(titulo)}</div>'
            f'<div class="s-asset-sector">{escape(sector)}</div>'
            f'<div class="s-ticker">{escape(ticker)}</div></div></div>{metrica}</div>'
        )
    st.markdown(''.join(bloques) + '</div>', unsafe_allow_html=True)


def iniciar_sesion() -> None:
    defaults = {
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
    for llave, valor in defaults.items():
        if llave not in st.session_state:
            st.session_state[llave] = valor


def ir_a(pagina: str) -> None:
    if pagina in PAGINAS:
        st.session_state.pagina_actual = pagina
        st.rerun()


def menu() -> None:
    etiquetas = {"Inicio": "⌂  Inicio", "Análisis": "▥  Análisis",
                 "Simulador": "▦  Simulador", "Conclusiones": "◎  Conclusiones"}
    with st.container(key="nav_stattum"):
        columnas = st.columns([1.7, 1.0, 1.05, 1.13, 1.37], gap="small", vertical_alignment="center")
        with columnas[0]:
            st.markdown(html_logo_principal("s-nav-mark"), unsafe_allow_html=True)
        for i, pagina in enumerate(PAGINAS, start=1):
            with columnas[i]:
                if st.button(etiquetas[pagina], key=f"menu_{pagina}",
                             type="primary" if st.session_state.pagina_actual == pagina else "secondary",
                             use_container_width=True):
                    ir_a(pagina)


def dinero(valor: float, moneda: str) -> str:
    if moneda in {"COP", "CLP"}:
        num = f"{valor:,.0f}".replace(",", ".")
    else:
        num = f"{valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return f"{moneda} {num}" if moneda != "N/D" else num


def porc(valor: float) -> str:
    return f"{valor:+.1%}" if np.isfinite(valor) else "—"


def pagina_inicio() -> None:
    with st.container(key="hero_stattum"):
        iz, de = st.columns([1.13, 1.16], gap="large", vertical_alignment="center")
        with iz:
            st.markdown(html_logo_principal("s-hero-identity"), unsafe_allow_html=True)
        with de:
            st.markdown("""
            <div class="s-hero-kicker">Descubre el mercado con datos</div>
            <h1 class="s-hero-title">Bienvenido a <b>STATTUM</b></h1>
            <p class="s-hero-sub">Compara activos del mercado colombiano, comprende sus riesgos
            y simula posibles resultados de inversión en una plataforma clara e interactiva.</p>
            <svg class="s-hero-graphic" viewBox="0 0 580 118" aria-label="Gráfica bursátil animada" role="img">
              <g opacity=".15" fill="#41d3ff"><rect x="25" y="76" width="24" height="42"/>
              <rect x="93" y="63" width="24" height="55"/><rect x="162" y="78" width="24" height="40"/>
              <rect x="232" y="44" width="24" height="74"/><rect x="313" y="52" width="24" height="66"/>
              <rect x="392" y="26" width="24" height="92"/><rect x="465" y="11" width="24" height="107"/></g>
              <polyline points="1,97 46,87 78,94 123,53 170,69 223,42 265,54 311,35 360,46 411,20 460,33 515,6 568,11"
              fill="none" stroke="#55e6ff" stroke-width="4" stroke-linejoin="round" stroke-linecap="round" />
            </svg>""", unsafe_allow_html=True)
            if st.button("Comenzar análisis  →", type="primary", use_container_width=True,
                         key="boton_inicio_analisis"):
                ir_a("Análisis")

    seccion("¿Qué ofrece STATTUM?", "Toda la información esencial organizada para que puedas explorar sin perderte.")
    st.markdown("""
    <div class="s-features">
      <div class="s-feature"><div class="s-feature-icon">▥</div><div class="s-feature-title">Compara activos</div>
      <div class="s-feature-desc">Estudia cuatro referentes del mercado y agrega otros tickers.</div></div>
      <div class="s-feature"><div class="s-feature-icon">◇</div><div class="s-feature-title">Evalúa el riesgo</div>
      <div class="s-feature-desc">Conoce la volatilidad, las caídas y las correlaciones.</div></div>
      <div class="s-feature"><div class="s-feature-icon">⌁</div><div class="s-feature-title">Simula escenarios</div>
      <div class="s-feature-desc">Descubre resultados posibles con el método Monte Carlo.</div></div>
      <div class="s-feature"><div class="s-feature-icon">◎</div><div class="s-feature-title">Entiende las conclusiones</div>
      <div class="s-feature-desc">Obtén explicaciones sencillas de los indicadores financieros.</div></div>
    </div>""", unsafe_allow_html=True)
    seccion("Activos analizados", "Cuatro referentes iniciales del mercado colombiano.")
    tarjeta_empresas(PREDETERMINADOS)
    pie()


@st.cache_data(ttl=3600, show_spinner=False)
def precios_crudos(tickers: tuple[str, ...], inicio: date, fin: date) -> pd.DataFrame:
    return datos.descargar_precios(tickers, inicio, fin)


@st.cache_data(ttl=86400, show_spinner=False)
def moneda_del_ticker(ticker: str) -> str | None:
    return datos.moneda_ticker(ticker)


def datos_activos() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame] | None:
    seleccion = list(dict.fromkeys(st.session_state.activos))
    if not seleccion:
        st.info("Selecciona al menos un activo en Análisis.")
        return None
    if st.session_state.fecha_inicio >= st.session_state.fecha_fin:
        st.warning("La fecha inicial debe ser anterior a la final.")
        return None
    try:
        with st.spinner("Consultando datos históricos…"):
            crudos = precios_crudos(tuple(seleccion), st.session_state.fecha_inicio, st.session_state.fecha_fin)
            precios, faltantes = datos.preparar_precios(crudos)
    except Exception:
        st.error("No fue posible consultar los precios en este momento. Comprueba la conexión e inténtalo nuevamente.")
        return None
    if faltantes:
        st.warning("No hay datos suficientes para: " + ", ".join(faltantes) + ". Puedes retirarlos desde Análisis.")
    if precios.empty or len(precios) < 35:
        st.warning("No hay suficientes fechas comunes. Ajusta el periodo o los activos desde Análisis.")
        return None
    if APLICAR_DEPURACION_HISTORICA:
        precios, _ = m.limpiar_saltos(precios)
    rets = m.retornos(precios)
    if len(rets) < 30:
        st.warning("Se necesitan más rendimientos diarios para generar indicadores.")
        return None
    benchmark = "ICOLCAP.CL" if "ICOLCAP.CL" in precios.columns else ""
    tabla = m.resumen(precios, rets, st.session_state.tasa_rf, benchmark)
    return precios, rets, tabla


def agregar_ticker() -> None:
    with st.form("ingresar_ticker", clear_on_submit=True, border=False):
        escrito = st.text_input("Agregar otra empresa", placeholder="Ej. AAPL o MSFT", max_chars=20,
                                help="Escribe el símbolo que utiliza Yahoo Finance.")
        enviado = st.form_submit_button("＋ Agregar activo", type="primary", use_container_width=True)
    if not enviado:
        return
    ticker = datos.normalizar_ticker(escrito)
    if not datos.ticker_valido(ticker):
        st.error("Introduce un ticker válido, por ejemplo AAPL o MSFT.")
        return
    disponibles = PREDETERMINADOS + st.session_state.extras
    if ticker in disponibles:
        if ticker not in st.session_state.activos:
            st.session_state.activos.append(ticker)
            st.session_state.selector_version += 1
            st.rerun()
        st.info("Ese ticker ya está agregado.")
        return
    if len(disponibles) >= MAX_ACTIVOS:
        st.warning(f"El máximo es de {MAX_ACTIVOS} activos para mantener las gráficas legibles.")
        return
    try:
        with st.spinner("Verificando los precios del ticker…"):
            verificacion = precios_crudos((ticker,), st.session_state.fecha_inicio, st.session_state.fecha_fin)
            n = int(verificacion[ticker].dropna().shape[0]) if ticker in verificacion.columns else 0
    except Exception:
        n = 0
    if n < 35:
        st.error("No encontramos suficientes datos para ese ticker en el periodo seleccionado.")
        return
    with st.spinner("Consultando la divisa del activo…"):
        divisa = moneda_del_ticker(ticker)
    st.session_state.divisas[ticker] = divisa or "N/D"
    st.session_state.extras.append(ticker)
    st.session_state.activos.append(ticker)
    st.session_state.selector_version += 1
    st.rerun()


def pagina_analisis() -> None:
    bloque_titulo("Análisis de activos", "Compara rentabilidad, riesgo y comportamiento del mercado, y añade las empresas que quieras explorar.")
    selector, nuevo = st.columns([2.1, 1], gap="large")
    with selector:
        disponibles = PREDETERMINADOS + st.session_state.extras
        seleccion = st.multiselect(
            "Activos para comparar", options=disponibles,
            default=[x for x in st.session_state.activos if x in disponibles],
            format_func=lambda x: f"{nombre_activo(x)} · {x}",
            help="Los activos seleccionados se usarán también en el Simulador y las Conclusiones.",
            key=f"elegir_activos_{st.session_state.selector_version}",
        )
        st.session_state.activos = list(seleccion)
        with st.expander("Periodo y ajustes del análisis"):
            c1, c2 = st.columns(2)
            with c1:
                st.session_state.fecha_inicio = st.date_input(
                    "Fecha inicial", value=st.session_state.fecha_inicio,
                    max_value=date.today(), key="periodo_inicio_v2")
            with c2:
                st.session_state.fecha_fin = st.date_input(
                    "Fecha final", value=st.session_state.fecha_fin,
                    max_value=date.today(), key="periodo_fin_v2")
            st.session_state.tasa_rf = st.slider(
                "Tasa anual de referencia para Sharpe (%)", 0.0, 20.0,
                value=float(st.session_state.tasa_rf * 100), step=0.5, key="rf_v2") / 100
        if st.session_state.extras:
            with st.expander("Retirar un ticker añadido"):
                retirar = st.selectbox("Ticker a retirar", st.session_state.extras, key="quitar_ticker_v2")
                if st.button("Retirar activo", key="confirmar_retiro_v2"):
                    st.session_state.extras.remove(retirar)
                    st.session_state.activos = [x for x in st.session_state.activos if x != retirar]
                    st.session_state.divisas.pop(retirar, None)
                    st.session_state.selector_version += 1
                    st.rerun()
    with nuevo:
        agregar_ticker()

    resultado = datos_activos()
    if resultado is None:
        return
    precios, rets, tabla = resultado
    seccion("Tu selección de activos")
    tarjeta_empresas(precios.columns, tabla)
    monedas = {st.session_state.divisas.get(x, "COP") for x in precios.columns}
    if len(monedas - {"N/D"}) > 1:
        st.caption("Los activos están expresados en monedas distintas. Sus porcentajes se calculan por separado; no hay conversión entre divisas.")

    validas = tabla.dropna(subset=["Retorno anualizado", "Volatilidad anual"])
    if not validas.empty:
        mayor = validas["Retorno anualizado"].idxmax()
        estable = validas["Volatilidad anual"].idxmin()
        sharpe = validas["Sharpe"].replace([np.inf, -np.inf], np.nan).dropna()
        mejor_sharpe = sharpe.idxmax() if not sharpe.empty else None
        indicadores([
            ("Mayor rentabilidad anual", nombre_activo(mayor), porc(validas.loc[mayor, "Retorno anualizado"]), colores([mayor])[mayor]),
            ("Menor volatilidad", nombre_activo(estable), f"{validas.loc[estable, 'Volatilidad anual']:.1%} anual", colores([estable])[estable]),
            ("Mejor relación riesgo-retorno", nombre_activo(mejor_sharpe) if mejor_sharpe else "Sin dato",
             f"Sharpe {sharpe.loc[mejor_sharpe]:.2f}" if mejor_sharpe else "—", "#0D86CE"),
            ("Activos comparados", str(len(precios.columns)), "Selección actual", "#8B5CF6"),
        ])

    c1, c2 = st.columns([1.35, 1], gap="medium")
    with c1:
        st.markdown('<div class="s-chart-label">Evolución de los precios (base 100)</div>', unsafe_allow_html=True)
        st.caption("Todas las series parten de 100 para facilitar la comparación.")
        st.plotly_chart(grafica_precios(precios), use_container_width=True, config={"displaylogo": False})
    with c2:
        st.markdown('<div class="s-chart-label">Riesgo frente a rentabilidad</div>', unsafe_allow_html=True)
        st.caption("Más arriba: mayor retorno histórico; más a la izquierda: menor volatilidad.")
        st.plotly_chart(grafica_riesgo(tabla), use_container_width=True, config={"displaylogo": False})

    if len(rets.columns) >= 2:
        st.markdown('<div class="s-chart-label">Correlación entre activos</div>', unsafe_allow_html=True)
        st.caption("Indica cuánto se parecen sus movimientos diarios; no equivale a una relación causal.")
        st.plotly_chart(grafica_correlacion(rets), use_container_width=True, config={"displaylogo": False})

    with st.expander("Explorar indicadores detallados y caídas históricas"):
        vista = tabla.copy().rename(index=nombre_activo)
        formato = {"Retorno acumulado": "{:.1%}", "Retorno anualizado": "{:.1%}",
                   "Volatilidad anual": "{:.1%}", "Sharpe": "{:.2f}",
                   "Máx. drawdown": "{:.1%}", "Beta": "{:.2f}"}
        st.dataframe(vista.style.format(formato, na_rep="—"), use_container_width=True)
        st.plotly_chart(grafica_drawdown(precios), use_container_width=True, config={"displaylogo": False})
    pie()


def pagina_simulador() -> None:
    bloque_titulo("Simulador de inversión", "Introduce un monto y explora escenarios de rentabilidad y riesgo mediante Monte Carlo.")
    resultado = datos_activos()
    if resultado is None:
        return
    _, rets, _ = resultado
    izquierda, derecha = st.columns([1, 2.15], gap="large")
    with izquierda:
        st.markdown("### Configura tu simulación")
        opciones = list(rets.columns)
        if st.session_state.get("activo_sim_v2") not in opciones:
            st.session_state["activo_sim_v2"] = opciones[0]
        ticker = st.selectbox("Activo a simular", options=opciones,
                              format_func=lambda t: f"{nombre_activo(t)} · {t}", key="activo_sim_v2")
        seleccion = colores([ticker])[ticker]
        st.markdown(
            f'<div class="s-panel" style="padding:10px 12px;display:flex;align-items:center;gap:12px;'
            f'border-left:5px solid {seleccion};background:#fbfdff;margin:3px 0 12px">'
            f'<div class="s-asset-image" style="flex:0 0 75px">{img_empresa(ticker)}</div>'
            f'<div><b style="color:#0c2e56">{escape(nombre_activo(ticker))}</b>'
            f'<div style="font-size:.75rem;color:#657d90">{escape(ticker)}</div></div></div>',
            unsafe_allow_html=True,
        )
        moneda = st.session_state.divisas.get(ticker, "N/D")
        if moneda == "N/D":
            st.caption("La divisa no está identificada; ingresa el importe en la moneda del ticker.")
        monto = st.number_input(
            f"Monto a invertir ({moneda if moneda != 'N/D' else 'moneda del activo'})",
            min_value=1.0, value=1_000_000.0 if moneda == "COP" else 1_000.0,
            step=50_000.0 if moneda == "COP" else 100.0,
            format="%.2f", key=f"importe_v2_{ticker}",
        )
        meses = st.selectbox("Horizonte de inversión", [6, 12, 24, 36, 60], index=1,
                             format_func=lambda x: (f"{x} meses" if x < 12 else f"{x // 12} año" + ("s" if x > 12 else "")),
                             key="horizonte_v2")
        with st.expander("Opciones avanzadas"):
            n_sim = st.select_slider("Número de simulaciones", [1000, 2500, 5000, 10000], value=5000, key="n_sim_v2")
            confianza = st.select_slider("Intervalo central", [0.80, 0.90, 0.95], value=0.95,
                                         format_func=lambda x: f"{x:.0%}", key="confianza_v2")
        firma_datos = pd.util.hash_pandas_object(rets[ticker], index=True).sum()
        firma = (ticker, float(monto), int(meses), int(n_sim), float(confianza),
                 str(st.session_state.fecha_inicio), str(st.session_state.fecha_fin), str(firma_datos))
        pulsado = st.button("▶  Simular inversión", type="primary", use_container_width=True, key="simular_v2")
        if pulsado:
            try:
                with st.spinner("Construyendo escenarios posibles…"):
                    sim = monte_carlo(rets[ticker], monto, meses, n_sim, confianza)
                st.session_state.ultima_simulacion = {
                    "firma": firma, "datos": sim, "ticker": ticker, "moneda": moneda,
                    "fecha_inicio": st.session_state.fecha_inicio,
                    "fecha_fin": st.session_state.fecha_fin,
                }
            except ValueError as exc:
                st.error(str(exc))
        st.markdown('<p class="s-soft-note">Cada escenario se genera a partir del comportamiento histórico diario del activo elegido.</p>', unsafe_allow_html=True)

    guardada = st.session_state.get("ultima_simulacion")
    vigente = guardada is not None and guardada.get("firma") == firma
    with derecha:
        if not vigente:
            st.markdown("""
              <div class="s-panel" style="min-height:350px;display:flex;flex-direction:column;justify-content:center;
                background:linear-gradient(150deg,#fff,#eaf6ff)">
                <span class="s-pill">MONTE CARLO</span>
                <div style="font-size:1.65rem;font-weight:850;color:#0b3567;margin:5px 0 9px">
                  Tu inversión, miles de posibilidades</div>
                <div style="color:#59728b;line-height:1.7;max-width:600px">
                  Elige un activo, escribe cuánto deseas invertir y pulsa <b>Simular inversión</b>;
                  aquí aparecerán el valor esperado, los escenarios conservador y optimista,
                  la probabilidad de ganancia y las trayectorias estimadas.</div>
                <div style="margin-top:27px;height:9px;border-radius:8px;
                  background:linear-gradient(90deg,#d2ebff,#36c9f9,#076bc0,#d2ebff)"></div>
              </div>""", unsafe_allow_html=True)
        else:
            sim = guardada["datos"]
            bajo_p = (1 - sim["confianza"]) / 2
            alto_p = 1 - bajo_p
            indicadores([
                ("Valor esperado", dinero(sim["media"], moneda), "Promedio de escenarios", "#0879CE"),
                ("Escenario conservador", dinero(sim["bajo"], moneda), f"Percentil {bajo_p:.1%}", "#EF8A23"),
                ("Escenario optimista", dinero(sim["alto"], moneda), f"Percentil {alto_p:.1%}", "#1B9E60"),
                ("Probabilidad de ganancia", f"{sim['prob_ganar']:.1%}", "Resultados por encima del monto inicial", "#7B5DD6"),
            ])
            st.markdown(f'<div class="s-chart-label">Simulación Monte Carlo · {escape(nombre_activo(ticker))}</div>',
                        unsafe_allow_html=True)
            st.plotly_chart(grafica_monte_carlo(sim, seleccion), use_container_width=True,
                            config={"displaylogo": False})
            st.markdown(f'<div class="s-soft-note">La banda contiene el {sim["confianza"]:.0%} central de las trayectorias simuladas en cada fecha; los valores son escenarios estadísticos, no resultados asegurados.</div>',
                        unsafe_allow_html=True)

    if vigente:
        with st.expander("Ver distribución de valores finales", expanded=False):
            st.plotly_chart(grafica_distribucion(guardada["datos"], seleccion),
                            use_container_width=True, config={"displaylogo": False})
        sim = guardada["datos"]
        cambio = sim["media"] / sim["monto"] - 1
        st.markdown(
            f'<div class="s-brief"><b>Lectura del resultado:</b><span>Para {escape(nombre_activo(ticker))}, '
            f'el promedio de los escenarios implica una variación de {cambio:+.1%} sobre el monto inicial '
            f'en {meses} meses.</span></div>', unsafe_allow_html=True,
        )
    pie()


def pagina_conclusiones() -> None:
    bloque_titulo("Conclusiones", "Una interpretación comprensible de los resultados obtenidos con los activos seleccionados.")
    resultado = datos_activos()
    if resultado is None:
        return
    precios, rets, tabla = resultado
    validas = tabla.dropna(subset=["Retorno anualizado", "Volatilidad anual"])
    if validas.empty:
        st.info("No hay indicadores suficientes para generar conclusiones.")
        return
    mayor = validas["Retorno anualizado"].idxmax()
    estable = validas["Volatilidad anual"].idxmin()
    vol_alta = validas["Volatilidad anual"].idxmax()
    sharpes = validas["Sharpe"].replace([np.inf, -np.inf], np.nan).dropna()
    equilibrado = sharpes.idxmax() if not sharpes.empty else estable
    # Se usa un indicador descriptivo, no una recomendación automática de compra.
    seccion("Hallazgos principales")
    indicadores([
        ("Mayor rentabilidad anual", nombre_activo(mayor), porc(validas.loc[mayor, "Retorno anualizado"]), colores([mayor])[mayor]),
        ("Menor volatilidad", nombre_activo(estable), f"{validas.loc[estable, 'Volatilidad anual']:.1%} anual", colores([estable])[estable]),
        ("Mayor exposición a variaciones", nombre_activo(vol_alta), f"{validas.loc[vol_alta, 'Volatilidad anual']:.1%} anual", "#EB8A2B"),
        ("Mejor Sharpe histórico", nombre_activo(equilibrado),
         f"{validas.loc[equilibrado, 'Sharpe']:.2f}" if not sharpes.empty else "—", "#7657D2"),
    ])

    if len(rets.columns) >= 2:
        corr = rets.corr().copy()
        np.fill_diagonal(corr.values, np.nan)
        pares = corr.stack().dropna()
        if pares.empty:
            texto_corr = "No hay suficientes observaciones conjuntas para estudiar las correlaciones."
        else:
            (a, b) = pares.idxmin()
            texto_corr = (f"{nombre_activo(a)} y {nombre_activo(b)} tienen una de las correlaciones "
                          f"más bajas ({pares.min():.2f}) dentro de la selección; su combinación merece examinarse al diversificar.")
    else:
        texto_corr = "Selecciona dos o más activos para comparar sus movimientos y estudiar diversificación."

    st.markdown('<div class="s-card-grid">' + ''.join([
        f'<div class="s-conclusion" style="--accent:#20a46b"><div class="s-conclusion-title">↗ Rentabilidad</div>'
        f'<div class="s-conclusion-body">{escape(nombre_activo(mayor))} registró el mayor rendimiento anualizado '
        f'durante el periodo observado ({validas.loc[mayor, "Retorno anualizado"]:+.1%}).</div></div>',
        f'<div class="s-conclusion" style="--accent:#eaa22e"><div class="s-conclusion-title">◇ Riesgo</div>'
        f'<div class="s-conclusion-body">{escape(nombre_activo(estable))} presentó menor volatilidad '
        f'({validas.loc[estable, "Volatilidad anual"]:.1%}); {escape(nombre_activo(vol_alta))} '
        f'tuvo la más elevada ({validas.loc[vol_alta, "Volatilidad anual"]:.1%}).</div></div>',
        f'<div class="s-conclusion" style="--accent:#087bcc"><div class="s-conclusion-title">▥ Diversificación</div>'
        f'<div class="s-conclusion-body">{escape(texto_corr)}</div></div>',
    ]) + '</div>', unsafe_allow_html=True)

    seccion("Interpretaciones según el perfil", "Estos perfiles permiten explorar distintas prioridades al analizar una inversión.")
    cards = [
        ("Perfil conservador", "Busca una volatilidad histórica más baja.", estable, "#1aa06a", "La menor volatilidad no elimina el riesgo de pérdida."),
        ("Perfil moderado", "Compara el rendimiento conseguido frente al riesgo.", equilibrado, "#087bc9", "El Sharpe no resume todos los riesgos posibles."),
        ("Perfil dinámico", "Evalúa mayores retornos históricos y acepta estudiar sus riesgos.", mayor, "#815bd4", "El rendimiento histórico elevado no implica que se repita."),
    ]
    partes = ['<div class="s-card-grid">']
    for titulo, descripcion, ticker, col, advertencia in cards:
        partes.append(
            f'<div class="s-conclusion" style="--accent:{col}"><span class="s-pill">{escape(titulo)}</span>'
            f'<div class="s-conclusion-title">{escape(nombre_activo(ticker))}</div>'
            f'<div class="s-conclusion-body">{escape(descripcion)} '
            f'Este activo destaca dentro de la selección actual.<br><br>'
            f'<span style="color:#73879a;font-size:.8rem">{escape(advertencia)}</span></div></div>'
        )
    st.markdown(''.join(partes) + '</div>', unsafe_allow_html=True)

    ultimo = st.session_state.get("ultima_simulacion")
    if (ultimo and ultimo.get("ticker") in precios.columns
            and ultimo.get("fecha_inicio") == st.session_state.fecha_inicio
            and ultimo.get("fecha_fin") == st.session_state.fecha_fin):
        sim = ultimo["datos"]
        seccion("Resumen de tu última simulación")
        st.markdown(
            f'<div class="s-brief"><b>{escape(nombre_activo(ultimo["ticker"]))} · Monte Carlo</b>'
            f'<span>Sobre {dinero(sim["monto"], ultimo["moneda"])} a {sim["horizonte_meses"]} meses, '
            f'la simulación estimó un valor medio de {dinero(sim["media"], ultimo["moneda"])} '
            f'y una probabilidad de ganancia de {sim["prob_ganar"]:.1%}.</span></div>',
            unsafe_allow_html=True,
        )
    pie()


iniciar_sesion()
menu()
if st.session_state.pagina_actual == "Inicio":
    pagina_inicio()
elif st.session_state.pagina_actual == "Análisis":
    pagina_analisis()
elif st.session_state.pagina_actual == "Simulador":
    pagina_simulador()
else:
    pagina_conclusiones()

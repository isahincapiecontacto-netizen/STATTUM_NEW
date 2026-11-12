"""Estilos y piezas visuales reutilizables de STATTUM."""
from __future__ import annotations
import base64
from html import escape
from pathlib import Path
import pandas as pd
import streamlit as st
from config import ACTIVOS_BASE, nombre_activo, colores

ROOT = Path(__file__).resolve().parent


def _logo_src() -> str:
    ruta = ROOT / "assets" / "logo_stattum.png"
    return "data:image/png;base64," + base64.b64encode(ruta.read_bytes()).decode("ascii")


def inyectar_css() -> None:
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
    :root { --navy:#071F40; --navy2:#063B72; --blue:#0876CB; --cyan:#26D3FA; --text:#092B53; --muted:#5C718C; }
    html, body, [class*="css"] { font-family:'Inter','Segoe UI',Arial,sans-serif; }
    .stApp { background: linear-gradient(145deg,#f8fbff 0%,#f1f6fc 70%,#f8fbff 100%); }
    .block-container { max-width:1480px !important; padding-top:1.1rem !important; padding-bottom:3.5rem !important; }
    h1,h2,h3,h4 { font-family:'Inter','Segoe UI',Arial,sans-serif; letter-spacing:-.035em; color:#072653; }
    h1 { font-weight:800; } h2,h3 {font-weight:750;}
    .stButton > button { border-radius:14px !important; min-height:43px; font-weight:700 !important;
      border:1px solid #d7e5f4; box-shadow:0 2px 8px rgba(10,51,98,.05); transition:all .18s ease; }
    .stButton > button:hover { transform:translateY(-1px); border-color:#159DE9; }
    button[kind="primary"] { background:linear-gradient(105deg,#0757B5,#079DDD) !important; color:#fff !important; border-color:#0786D6 !important; }
    .st-key-site_header { background:linear-gradient(105deg,#062146,#073465 80%,#041e3c);
      padding:9px 18px 6px; border-radius:20px; margin-bottom:16px;
      box-shadow:0 12px 28px rgba(3,34,72,.13); }
    .st-key-site_header img { border-radius:12px; max-height:79px; object-fit:contain; }
    .st-key-site_header .stButton > button { border-color:rgba(235,244,255,.16) !important;
      background:rgba(255,255,255,.08); color:#fff; font-size:.94rem; white-space:nowrap; }
    .st-key-site_header button[kind="primary"] { background:#fff !important; color:#073c78 !important; border-color:#fff !important; }
    .st-key-site_header .stButton > button:hover { background:rgba(255,255,255,.17); }
    .st-key-home_hero { background:radial-gradient(circle at 78% 40%,rgba(0,168,240,.22),transparent 37%),
      linear-gradient(113deg,#06244d 0%,#063E72 60%,#052246 100%); border-radius:24px;
      padding:32px 34px 27px; box-shadow:0 20px 45px rgba(5,42,83,.20); overflow:hidden; }
    .st-key-home_hero p,.st-key-home_hero h1 { color:white; }
    .st-key-home_hero img { border-radius:22px; padding:6px; background:#fff; }
    .st-key-home_hero .stButton > button { background:linear-gradient(95deg,#0072DC,#00B3E8) !important;
      border:1px solid #5adfff !important; color:#fff !important; min-height:54px; font-size:1.03rem; }
    .hero-kicker { font-size:.75rem; letter-spacing:.19em; font-weight:800; color:#65E3FF; text-transform:uppercase; margin-top:12px; }
    .hero-title { font-weight:800; letter-spacing:-.06em; font-size:clamp(2rem,3.3vw,3.3rem); line-height:1.1;
      color:#fff; margin:14px 0 12px; }
    .hero-title span { color:#35CDFC; }
    .hero-sub { max-width:600px; font-size:1.04rem; line-height:1.72; color:#DCEEFE !important; }
    .hero-chart {width:100%; height:80px; margin:5px 0 0; overflow:visible; }
    .hero-chart path.trace {stroke:#32D9FF;stroke-width:4;fill:none;stroke-linecap:round;
      stroke-dasharray:800;stroke-dashoffset:800;animation:trace-in 2.8s ease forwards;}
    .hero-chart .area {fill:rgba(28,173,247,.14)}
    @keyframes trace-in {to{stroke-dashoffset:0}}
    @media (prefers-reduced-motion:reduce) {.hero-chart path.trace{animation:none;stroke-dashoffset:0}
      .feature-card, .asset-card {animation:none !important;transition:none !important;}}
    .section-heading { margin:28px 0 12px; font-size:1.46rem; font-weight:800; color:#082950; }
    .section-heading:after { content:''; display:block; width:54px; height:4px; border-radius:5px;
      background:linear-gradient(90deg,#0576D8,#2ED9EE); margin-top:9px; }
    .section-lead {color:#536e88; font-size:.93rem; line-height:1.6; margin-top:-3px;}
    .feature-grid {display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:14px;margin:10px 0 28px;}
    .feature-card { background:#fff;border:1px solid #DFEBF7;border-radius:18px;
      padding:19px 17px;box-shadow:0 5px 18px rgba(18,56,99,.055);transition:transform .18s ease; }
    .feature-card:hover,.asset-card:hover{ transform:translateY(-3px); }
    .feature-icon {display:inline-grid;place-items:center;width:42px;height:42px;border-radius:13px;
      background:#E5F5FD;color:#0575C8;font-weight:800;font-size:25px;margin-bottom:10px;}
    .feature-card b {display:block;color:#0B2E56;font-size:1rem; margin-bottom:7px;}
    .feature-card span.description{color:#62768C;font-size:.84rem;line-height:1.5;}
    .asset-grid {display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:14px;margin:13px 0 15px;}
    .asset-card {background:#fff;border:1px solid #DFE8F2;border-radius:18px; overflow:hidden;
      box-shadow:0 5px 16px rgba(12,51,97,.07);transition:transform .18s ease;}
    .asset-top {background:linear-gradient(120deg,var(--asset), color-mix(in srgb,var(--asset),white 28%));
      padding:15px 16px; font-weight:800;font-size:1.04rem; color:#fff;}
    .asset-card.asset-yellow .asset-top {color:#122B46;}
    .asset-bottom {padding:12px 16px 14px;color:#62738A;font-size:.83rem;}
    .asset-meta {display:flex;justify-content:space-between;padding:5px 0;border-bottom:1px solid #EDF3F9;gap:8px;}
    .asset-meta:last-child{border:0}.asset-meta b{color:#0B2E56;}
    .subticker {font-size:.72rem;opacity:.8; margin-left:8px;font-weight:600;}
    .title-band {border-radius:20px; padding:23px 27px; margin:7px 0 24px;
      background:linear-gradient(100deg,#06234C,#074778 78%,#067DB6); color:white;
      box-shadow:0 12px 24px rgba(4,45,89,.12); }
    .title-band strong {display:block;color:white;font-size:clamp(1.6rem,2.5vw,2.35rem);
      letter-spacing:-.05em;font-weight:800;}
    .title-band small {display:block;color:#D0EEFF;font-size:.91rem;margin-top:7px;line-height:1.5;}
    .kpi-grid {display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:12px;margin:6px 0 18px;}
    .kpi {padding:17px;border:1px solid #DDEAF7;background:#fff;border-radius:17px;
      box-shadow:0 5px 17px rgba(12,51,97,.05);border-top:4px solid var(--accent,#0785CC)}
    .kpi .eyebrow {display:block;font-size:.78rem;font-weight:650;color:#5B728B;}
    .kpi strong {display:block;font-size:clamp(1.12rem,1.9vw,1.65rem);font-weight:800;color:#092B53;white-space:normal;margin:5px 0 3px;}
    .kpi small{font-size:.76rem;color:#6A8196;line-height:1.4;}
    .insight-panel {background:linear-gradient(100deg,#073266,#075389);border-radius:16px;
      color:#fff;padding:17px 22px;margin-top:15px;line-height:1.65;}
    .insight-panel strong {color:#59D9FF;}
    .insight-panel span{color:#E0F4FF;font-size:.92rem;}
    .info-card{background:#fff;border:1px solid #DDE9F6;border-radius:18px;padding:21px;
      height:100%;box-shadow:0 5px 15px rgba(12,51,97,.06);}
    .info-card h3{font-size:1.1rem;margin:0 0 9px;color:#092B53;}
    .info-card p{font-size:.91rem;color:#526C84;line-height:1.7;margin:0;}
    .pill {display:inline-block;padding:5px 12px;border-radius:30px;font-size:.77rem;font-weight:700;}
    .soft-plain{background:#E5F4FC;color:#0B6C9D}.soft-green{background:#E2F7EA;color:#1B7841}
    .soft-purple{background:#F1EBFC;color:#6F45B7}
    .footerline{text-align:center;color:#74899F;font-size:.78rem;margin-top:31px;padding:20px 0 0;border-top:1px solid #DDE8F3;}
    div[data-testid="stPlotlyChart"]{background:#fff;border:1px solid #DFEAF4;border-radius:17px;
      padding:6px;box-shadow:0 4px 15px rgba(22,53,94,.045);}
    div[data-testid="stNumberInput"] input,div[data-testid="stTextInput"] input{border-radius:10px;}
    @media(max-width:1000px){.feature-grid,.asset-grid,.kpi-grid{grid-template-columns:repeat(2,minmax(0,1fr))}}
    @media(max-width:600px){.feature-grid,.asset-grid,.kpi-grid{grid-template-columns:1fr}
      .st-key-home_hero{padding:19px 15px}.st-key-site_header{padding:10px 8px}}
    </style>
    """, unsafe_allow_html=True)


def encabezado(titulo: str, descripcion: str, icono: str = "▥") -> None:
    st.markdown(
        f'<div class="title-band"><strong>{escape(icono)} &nbsp;{escape(titulo)}</strong>'
        f'<small>{escape(descripcion)}</small></div>', unsafe_allow_html=True)


def seccion(titulo: str, descripcion: str = "") -> None:
    st.markdown(f'<div class="section-heading">{escape(titulo)}</div>' +
                (f'<p class="section-lead">{escape(descripcion)}</p>' if descripcion else ""),
                unsafe_allow_html=True)


def tarjetas_activos(tickers, tabla: pd.DataFrame | None = None) -> None:
    parts = ['<div class="asset-grid">']
    mapa = colores(tickers)
    for ticker in tickers:
        base = ACTIVOS_BASE.get(ticker, {})
        nombre = nombre_activo(ticker)
        col = mapa[ticker]
        yellow = " asset-yellow" if ticker == "EXITO.CL" else ""
        sector = base.get("sector", "Activo añadido")
        lineas = f'<div class="asset-bottom">{escape(sector)}</div>'
        if tabla is not None and ticker in tabla.index:
            ret, vol = tabla.loc[ticker, ["Retorno anualizado", "Volatilidad anual"]]
            lineas = (f'<div class="asset-bottom"><div class="asset-meta">Rentabilidad anual'
                      f'<b>{ret:+.1%}</b></div><div class="asset-meta">Volatilidad anual'
                      f'<b>{vol:.1%}</b></div></div>')
        parts.append(f'<div class="asset-card{yellow}" style="--asset:{col}">'
                     f'<div class="asset-top">{escape(nombre)}<span class="subticker">{escape(ticker)}</span>'
                     f'</div>{lineas}</div>')
    parts.append('</div>')
    st.markdown(''.join(parts), unsafe_allow_html=True)


def tarjetas_kpi(datos: list[tuple[str, str, str, str]]) -> None:
    contenido = ['<div class="kpi-grid">']
    for titulo, valor, pie, col in datos:
        contenido.append(f'<div class="kpi" style="--accent:{col}">'
                         f'<span class="eyebrow">{escape(titulo)}</span><strong>{escape(valor)}</strong>'
                         f'<small>{escape(pie)}</small></div>')
    contenido.append('</div>')
    st.markdown(''.join(contenido), unsafe_allow_html=True)


def panel_insight(texto: str, etiqueta: str = "Lectura de los datos") -> None:
    st.markdown(f'<div class="insight-panel"><strong>{escape(etiqueta)} &nbsp;·&nbsp; </strong>'
                f'<span>{escape(texto)}</span></div>', unsafe_allow_html=True)


def pie_pagina() -> None:
    st.markdown('<div class="footerline">STATTUM · Análisis financiero inteligente · Datos históricos: Yahoo Finance</div>',
                unsafe_allow_html=True)


def logo_data_uri() -> str:
    return _logo_src()

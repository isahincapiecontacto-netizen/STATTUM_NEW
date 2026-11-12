"""Visualizaciones interactivas de precios, riesgo y escenarios."""
from __future__ import annotations
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import metricas as m
from config import nombre_activo, colores

AZUL = "#092B53"
GRILLA = "#E8EEF6"


def estilo(fig: go.Figure, altura: int = 370) -> go.Figure:
    fig.update_layout(
        height=altura, margin=dict(l=18, r=18, t=20, b=45),
        plot_bgcolor="rgba(255,255,255,0)", paper_bgcolor="rgba(255,255,255,0)",
        font=dict(family="Inter, Segoe UI, sans-serif", color=AZUL, size=12),
        hovermode="x unified", legend=dict(orientation="h", y=-0.20, x=0, title=""),
    )
    fig.update_xaxes(showgrid=True, gridcolor=GRILLA, zeroline=False, linecolor=GRILLA)
    fig.update_yaxes(showgrid=True, gridcolor=GRILLA, zeroline=False, linecolor=GRILLA)
    return fig


def grafica_precios(precios: pd.DataFrame) -> go.Figure:
    fig = go.Figure()
    normalizadas = m.base_100(precios)
    paleta = colores(precios.columns)
    for ticker in precios.columns:
        normal = normalizadas[ticker]
        fig.add_trace(go.Scatter(
            x=normal.index, y=normal, mode="lines", name=nombre_activo(ticker),
            line=dict(color=paleta[ticker], width=2.9),
            hovertemplate="%{y:.1f}<extra>" + ticker + "</extra>",
        ))
    fig.update_yaxes(title="Base 100")
    fig.update_xaxes(title=None)
    return estilo(fig, 395)


def grafica_riesgo(tabla: pd.DataFrame) -> go.Figure:
    fig = go.Figure()
    mapa = colores(tabla.index)
    for ticker, row in tabla.iterrows():
        if not np.isfinite(row["Retorno anualizado"]) or not np.isfinite(row["Volatilidad anual"]):
            continue
        fig.add_trace(go.Scatter(
            x=[row["Volatilidad anual"]], y=[row["Retorno anualizado"]],
            mode="markers+text", name=nombre_activo(ticker),
            text=[nombre_activo(ticker)], textposition="top center",
            marker=dict(color=mapa[ticker], size=14, line=dict(width=2, color="white")),
            hovertemplate="Volatilidad: %{x:.1%}<br>Retorno anual: %{y:.1%}<extra>" + ticker + "</extra>",
            showlegend=False,
        ))
    fig.update_xaxes(title="Volatilidad anual", tickformat=".0%")
    fig.update_yaxes(title="Retorno anual", tickformat=".0%")
    return estilo(fig, 365)


def grafica_correlacion(rets: pd.DataFrame) -> go.Figure:
    corr = rets.corr()
    nombres = [nombre_activo(t) for t in corr.index]
    fig = go.Figure(data=go.Heatmap(
        z=corr.values, x=nombres, y=nombres, zmin=-1, zmax=1, zmid=0,
        colorscale=[[0, "#F8AEB1"], [.5, "#F2F6FA"], [1, "#17845F"]],
        text=np.round(corr.values, 2), texttemplate="%{text:.2f}",
        colorbar=dict(title="r", thickness=12),
        hovertemplate="%{y} / %{x}<br>Correlación: %{z:.2f}<extra></extra>",
    ))
    fig.update_yaxes(autorange="reversed")
    return estilo(fig, 365)


def grafica_drawdown(precios: pd.DataFrame) -> go.Figure:
    dd = m.drawdown(precios)
    fig = go.Figure()
    mapa = colores(precios.columns)
    for t in precios.columns:
        fig.add_trace(go.Scatter(x=dd.index, y=dd[t], name=nombre_activo(t),
                                 line=dict(color=mapa[t], width=2.5)))
    fig.update_yaxes(title="Caída desde máximo", tickformat=".0%")
    return estilo(fig, 310)


def grafica_monte_carlo(sim: dict, color: str = "#0082DE") -> go.Figure:
    dias = np.arange(sim["dias"] + 1)
    meses = dias * 12 / 252
    fig = go.Figure()
    for n in range(sim["trayectorias"].shape[1]):
        fig.add_trace(go.Scatter(
            x=meses, y=sim["trayectorias"][:, n], mode="lines",
            line=dict(color="rgba(46,148,237,0.15)", width=1),
            showlegend=False, hoverinfo="skip",
        ))
    fig.add_trace(go.Scatter(x=meses, y=sim["banda_superior"], mode="lines",
                             line=dict(color="rgba(16,185,189,0)", width=0),
                             showlegend=False, hoverinfo="skip"))
    fig.add_trace(go.Scatter(x=meses, y=sim["banda_inferior"], mode="lines",
                             fill="tonexty", fillcolor="rgba(6,182,212,0.18)",
                             line=dict(color="rgba(16,185,189,0)", width=0),
                             name=f"Intervalo {sim['confianza']:.0%}",
                             hovertemplate="Límite inferior: %{y:,.0f}<extra></extra>"))
    fig.add_trace(go.Scatter(x=meses, y=sim["banda_mediana"], mode="lines",
                             line=dict(color=color, width=3.5), name="Mediana",
                             hovertemplate="Mediana: %{y:,.0f}<extra></extra>"))
    fig.add_hline(y=sim["monto"], line_dash="dot", line_color="#8394AB",
                  annotation_text="Monto inicial", annotation_position="bottom right")
    # El público puede reproducir cómo se dibujan las trayectorias sin recalcular el modelo.
    pasos_animacion = np.unique(np.linspace(2, len(meses), 12, dtype=int))
    n_trazas = sim["trayectorias"].shape[1]
    frames = []
    for hasta in pasos_animacion:
        segmentadas = [
            go.Scatter(x=meses[:hasta], y=sim["trayectorias"][:hasta, n])
            for n in range(n_trazas)
        ]
        frames.append(go.Frame(data=segmentadas, traces=list(range(n_trazas)), name=str(hasta)))
    fig.frames = frames
    fig.update_layout(updatemenus=[dict(
        type="buttons", direction="left", showactive=False,
        x=0.02, y=1.20, xanchor="left", yanchor="top",
        buttons=[dict(label="▶ Reproducir trayectorias", method="animate",
                      args=[None, {"frame": {"duration": 125, "redraw": False},
                                   "transition": {"duration": 0},
                                   "fromcurrent": False, "mode": "immediate"}])],
        bgcolor="rgba(255,255,255,.85)", bordercolor="#DBE9F5", borderwidth=1,
    )])
    fig.update_xaxes(title="Meses de inversión", range=[0, meses[-1]])
    fig.update_yaxes(title="Valor de la inversión")
    fig = estilo(fig, 445)
    fig.update_layout(hovermode="x")
    return fig


def grafica_distribucion(sim: dict, color: str = "#0082DE") -> go.Figure:
    fig = go.Figure()
    fig.add_trace(go.Histogram(x=sim["finales"], nbinsx=55, marker_color=color,
                               opacity=.75, name="Escenarios", hovertemplate="Valor final: %{x:,.0f}<br>Frecuencia: %{y}<extra></extra>"))
    fig.add_vline(x=sim["monto"], line_dash="dash", line_color="#ED6A2F",
                  annotation_text="Inversión inicial", annotation_position="top left")
    fig.update_xaxes(title="Valor final")
    fig.update_yaxes(title="Número de escenarios")
    return estilo(fig, 260)

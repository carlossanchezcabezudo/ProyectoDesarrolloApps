
# graphics.py
"""Funciones que devuelven figuras de Plotly utilizadas en la app."""

import plotly.graph_objects as go


def figura_franjas(riesgo_principal, alternativas):
    """Construye un gráfico de barras con la franja seleccionada
    y las franjas alternativas.

    Parameters
    ----------
    riesgo_principal : float
        Probabilidad para la franja seleccionada (0–1).
    alternativas : list of (str, float)
        Lista de pares (nombre_franja_legible, riesgo).

    Returns
    -------
    fig : plotly.graph_objects.Figure
    """
    if riesgo_principal is None or alternativas is None:
        return figura_vacia()

    nombres = ["Franja seleccionada"] + [alt[0] for alt in alternativas]
    valores = [riesgo_principal] + [alt[1] for alt in alternativas]
    porcentajes = [v * 100 for v in valores]

    fig = go.Figure()
    fig.add_bar(
        x=nombres,
        y=valores,
        text=[f"{p:.1f} %" for p in porcentajes],
        textposition="auto",
    )
    fig.update_layout(
        title="Comparación de franjas horarias",
        yaxis=dict(
            title="Probabilidad de lesión grave",
            tickformat=".0%",
            range=[0, max(valores) * 1.2],
        ),
        xaxis_title="Franja",
        bargap=0.3,
    )

    return fig


def figura_vacia():
    """Figura vacía para cuando aún no hay escenario completo."""
    fig = go.Figure()
    fig.update_layout(
        title="Franjas alternativas",
        xaxis_title="Franja",
        yaxis_title="Probabilidad de lesión grave",
    )
    return fig

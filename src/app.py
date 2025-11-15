from dash import Dash, html, dcc, Input, Output
import plotly.graph_objects as go

from .model import calcular_riesgo


# Creamos la app Dash
app = Dash(__name__, title="MADly Safe · Riesgo de lesión grave en Madrid")
server = app.server

# ----- Opciones de los controles -----

TIPOS_PERSONA = [
    {"label": "Conductor", "value": "Conductor"},
    {"label": "Pasajero", "value": "Pasajero"},
    {"label": "Peatón", "value": "Peatón"},
]

TIPOS_VEHICULO = [
    {"label": "Turismo", "value": "Turismo"},
    {"label": "Motocicleta", "value": "Motocicleta"},
    {"label": "Furgoneta", "value": "Furgoneta"},
    {"label": "Bicicleta", "value": "Bicicleta"},
    {"label": "VMP / Patinete", "value": "VMP"},
    {"label": "Sin vehículo (peatón)", "value": "Sin_vehiculo"},
]

RANGOS_EDAD = [
    {"label": "Menor de 18 años", "value": "<18"},
    {"label": "18–24 años", "value": "18-24"},
    {"label": "25–34 años", "value": "25-34"},
    {"label": "35–44 años", "value": "35-44"},
    {"label": "45–54 años", "value": "45-54"},
    {"label": "55–64 años", "value": "55-64"},
    {"label": "65–74 años", "value": "65-74"},
    {"label": "75+ años", "value": "75+"},
]

SEXO_OPCIONES = [
    {"label": "Hombre", "value": "Hombre"},
    {"label": "Mujer", "value": "Mujer"},
    {"label": "Desconocido / Otro", "value": "Desconocido"},
]

DISTRITOS = [
    {"label": "Centro", "value": "CENTRO"},
    {"label": "Arganzuela", "value": "ARGANZUELA"},
    {"label": "Retiro", "value": "RETIRO"},
    {"label": "Salamanca", "value": "SALAMANCA"},
    {"label": "Chamartín", "value": "CHAMARTIN"},
    {"label": "Tetuán", "value": "TETUAN"},
    {"label": "Chamberí", "value": "CHAMBERI"},
]

DIAS_SEMANA = [
    {"label": "Lunes", "value": "Lunes"},
    {"label": "Martes", "value": "Martes"},
    {"label": "Miércoles", "value": "Miércoles"},
    {"label": "Jueves", "value": "Jueves"},
    {"label": "Viernes", "value": "Viernes"},
    {"label": "Sábado", "value": "Sábado"},
    {"label": "Domingo", "value": "Domingo"},
]

METEOROLOGIA = [
    {"label": "Despejado", "value": "Despejado"},
    {"label": "Nublado", "value": "Nublado"},
    {"label": "Lluvia débil", "value": "Lluvia debil"},
    {"label": "Lluvia intensa", "value": "Lluvia intensa"},
    {"label": "Se desconoce", "value": "Desconocido"},
]

FRANJAS_HORARIAS = [
    {"label": "00:00 – 05:59", "value": "Noche_madrugada"},
    {"label": "06:00 – 09:59", "value": "Manana_punta"},
    {"label": "10:00 – 13:59", "value": "Manana_media"},
    {"label": "14:00 – 17:59", "value": "Tarde"},
    {"label": "18:00 – 21:59", "value": "Tarde_punta"},
    {"label": "22:00 – 23:59", "value": "Noche"},
]

# ----- Layout de la app -----

app.layout = html.Div(
    children=[
        # Cabecera
        html.Div(
            children=[
                html.H1("MADly Safe", style={"marginBottom": "5px"}),
                html.H3(
                    "Recomendador de franjas más seguras según perfil y contexto en Madrid",
                    style={"fontWeight": "normal", "color": "#444"},
                ),
                html.P(
                    "Selecciona tu perfil y condiciones de desplazamiento. "
                    "La aplicación estima la probabilidad de lesión grave "
                    "(condicionada a que ocurra un accidente) y sugiere franjas alternativas.",
                    style={"maxWidth": "900px"},
                ),
            ],
            style={
                "textAlign": "left",
                "padding": "20px 40px 10px 40px",
                "backgroundColor": "#f8f9fa",
                "borderBottom": "1px solid #ddd",
            },
        ),

        # Cuerpo: formulario + resultados
        html.Div(
            children=[
                # Columna izquierda: formulario
                html.Div(
                    children=[
                        html.H4("1. Define tu escenario"),

                        html.Label("Tipo de persona"),
                        dcc.Dropdown(
                            id="input-tipo-persona",
                            options=TIPOS_PERSONA,
                            value="Conductor",
                        ),
                        html.Br(),

                        html.Label("Tipo de vehículo"),
                        dcc.Dropdown(
                            id="input-tipo-vehiculo",
                            options=TIPOS_VEHICULO,
                            value="Turismo",
                        ),
                        html.Br(),

                        html.Label("Rango de edad"),
                        dcc.Dropdown(
                            id="input-rango-edad",
                            options=RANGOS_EDAD,
                            value="25-34",
                        ),
                        html.Br(),

                        html.Label("Sexo"),
                        dcc.Dropdown(
                            id="input-sexo",
                            options=SEXO_OPCIONES,
                            value="Hombre",
                        ),
                        html.Br(),

                        html.Label("Distrito de Madrid"),
                        dcc.Dropdown(
                            id="input-distrito",
                            options=DISTRITOS,
                            value="CENTRO",
                        ),
                        html.Br(),

                        html.Label("Día de la semana"),
                        dcc.Dropdown(
                            id="input-dia",
                            options=DIAS_SEMANA,
                            value="Lunes",
                        ),
                        html.Br(),

                        html.Label("Franja horaria"),
                        dcc.Dropdown(
                            id="input-franja",
                            options=FRANJAS_HORARIAS,
                            value="Tarde_punta",
                        ),
                        html.Br(),

                        html.Label("Estado meteorológico"),
                        dcc.Dropdown(
                            id="input-meteo",
                            options=METEOROLOGIA,
                            value="Despejado",
                        ),
                    ],
                    style={
                        "display": "inline-block",
                        "verticalAlign": "top",
                        "width": "30%",
                        "padding": "20px 40px",
                        "boxSizing": "border-box",
                        "borderRight": "1px solid #eee",
                    },
                ),

                # Columna derecha: resultados
                html.Div(
                    children=[
                        html.H4("2. Riesgo estimado y franjas alternativas"),
                        html.Div(
                            id="card-riesgo",
                            style={
                                "padding": "15px 20px",
                                "borderRadius": "10px",
                                "backgroundColor": "#fff3cd",
                                "border": "1px solid #ffeeba",
                                "marginBottom": "20px",
                            },
                        ),
                        dcc.Graph(
                            id="grafico-franjas",
                            style={"height": "380px"},
                        ),
                        html.Div(
                            id="explicacion",
                            style={"marginTop": "15px", "color": "#555"},
                        ),
                    ],
                    style={
                        "display": "inline-block",
                        "verticalAlign": "top",
                        "width": "70%",
                        "padding": "20px 40px",
                        "boxSizing": "border-box",
                    },
                ),
            ]
        ),
    ]
)

# ----- Función auxiliar para figura vacía -----


def figura_vacia():
    fig = go.Figure()
    fig.update_layout(
        title="Franjas alternativas",
        xaxis_title="Franja",
        yaxis_title="Probabilidad de lesión grave",
    )
    return fig


# ----- Callback -----


@app.callback(
    Output("card-riesgo", "children"),
    Output("grafico-franjas", "figure"),
    Output("explicacion", "children"),
    Input("input-tipo-persona", "value"),
    Input("input-tipo-vehiculo", "value"),
    Input("input-rango-edad", "value"),
    Input("input-sexo", "value"),
    Input("input-distrito", "value"),
    Input("input-dia", "value"),
    Input("input-franja", "value"),
    Input("input-meteo", "value"),
)
def actualizar_salida(tipo_persona, tipo_vehiculo, rango_edad, sexo,
                      distrito, dia, franja, meteo):

    try:
        riesgo, alternativas = calcular_riesgo(
            tipo_persona, tipo_vehiculo, rango_edad, sexo,
            distrito, dia, franja, meteo
        )
    except Exception as e:
        card = html.Div(
            [
                html.Div(
                    "Se ha producido un error al calcular el riesgo.",
                    style={"fontWeight": "bold"},
                ),
                html.Div(
                    "Revisa los valores seleccionados o contacta con la persona responsable de la aplicación.",
                    style={"fontSize": "13px"},
                ),
            ]
        )
        figura = figura_vacia()
        explicacion = f"Detalle técnico del error (solo para depuración): {e}"
        return card, figura, explicacion

    if riesgo is None or alternativas is None:
        card = html.Div(
            "Completa los campos de la izquierda para ver la estimación de riesgo.",
            style={"fontWeight": "bold"},
        )
        figura = figura_vacia()
        explicacion = ""
        return card, figura, explicacion

    # Tarjeta de riesgo
    riesgo_pct = round(riesgo * 100, 2)
    card = html.Div(
        [
            html.Div("Escenario seleccionado", style={"fontSize": "14px", "color": "#777"}),
            html.Div(
                f"{riesgo_pct} %",
                style={"fontSize": "34px", "fontWeight": "bold"},
            ),
            html.Div(
                "Probabilidad estimada de lesión grave o fallecimiento "
                "condicionada a que ocurra un accidente.",
                style={"fontSize": "13px"},
            ),
            html.Div(
                "Modelo actual: Regresión Logística (class_weight='balanced').",
                style={"fontSize": "12px", "color": "#666", "marginTop": "4px"},
            ),
        ]
    )

    # Figura construida directamente aquí usando los nombres de alternativas
    nombres = ["Franja seleccionada"] + [alt[0] for alt in alternativas]
    valores = [riesgo] + [alt[1] for alt in alternativas]
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

    # Texto explicativo
    nombres_alternativas = [alt[0] for alt in alternativas]
    alternativas_texto = ", ".join(nombres_alternativas)

    explicacion = (
        "Con el perfil seleccionado, la franja actual presenta un riesgo aproximado "
        f"del {riesgo_pct} %. "
        "Las franjas alternativas sugeridas son: "
        f"{alternativas_texto}. "
        "En todos los casos se mantiene fijo el resto del escenario "
        "(perfil, distrito, día de la semana y meteorología). "
        "Esta estimación se basa en un modelo estadístico entrenado con datos históricos "
        "de la ciudad de Madrid y debe interpretarse solo con fines informativos."
    )

    return card, fig, explicacion


if __name__ == "__main__":
    app.run(debug=False, use_reloader=False)

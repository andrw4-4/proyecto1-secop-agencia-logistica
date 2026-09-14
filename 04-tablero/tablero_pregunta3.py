from pathlib import Path

import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import pandas as pd
import plotly.express as px
from scipy import stats


# Configuración inicial
external_stylesheets = ["https://codepen.io/chriddyp/pen/bWLwgP.css"]
app = dash.Dash(
    __name__,
    external_stylesheets=external_stylesheets,
    suppress_callback_exceptions=True,
)
server = app.server

CARPETA_PROYECTO = Path(__file__).resolve().parent


def buscar_archivo(nombre):
    """Busca los CSV en la carpeta de la aplicación o en 03-analisis-datos."""
    opciones = [
        CARPETA_PROYECTO / nombre,
        CARPETA_PROYECTO / "03-analisis-datos" / nombre,
    ]

    for ruta in opciones:
        if ruta.exists():
            return ruta

    raise FileNotFoundError(
        f"No se encontró {nombre}. Déjalo junto a app.py o dentro de "
        "la carpeta 03-analisis-datos."
    )


# Datos para el análisis de estacionalidad
df = pd.read_csv(buscar_archivo("secop_ii_agencia_logistica_features_p3.csv"))
df["fecha_de_firma"] = pd.to_datetime(df["fecha_de_firma"], errors="coerce")

anios_disponibles = sorted(df["anio_firma"].dropna().unique().astype(int))
meses_orden = [
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December",
]
nombres_meses_es = [
    "Ene", "Feb", "Mar", "Abr", "May", "Jun",
    "Jul", "Ago", "Sep", "Oct", "Nov", "Dic",
]

# Pruebas estadísticas de estacionalidad
grupos_trimestre = [
    df.loc[df["trimestre_firma"] == t, "valor_contrato_capped"].dropna()
    for t in sorted(df["trimestre_firma"].dropna().unique())
]
h_stat, p_kruskal = stats.kruskal(*grupos_trimestre)

conteo_observado = (
    df.groupby("mes_firma").size().reindex(range(1, 13), fill_value=0)
)
esperado_uniforme = [conteo_observado.sum() / 12] * 12
chi2_stat, p_chi2 = stats.chisquare(
    conteo_observado,
    f_exp=esperado_uniforme,
)


layout_estacionalidad = html.Div(
    style={"fontFamily": "Arial", "margin": "30px"},
    children=[
        html.H1("Estacionalidad de la contratación — Agencia Logística de las FFMM"),
        html.P(
            "Pregunta de negocio: ¿Cómo se distribuye en el tiempo la contratación "
            "de la Agencia, y qué tan predecible es el ciclo de gasto para efectos "
            "de planeación presupuestal?"
        ),
        html.P(
            "Usuario: área de planeación financiera / presupuesto de la Agencia.",
            style={"fontStyle": "italic", "color": "#555"},
        ),
        html.Hr(),
        html.Label('Seleccione un año (o "Todos" para el patrón agregado):'),
        dcc.Dropdown(
            id="filtro-anio",
            options=[{"label": "Todos los años", "value": "todos"}]
            + [{"label": str(a), "value": a} for a in anios_disponibles],
            value="todos",
            style={"width": "300px"},
        ),
        html.Div(
            style={
                "display": "flex",
                "flexWrap": "wrap",
                "gap": "20px",
                "marginTop": "20px",
            },
            children=[
                dcc.Graph(id="grafico-mensual", style={"width": "48%"}),
                dcc.Graph(
                    id="grafico-boxplot-trimestre",
                    style={"width": "48%"},
                ),
            ],
        ),
        html.H3("¿El patrón se repite entre años?"),
        dcc.Graph(id="grafico-heatmap"),
        html.H3("Resultados de las pruebas estadísticas"),
        html.Div(
            style={
                "backgroundColor": "#f4f4f4",
                "padding": "15px",
                "borderRadius": "8px",
            },
            children=[
                html.P(
                    "Chi-cuadrado de bondad de ajuste (uniformidad mensual): "
                    f"χ² = {chi2_stat:.2f}, p-valor = {p_chi2:.2e}"
                ),
                html.P(
                    "→ Se rechaza H0: la contratación NO es uniforme en el año, "
                    "hay estacionalidad."
                    if p_chi2 < 0.05
                    else "→ No se rechaza H0."
                ),
                html.P(
                    "Kruskal-Wallis (valor del contrato por trimestre): "
                    f"H = {h_stat:.2f}, p-valor = {p_kruskal:.4f}"
                ),
                html.P(
                    "→ Se rechaza H0: el valor del contrato difiere "
                    "significativamente entre trimestres."
                    if p_kruskal < 0.05
                    else "→ No se rechaza H0."
                ),
            ],
        ),
        html.H3("Hallazgo y recomendación"),
        html.P(
            "La contratación se concentra en marzo-mayo y cae fuertemente en "
            "noviembre-enero, un patrón que se repite en la mayoría de los años "
            "con datos completos. El área de planeación presupuestal puede "
            "anticipar mayor carga operativa entre marzo y junio, y debería "
            "investigar por qué la actividad contractual cae tanto al cierre "
            "del año fiscal."
        ),
    ],
)


# Datos para el análisis de proveedores
df_p1 = pd.read_csv(buscar_archivo("base_analitica.csv"))
df_p1["anio_firma"] = pd.to_numeric(df_p1["anio_firma"], errors="coerce")

anios_p1 = sorted(df_p1["anio_firma"].dropna().unique().astype(int))
modalidades_p1 = sorted(
    df_p1["modalidad_de_contratacion"].dropna().unique()
)


layout_proveedores = html.Div(
    style={"fontFamily": "Arial", "margin": "30px"},
    children=[
        html.H1("Dependencia de proveedores — Agencia Logística de las FFMM"),
        html.P(
            "Pregunta de negocio: ¿Qué tan dependiente es la Agencia Logística "
            "de un grupo reducido de proveedores, y en qué modalidades de "
            "contratación se concentra ese riesgo?"
        ),
        html.P(
            "Usuario: áreas de contratación, compras y gestión de riesgos de la Agencia.",
            style={"fontStyle": "italic", "color": "#555"},
        ),
        html.Hr(),
        html.Div(
            style={"display": "flex", "gap": "30px", "flexWrap": "wrap"},
            children=[
                html.Div(
                    [
                        html.Label("Seleccione un año:"),
                        dcc.Dropdown(
                            id="filtro-anio-p1",
                            options=[
                                {"label": "Todos los años", "value": "todos"}
                            ]
                            + [
                                {"label": str(a), "value": a}
                                for a in anios_p1
                            ],
                            value="todos",
                            style={"width": "300px"},
                        ),
                    ]
                ),
                html.Div(
                    [
                        html.Label("Seleccione una modalidad:"),
                        dcc.Dropdown(
                            id="filtro-modalidad-p1",
                            options=[
                                {
                                    "label": "Todas las modalidades",
                                    "value": "todas",
                                }
                            ]
                            + [
                                {"label": m, "value": m}
                                for m in modalidades_p1
                            ],
                            value="todas",
                            style={"width": "430px"},
                        ),
                    ]
                ),
            ],
        ),
        html.Div(
            style={
                "display": "flex",
                "gap": "20px",
                "marginTop": "25px",
                "flexWrap": "wrap",
            },
            children=[
                html.Div(
                    [html.H4("HHI"), html.H2(id="kpi-hhi-p1")],
                    style={
                        "backgroundColor": "#f4f4f4",
                        "padding": "15px",
                        "borderRadius": "8px",
                        "width": "20%",
                        "minWidth": "180px",
                        "textAlign": "center",
                    },
                ),
                html.Div(
                    [html.H4("Participación del top 10"), html.H2(id="kpi-top10-p1")],
                    style={
                        "backgroundColor": "#f4f4f4",
                        "padding": "15px",
                        "borderRadius": "8px",
                        "width": "20%",
                        "minWidth": "180px",
                        "textAlign": "center",
                    },
                ),
                html.Div(
                    [
                        html.H4("Proveedores para alcanzar 80%"),
                        html.H2(id="kpi-80-p1"),
                    ],
                    style={
                        "backgroundColor": "#f4f4f4",
                        "padding": "15px",
                        "borderRadius": "8px",
                        "width": "20%",
                        "minWidth": "180px",
                        "textAlign": "center",
                    },
                ),
                html.Div(
                    [html.H4("Valor contratado"), html.H2(id="kpi-valor-p1")],
                    style={
                        "backgroundColor": "#f4f4f4",
                        "padding": "15px",
                        "borderRadius": "8px",
                        "width": "20%",
                        "minWidth": "180px",
                        "textAlign": "center",
                    },
                ),
            ],
        ),
        html.Div(
            style={
                "display": "flex",
                "flexWrap": "wrap",
                "gap": "20px",
                "marginTop": "25px",
            },
            children=[
                dcc.Graph(id="grafico-top10-p1", style={"width": "48%"}),
                dcc.Graph(id="grafico-acumulado-p1", style={"width": "48%"}),
            ],
        ),
        dcc.Graph(id="grafico-hhi-p1"),
        html.H3("Hallazgo principal"),
        html.Div(
            id="hallazgo-p1",
            style={
                "backgroundColor": "#f4f4f4",
                "padding": "15px",
                "borderRadius": "8px",
            },
        ),
    ],
)


# Organización del tablero en pestañas
app.layout = html.Div(
    children=[
        html.Div(
            [
                html.H2(
                    "Analítica de contratación pública — Agencia Logística de las FFMM",
                    style={"marginBottom": "5px"},
                ),
                html.P(
                    "Seleccione una pestaña para consultar cada pregunta de negocio.",
                    style={"marginTop": "0", "color": "#555"},
                ),
            ],
            style={"fontFamily": "Arial", "margin": "25px 30px 5px 30px"},
        ),
        dcc.Tabs(
            value="proveedores",
            children=[
                dcc.Tab(
                    label="Concentración de proveedores",
                    value="proveedores",
                    children=[layout_proveedores],
                ),
                dcc.Tab(
                    label="Estacionalidad de la contratación",
                    value="estacionalidad",
                    children=[layout_estacionalidad],
                ),
            ],
        ),
    ]
)


# Gráficos de estacionalidad
@app.callback(Output("grafico-mensual", "figure"), Input("filtro-anio", "value"))
def actualizar_grafico_mensual(anio_seleccionado):
    dff = (
        df
        if anio_seleccionado == "todos"
        else df[df["anio_firma"] == anio_seleccionado]
    )
    conteo = dff.groupby("mes_firma").size().reindex(range(1, 13), fill_value=0)

    fig = px.bar(
        x=nombres_meses_es,
        y=conteo.values,
        labels={"x": "Mes", "y": "N° de contratos"},
        title=(
            "Contratos por mes — "
            + (
                "Todos los años"
                if anio_seleccionado == "todos"
                else str(anio_seleccionado)
            )
        ),
    )
    return fig


@app.callback(
    Output("grafico-boxplot-trimestre", "figure"),
    Input("filtro-anio", "value"),
)
def actualizar_boxplot(anio_seleccionado):
    dff = (
        df
        if anio_seleccionado == "todos"
        else df[df["anio_firma"] == anio_seleccionado]
    )

    fig = px.box(
        dff,
        x="trimestre_firma",
        y="valor_contrato_capped",
        labels={
            "trimestre_firma": "Trimestre",
            "valor_contrato_capped": "Valor del contrato (COP)",
        },
        title="Valor del contrato por trimestre",
        log_y=True,
    )
    return fig


@app.callback(Output("grafico-heatmap", "figure"), Input("filtro-anio", "value"))
def actualizar_heatmap(_):
    tabla = df.pivot_table(
        index="mes_firma",
        columns="anio_firma",
        values="valor_del_contrato",
        aggfunc="count",
        fill_value=0,
    )
    tabla.index = [nombres_meses_es[int(mes) - 1] for mes in tabla.index]

    fig = px.imshow(
        tabla,
        text_auto=True,
        aspect="auto",
        labels=dict(x="Año", y="Mes", color="N° contratos"),
        title="N° de contratos por mes y año",
        color_continuous_scale="YlOrRd",
    )
    return fig


# Gráficos de concentración de proveedores
@app.callback(
    [
        Output("kpi-hhi-p1", "children"),
        Output("kpi-top10-p1", "children"),
        Output("kpi-80-p1", "children"),
        Output("kpi-valor-p1", "children"),
        Output("grafico-top10-p1", "figure"),
        Output("grafico-acumulado-p1", "figure"),
        Output("grafico-hhi-p1", "figure"),
        Output("hallazgo-p1", "children"),
    ],
    [
        Input("filtro-anio-p1", "value"),
        Input("filtro-modalidad-p1", "value"),
    ],
)
def actualizar_tablero_proveedores(anio, modalidad):
    dff = df_p1.copy()

    if anio != "todos":
        dff = dff[dff["anio_firma"] == int(anio)]

    if modalidad != "todas":
        dff = dff[dff["modalidad_de_contratacion"] == modalidad]

    if dff.empty or dff["valor_del_contrato"].sum() <= 0:
        figura_vacia = px.scatter(title="No hay datos para los filtros seleccionados")
        return (
            "Sin datos",
            "Sin datos",
            "Sin datos",
            "$0",
            figura_vacia,
            figura_vacia,
            figura_vacia,
            "No existen contratos para la combinación seleccionada.",
        )

    dff["nombre_proveedor"] = dff["proveedor"].fillna(
        dff["id_proveedor"].astype(str)
    )

    proveedores = (
        dff.groupby(["id_proveedor", "nombre_proveedor"], dropna=False)
        .agg(
            numero_contratos=("id_contrato", "count"),
            valor_total=("valor_del_contrato", "sum"),
        )
        .reset_index()
        .sort_values("valor_total", ascending=False)
        .reset_index(drop=True)
    )

    total = proveedores["valor_total"].sum()
    proveedores["participacion"] = proveedores["valor_total"] / total
    proveedores["participacion_pct"] = proveedores["participacion"] * 100
    proveedores["acumulada"] = proveedores["participacion"].cumsum() * 100
    proveedores["ranking"] = proveedores.index + 1

    hhi = (proveedores["participacion"] ** 2).sum() * 10000
    top10 = proveedores.head(10)["participacion"].sum() * 100
    proveedores_80 = int((proveedores["acumulada"] < 80).sum() + 1)

    top10_df = proveedores.head(10).sort_values("participacion_pct")
    fig_top10 = px.bar(
        top10_df,
        x="participacion_pct",
        y="nombre_proveedor",
        orientation="h",
        text="participacion_pct",
        labels={
            "participacion_pct": "Participación en el valor contratado (%)",
            "nombre_proveedor": "Proveedor",
        },
        title="Diez proveedores con mayor participación",
        hover_data={
            "valor_total": ":,.0f",
            "numero_contratos": True,
            "participacion_pct": ":.2f",
        },
    )
    fig_top10.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
    fig_top10.update_layout(margin={"l": 260, "r": 40, "t": 60, "b": 50})

    fig_acumulada = px.line(
        proveedores,
        x="ranking",
        y="acumulada",
        labels={
            "ranking": "Número acumulado de proveedores",
            "acumulada": "Participación acumulada (%)",
        },
        title="Concentración acumulada del valor contratado",
    )
    fig_acumulada.add_hline(y=80, line_dash="dash", line_color="red")
    fig_acumulada.add_vline(
        x=proveedores_80,
        line_dash="dash",
        line_color="orange",
    )

    # Comparación del HHI por modalidad para el año seleccionado
    base_hhi = (
        df_p1.copy()
        if anio == "todos"
        else df_p1[df_p1["anio_firma"] == int(anio)].copy()
    )

    pm = (
        base_hhi.groupby(
            ["modalidad_de_contratacion", "id_proveedor"],
            dropna=False,
        )
        .agg(valor_proveedor=("valor_del_contrato", "sum"))
        .reset_index()
    )
    pm["total_modalidad"] = pm.groupby("modalidad_de_contratacion")[
        "valor_proveedor"
    ].transform("sum")
    pm["participacion"] = pm["valor_proveedor"] / pm["total_modalidad"]

    hhi_modalidad = (
        pm.groupby("modalidad_de_contratacion")
        .agg(
            hhi=("participacion", lambda x: (x**2).sum() * 10000),
            proveedores=("id_proveedor", "nunique"),
            valor_modalidad=("valor_proveedor", "sum"),
        )
        .reset_index()
    )

    contratos_modalidad = (
        base_hhi.groupby("modalidad_de_contratacion")["id_contrato"]
        .count()
        .reset_index(name="contratos")
    )
    hhi_modalidad = hhi_modalidad.merge(
        contratos_modalidad,
        on="modalidad_de_contratacion",
        how="left",
    )
    hhi_modalidad["peso_valor"] = (
        hhi_modalidad["valor_modalidad"]
        / hhi_modalidad["valor_modalidad"].sum()
        * 100
    )
    hhi_modalidad = hhi_modalidad.sort_values("hhi")

    fig_hhi = px.bar(
        hhi_modalidad,
        x="hhi",
        y="modalidad_de_contratacion",
        orientation="h",
        color="peso_valor",
        color_continuous_scale="YlOrRd",
        labels={
            "hhi": "Índice HHI",
            "modalidad_de_contratacion": "Modalidad",
            "peso_valor": "% del valor total",
        },
        hover_data={
            "proveedores": True,
            "contratos": True,
            "valor_modalidad": ":,.0f",
            "peso_valor": ":.2f",
        },
        title="Concentración de proveedores por modalidad",
    )
    fig_hhi.add_vline(x=1500, line_dash="dash", line_color="orange")
    fig_hhi.add_vline(x=2500, line_dash="dash", line_color="red")
    fig_hhi.update_layout(margin={"l": 260, "r": 40, "t": 60, "b": 50})

    valor_total = dff["valor_del_contrato"].sum()

    hallazgo = html.P(
        [
            f"Para los filtros seleccionados, el HHI es {hhi:.0f}. ",
            f"Los 10 principales proveedores concentran {top10:.1f}% del valor ",
            f"y se necesitan {proveedores_80} proveedores para alcanzar el 80%. ",
            "La gráfica por modalidad permite distinguir cuáles presentan mayor "
            "concentración y, mediante el color, cuáles representan una mayor "
            "parte del valor contratado.",
        ]
    )

    return (
        f"{hhi:.0f}",
        f"{top10:.1f}%",
        proveedores_80,
        f"${valor_total / 1e12:.2f} billones",
        fig_top10,
        fig_acumulada,
        fig_hhi,
        hallazgo,
    )


if __name__ == "__main__":
    app.run(debug=True)

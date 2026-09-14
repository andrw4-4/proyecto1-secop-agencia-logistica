import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd
from scipy import stats

# ------------------------------------------------------------------
# Carga de datos
# ------------------------------------------------------------------
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server

df = pd.read_csv("secop_ii_agencia_logistica_features_p3.csv")
df['fecha_de_firma'] = pd.to_datetime(df['fecha_de_firma'], errors='coerce')

anios_disponibles = sorted(df['anio_firma'].dropna().unique().astype(int))
meses_orden = ['January','February','March','April','May','June',
               'July','August','September','October','November','December']
nombres_meses_es = ['Ene','Feb','Mar','Abr','May','Jun','Jul','Ago','Sep','Oct','Nov','Dic']

# ------------------------------------------------------------------
# Pruebas estadísticas (se calculan una sola vez al arrancar la app)
# ------------------------------------------------------------------
grupos_trimestre = [
    df.loc[df['trimestre_firma'] == t, 'valor_contrato_capped'].dropna()
    for t in sorted(df['trimestre_firma'].dropna().unique())
]
h_stat, p_kruskal = stats.kruskal(*grupos_trimestre)

conteo_observado = df.groupby('mes_firma').size().reindex(range(1, 13), fill_value=0)
esperado_uniforme = [conteo_observado.sum() / 12] * 12
chi2_stat, p_chi2 = stats.chisquare(conteo_observado, f_exp=esperado_uniforme)

# ------------------------------------------------------------------
# Layout
# ------------------------------------------------------------------
app.layout = html.Div(style={'fontFamily': 'Arial', 'margin': '30px'}, children=[

    html.H1('Estacionalidad de la contratación — Agencia Logística de las FFMM'),
    html.P('Pregunta de negocio: ¿Cómo se distribuye en el tiempo la contratación de la Agencia, '
           'y qué tan predecible es el ciclo de gasto para efectos de planeación presupuestal?'),
    html.P('Usuario: área de planeación financiera / presupuesto de la Agencia.',
           style={'fontStyle': 'italic', 'color': '#555'}),

    html.Hr(),

    html.Label('Seleccione un año (o "Todos" para el patrón agregado):'),
    dcc.Dropdown(
        id='filtro-anio',
        options=[{'label': 'Todos los años', 'value': 'todos'}] +
                [{'label': str(a), 'value': a} for a in anios_disponibles],
        value='todos',
        style={'width': '300px'}
    ),

    html.Div(style={'display': 'flex', 'flexWrap': 'wrap', 'gap': '20px', 'marginTop': '20px'}, children=[
        dcc.Graph(id='grafico-mensual', style={'width': '48%'}),
        dcc.Graph(id='grafico-boxplot-trimestre', style={'width': '48%'}),
    ]),

    html.H3('¿El patrón se repite entre años?'),
    dcc.Graph(id='grafico-heatmap'),

    html.H3('Resultados de las pruebas estadísticas'),
    html.Div(style={'backgroundColor': '#f4f4f4', 'padding': '15px', 'borderRadius': '8px'}, children=[
        html.P(f"Chi-cuadrado de bondad de ajuste (uniformidad mensual): "
               f"χ² = {chi2_stat:.2f}, p-valor = {p_chi2:.2e}"),
        html.P("→ Se rechaza H0: la contratación NO es uniforme en el año, hay estacionalidad."
               if p_chi2 < 0.05 else "→ No se rechaza H0."),
        html.P(f"Kruskal-Wallis (valor del contrato por trimestre): "
               f"H = {h_stat:.2f}, p-valor = {p_kruskal:.4f}"),
        html.P("→ Se rechaza H0: el valor del contrato difiere significativamente entre trimestres."
               if p_kruskal < 0.05 else "→ No se rechaza H0."),
    ]),

    html.H3('Hallazgo y recomendación'),
    html.P('La contratación se concentra en marzo-mayo y cae fuertemente en noviembre-enero, '
           'un patrón que se repite en la mayoría de los años con datos completos. El área de '
           'planeación presupuestal puede anticipar mayor carga operativa entre marzo y junio, '
           'y debería investigar por qué la actividad contractual cae tanto al cierre del año fiscal.')
])


# ------------------------------------------------------------------
# Callbacks
# ------------------------------------------------------------------
@app.callback(Output('grafico-mensual', 'figure'), Input('filtro-anio', 'value'))
def actualizar_grafico_mensual(anio_seleccionado):
    dff = df if anio_seleccionado == 'todos' else df[df['anio_firma'] == anio_seleccionado]
    conteo = dff.groupby('mes_firma').size().reindex(range(1, 13), fill_value=0)

    fig = px.bar(
        x=nombres_meses_es, y=conteo.values,
        labels={'x': 'Mes', 'y': 'N° de contratos'},
        title=f"Contratos por mes — {'Todos los años' if anio_seleccionado == 'todos' else anio_seleccionado}"
    )
    return fig


@app.callback(Output('grafico-boxplot-trimestre', 'figure'), Input('filtro-anio', 'value'))
def actualizar_boxplot(anio_seleccionado):
    dff = df if anio_seleccionado == 'todos' else df[df['anio_firma'] == anio_seleccionado]

    fig = px.box(
        dff, x='trimestre_firma', y='valor_contrato_capped',
        labels={'trimestre_firma': 'Trimestre', 'valor_contrato_capped': 'Valor del contrato (COP)'},
        title='Valor del contrato por trimestre',
        log_y=True
    )
    return fig


@app.callback(Output('grafico-heatmap', 'figure'), Input('filtro-anio', 'value'))
def actualizar_heatmap(_):
    tabla = df.pivot_table(index='mes_firma', columns='anio_firma',
                            values='valor_del_contrato', aggfunc='count', fill_value=0)
    tabla.index = nombres_meses_es[:len(tabla.index)]

    fig = px.imshow(
        tabla, text_auto=True, aspect='auto',
        labels=dict(x='Año', y='Mes', color='N° contratos'),
        title='N° de contratos por mes y año',
        color_continuous_scale='YlOrRd'
    )
    return fig


if __name__ == '__main__':
    app.run(debug=True)
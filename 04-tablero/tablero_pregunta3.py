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







#############################Pregunta 1 ---#################################











# ------------------------------------------------------------------
# Carga de datos
# ------------------------------------------------------------------

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server

df = pd.read_csv("base_analitica.csv")

anios_disponibles = sorted(df["anio_firma"].dropna().unique().astype(int))
modalidades = sorted(df["modalidad_de_contratacion"].dropna().unique())

# ------------------------------------------------------------------
# Layout
# ------------------------------------------------------------------

app.layout = html.Div(
    style={'fontFamily': 'Arial', 'margin': '30px'},
    children=[

        html.H1(
            'Dependencia de proveedores — Agencia Logística de las FFMM'
        ),

        html.P(
            'Pregunta de negocio: ¿Qué tan dependiente es la Agencia Logística '
            'de un grupo reducido de proveedores, y en qué modalidades de '
            'contratación se concentra ese riesgo?'
        ),

        html.Hr(),

        # Filtros
        html.Div(
            style={'display': 'flex', 'gap': '30px'},
            children=[

                html.Div([
                    html.Label('Seleccione un año:'),
                    dcc.Dropdown(
                        id='filtro-anio-p1',
                        options=[{'label': 'Todos los años', 'value': 'todos'}] +
                                [{'label': str(a), 'value': a}
                                 for a in anios_disponibles],
                        value='todos',
                        style={'width': '300px'}
                    )
                ]),

                html.Div([
                    html.Label('Seleccione una modalidad:'),
                    dcc.Dropdown(
                        id='filtro-modalidad-p1',
                        options=[{'label': 'Todas las modalidades', 'value': 'todas'}] +
                                [{'label': m, 'value': m} for m in modalidades],
                        value='todas',
                        style={'width': '400px'}
                    )
                ])
            ]
        ),

        # Indicadores
        html.Div(
            style={
                'display': 'flex',
                'gap': '20px',
                'marginTop': '25px',
                'flexWrap': 'wrap'
            },
            children=[

                html.Div([
                    html.H4('HHI'),
                    html.H2(id='kpi-hhi-p1')
                ], style={
                    'backgroundColor': '#f4f4f4',
                    'padding': '15px',
                    'borderRadius': '8px',
                    'width': '20%',
                    'textAlign': 'center'
                }),

                html.Div([
                    html.H4('Top 10'),
                    html.H2(id='kpi-top10-p1')
                ], style={
                    'backgroundColor': '#f4f4f4',
                    'padding': '15px',
                    'borderRadius': '8px',
                    'width': '20%',
                    'textAlign': 'center'
                }),

                html.Div([
                    html.H4('Proveedores para 80%'),
                    html.H2(id='kpi-80-p1')
                ], style={
                    'backgroundColor': '#f4f4f4',
                    'padding': '15px',
                    'borderRadius': '8px',
                    'width': '20%',
                    'textAlign': 'center'
                }),

                html.Div([
                    html.H4('Valor contratado'),
                    html.H2(id='kpi-valor-p1')
                ], style={
                    'backgroundColor': '#f4f4f4',
                    'padding': '15px',
                    'borderRadius': '8px',
                    'width': '20%',
                    'textAlign': 'center'
                })
            ]
        ),

        # Gráficas
        html.Div(
            style={
                'display': 'flex',
                'flexWrap': 'wrap',
                'gap': '20px',
                'marginTop': '25px'
            },
            children=[
                dcc.Graph(id='grafico-acumulado-p1', style={'width': '48%'}),
                dcc.Graph(id='grafico-hhi-p1', style={'width': '48%'})
            ]
        ),

        html.H3('Hallazgo principal'),

        html.Div(
            id='hallazgo-p1',
            style={
                'backgroundColor': '#f4f4f4',
                'padding': '15px',
                'borderRadius': '8px'
            }
        )
    ]
)

# ------------------------------------------------------------------
# Callback
# ------------------------------------------------------------------

@app.callback(
    [
        Output('kpi-hhi-p1', 'children'),
        Output('kpi-top10-p1', 'children'),
        Output('kpi-80-p1', 'children'),
        Output('kpi-valor-p1', 'children'),
        Output('grafico-acumulado-p1', 'figure'),
        Output('grafico-hhi-p1', 'figure'),
        Output('hallazgo-p1', 'children')
    ],
    [
        Input('filtro-anio-p1', 'value'),
        Input('filtro-modalidad-p1', 'value')
    ]
)
def actualizar_tablero(anio, modalidad):

    dff = df.copy()

    if anio != 'todos':
        dff = dff[dff['anio_firma'] == anio]

    if modalidad != 'todas':
        dff = dff[dff['modalidad_de_contratacion'] == modalidad]

    # Concentración por proveedor
    proveedores = (
        dff.groupby('id_proveedor')['valor_del_contrato']
        .sum()
        .sort_values(ascending=False)
        .reset_index(name='valor_total')
    )

    total = proveedores['valor_total'].sum()

    proveedores['participacion'] = proveedores['valor_total'] / total
    proveedores['acumulada'] = proveedores['participacion'].cumsum()
    proveedores['ranking'] = proveedores.index + 1

    hhi = (proveedores['participacion'] ** 2).sum() * 10000
    top10 = proveedores.head(10)['participacion'].sum() * 100
    proveedores_80 = (proveedores['acumulada'] < 0.80).sum() + 1

    # Gráfica acumulada
    fig_acumulada = px.line(
        proveedores,
        x='ranking',
        y=proveedores['acumulada'] * 100,
        labels={
            'ranking': 'Número acumulado de proveedores',
            'y': 'Participación acumulada (%)'
        },
        title='Concentración acumulada del valor contratado'
    )

    fig_acumulada.add_hline(y=80, line_dash='dash', line_color='red')
    fig_acumulada.add_vline(
        x=proveedores_80,
        line_dash='dash',
        line_color='orange'
    )

    # HHI por modalidad
    base_hhi = df if anio == 'todos' else df[df['anio_firma'] == anio]

    pm = (
        base_hhi.groupby(
            ['modalidad_de_contratacion', 'id_proveedor']
        )['valor_del_contrato']
        .sum()
        .reset_index()
    )

    pm['total_modalidad'] = (
        pm.groupby('modalidad_de_contratacion')['valor_del_contrato']
        .transform('sum')
    )

    pm['participacion'] = (
        pm['valor_del_contrato'] / pm['total_modalidad']
    )

    hhi_modalidad = (
        pm.groupby('modalidad_de_contratacion')
        .agg(
            hhi=('participacion', lambda x: (x ** 2).sum() * 10000),
            proveedores=('id_proveedor', 'nunique')
        )
        .reset_index()
    )

    # Evitar modalidades con un único proveedor
    hhi_modalidad = hhi_modalidad[
        hhi_modalidad['proveedores'] > 1
    ].sort_values('hhi')

    fig_hhi = px.bar(
        hhi_modalidad,
        x='hhi',
        y='modalidad_de_contratacion',
        orientation='h',
        labels={
            'hhi': 'Índice HHI',
            'modalidad_de_contratacion': 'Modalidad'
        },
        title='Concentración de proveedores por modalidad'
    )

    fig_hhi.add_vline(x=1500, line_dash='dash', line_color='orange')
    fig_hhi.add_vline(x=2500, line_dash='dash', line_color='red')

    valor_total = dff['valor_del_contrato'].sum()

    hallazgo = (
        f'El HHI es {hhi:.0f}. Los 10 principales proveedores concentran '
        f'{top10:.1f}% del valor y {proveedores_80} proveedores son '
        f'necesarios para alcanzar el 80% del valor contratado.'
    )

    return (
        f'{hhi:.0f}',
        f'{top10:.1f}%',
        proveedores_80,
        f'${valor_total / 1e12:.2f} billones',
        fig_acumulada,
        fig_hhi,
        hallazgo
    )

# Ordenar las modalidades según su HHI

hhi_modalidades = resumen_modalidades.sort_values(
    "hhi",
    ascending=True
)

plt.figure(figsize=(11, 7))

plt.barh(
    hhi_modalidades["modalidad"],
    hhi_modalidades["hhi"],
    color="darkorange"
)

plt.xlabel("Índice HHI")
plt.ylabel("Modalidad de contratación")
plt.title("Concentración de proveedores por modalidad")

plt.tight_layout()
plt.show()

# ------------------------------------------------------------------

if __name__ == '__main__':
    app.run(debug=True)
# ==============================
#   DASH Credit Dashboard
#   Códigos categóricos → etiquetas legibles
# ==============================

from dash import Dash, html, dash_table, dcc, callback, Output, Input
import dash_bootstrap_components as dbc
import plotly.express as px
import pandas as pd

# ---------------------------------------
# 1) Cargar datos y preparar columnas
# ---------------------------------------
df = pd.read_excel('data/raw/default_credit_new.xlsx')

# Variable target con nombre corto
df['DEFAULT'] = df['default payment next month']

# --- Mapeos de códigos a etiquetas legibles ---
sex_map = {1: 'MALE', 2: 'FEMALE'}
edu_map = {1: 'GRAD_SCHOOL', 2: 'UNIVERSITY', 3: 'HIGH_SCHOOL', 4: 'OTHERS'}
mar_map = {1: 'MARRIED', 2: 'SINGLE', 3: 'OTHERS'}

# Asegura tipos numéricos donde vienen como texto
for col in ['SEX', 'EDUCATION', 'MARRIAGE']:
    if col in df.columns:
        # intenta convertir a número; valores no convertibles quedan como NaN
        df[col] = pd.to_numeric(df[col], errors='coerce')

# Crea columnas “_LABEL” con las descripciones
df['SEX_LABEL'] = df['SEX'].map(sex_map).fillna('UNKNOWN')
df['EDUCATION_LABEL'] = df['EDUCATION'].map(edu_map).fillna('UNKNOWN')
df['MARRIAGE_LABEL'] = df['MARRIAGE'].map(mar_map).fillna('UNKNOWN')

# Por claridad: métrica usada en el gráfico
METRIC = 'AVG_CREDIT_UTILIZATION'
if METRIC not in df.columns:
    raise ValueError(f'No existe la columna {METRIC} en tu Excel.')

# Mapea selección → columna con etiquetas
CAT_TO_LABEL = {
    'SEX': 'SEX_LABEL',
    'EDUCATION': 'EDUCATION_LABEL',
    'MARRIAGE': 'MARRIAGE_LABEL'
}

# ---------------------------------------
# 2) Inicializar la app
# ---------------------------------------
app = Dash(__name__, external_stylesheets=[dbc.themes.FLATLY])

# ---------------------------------------
# 3) Layout
# ---------------------------------------
app.layout = dbc.Container(fluid=True, children=[

    dbc.Row(dbc.Col(html.H1('Credit Risk Dashboard'), width=12), className="mt-2 mb-3"),

    # Sección descriptiva
dbc.Row(
    dbc.Col(
        dbc.Card(
            dbc.CardBody([
                html.H5("Guide", className="mb-2"),

                html.P([
                    html.Strong("SEX: "), "MALE = 1, FEMALE = 2", html.Br(),
                    html.Strong("EDUCATION: "), "GRAD_SCHOOL = 1, UNIVERSITY = 2, HIGH_SCHOOL = 3, OTHERS = 4", html.Br(),
                    html.Strong("MARRIAGE: "), "MARRIED = 1, SINGLE = 2, OTHERS = 3", html.Br(),
                    html.Br(),
                    html.Strong("Avg Credit Utilization: "),
                    "Ratio of used credit to total credit limit.", html.Br(),
                    html.Strong("Default Rate: "),
                    "Percentage of clients who default next month.", html.Br(),
                ], className="mb-2"),

                html.P(
                    "Default: client failed to make required payments on a debt.",
                    style={'fontStyle': 'italic'},
                    className="mb-1"
                ),

                html.P(
                    "This dashboard analyzes credit utilization and default risk patterns by demographic segments.",
                    style={'fontStyle': 'italic'}
                )
            ])
        ),
        width=12
    ),
    className="mb-3"
), 

    # Selector de dimensión categórica
    dbc.Row([
        dbc.Col(
            dcc.RadioItems(
                options=['SEX', 'EDUCATION', 'MARRIAGE'],
                value='SEX',
                id='cat-selector',
                inline=True
            ),
            width=12,
            className="mb-3"
        )
    ]),

    # Tabla y gráfico
    dbc.Row([
        dbc.Col(
            dbc.Card(dbc.CardBody([
                html.H6("Vista previa del dataset"),
                dash_table.DataTable(
                    data=df.head(12).to_dict('records'),
                    page_size=12,
                    style_table={'overflowX': 'auto'}
                )
            ])),
            width=6
        ),
        dbc.Col(
            dbc.Card(dbc.CardBody([
                html.H6("Avg Utilization (%) y Default Rate (%) por categoría"),
                dcc.Graph(id='bar-avg-util')
            ])),
            width=6
        ),
    ]),
])

# ---------------------------------------
# 4) Callback: usa columnas *_LABEL para el eje X
# ---------------------------------------
@callback(
    Output('bar-avg-util', 'figure'),
    Input('cat-selector', 'value')
)
def update_bar(selected_cat):
    # Columna legible correspondiente a la selección
    label_col = CAT_TO_LABEL.get(selected_cat, selected_cat)

    d = df.copy()
    # Asegura texto limpio en la columna de etiquetas
    d[label_col] = d[label_col].astype('string').str.strip().fillna('UNKNOWN')

    # Agregados: promedio de utilización y tasa de default
    agg = d.groupby(label_col, dropna=False).agg(
        avg_util=(METRIC, 'mean'),
        default_rate=('DEFAULT', 'mean')
    ).reset_index()

    # A porcentaje
    agg['avg_util_pct'] = agg['avg_util'] * 100
    agg['default_pct'] = agg['default_rate'] * 100

    # Barras agrupadas: utilización vs default
    fig = px.bar(
        agg,
        x=label_col,
        y=['avg_util_pct', 'default_pct'],
        barmode='group',
        labels={'value': 'Porcentaje', 'variable': 'Métrica'},
        title=f"Utilización vs Default Rate por {selected_cat}"
    )
    fig.update_traces(texttemplate='%{y:.1f}%', textposition='outside')
    fig.update_layout(yaxis_tickformat='.1f%', margin=dict(l=10, r=10, t=40, b=10))

    return fig

# ---------------------------------------
# 5) Run
# ---------------------------------------
if __name__ == "__main__":
    app.run(debug=True)

# pip install dash dash-core-components dash-html-components plotly
import dash
from dash import html, dcc
import plotly.express as px
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
import warnings

# Filter out warnings
warnings.filterwarnings('ignore')

# Load dataset. 
df = pd.read_excel("data/raw/default_credit.xls", header=1)

fig = px.bar()    

app = dash.Dash(__name__)

app.layout = html.Div(children=[
        html.H1(children='My First Dash Dashboard'),

        html.Div(children='''
            Dash: A web application framework for Python.
        '''),

        dcc.Graph(
            id='example-graph',
            figure=fig
        )
    ])

if __name__ == '__main__':
        app.run(debug=True)

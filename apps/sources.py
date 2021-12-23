from dash import dcc
from dash import html
from dash.dependencies import Input, Output
import pandas as pd
import dash

from app import app

sources = ['source 1', 'source 2']

# layout = html.Div([html.H3(s) for s in sources])
# df = pd.read_csv('https://raw.githubusercontent.com/plotly/datasets/master/solar.csv')
# print(df.to_dict())

# layout = dash_table.DataTable(
#     data=[['test'], ['test1']],
#     columns=[{'id': 'test', 'name': 'test1'}],
#     style_as_list_view=True,
#     style_cell={'padding': '5px'},
#     style_header={
#         'backgroundColor': 'white',
#         'fontWeight': 'bold'
#     },
#     # style_cell_conditional=[
#     #     {
#     #         'if': {'column_id': c},
#     #         'textAlign': 'left'
#     #     } for c in ['Date', 'Region']
#     # ],
# )
# layout = dash.html.Table(dataaa='a')

import datetime
data = {'Cap' : ['A', 'B', 'C', ], 'non-Cap' : ['a','b','c', ]}
df = pd.DataFrame(data)


@app.callback(
    Output('table', 'children'),
    Input('dummy', 'value'))
def generate_table(dataframe, max_rows=26):
    from Platform import data
    sources = data.get_sources()
    dataframe = df
    cols = ['Source name', 'BLABLABLABLA', 'BLABLABLABLA', 'BLABLABLABLA']
    return html.Table(
        # Header
        [html.Tr([html.Th(col) for col in cols]) ] +
        # Body
        [html.Tr([html.Td(s), 'Standard display', 'Details', 'Edit']) for s in sources.keys()]
    )

layout = html.Div(children=[
    html.H4(children='List of sources'),
    html.Div(id='table'),
    # dcc.Input(
    #     id="dummy",
    #     max=1.00,
    #     min=0.00,
    #     step=0.01,
    #     value=.5,
    #     type="number"
    # ),
    html.Div(id='dummy'),
])

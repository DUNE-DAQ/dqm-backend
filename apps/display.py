from dash import dcc
from dash import html
from dash.dependencies import Input, Output
import numpy as np

from app import app
import plotly.express as px
import pandas as pd

# From the list of sources get the available displays

from Platform import data

displays = data.get_displays()
print(displays)

streams = {}



# ls = []
# for i, d in enumerate(displays['testsource']):
#     print('Running')
#     stream = d
#     values = data.DataStream(d, data.DataSource('testsource')).get_data()
#     d = displays['testsource'][d]
#     if 'heatmap' in d:
#         @app.callback(
#             Output(f"graph-{i}", "figure"), 
#             [Input("medals", "value")])
#         def plot(cols):
#             fig = px.imshow([[1, 20, 30],
#                         [20, 1, 60],
#                         [30, 60, 1]])
#             return fig
#         ls.append(plot)
#     elif 'scatter' in d:
#         @app.callback(
#             Output(f"graph-{i}", "figure"), 
#             [Input("medals", "value")])
#         def plot(cols):
#             fig = px.scatter(x=np.arange(100),
#                               y=np.random.random(100),
#                               width=500)
#             return fig
#         ls.append(plot)
    
df = px.data.medals_wide(indexed=True)
sources = ['source 1', 'source 2']

# layout = html.Div(children=[
#      dcc.Checklist(
#         id='medals',
#         options=[{'label': x, 'value': x} 
#                  for x in df.columns],
#         value=df.columns.tolist(),
#     ),
#      # dcc.Graph(id='graph'),
#     ] +
#     [html.Div([
             
#         html.Div([dcc.Graph(id=f'graph-{i}')],
#                  className='four columns')
#         for i in range(len(ls))], className='row')
#     ]
#     # ] + [html.Div(id=f'graph-{i}') for i in range(len(displays))]
# )

def get_layout(pathname):
    comp = pathname.split('-')
    source_name = comp[1]
    display_name = comp[2]

    print('Running get_layout', pathname, source_name, display_name)
    # ds = data.DataStream('rmsm_display', data.DataSource('testsource'))
    # ndf = ds.get_data()
    # print(ndf)
    # dat = data.get_data_direct(source_name, display_name)

    @app.callback(
        Output(f"interm", "value"), 
        Input('medals', "value"))
    def get_data(_):
        print('Getting data')
        ds = data.DataStream('rmsm_display', data.DataSource('testsource'))
        ndf = ds.get_data()
        ret = {}
        # ret['data'] = '1 2 3'
        ret['data'] = ndf.to_dict()
        return ret

    ls = []
    i = 0
    @app.callback(
        Output(f"graph-{i}", "figure"), 
        Input('interm', "value"))
    def plot_scatter(dic):
        ndf = pd.DataFrame(dic['data'])
        # print('Ndf in plot_scatter', np.array(ndf.columns, dtype=np.float), np.array(ndf.values, dtype=np.float))
        fig = px.scatter(x=np.array(ndf.columns, dtype=np.float), y=np.array(ndf.values, dtype=np.float)[0])
        # fig = px.scatter(x=np.arange(100), y=np.random.random(100))
        return fig
    ls.append(plot_scatter)

    layout = html.Div(children=[
        dcc.Checklist(
            id='medals',
            options=[{'label': x, 'value': x} 
                    for x in df.columns],
            value=df.columns.tolist(),
        ),
        # dcc.Graph(id='graph'),
        ] +
        [html.Div([

            html.Div([dcc.Graph(id=f'graph-{i}')],
                    className='four columns')
            for i in range(len(ls))], className='row')
        ]
        +
        [html.Div(id='interm', style={'display': 'none'})]
    )
    return layout
    


# df_bar = pd.DataFrame({
#     "Fruit": ["Apples", "Oranges", "Bananas", "Apples", "Oranges", "Bananas"],
#     "Amount": [4, 1, 2, 2, 4, 5],
#     "City": ["SF", "SF", "SF", "Montreal", "Montreal", "Montreal"]
# })

# fig = px.bar(df_bar, x="Fruit", y="Amount", color="City", barmode="group")

# layout = html.Div(children=[
#     # All elements from the top of the page
#     html.Div([
#         html.Div([
#             html.H1(children='Hello Dash'),

#             html.Div(children='''
#                 Dash: A web application framework for Python.
#             '''),

#             dcc.Graph(
#                 id='graph1',
#                 figure=fig
#             ),  
#         ], className='six columns'),
#         html.Div([
#             html.H1(children='Hello Dash'),

#             html.Div(children='''
#                 Dash: A web application framework for Python.
#             '''),

#             dcc.Graph(
#                 id='graph2',
#                 figure=fig
#             ),  
#         ], className='six columns'),
#     ], className='row'),
#     # New Div for all elements in the new 'row' of the page
#     html.Div([
#         html.H1(children='Hello Dash'),

#         html.Div(children='''
#             Dash: A web application framework for Python.
#         '''),

#         dcc.Graph(
#             id='graph3',
#             figure=fig
#         ),  
#     ], className='row'),
# ])

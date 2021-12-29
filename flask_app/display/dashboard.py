from dash import dcc
from dash import html
from dash.dependencies import Input, Output
import numpy as np
import dash

from app import app
import plotly.express as px
import pandas as pd

# From the list of sources get the available displays

from Platform import data

def init_dashboard(server):
    dash_app = dash.Dash(
        server=server,
        routes_pathname_prefix='/dashapp/',
        external_stylesheets=[
            '/static/dist/css/styles.css',
        ]
    )

    # Create Dash Layout
    dash_app.layout = html.Div(id='dash-container')

    return dash_app.server


# streams = {}


# displays = data.get_displays()
# print(displays)

# layout = html.Div(children=[
#     ] +
#     [dcc.Link(s, href=f'/display-{s}') for s in displays]

    
#     # ] + [html.Div(id=f'graph-{i}') for i in range(len(displays))]
# )

# layout_dic = {}
# data_streams_dic = {}

def get_layout(pathname):
    if pathname in layout_dic:
        return layout_dic[pathname]
    # comp = pathname.split('-')
    # source_name = comp[1]
    # display_name = comp[2]

    print('Running get_layout')
    # ds = data.DataStream('rmsm_display', data.DataSource('testsource'))
    # ndf = ds.get_data()
    # print(ndf)
    # dat = data.get_data_direct(source_name, display_name)

    num_plots = len(displays[pathname.split('-')[1]])

    data_funcs = []
    plot_ls = []

    for i in range(num_plots):

        # ds = data.DataStream(f'rmsm_display{i}', data.DataSource('testsource'))
        # data_streams_dic[f'rmsm_display{i}'] = ds


        @app.callback(
            Output(f'interm-{pathname}-{i}', 'value'), 
            Input(f'interval-component', 'n_intervals'))
        def get_data(_, name=f'rmsm_display{i}'):
            print('Getting data')
            ds = data.DataStream(name, data.DataSource('testsource'))
            # ds = data_stream_dics
            ndf = ds.get_data()
            if ndf is None:
                return None
            ret = {}
            # ret['data'] = '1 2 3'
            ret['data'] = ndf.to_dict()
            # print(ret['data'])
            return ret
        data_funcs.append(get_data)

        @app.callback(
            Output(f'graph-{i}', 'figure'), 
            Input(f'interm-{pathname}-{i}', 'value'))
        def plot_scatter(dic):
            if dic is None:
                print('NONE')
                return px.scatter()
            print('Calling plot_scatter')
            ndf = pd.DataFrame(dic['data'])
            # print('Ndf in plot_scatter', np.array(ndf.columns, dtype=np.float), np.array(ndf.values, dtype=np.float))
            fig = px.scatter(x=np.array(ndf.columns, dtype=np.float), y=np.array(ndf.values, dtype=np.float)[0])
            # fig = px.scatter(x=np.arange(100), y=np.random.random(100))
            return fig
        plot_ls.append(plot_scatter)
        del i

    layout = html.Div(children=[
        ] +
        [html.Div([

            html.Div([dcc.Graph(id=f'graph-{i}')],
                    className='four columns')
            for i in range(len(plot_ls))], className='row')
        ]
        +
        [html.Div(id=f'interm-{pathname}-0', style={'display': 'none'})]
        +
        [html.Div(id=f'interm-{pathname}-1', style={'display': 'none'})]
        +
        [html.Div(id=f'interm-{pathname}-2', style={'display': 'none'})]
        +
        [dcc.Interval(
            id='interval-component',
            interval=2*1000, # in milliseconds
            n_intervals=0
        )]
                      
    )
    layout_dic[pathname] = layout
    return layout

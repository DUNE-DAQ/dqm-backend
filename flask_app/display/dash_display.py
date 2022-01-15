from dash import Dash
from dash.dependencies import Input, State, Output
from .Dash_fun import apply_layout_with_auth, load_object, save_object
from dash import dcc
from dash import html
from flask import request

from Platform import data
import pandas as pd
import plotly.express as px
import numpy as np


layout_dic = {}

def Add_Dash(server):
    
    external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
    app = Dash(server=server, url_base_pathname='/dash/', external_stylesheets=external_stylesheets)

    app.layout = html.Div([
        dcc.Location(id='url', refresh=False),
        html.Div(id='page-content')
    ])

    @app.callback(Output('page-content', 'children'),
                Input('url', 'pathname'))
    def get_layout(pathname):
        print(f'Running get_layout with {pathname=}')
        if pathname in layout_dic:
            print(f'{pathname} in layout_dic')
            return layout_dic[pathname]
        # comp = pathname.split('-')
        # source_name = comp[1]
        # display_name = comp[2]

        # ds = data.DataStream('rmsm_display', data.DataSource('testsource'))
        # ndf = ds.get_data()
        # print(ndf)
        # dat = data.get_data_direct(source_name, display_name)

        displays = data.DataSource(pathname.replace('/dash/', '')).get_displays()
        print(displays)
        num_plots = len(displays)

        data_funcs = []
        plot_ls = []

        for i, key in enumerate(displays):
            plottype = displays[key]

            # ds = data.DataStream(f'rmsm_display{i}', data.DataSource('testsource'))
            # data_streams_dic[f'rmsm_display{i}'] = ds
            @app.callback(
                Output(f'interm-{pathname}-{i}', 'value'), 
                Input(f'interval-component', 'n_intervals'))
            def get_data(_, name=f'{key}'):
                print('Getting data')
                ds = data.DataStream(name, data.DataSource('testsource'))
                # ds = data_stream_dics
                ndf = ds.get_data()
                if ndf is None:
                    return None
                ret = {}
                ret['data'] = ndf.to_dict()
                # print(ret['data'])
                return ret
            data_funcs.append(get_data)

            if plottype == 'scatter':
                @app.callback(
                    Output(f'{pathname}-graph-{i}', 'figure'),
                    Input(f'interm-{pathname}-{i}', 'value'))
                def plot_scatter(dic):
                    if dic is None:
                        print('NONE')
                        return px.scatter()
                    print('Calling plot_scatter')
                    ndf = pd.DataFrame(dic['data'])
                    fig = px.scatter(x=np.array(ndf.columns, dtype=np.float), y=np.array(ndf.values, dtype=np.float)[0],
                                     labels={'x': 'Channel number', 'y': 'RMS'})

                    fig.update_layout({'xaxis_title': 'Channel number', 'yaxis_title': 'RMS',
                                       'title': 'Induction plane',
                                       'plot_bgcolor': 'rgba(0, 0, 0, 0)'})

                    fig.update_xaxes(showgrid=False, zeroline=False)
                    fig.update_yaxes(showgrid=True, zeroline=False, gridwidth=1, gridcolor='black')
                    return fig
                plot_ls.append(plot_scatter)
            elif plottype == 'heatmap':
                @app.callback(
                    Output(f'{pathname}-graph-{i}', 'figure'),
                    Input(f'interm-{pathname}-{i}', 'value'))
                def plot_heatmap(dic):
                    if dic is None:
                        print('NONE')
                        return px.scatter()
                    print('Calling plot_heatmap')
                    ndf = pd.DataFrame(dic['data'])
                    # aspect=100 makes it a square, the default option 'equal' uses as much spacing as elements
                    # has each axis (i.e. a 200x100 array is plotted as a 200x100 rectangle in arbritrary units)
                    fig = px.imshow(ndf, aspect=100, origin='lower', labels={'x': 'Channel number', 'y': 'Time tick', 'color': 'ADC'})
                    fig.update_layout({'xaxis_title': 'Channel number', 'yaxis_title': 'Time ticks',
                                       'title': 'Induction plane',
                                       'plot_bgcolor': 'rgba(0, 0, 0, 0)'})
                    fig.update_xaxes(showgrid=False, zeroline=False)
                    fig.update_yaxes(showgrid=False, zeroline=False)
                    return fig
                plot_ls.append(plot_heatmap)
            del i

        layout = html.Div(
            [html.Div([dcc.Graph(id=f'{pathname}-graph-{i}')],
                            className='col-4') for i in range(num_plots)]
            +
            [dcc.Interval(
                            id='interval-component',
                            interval=10*1000, # in milliseconds
                            n_intervals=0),
            ]
            +
            [html.Div([html.Div(id=f'interm-{pathname}-{i}', style={'display': 'none'}) for i in range(num_plots)],)

            ],className='row')

        layout_dic[pathname] = layout
        return layout

    return app.server

# def apply_layout_with_auth(app, layout):
#     def serve_layout():
#         # if current_user and current_user.is_authenticated:
#         if True:
#             session_id = str(uuid.uuid4())
#             # clean_Dir_Store()
#             return html.Div([
#                 html.Div(session_id, id='session_id', style={'display': 'none'}),
#                 layout
#             ])
#         return html.Div('403 Access Denied')
    
#     app.config.suppress_callback_exceptions = True
#     app.layout = serve_layout

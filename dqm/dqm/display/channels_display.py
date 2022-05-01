from dash import Dash
from dash.dependencies import Input, State, Output
import dash_core_components as dcc
import dash_html_components as html
import dpd_components as dpd

import plotly.graph_objects as go

from display.models import SystemDisplay, OverviewDisplay

from Platform import utils
import pandas as pd
import plotly.express as px
import numpy as np

from django_plotly_dash import DjangoDash
from django_plotly_dash.consumers import send_to_pipe_channel
from datetime import datetime

from templates.models import SystemTemplate

import flask

def create_channel_display(partition, app_name):
    print(f'Calling create_channel_display {partition=} {app_name=}')

    app = DjangoDash(f'channel-{partition}-{app_name}')

    source = f'{partition}_{app_name}'
    stream = 'raw_display'

    @app.callback(
        Output(f'interm-channel', 'value'),
        Input(f'pipe-{partition}-{stream}', 'value'))
    def get_data(_):
        # print('Getting data', name, source)
        ds = utils.DataStream(stream, partition, app_name)
        res = ds.get_all_streams(stream_name=stream)
        if res is None:
            return None
        ndf, date = res
        ret = {}
        ret['data'] = ndf.to_dict()
        return (ret, date)

    @app.callback(
        Output(f'channel-graph', 'figure'),
        [Input(f'interm-channel', 'value'),
        Input(f'url', 'pathname')],
        [State(f'channel-graph', 'relayoutData')]
    )
    def plot_line(data={}, pathname=None, relayout_data=None):
        _, _, overview_name, app_name, channel = pathname.split('/')
        dic, date = data
        if dic is None:
            print('NONE')
            return px.line()
        ndf = pd.DataFrame(dic['data'])
        fig = px.line(y=ndf.loc[:, channel],
                        labels={'x': 'Time tick', 'y': 'ADC'})

        title = f'Channel {channel}'
        fig.update_layout({'xaxis_title': 'Time tick', 'yaxis_title': 'ADC',
                            'title': title,
                            'plot_bgcolor': 'rgba(0, 0, 0, 0)',
                            'margin': dict(l=20, r=20, t=80, b=20),
                            })

        fig.update_xaxes(showgrid=False, zeroline=False)
        fig.update_yaxes(showgrid=True, zeroline=False, gridwidth=.05, gridcolor='lightgrey')
        fig.add_annotation(xref='paper', yref='paper', x=.9, y=1.15,
                            text=f'Last updated at {datetime.strptime(date, "%y%m%d-%H%M%S").strftime("%H:%M:%S %d/%m/%Y")}',
                            showarrow=False)

        # if reference_run is not None:
        #     ds = utils.DataStream(stream, partition, app_name)
        #     ndf = pd.DataFrame(ds.get_data(reference_run)[0])
        #     fig.add_trace(go.Scatter(x=np.array(ndf.columns, dtype=np.float),
        #                                 y=np.array(ndf.values, dtype=np.float)[0],
        #                                 mode='lines',
        #                                 name=f'Run {reference_run}'))

        try:
            fig['layout']['xaxis']['range'] = [relayout_data['xaxis.range[0]'], relayout_data['xaxis.range[1]']]
            fig['layout']['yaxis']['range'] = [relayout_data['yaxis.range[0]'], relayout_data['yaxis.range[1]']]
        except:
            pass

        return fig

    pipe_ls = []
    pipe_ls.append(dpd.Pipe(id=f'pipe-{partition}-{stream}',
                            value='',
                            label=f'{source}-raw_display0',
                            channel_name=f'{source}-raw_display0'),)

    layout = html.Div(
        [dcc.Location(id='url', refresh=False)]
        +
        [html.Div([dcc.Graph(id=f'channel-graph')],
                        className=f'col-8')]
        +
        pipe_ls
        +
        [html.Div(id=f'interm-channel')]
        )

    app.layout = layout

    return app

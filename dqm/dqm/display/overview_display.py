from datetime import datetime
import numpy as np
import pandas as pd
from dash import Dash
from dash.dependencies import Input, State, Output
import dash_core_components as dcc
import dash_html_components as html
import dpd_components as dpd
import plotly.graph_objects as go
from django_plotly_dash import DjangoDash
from django_plotly_dash.consumers import send_to_pipe_channel
import plotly.express as px
from Platform import utils

from display.models import OverviewDisplay

layout_dic = {}

def create_overview_display(name):

    pathname = name

    print(f'Creating app with {name=}')
    app = DjangoDash(name)

    if not pathname:
        return html.Div()
    if '/' in pathname:
        pathname = pathname.split('/')[-1]
    if not pathname:
        return html.Div()
    if pathname in layout_dic:
        print(f'{pathname} in layout_dic')
        return layout_dic[pathname]

    @app.callback(
        Output(f'{pathname}-graph-{0}', 'figure'),
        [Input(f'pipe-partition-{pathname}-{i}', 'value') for i in range(3)])
    def plot_scatter(dic_0={}, dic_1={}, dic_2={}):
        print('Calling plot_scatter')
        # print(dic)
        # ndf = pd.DataFrame(dic['data'])
        fig = px.scatter(x=pd.to_datetime(dic_0['timestamp'], unit='s'), y=dic_0['data'],
                            labels={'x': 'Time', 'y': 'RMS'})
        fig['data'][0]['showlegend'] = True
        fig['data'][0]['name'] = 'Induction plane 1'

        fig.add_trace(go.Scatter(x=pd.to_datetime(dic_1['timestamp'], unit='s'),
                                    y=dic_1['data'],
                                    mode='markers',
                                    name=f'Induction plane 2'))

        fig.add_trace(go.Scatter(x=pd.to_datetime(dic_2['timestamp'], unit='s'),
                                    y=dic_2['data'],
                                    mode='markers',
                                    name=f'Collection plane'))

        fig.update_layout({'xaxis_title': 'Channel number', 'yaxis_title': 'RMS',
                            'plot_bgcolor': 'rgba(0, 0, 0, 0)',
                            })

        fig.update_xaxes(showgrid=False, zeroline=False)
        fig.update_yaxes(showgrid=True, zeroline=False, gridwidth=.05, gridcolor='lightgrey')
        # fig.add_annotation(xref='paper', yref='paper', x=.9, y=1.15,
        #                     text=f'Last updated at {datetime.now().strftime("%H:%M:%S %d/%m/%Y")}',
        #                     showarrow=False)

        return fig

    # @app.callback(
    #     Output(f'{pathname}-graph-{0}', 'extendData'),
    #     [Input(f'pipe-partition-{pathname}-{i}', 'value') for i in range(1)])
    #     # [State(f'{pathname}-graph-{0}', 'figure')])
    # def plot_scatter(dic_0={}):
    #     print('Calling plot_scatter')

    #     return (dict(x=[
    #         [pd.to_datetime(dic_0['timestamp'], unit='s')],
    #         # [pd.to_datetime(dic_1['timestamp'], unit='s')],
    #         # [pd.to_datetime(dic_2['timestamp'], unit='s')],
    #     ],
    #         y=[
    #         [dic_0['data']],
    #         # [dic_1['data']],
    #         # [dic_2['data']]
    #     ]),
    #         # [0, 1, 2]
    #         [0]
    #     )

    #     return fig

    display = OverviewDisplay.objects.filter(name=pathname)[0]
    partition = display.partition

    runs = utils.get_all_runs(partition)
    current_run = utils.get_current_run(partition)

    apps = utils.get_apps_for_partition(partition)

    layout = html.Div(
        [html.Div(children=f'Overview for partition {partition}', className='h1')]
        +
        [html.Div(children=f'The current run number is {current_run}', className='h1')]
        +
        [html.Details(children=
        [html.Summary(children=f'Receiving data from the following apps', className='h1')]
        +
        # [html.Div(children='<ul class="list-group">' + ''.join([f'<li class="list-group-item">{app}</li>' for apps in apps]) + '</ul>')]
        # [html.Ul(children=['<li class="list-group-item">{app}</li>' for apps in apps])]
        [html.Div(children=[html.A(f'{app}', href=f'/overview/{pathname}/{app}', className="list-group-item list-group-item-action") for app in apps], className="list-group")]
                        )]
        +
        [html.Div(children=f'Mean value of the RMS (for all channels) for each plane', className='h1')]
        +
        # [    dcc.Graph(
        #         id=f'{pathname}-graph-{0}',
        #         figure=dict(
        #             data=[{'x': [],
        #                    'y': [],
        #                    'mode':'markers',
        #                    'name': 'Induction plane 1',
        #                    },
        #                   # {'x': [],
        #                   #  'y': [],
        #                   #  'mode': 'markers',
        #                   #  'name': 'Induction plane 2',
        #                   #  },
        #                   # {'x': [],
        #                   #  'y': [],
        #                   #  'mode': 'markers',
        #                   #  'name': 'Collection plane',
        #                   #  },
        #                   ],
        #             layout={'xaxis': {'title': 'Date'},
        #                     'yaxis': {'title': 'Mean RMS'}}
        #         )
        #     ),
        # ]
        [dcc.Graph(id=f'{pathname}-graph-{0}')]
        +
        [dpd.Pipe(id=f'pipe-partition-{pathname}-{i}',
                    value={'data': []},
                    label=f'time_evol_{i}',
                    channel_name=f'time_evol_{i}')
                    for i in range(3)]

        )

    layout_dic[pathname] = layout

    app.layout = layout

    return app

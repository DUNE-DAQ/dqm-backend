from datetime import datetime
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import plotly.subplots as subplots
from dash import Dash
from dash.dependencies import Input, State, Output
import dash_core_components as dcc
import dash_html_components as html
from django_plotly_dash import DjangoDash
from django_plotly_dash.consumers import send_to_pipe_channel
import dpd_components as dpd
from django.core.cache import cache

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

    display = OverviewDisplay.objects.filter(name=pathname)[0]
    partition = display.partition
    source = partition + '_dqm0_ru'

    @app.callback(
        Output(f'{pathname}-graph-{0}', 'figure'),
        [Input(f'pipe-partition-{pathname}-{i}', 'value') for i in range(3)],
        [State(f'{pathname}-graph-{0}', 'relayoutData')]
    )
    def plot_scatter(dic_0={}, dic_1={}, dic_2={}, relayout_data=None):

        if not dic_0 and not dic_1 and not dic_2:
            dic_0 = utils.get_last_result(partition, 'dqm0_ru', 'std-0')
            dic_1 = utils.get_last_result(partition, 'dqm0_ru', 'std-1')
            dic_2 = utils.get_last_result(partition, 'dqm0_ru', 'std-2')
            cache.set(name, [dic_0, dic_1, dic_2], None)

        previous_data_0, previous_data_1, previous_data_2 = cache.get(name)
        data_0 = pd.concat((previous_data_0, pd.DataFrame(dic_0)))
        data_1 = pd.concat((previous_data_1, pd.DataFrame(dic_1)))
        data_2 = pd.concat((previous_data_2, pd.DataFrame(dic_2)))

        fig = px.scatter(x=pd.to_datetime(data_0['timestamp'], unit='s', utc=True), y=data_0['values'],
                            labels={'x': 'Time', 'y': 'RMS'})

        fig['data'][0]['showlegend'] = True
        fig['data'][0]['name'] = 'Induction plane 1'

        fig.add_trace(go.Scatter(x=pd.to_datetime(data_1['timestamp'], unit='s', utc=True),
                                    y=data_1['values'],
                                    mode='markers',
                                    name=f'Induction plane 2'))

        fig.add_trace(go.Scatter(x=pd.to_datetime(data_2['timestamp'], unit='s', utc=True),
                                    y=data_2['values'],
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

        try:
            fig['layout']['xaxis']['range'] = [relayout_data['xaxis.range[0]'], relayout_data['xaxis.range[1]']]
            fig['layout']['yaxis']['range'] = [relayout_data['yaxis.range[0]'], relayout_data['yaxis.range[1]']]
        except (KeyError, TypeError):
            pass


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

    for i in range(3):
        @app.callback(
                    Output(f'interm-{pathname}-{i}', 'value'),
                    [Input(f'pipe-rmsm-{pathname}-{i}', 'value')])
        def get_data(_, source=source, stream_name='std0'):
            print('Getting data', stream_name, source)
            ds = utils.DataStream(stream_name, partition, 'dqm0_ru')
            # ds = data_stream_dics
            res = ds.get_data()
            if res is None:
                return None
            ndf, date = res
            ret = {}
            ret['data'] = ndf.to_dict()
            return (ret, date)


    @app.callback(
        Output(f'{pathname}-graph-{0}-run-comparison', 'figure'),
        [Input(f'interm-{pathname}-{i}', 'value') for i in range(3)],
        [State(f'{pathname}-graph-{0}-run-comparison', 'relayoutData')]
    )
    def plot_run_comparison(dic_0={}, dic_1={}, dic_2={}, relayout_data=None):

        if not cache.get(f'plot-comparison-{name}'):
            runs = sorted(utils.get_ordered_runs(partition))
            if len(runs) > 1:
                previous_run = runs[-2][1]

                dic_0 = utils.get_average(partition, 'dqm0_ru', 'std-0', previous_run)
                dic_1 = utils.get_average(partition, 'dqm0_ru', 'std-1', previous_run)
                dic_2 = utils.get_average(partition, 'dqm0_ru', 'std-2', previous_run)
            else:
                dic_0 = pd.DataFrame()
                dic_1 = pd.DataFrame()
                dic_2 = pd.DataFrame()

            cache.set(f'plot-comparison-{name}', [dic_0, dic_1, dic_2], None)

        previous_data_0, previous_data_1, previous_data_2 = cache.get(f'plot-comparison-{name}')

        fig = subplots.make_subplots(rows=2, cols=1)

        # fig['data'][0]['showlegend'] = True
        # fig['data'][0]['name'] = 'Induction plane 1'

        fig.update_layout({'xaxis_title': 'Channel number', 'yaxis_title': 'RMS',
                            'plot_bgcolor': 'rgba(0, 0, 0, 0)',
                            })

        fig.update_xaxes(showgrid=False, zeroline=False)
        fig.update_yaxes(showgrid=True, zeroline=False, gridwidth=.05, gridcolor='lightgrey')
        # fig.add_annotation(xref='paper', yref='paper', x=.9, y=1.15,
        #                     text=f'Last updated at {datetime.now().strftime("%H:%M:%S %d/%m/%Y")}',
        #                     showarrow=False)

        for data in [previous_data_0, previous_data_1, previous_data_2]:
            fig.add_trace(go.Scatter(x=data.columns,
                                     y=data.values.flatten(),
                                     mode='markers',
                                     name=f'Induction plane 1'), row=1, col=1)

        if len(dic_0) > 1:
            dic_0 = dic_0[0]['data']
        dic_0 = pd.DataFrame(dic_0)
        dic_0.columns = dic_0.columns.astype('int64')
        ratio_0 = pd.DataFrame(dic_0).reset_index(drop=True).div(previous_data_0)
        fig.add_trace(go.Scatter(x=ratio_0.columns, y=ratio_0.values.flatten(), mode='markers',
                                 name=f'Induction plane 2'), row=2, col=1)

        # try:
        #     fig['layout']['xaxis']['range'] = [relayout_data['xaxis.range[0]'], relayout_data['xaxis.range[1]']]
        #     fig['layout']['yaxis']['range'] = [relayout_data['yaxis.range[0]'], relayout_data['yaxis.range[1]']]
        # except (KeyError, TypeError):
        #     print('Hello')
        #     pass

        return fig

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
        [html.Div(dcc.Graph(id=f'{pathname}-graph-{0}'), className='col-8')]
        +
        [html.Div(children=f'Comparison of the RMS between the current run and the previous run', className='h1')]
        +
        [html.Div(dcc.Graph(id=f'{pathname}-graph-{0}-run-comparison'), className='col-8')]
        +
        [dpd.Pipe(id=f'pipe-partition-{pathname}-{i}',
                    value={},
                    label=f'time_evol_{i}',
                    channel_name=f'time_evol_{i}')
                    for i in range(3)]
        +
        [dpd.Pipe(id=f'pipe-rmsm-{pathname}-{i}',
                    value={},
                    label=f'{source}-std{i}',
                    channel_name=f'{source}-std{i}')
                    for i in range(3)]
        +
        [html.Div(id=f'interm-{pathname}-{i}') for i in range(3)]

        )

    layout_dic[pathname] = layout

    app.layout = layout

    return app

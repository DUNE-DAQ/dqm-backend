
from dash import Dash
from dash.dependencies import Input, State, Output
import dash_core_components as dcc
import dash_html_components as html
import dpd_components as dpd

import plotly.graph_objects as go

from display.models import Display


from Platform import utils
import pandas as pd
import plotly.express as px
import numpy as np

from django_plotly_dash import DjangoDash
from django_plotly_dash.consumers import send_to_pipe_channel
from datetime import datetime


layout_dic = {}

def create_overview_display(name):

    # app = Dash(server=server, url_base_pathname='/dash/')
    print(f'Creating app with {name=}')
    app = DjangoDash(name)

    app.layout = html.Div([
        dcc.Location(id='url', refresh=False),
        html.Div(id='page-content'),
    ])

    @app.callback(Output('page-content', 'children'),
                    Input('url', 'pathname'), prevent_inital_call=False)
    def get_layout(pathname):
        print(f'Running get_layout with {pathname=}')
        if '/' in pathname:
            pathname = pathname.split('/')[-1]
        if not pathname:
            return html.Div()
        if pathname in layout_dic:
            print(f'{pathname} in layout_dic')
            return layout_dic[pathname]

        @app.callback(
            Output(f'{pathname}-graph-{0}', 'figure'),
            [Input(f'pipe-partition-{pathname}-{0}', 'value')])
        def plot_scatter(dic={}):
            print(dic)
            # ndf = pd.DataFrame(dic['data'])
            fig = px.scatter(x=pd.to_datetime(dic['timestamp'], unit='s'), y=dic['data'],
                            labels={'x': 'Time', 'y': 'RMS'})

            # fig.update_layout({'xaxis_title': 'Channel number', 'yaxis_title': 'RMS',
            #                     'title': f'Induction plane {int(stream[-1]) + 1}' if int(stream[-1]) < 2 else 'Collection plane',
            #                     'plot_bgcolor': 'rgba(0, 0, 0, 0)',
            #                     })

            # fig.update_xaxes(showgrid=False, zeroline=False)
            # fig.update_yaxes(showgrid=True, zeroline=False, gridwidth=.05, gridcolor='lightgrey')
            # fig.add_annotation(xref='paper', yref='paper', x=.9, y=1.15,
            #                     text=f'Last updated at {datetime.now().strftime("%H:%M:%S %d/%m/%Y")}',
            #                     showarrow=False)

            return fig


        apps = utils.get_apps_for_partition(pathname)

        runs = utils.get_all_runs(pathname)
        current_run = max(runs)

        layout = html.Div(
            [html.Div(children=f'Overview for partition {name}', className='h1')]
            +
            [html.Div(children=f'The current run number is {current_run}', className='h1')]
            +
            [html.Details(children=
            [html.Summary(children=f'Receiving data from the following apps', className='h1')]
            +
            # [html.Div(children='<ul class="list-group">' + ''.join([f'<li class="list-group-item">{app}</li>' for apps in apps]) + '</ul>')]
            # [html.Ul(children=['<li class="list-group-item">{app}</li>' for apps in apps])]
            [html.Div(children=[html.A(f'{app}', href=f'/displays/{pathname}_{app}', className="list-group-item list-group-item-action") for app in apps], className="list-group")]
                          )]
            +
            [html.Div(children=f'This is an interesting plot', className='h1')]
            +
            [dcc.Graph(id=f'{pathname}-graph-{0}')]
            +
            [dpd.Pipe(id=f'pipe-partition-{pathname}-{0}',
                        value={'data': []},
                        label=f'time_evol',
                        channel_name=f'time_evol'),
                        ]
            
            )

        layout_dic[pathname] = layout
        return layout

    return app

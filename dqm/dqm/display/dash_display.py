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


layout_dic = {}

def create_display(overview_name, name):
    print(f'Calling create_display with args {overview_name} {name}')

    print(f'Creating app with {name=}')
    app = DjangoDash(overview_name + name)

    app.layout = html.Div([
        dcc.Location(id='url', refresh=False),
        html.Div(id='page-content'),
    ])

    @app.callback(Output('page-content', 'children'),
                    Input('url', 'pathname'), prevent_inital_call=False)
    def get_layout(pathname):
        print(f'Running get_layout with {pathname=}')
        if '/' in pathname:
            _, _, overview_name, app_name = pathname.split('/')
            print(f'overview_name set to {overview_name} and app_name set to {app_name}')
            # pathname = pathname.split('/')[-1]
        if not pathname:
            return html.Div()
        if (overview_name, app_name) in layout_dic:
            print(f'{(overview_name, app_name)} in layout_dic')
            return layout_dic[(overview_name, app_name)]

        obj = OverviewDisplay.objects.filter(name=overview_name)[0]
        partition = obj.partition


        # displays = utils.DataSource(pathname.replace('/dash/', '')).get_displays()
        # displays = SystemDisplay.objects.filter(name=pathname.replace('/dash/', ''))[0].data
        displays = SystemTemplate.objects.filter()[0].display
        displays = {f'{partition}_{app_name}': displays}

        num_plots = sum([len(displays[s]) for s in displays])

        data_funcs = []
        plot_ls = []
        sizes = []

        i = -1
        for source in displays:
            pos_keys = sorted([(val['pos'] if 'pos' in val else i, key) for key,val in displays[source].items()])
            for pos, key in pos_keys:
                i += 1
                plottype = displays[source][key]['plot_type']
                sizes.append(displays[source][key]['size'])

                @app.callback(
                    Output(f'interm-{pathname}-{i}', 'value'), 
                    Input(f'pipe-{source}-{key}', 'value'))
                    # Input(f'interval-component', 'n_intervals'))
                def get_data(_, name=f'{key}', source=source):
                    print('Getting data', name, source)
                    ds = utils.DataStream(name, utils.DataSource(source))
                    # ds = data_stream_dics
                    ndf = ds.get_data()
                    if ndf is None:
                        return None
                    ret = {}
                    ret['data'] = ndf.to_dict()
                    return ret
                data_funcs.append(get_data)

                if plottype == 'scatter':
                    @app.callback(
                        Output(f'{pathname}-graph-{i}', 'figure'),
                       [Input(f'interm-{pathname}-{i}', 'value'),
                        Input('run-dropdown', 'value'),
                        Input('rewind-dropdown', 'value')])
                    def plot_scatter(dic={}, args=None, rewind_run=None, source=source, stream=key):
                        reference_run = args
                        print('PLOT SCATTER', reference_run)
                        if dic is None:
                            print('NONE')
                            return px.scatter()
                        print('Calling plot_scatter')
                        ndf = pd.DataFrame(dic['data'])
                        fig = px.scatter(x=np.array(ndf.columns, dtype=np.float), y=np.array(ndf.values, dtype=np.float)[0],
                                        labels={'x': 'Channel number', 'y': 'RMS'})

                        fig.update_layout({'xaxis_title': 'Channel number', 'yaxis_title': 'RMS',
                                           'title': f'Induction plane {int(stream[-1]) + 1}' if int(stream[-1]) < 2 else 'Collection plane',
                                           'plot_bgcolor': 'rgba(0, 0, 0, 0)',
                                           })

                        fig.update_xaxes(showgrid=False, zeroline=False)
                        fig.update_yaxes(showgrid=True, zeroline=False, gridwidth=.05, gridcolor='lightgrey')
                        fig.add_annotation(xref='paper', yref='paper', x=.9, y=1.15,
                                           text=f'Last updated at {datetime.now().strftime("%H:%M:%S %d/%m/%Y")}',
                                           showarrow=False)
                        if reference_run is not None:
                            ds = utils.DataStream(stream, utils.DataSource(source))
                            ndf = pd.DataFrame(ds.get_data(reference_run))
                            fig.add_trace(go.Scatter(x=np.array(ndf.columns, dtype=np.float),
                                                     y=np.array(ndf.values, dtype=np.float)[0],
                                                     mode='markers',
                                                     name=f'Run {reference_run}'))

                        return fig
                    plot_ls.append(plot_scatter)
                elif plottype == 'heatmap':
                    @app.callback(
                        Output(f'{pathname}-graph-{i}', 'figure'),
                        [Input(f'interm-{pathname}-{i}', 'value'),
                         Input('rewind-dropdown', 'value')])
                    def plot_heatmap(dic={}, rewind_run=None, source=source, stream=key):
                        if dic is None:
                            print('NONE')
                            return px.scatter()
                        print('Calling plot_heatmap')
                        ndf = pd.DataFrame(dic['data'])
                        # aspect=100 makes it a square, the default option 'equal' uses as much spacing as elements
                        # has each axis (i.e. a 200x100 array is plotted as a 200x100 rectangle in arbritrary units)
                        fig = px.imshow(ndf, aspect=100, origin='lower', labels={'x': 'Channel number', 'y': 'Time tick', 'color': 'ADC'})
                        fig.update_layout({'xaxis_title': 'Channel number', 'yaxis_title': 'Time ticks',
                                           'title': f'Induction plane {int(stream[-1]) + 1}' if int(stream[-1]) < 2 else 'Collection plane',
                                        'plot_bgcolor': 'rgba(0, 0, 0, 0)'})
                        fig.update_xaxes(showgrid=False, zeroline=False)
                        fig.update_yaxes(showgrid=False, zeroline=False)
                        fig.add_annotation(xref='paper', yref='paper', x=.9, y=1.15,
                                           text=f'Last updated at {datetime.now().strftime("%H:%M:%S %d/%m/%Y")}',
                                           showarrow=False)
                        return fig
                    plot_ls.append(plot_heatmap)
                elif plottype == 'line':
                    @app.callback(
                        Output(f'{pathname}-graph-{i}', 'figure'),
                        [Input(f'interm-{pathname}-{i}', 'value'),
                         Input('rewind-dropdown', 'value')])
                    def plot_line(dic={}, rewind_run=None, source=source, stream=key):
                        if dic is None:
                            print('NONE')
                            return px.scatter()
                        print('Calling plot_scatter')
                        ndf = pd.DataFrame(dic['data'])
                        fig = px.line(x=np.array(ndf.columns, dtype=np.float), y=np.array(ndf.values, dtype=np.float)[0],
                                        labels={'x': 'Frequency [Hz]', 'y': 'abs(fft(ADC))'})

                        if int(stream[-1]) < 2:
                            title = f'Induction plane {int(stream[-1]) + 1}'
                        elif int(stream[-1]) < 3:
                            title = f'Collection plane'
                        else:
                            title = 'All planes'
                        fig.update_layout({'xaxis_title': 'Frequency [Hz]', 'yaxis_title': 'abs(fft(ADC))',
                                           'title': title,
                                           'plot_bgcolor': 'rgba(0, 0, 0, 0)',
                                           })

                        fig.update_xaxes(showgrid=False, zeroline=False)
                        fig.update_yaxes(showgrid=True, zeroline=False, gridwidth=.05, gridcolor='lightgrey')
                        fig.add_annotation(xref='paper', yref='paper', x=.9, y=1.15,
                                           text=f'Last updated at {datetime.now().strftime("%H:%M:%S %d/%m/%Y")}',
                                           showarrow=False)
                        return fig
                    plot_ls.append(plot_line)


        pipe_ls = []
        i = -1
        for source in displays:
            for key in displays[source]:
                i += 1
                pipe_ls.append(dpd.Pipe(id=f'pipe-{source}-{key}',
                                        value='',
                                        label=f'{source}-{key}',
                                        channel_name=f'{source}-{key}'),)

        run_numbers = utils.get_runs(list(displays.keys())[0])

        layout = html.Div(
            [html.Div([dcc.Graph(id=f'{pathname}-graph-{i}')],
                            className=f'col-{sizes[i]}') for i in range(num_plots)]
            +
            [dcc.Interval(
                            id='interval-component',
                            interval=5*1000, # in milliseconds
                            ),
            ]
            +
            pipe_ls
            +
            [html.Div(id=f'interm-{pathname}-{i}') for i in range(num_plots)]
            +
            [dcc.Dropdown(
                id='run-dropdown',
                options=[{'label': f'Run {n}', 'value': n}
                         for n in run_numbers],
                value=None,
                className='col-4'
                )
             ]
            +
            [dcc.Dropdown(
                id='rewind-dropdown',
                options=[{'label': f'Run {n}', 'value': n}
                         for n in run_numbers],
                value=None,
                className='col-4'
                )
             ]
            ,className='row')

        layout_dic[(overview_name, app_name)] = layout
        return layout
    return app

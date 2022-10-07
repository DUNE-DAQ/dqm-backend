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

    app = DjangoDash(overview_name + name)

    app_name = name
    pathname = f'{overview_name}_{name}'

    if (overview_name, app_name) in layout_dic:
        print(f'{(overview_name, app_name)} in layout_dic')
        return layout_dic[(overview_name, app_name)]

    obj = OverviewDisplay.objects.filter(name=overview_name)[0]
    partition = obj.partition
    displays = obj.data
    num_plots = sum([len(displays[s]) for s in displays])

    data_funcs = []
    plot_ls = []
    sizes = []

    i = -1
    for source in displays:
        pos_keys = sorted([(data['pos'] if 'pos' in data else i, stream) for stream,data in displays[source].items()])
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
                ds = utils.DataStream(name, partition, app_name)
                # ds = data_stream_dics
                res = ds.get_data()
                if res is None:
                    return None
                ndf, date = res
                ret = {}
                ret['data'] = ndf.to_dict()
                return (ret, date)
            data_funcs.append(get_data)

            if plottype == 'scatter':
                @app.callback(
                    Output(f'{pathname}-graph-{i}', 'figure'),
                    [Input(f'interm-{pathname}-{i}', 'value'),
                    Input('run-dropdown', 'value'),
                    Input('rewind-dropdown', 'value'),
                    ],
                    [State(f'{pathname}-graph-{i}', 'relayoutData')]
                )
                def plot_scatter(data={}, reference_run=None, rewind_run=None, relayout_data=None, source=source, stream=key):
                    print('PLOT SCATTER', reference_run)
                    dic, date = data
                    if dic is None:
                        print('Calling PLOT SCATTER returned no data')
                        return px.scatter()
                    print('Calling plot_scatter')
                    ndf = pd.DataFrame(dic['data'])
                    fig = px.scatter(x=np.array(ndf.columns, dtype=np.float), y=np.array(ndf.values, dtype=np.float)[0],
                                    labels={'x': 'Channel number', 'y': 'RMS'})

                    fig.update_layout({'xaxis_title': 'Channel number', 'yaxis_title': 'RMS',
                                        'title': f'Induction plane {int(stream[-1]) + 1}' if int(stream[-1]) < 2 else 'Collection plane',
                                        'plot_bgcolor': 'rgba(0, 0, 0, 0)',
                                        'margin': dict(l=20, r=20, t=80, b=20),
                                        })

                    fig.update_xaxes(showgrid=False, zeroline=False)
                    fig.update_yaxes(showgrid=True, zeroline=False, gridwidth=.05, gridcolor='lightgrey')
                    fig.add_annotation(xref='paper', yref='paper', x=.9, y=1.15,
                                        text=f'Last updated at {datetime.strptime(date, "%y%m%d-%H%M%S").strftime("%H:%M:%S %d/%m/%Y")}',
                                        showarrow=False)
                    if reference_run is not None:
                        print('reference_run', reference_run, stream, partition, app_name)
                        ds = utils.DataStream(stream, partition, app_name)
                        ndf = pd.DataFrame(ds.get_data(reference_run)[0])
                        fig.add_trace(go.Scatter(x=np.array(ndf.columns, dtype=np.float),
                                                    y=np.array(ndf.values, dtype=np.float)[0],
                                                    mode='markers',
                                                    name=f'Run {reference_run}'))

                    try:
                        fig['layout']['xaxis']['range'] = [relayout_data['xaxis.range[0]'], relayout_data['xaxis.range[1]']]
                        fig['layout']['yaxis']['range'] = [relayout_data['yaxis.range[0]'], relayout_data['yaxis.range[1]']]
                    except (KeyError, TypeError):
                        pass

                    return fig
                plot_ls.append(plot_scatter)
            elif plottype == 'heatmap':
                @app.callback(
                    Output(f'{pathname}-graph-{i}', 'figure'),
                    [Input(f'interm-{pathname}-{i}', 'value'),
                        Input('rewind-dropdown', 'value')],
                    [State(f'{pathname}-graph-{i}', 'relayoutData')]
                )
                def plot_heatmap(data={}, rewind_run=None, relayout_data=None, source=source, stream=key):
                    print('PLOT HEATMAP')
                    dic, date = data
                    if dic is None:
                        print('HEATMAP NONE')
                        return px.scatter()
                    print('Calling plot_heatmap')
                    ndf = pd.DataFrame(dic['data'])
                    # Subtract the baseline, the median for all frames
                    ndf -= ndf.mean(axis=0)

                    # aspect=100 makes it a square, the default option 'equal' uses as much spacing as elements
                    # has each axis (i.e. a 200x100 array is plotted as a 200x100 rectangle in arbritrary units)
                    fig = px.imshow(ndf, aspect=100, origin='lower', labels={'x': 'Channel number', 'y': 'Time tick', 'color': 'ADC-baseline'})
                    fig.update_layout({'xaxis_title': 'Channel number', 'yaxis_title': 'Time ticks',
                                        'title': f'Induction plane {int(stream[-1]) + 1}' if int(stream[-1]) < 2 else 'Collection plane',
                                        'plot_bgcolor': 'rgba(0, 0, 0, 0)',
                                        'margin': dict(l=20, r=20, t=80, b=20),
                                        })
                    fig.update_xaxes(showgrid=False, zeroline=False)
                    fig.update_yaxes(showgrid=False, zeroline=False)
                    fig.add_annotation(xref='paper', yref='paper', x=.9, y=1.15,
                                        text=f'Last updated at {datetime.strptime(date, "%y%m%d-%H%M%S").strftime("%H:%M:%S %d/%m/%Y")}',
                                        showarrow=False)
                    try:
                        fig['layout']['xaxis']['range'] = [relayout_data['xaxis.range[0]'], relayout_data['xaxis.range[1]']]
                        fig['layout']['yaxis']['range'] = [relayout_data['yaxis.range[0]'], relayout_data['yaxis.range[1]']]
                    except (KeyError, TypeError):
                        pass

                    return fig
                plot_ls.append(plot_heatmap)
            elif plottype == 'line':
                @app.callback(
                    Output(f'{pathname}-graph-{i}', 'figure'),
                    [Input(f'interm-{pathname}-{i}', 'value'),
                        Input('run-dropdown', 'value'),
                        Input('rewind-dropdown', 'value')],
                    [State(f'{pathname}-graph-{i}', 'relayoutData')]
                )
                def plot_line(data={}, reference_run=None, rewind_run=None, relayout_data=None, source=source, stream=key):
                    dic, date = data
                    if dic is None:
                        print('NONE')
                        return px.scatter()
                    print('Calling plot_scatter')
                    ndf = pd.DataFrame(dic['data'])
                    fig = px.line(x=np.array(ndf.columns, dtype=np.float), y=np.array(ndf.values, dtype=np.float)[0],
                                    labels={'x': 'Frequency [Hz]', 'y': 'abs(fft(ADC))'}, log_y=True)

                    if int(stream[-1]) < 2:
                        title = f'Induction plane {int(stream[-1]) + 1}'
                    elif int(stream[-1]) < 3:
                        title = f'Collection plane'
                    else:
                        title = 'All planes'
                    fig.update_layout({'xaxis_title': 'Frequency [Hz]', 'yaxis_title': 'abs(fft(ADC))',
                                        'title': title,
                                        'plot_bgcolor': 'rgba(0, 0, 0, 0)',
                                        'margin': dict(l=20, r=20, t=80, b=20),
                                        })

                    fig.update_xaxes(showgrid=False, zeroline=False)
                    fig.update_yaxes(showgrid=True, zeroline=False, gridwidth=.05, gridcolor='lightgrey')
                    fig.add_annotation(xref='paper', yref='paper', x=.9, y=1.15,
                                        text=f'Last updated at {datetime.strptime(date, "%y%m%d-%H%M%S").strftime("%H:%M:%S %d/%m/%Y")}',
                                        showarrow=False)

                    if reference_run is not None:
                        ds = utils.DataStream(stream, partition, app_name)
                        ndf = pd.DataFrame(ds.get_data(reference_run)[0])
                        fig.add_trace(go.Scatter(x=np.array(ndf.columns, dtype=np.float),
                                                    y=np.array(ndf.values, dtype=np.float)[0],
                                                    mode='lines',
                                                    name=f'Run {reference_run}'))

                    try:
                        fig['layout']['xaxis']['range'] = [relayout_data['xaxis.range[0]'], relayout_data['xaxis.range[1]']]
                        fig['layout']['yaxis']['range'] = [relayout_data['yaxis.range[0]'], relayout_data['yaxis.range[1]']]
                    except (KeyError, TypeError):
                        pass

                    return fig
                plot_ls.append(plot_line)


    @app.callback(
        Output(f'run-list', 'value'),
        [Input('run-dropdown', 'n_clicks'),
            Input('run-button', 'n_clicks')])
    def get_display_run_list():
        changed_id = [p['prop_id'] for p in callback_context.triggered][0]
        run_list


    pipe_ls = []
    i = -1
    for source in displays:
        for key in displays[source]:
            i += 1
            pipe_ls.append(dpd.Pipe(id=f'pipe-{source}-{key}',
                                    value='',
                                    label=f'{source}-{key}',
                                    channel_name=f'{source}-{key}'),)

    run_numbers = utils.get_runs(partition, app_name)

    layout = html.Div(
        [html.Div([dcc.Graph(id=f'{pathname}-graph-{i}')],
                        className=f'col-{sizes[i]}') for i in range(num_plots)]
        +
        pipe_ls
        +
        [html.Div(id=f'interm-{pathname}-{i}') for i in range(num_plots)]
        +
        [html.Div('Plot options', className='h2')]
        +
        [html.Div('Add another run to the fourier and RMS plots')]
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
        # [html.Button('Button 1', id='run-button', n_clicks=0)]
        # +
        [html.Div('Rewind to a previous run')]
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

    app.layout = layout

    return app

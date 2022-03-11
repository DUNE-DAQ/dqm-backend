from dash import Dash
from dash.dependencies import Input, State, Output
import dash_core_components as dcc
import dash_html_components as html
import dpd_components as dpd

from .models import Display

from Platform import data
import pandas as pd
import plotly.express as px
import numpy as np

from django_plotly_dash import DjangoDash

layout_dic = {}


def create_display(name):

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

        # displays = data.DataSource(pathname.replace('/dash/', '')).get_displays()
        displays = Display.objects.filter(name=pathname.replace('/dash/', ''))[0].data
        num_plots = sum([len(displays[s]) for s in displays])

        data_funcs = []
        plot_ls = []

        i = -1
        for source in displays:
            for key in displays[source]:
                i += 1
                plottype = displays[source][key]

                @app.callback(
                    Output(f'interm-{pathname}-{i}', 'value'), 
                    Input(f'interval-component', 'n_intervals'))
                def get_data(_, name=f'{key}', source=source):
                    print('Getting data', name, source)
                    ds = data.DataStream(name, data.DataSource(source))
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
                        fig.update_yaxes(showgrid=True, zeroline=False, gridwidth=.05, gridcolor='lightgrey')
                        fig.add_annotation(xref='paper', yref='paper', x=.9, y=1.15,
                                           text=f'Last updated at {datetime.now().strftime("%H:%M:%S %d/%m/%Y")}',
                                           showarrow=False)
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
                        fig.add_annotation(xref='paper', yref='paper', x=.9, y=1.15,
                                           text=f'Last updated at {datetime.now().strftime("%H:%M:%S %d/%m/%Y")}',
                                           showarrow=False)
                        return fig
                    plot_ls.append(plot_heatmap)
                elif plottype == 'line':
                    @app.callback(
                        Output(f'{pathname}-graph-{i}', 'figure'),
                        Input(f'interm-{pathname}-{i}', 'value'))
                    def plot_line(dic):
                        if dic is None:
                            print('NONE')
                            return px.scatter()
                        print('Calling plot_scatter')
                        ndf = pd.DataFrame(dic['data'])
                        fig = px.line(x=np.array(ndf.columns, dtype=np.float), y=np.array(ndf.values, dtype=np.float)[0],
                                        labels={'x': 'Frequency [Hz]', 'y': 'abs(fft(ADC))'})

                        fig.update_layout({'xaxis_title': 'Frequency [Hz]', 'yaxis_title': 'abs(fft(ADC))',
                                           'title': 'Induction plane',
                                           'plot_bgcolor': 'rgba(0, 0, 0, 0)',
                                           })

                        fig.update_xaxes(showgrid=False, zeroline=False)
                        fig.update_yaxes(showgrid=True, zeroline=False, gridwidth=.05, gridcolor='lightgrey')
                        fig.add_annotation(xref='paper', yref='paper', x=.9, y=1.15,
                                           text=f'Last updated at {datetime.now().strftime("%H:%M:%S %d/%m/%Y")}',
                                           showarrow=False)
                        return fig
                    plot_ls.append(plot_line)

        layout = html.Div(
            [html.Div([dcc.Graph(id=f'{pathname}-graph-{i}')],
                            className='col-4') for i in range(num_plots)]
            +
            [dcc.Interval(
                            id='interval-component',
                            interval=5*1000, # in milliseconds
                            ),
            ]
            +
            [html.Div(id=f'interm-{pathname}-{i}') for i in range(num_plots)]
            ,className='row')

        layout_dic[pathname] = layout
        return layout
    return app

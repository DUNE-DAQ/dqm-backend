from dash import dcc
from dash import html
from dash.dependencies import Input, Output

from app import app
from apps import app1, app2, sources, display


app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content')
])

index_page = html.Div([
    dcc.Link('Go to Page 1', href='/apps/app1'),
    html.Br(),
    dcc.Link('Go to Page 2', href='/apps/app2'),
    dcc.Link('Sources', href='/apps/sources'),
])


@app.callback(Output('page-content', 'children'),
              Input('url', 'pathname'))
def display_page(pathname):
    if pathname == '/apps/app1':
        return app1.layout
    elif pathname == '/apps/app2':
        return app2.layout
    elif pathname == '/apps/sources':
        return sources.layout
    elif pathname == '/apps/display':
        return display.layout
    elif 'display' in pathname:
        return display.get_layout(pathname)
    else:
        return index_page

if __name__ == '__main__':
    app.run_server(debug=True)

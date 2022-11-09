from dash import Dash, html, dcc
import chloropleth
# from components import navbar

# # Define the navbar
# nav = navbar.Navbar()

application = Dash(__name__)
server = application.server

fig = chloropleth.get_figure()

application.layout = html.Div(children=[
    dcc.Location(id='url', refresh=False),
    # nav,
    html.H1(children='Paris Bikes'),

    html.Div(children='''
        Figure: Chloropleth
    '''),

    dcc.Graph(
        id='chloropleth-graph',
        figure=fig
    ),
])


if __name__ == '__main__':
    application.run_server(debug=False, port=5000)

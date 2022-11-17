import geopandas as gpd
from dash import Dash, dcc, html

from paris_bikes.mapping import create_map
from paris_bikes.utils import get_data_root

# # Define the navbar
# nav = navbar.Navbar()

application = Dash(__name__)
server = application.server

df = gpd.read_file(get_data_root() / "feature" / "feature.geojson")

fig = create_map(df, "nb_pop")

application.layout = html.Div(
    children=[
        dcc.Location(id="url", refresh=False),
        # nav,
        html.H1(children="Paris Bikes"),
        html.Div(
            children="""
        Figure: Chloropleth
    """
        ),
        dcc.Graph(id="chloropleth-graph", figure=fig),
    ]
)


if __name__ == "__main__":
    application.run_server(debug=False, port=5000)

import geopandas as gpd
from dash import Dash, Input, Output, dcc, html

from paris_bikes.mapping import create_map
from paris_bikes.utils import get_data_root

# Load data
df = gpd.read_file(get_data_root() / "feature" / "feature.geojson").set_index("iris")

# Initialize the dash app
application = Dash(__name__)
server = application.server

# Define the dash app layout
application.layout = html.Div(
    children=[
        dcc.Location(id="url", refresh=False),
        # nav,
        html.H1(children="Paris Bikes"),
        html.Br(),
        dcc.RadioItems(df.columns.drop("geometry"), "nb_pop", id="plot-column-input"),
        html.Br(),
        html.Div(children="Figure: Chloropleth"),
        dcc.Graph(id="map"),
    ]
)

# Link the plot-column-input with the map
@application.callback(
    Output(component_id="map", component_property="figure"),
    Input(component_id="plot-column-input", component_property="value"),
)
def update_map(input_value):
    return create_map(df, input_value)


if __name__ == "__main__":
    application.run_server(debug=True, port=5000)

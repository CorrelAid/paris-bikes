import geopandas as gpd
from dash import Dash, Input, Output, dcc, html

from paris_bikes.mapping import create_map
from paris_bikes.utils import get_data_root

# Load data
df = gpd.read_file(get_data_root() / "feature" / "feature.geojson").set_index("iris")
# Aggregate nb of parking spots into a single column
df["nb_parking_spots"] += df["nb_parking_spots_idfm"].fillna(0)
# Drop the idfm parking spots column
df.drop(columns=["nb_parking_spots_idfm"], inplace=True)
# Impute missing values with 0
df.fillna(0, inplace=True)
# Create normalized columns
# Note: adding +1 to the denominator to avoid dividing by 0
df = df.assign(
    **{(col + "_normalized"): (df.loc[:, col] / (df["nb_parking_spots"] + 1)) for col in df.columns.drop("geometry")}
)

# Initialize the dash app
application = Dash(__name__)
server = application.server

# Define the dash app layout
application.layout = html.Div(
    children=[
        dcc.Location(id="url", refresh=False),
        html.H1(children="Paris Bikes"),
        html.Br(),
        dcc.RadioItems(df.columns.drop(["geometry"]), "nb_pop", id="plot-column-selector"),
        html.Br(),
        dcc.Checklist(["Normalize metrics by number of parking spots"], id="normalize-button"),
        html.Br(),
        dcc.Graph(id="map"),
    ]
)

# Link the plot-column-selector with the output-map
@application.callback(
    Output(component_id="map", component_property="figure"),
    Input(component_id="plot-column-selector", component_property="value"),
)
def update_map(input_value):
    return create_map(df, input_value)


# Link the normalize-button with the plot-column-selector
@application.callback(
    Output(component_id="plot-column-selector", component_property="options"),
    Input(component_id="normalize-button", component_property="value"),
)
def update_plot_column_selector(input_value):
    cols = df.columns.drop(["geometry"])
    # If nothing is selected, use raw metrics
    if input_value is None:
        return [col for col in cols if "_normalized" not in col]
    # Otherwise, use normalized metrics
    else:
        return [col for col in cols if "_normalized" in col]


if __name__ == "__main__":
    application.run_server(debug=True, port=5001)

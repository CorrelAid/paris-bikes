import dash_bootstrap_components as dbc
import geopandas as gpd
from dash import Dash, Input, Output, State, dcc, html

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
application = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP, dbc.icons.BOOTSTRAP])
server = application.server

# Define the dash app layout
application.layout = dbc.Container(
    [
        dbc.Row(
            [
                html.H1(children="Paris Parking Demand Index", style={'marginTop': 20}),
                html.Br(),
                html.Div("The Paris Parking Demand Index visualizes the number of bicycle parking spaces in relation to metrics that indicate parking demand, such as the number of stores or people entering the metro."),
                html.Br(),
                html.Div("Aggregated at the IRIS level, the smallest unit of municipal infrastructure in France, this index helps determine how adequately areas are served in terms of parking facilities, while leaving flexibility as to which exact location they should be built.")
            ]
        ),
        html.Hr(),
        dbc.Row(
            [
                dbc.Col(
                    [
                        dbc.Card(
                            [
                                dbc.CardBody(
                                    [
                                        html.H4(
                                            [html.I(className="bi bi-bar-chart-line me-2"), "Metrics"],
                                        ),
                                        dbc.RadioItems(options=[], value="nb_pop", id="plot-column-selector"),
                                    ]
                                ),
                                dbc.CardFooter(
                                    dbc.Checklist(
                                        options=[{"label": "Normalize metrics by number of parking spots", "value": 1}],
                                        value=[],
                                        id="normalize-button",
                                        switch=True,
                                    ),
                                ),
                            ],
                        )
                    ],
                    width=3,
                ),
                dbc.Col(
                    dcc.Graph(id="map"),
                ),
            ]
        ),
        html.Hr(),
        dbc.Row(
            [
                html.Div("Version: Alpha/Prototype", style={'color': 'grey','font-style': 'italic'}),
                html.P(
                    [
                        "This project was developed by ",
                        html.A(
                            "CorrelAid",
                            href="https://correlaid.org/",
                        ),
                        " for the City of Paris. The source code can be found ",
                        html.A(
                            "on GitHub",
                            href="https://github.com/CorrelAid/paris-bikes",
                        ),
                        ".",
                    ]
                ),
            ]
        ),
    ]
)

# Link the plot-column-selector with the output-map
@application.callback(
    Output(component_id="map", component_property="figure"),
    Input(component_id="plot-column-selector", component_property="value"),
)
def update_map(input_value):
    fig = create_map(df, input_value, width=None, height=None)
    # Remove legend title
    fig.update_layout(coloraxis_colorbar={"title": ""})
    return fig


# Link the normalize-button with the plot-column-selector
@application.callback(
    Output(component_id="plot-column-selector", component_property="options"),
    Output(component_id="plot-column-selector", component_property="value"),
    Input(component_id="normalize-button", component_property="value"),
    State(component_id="plot-column-selector", component_property="value"),
)
def update_plot_column_selector(button_value, selector_value):
    cols = df.columns.drop(["geometry"])
    col_labels = [
        "Population",
        "Parking spots",
        "Museum visitors",
        "Metro passengers",
        "Train passengers",
        "Number of shops",
        "School capacity",
    ]
    # If nothing is selected, use raw metrics
    if len(button_value) == 0:
        if "_normalized" in selector_value:
            selector_value = selector_value.replace("_normalized", "")
        cols = [col for col in cols if "_normalized" not in col]
        options = [{"label": col_label, "value": col} for col_label, col in zip(col_labels, cols)]
        return options, selector_value
    # Otherwise, use normalized metrics
    else:
        if "_normalized" not in selector_value:
            selector_value = selector_value + "_normalized"
        cols = [col for col in cols if "_normalized" in col]
        options = [{"label": col_label, "value": col} for col_label, col in zip(col_labels, cols)]
        return options, selector_value


if __name__ == "__main__":
    application.run_server(debug=True, port=5001)

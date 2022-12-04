import dash_bootstrap_components as dbc
import geopandas as gpd
from dash import Dash, Input, Output, State, callback_context, dcc, html
from dash.exceptions import PreventUpdate

from paris_bikes.mapping import create_map
from paris_bikes.pipelines import create_parking_index
from paris_bikes.utils import get_data_root

# Load data
df = gpd.read_file(get_data_root() / "feature" / "feature.geojson").set_index(
    "iris", drop=False
)
# Aggregate nb of parking spots into a single series
df["nb_parking_spots"] += df["nb_parking_spots_idfm"].fillna(0)
# Drop the parking spots columns
df.drop(columns=["nb_parking_spots_idfm"], inplace=True)
# Impute missing values with 0
df.fillna(0, inplace=True)
# Create normalized columns
# Note: adding +1 to the denominator to avoid dividing by 0
df = df.assign(
    **{
        (col + "_normalized"): (df.loc[:, col] / (df["nb_parking_spots"] + 1))
        for col in df.columns.drop(["geometry", "iris"])
    }
)
# Create scaled columns
df = df.join(
    create_parking_index(df)
    .loc[:, ["parking_index", "parking_normalized"]]
    .rename(
        columns={"parking_index": "demand_index", "parking_normalized": "supply_index"}
    )
    .assign(demand_supply_index=lambda x: x["demand_index"] / x["supply_index"])
)

# Initialize the dash app
application = Dash(
    __name__, external_stylesheets=[dbc.themes.BOOTSTRAP, dbc.icons.BOOTSTRAP]
)
server = application.server

# Define the dash app layout
application.layout = dbc.Container(
    [
        dbc.Row(
            [
                html.H1(children="Paris Parking Demand Index", style={"marginTop": 20}),
                html.Br(),
                html.Div(
                    "The Paris Parking Demand Index visualizes the number of existing bicycle parking spaces in the City of Paris in relation to metrics that might indicate demand for bicycle parking, such as the number of stores or people entering the metro."
                ),
                html.Br(),
                html.Div(
                    "Aggregated at the IRIS level, the smallest unit of municipal infrastructure in France, this index helps determine how adequately areas are served in terms of parking facilities, while leaving flexibility as to which exact location they should be built."
                ),
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
                                            [
                                                html.I(
                                                    className="bi bi-bar-chart-line me-2"
                                                ),
                                                "Indices",
                                            ],
                                        ),
                                        dbc.RadioItems(
                                            options=[
                                                {
                                                    "label": "Demand index",
                                                    "value": "demand_index",
                                                },
                                                {
                                                    "label": "Supply index",
                                                    "value": "supply_index",
                                                },
                                                {
                                                    "label": "Demand/Supply Index",
                                                    "value": "demand_supply_index",
                                                },
                                            ],
                                            value=None,
                                            id="demand-index-column-selector",
                                        ),
                                    ]
                                ),
                            ],
                        ),
                        html.Br(),
                        dbc.Card(
                            [
                                dbc.CardBody(
                                    [
                                        html.H4(
                                            [
                                                html.I(className="bi bi-cart3 me-2"),
                                                "Demand metrics",
                                            ],
                                        ),
                                        dbc.RadioItems(
                                            options=[
                                                {
                                                    "label": "Population",
                                                    "value": "nb_pop",
                                                },
                                                {
                                                    "label": "Museum visitors",
                                                    "value": "visitors",
                                                },
                                                {
                                                    "label": "Metro passengers",
                                                    "value": "nb_metro_rer_passengers",
                                                },
                                                {
                                                    "label": "Train passengers",
                                                    "value": "nb_train_passengers",
                                                },
                                                {
                                                    "label": "Number of shops",
                                                    "value": "shops_weighted",
                                                },
                                                {
                                                    "label": "School capacity",
                                                    "value": "school_capacity",
                                                },
                                            ],
                                            value="nb_pop",
                                            id="demand-column-selector",
                                        ),
                                    ]
                                ),
                                dbc.CardFooter(
                                    dbc.Checklist(
                                        options=[
                                            {
                                                "label": "Normalize by parking spots",
                                                "value": 1,
                                            }
                                        ],
                                        value=[],
                                        id="normalize-button",
                                        switch=True,
                                    ),
                                ),
                            ],
                        ),
                        html.Br(),
                        dbc.Card(
                            [
                                dbc.CardBody(
                                    [
                                        html.H4(
                                            [
                                                html.I(className="bi bi-box-seam me-2"),
                                                "Supply metrics",
                                            ],
                                        ),
                                        dbc.RadioItems(
                                            options=[
                                                {
                                                    "label": "Parking spots",
                                                    "value": "nb_parking_spots",
                                                }
                                            ],
                                            value=None,
                                            id="supply-column-selector",
                                        ),
                                    ]
                                ),
                            ],
                        ),
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
                html.Div(
                    "Version: Alpha/Prototype",
                    style={"color": "grey", "font-style": "italic"},
                ),
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


@application.callback(
    Output(component_id="map", component_property="figure"),
    Input(component_id="demand-column-selector", component_property="value"),
    Input(component_id="supply-column-selector", component_property="value"),
    Input(component_id="demand-index-column-selector", component_property="value"),
    Input(component_id="normalize-button", component_property="value"),
)
def update_map(demand_input_value, supply_input_value, index_input_value, normalize):
    """Update the map according to the selected item on the RadioItems"""
    # Plot from supply RadioItems or demand RadioItems?
    if demand_input_value:
        col = demand_input_value
        colorscale = "OrRd"
        # Normalize or not?
        if normalize:
            col += "_normalized"
    elif supply_input_value:
        col = supply_input_value
        colorscale = "Greens"
    elif index_input_value:
        col = index_input_value
        if col == "demand_index":
            colorscale = "OrRd"
        elif col == "supply_index":
            colorscale = "Greens"
        else:
            colorscale = "Blues"

    fig = create_map(df, col, width=None, height=None, colorscale=colorscale)
    # Remove legend title
    fig.update_layout(coloraxis_colorbar={"title": ""})
    return fig


@application.callback(
    Output(component_id="demand-column-selector", component_property="value"),
    Output(component_id="supply-column-selector", component_property="value"),
    Output(component_id="demand-index-column-selector", component_property="value"),
    Input(component_id="demand-column-selector", component_property="value"),
    Input(component_id="supply-column-selector", component_property="value"),
    Input(component_id="demand-index-column-selector", component_property="value"),
    prevent_initial_call=True,
)
def update_supply_demand_radioitems(
    demand_input_value, supply_input_value, index_input_value
):
    """Guarantee only one RadioItems has a value selected"""
    if callback_context.triggered_id == "demand-column-selector":
        return demand_input_value, None, None
    elif callback_context.triggered_id == "supply-column-selector":
        return None, supply_input_value, None
    elif callback_context.triggered_id == "demand-index-column-selector":
        return None, None, index_input_value


if __name__ == "__main__":
    application.run_server(debug=True, port=5001)

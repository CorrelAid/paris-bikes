import geopandas as gpd
import numpy as np
import plotly.express as px


def create_map(df: gpd.GeoDataFrame, var: str, width=600, height=400):
    """Compute number of bike parking spots per IRIS.

    Args:
        df (gpd.GeoDataFrame): Dataframe with information to map.
        var (str): Variable to map

    Returns:
        plotly map
    """
    # Create basemap
    fig = px.choropleth_mapbox(
        df,
        geojson=df.geometry,
        locations="iris",
        # projection="mercator",
        color=var,
        width=width,
        height=height,
        color_continuous_scale="OrRd",
        opacity=0.75,
        center={"lat": 48.86, "lon": 2.34},
        zoom=11,
        mapbox_style="carto-positron",
        hover_name="iris",
        hover_data={"iris": False, "nb_parking_spots": True},
    )

    # Zoom map
    fig.update_geos(fitbounds="locations", visible=True)

    # Enhance layout
    fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0}, uirevision="no reset")

    return fig

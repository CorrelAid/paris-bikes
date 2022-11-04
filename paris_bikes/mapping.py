import geopandas as gpd
import plotly.express as px


def create_map(df: gpd.GeoDataFrame, var: str, width = 600, height = 400):

    """Compute number of bike parking spots per IRIS.

    Args:
        df (gpd.GeoDataFrame): Dataframe with information to map.
        var (str): Variable to map

    Returns:
        plotly map
    """

    # Create basemap
    fig = px.choropleth(
        df,
        geojson=df.geometry,
        locations=df.index,
        projection="mercator",
        color=var,
        width=width, height=height
        )

    # Zoom map
    fig.update_geos(fitbounds="locations", visible=True)

    # Enhance layout
    fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})

    return fig

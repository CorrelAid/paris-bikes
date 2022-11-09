from pathlib import Path
import plotly.express as px
import geopandas as gpd


def get_figure():
    # Load data 
    census_filepath = Path("./data/raw/RECENSEMENT_IRIS_POPULATION.geojson")
    parking_filepath = Path("./data/raw/stationnement-voie-publique-emplacements.geojson")
    green_spaces_filepath = Path("./data/raw/espaces_verts.geojson")

    df_census = gpd.read_file(census_filepath).set_index("l_ir")
    df_parking = gpd.read_file(parking_filepath)
    df_green = gpd.read_file(green_spaces_filepath).set_index("nom_ev")

    # Identify the IRIS of each parking spot
    df_bike_parking = df_parking.loc[df_parking.regpar.isin(["Vélos", "Box à vélos"])]
    df_parks_with_iris = df_bike_parking.sjoin(df_census.loc[:, ["nb_pop", "geometry"]], how="inner")

    # Get the total parking spots per IRIS
    parks_per_iris = df_parks_with_iris.groupby("index_right")["plarel"].sum()

    # Compute parking spots per person (per IRIS)
    df_census_with_parks = df_census.join(parks_per_iris)
    df_census_with_parks["parks_per_person"] = (
        df_census_with_parks["plarel"] / df_census_with_parks["nb_pop"]
    )

    df_census_with_parks["plarel"].isnull().sum()
    # Remove NaNs
    df_census_with_parks.dropna(subset=["plarel"], inplace=True)
    df_census_with_parks["parks_per_person"].describe()

    df_plot = df_census_with_parks[["parks_per_person", "geometry"]].copy()
    df_plot["parks_per_person"].clip(
        upper=df_plot["parks_per_person"].quantile(0.95),
        inplace=True
    )
    fig = px.choropleth(
        df_plot, 
        geojson=df_plot.geometry, 
        locations=df_plot.index, 
        projection="mercator", 
        color="parks_per_person"
    )
    fig.update_geos(fitbounds="locations", visible=True)
    fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})

    return fig

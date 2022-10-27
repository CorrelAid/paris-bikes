import geopandas as gpd
import pandas as pd


def get_parkings_per_iris(df_parking_raw: gpd.GeoDataFrame, df_iris: gpd.GeoDataFrame) -> pd.DataFrame:
    """Compute number of bike parking spots per IRIS.

    Args:
        df_parking_raw (gpd.GeoDataFrame): Raw data with location of all parking spots within the city.
        df_iris (gpd.GeoDataFrame): Raw data with location of all IRIS within the city.

    Returns:
        pd.DataFrame: Number of bike parking spots per IRIS.
    """
    # Include only bike parking spots
    df_bike_parking = (
        df_parking_raw.loc[df_parking_raw.regpar.isin(["Vélos", "Box à vélos"])]
        .copy()
        .rename(columns={"plarel": "nb_parking_spots"})
    )

    # Identify the IRIS of each parking spot
    df_parks_with_iris = df_bike_parking.sjoin(df_iris.loc[:, ["nb_pop", "geometry"]], how="inner")

    # Get the total parking spots per IRIS
    df_parks_per_iris = df_parks_with_iris.groupby("index_right")["nb_parking_spots"].sum()
    df_parks_per_iris.index.rename("iris", inplace=True)

    return pd.DataFrame(df_parks_per_iris)


def get_population_per_iris(df_iris_raw: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    """Get the population per IRIS.

    Args:
        df_iris_raw (gpd.GeoDataFrame): Raw data with location of all IRIS within the city, as well as the population.

    Returns:
        gpd.GeoDataFrame: Population per IRIS.
    """
    df_iris = (
        df_iris_raw.loc[:, ["l_ir", "nb_pop", "geometry"]].copy().rename(columns={"l_ir": "iris"}).set_index("iris")
    )

    # Drop duplicated indices
    df_iris = df_iris.loc[~df_iris.index.duplicated()]

    return df_iris

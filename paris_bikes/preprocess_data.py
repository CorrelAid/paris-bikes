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

def get_school_capacity_per_iris(df_school_raw: gpd.GeoDataFrame, df_iris: gpd.GeoDataFrame) -> pd.DataFrame:
    """Compute school capacity per IRIS.

    Args:
        df_school_raw (gpd.GeoDataFrame): Raw data with location and capacity of Paris schools.
        df_iris (gpd.GeoDataFrame): Raw data with location of all IRIS within the city.

    Returns:
        pd.DataFrame: School capacity per IRIS.
    """
    # Select relevant variables and rename them
    df_schools = df_schools_raw[['c_cainsee', 'l_ep_min', 'c_niv2', 'c_niv3', 'lib_qn2', 'val_qn2', 'geometry']]
    df_schools = df_schools.rename(
        columns={
            "c_cainsee": "insee_code",
            "l_ep_min": "school_name",
            "c_niv2": "school_type",
            "c_niv3": "school_subtype",
            "val_qn2": "capacity"
        }
    )

    # Filter only IRIS in Paris
    df_schools = df_schools[df_schools['insee_code'].between(75000, 75999)]

    # Filter only primary and secondary education institutions (other institutions have no info on capacity)
    df_schools = df_schools[(df_schools['school_type'] == 101) | (df_schools['school_type'] == 102)]

    # Impute missing values of school capacity with mean capacity of similar type
    df_schools['capacity'] = df_schools['capacity'].fillna(df_schools.groupby('school_subtype')['capacity'].transform('mean'))

    # Identify the IRIS of each school
    df_schools = df_schools.sjoin(df_iris.loc[:, ["geometry"]], how="inner")

    # Get the total school capacity per IRIS
    df_schools = df_schools.groupby("index_right")["capacity"].sum()
    df_schools.index.rename("iris", inplace=True)

    return df_schools

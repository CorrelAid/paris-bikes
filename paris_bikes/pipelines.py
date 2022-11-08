from pathlib import Path
from typing import Dict

import geopandas as gpd
import pandas as pd

from paris_bikes.preprocess_data import (
    clean_museum_data,
    get_idfm_parkings_per_iris,
    get_metro_rer_passengers_per_iris,
    get_museum_visitors_per_iris,
    get_parkings_per_iris,
    get_population_per_iris,
    get_school_capacity_per_iris,
    get_shops_per_iris,
    get_train_passengers_per_iris,
)
from paris_bikes.utils import get_data_root


def primary_pipeline() -> Dict[str, pd.DataFrame]:
    """Generate the primary datasets from the raw datasets."""
    # Define location of the raw data
    raw_root_filepath = get_data_root() / "raw"
    raw_census_filepath = raw_root_filepath / "RECENSEMENT_IRIS_POPULATION.geojson"
    raw_parking_filepath = (
        raw_root_filepath / "stationnement-voie-publique-emplacements.geojson"
    )
    raw_parking_idfm_filepath = (
        raw_root_filepath / "parking-velos-ile-de-france-mobilites.csv"
    )
    raw_museum_filepath = raw_root_filepath / "frequentation-des-musees-de-france.csv"
    raw_train_filepath = raw_root_filepath / "frequentation-gares.csv"
    raw_metro_filepath = (
        raw_root_filepath / "trafic-annuel-entrant-par-station-du-reseau-ferre-2021.csv"
    )
    raw_shops_filepath = raw_root_filepath / "BDCOM_2020.geojson"
    raw_schools_filepath = (
        raw_root_filepath / "EQUIPEMENT_PONCTUEL_ENSEIGNEMENT_EDUCATION.geojson"
    )

    # Read the raw data
    df_raw_census = gpd.read_file(raw_census_filepath)
    df_raw_parking = gpd.read_file(raw_parking_filepath)
    df_raw_parking_idfm = pd.read_csv(raw_parking_idfm_filepath, delimiter=";")
    df_raw_museum = pd.read_csv(raw_museum_filepath, delimiter=";")
    df_raw_train = pd.read_csv(raw_train_filepath, delimiter=";")
    df_raw_metro = pd.read_csv(raw_metro_filepath, delimiter=";")
    df_raw_shops = gpd.read_file(raw_shops_filepath)
    df_raw_schools = gpd.read_file(raw_schools_filepath)

    # Transform raw data into primary data
    df_iris = get_population_per_iris(df_raw_census)
    df_parking = get_parkings_per_iris(df_raw_parking, df_iris)
    df_parking_idfm = get_idfm_parkings_per_iris(df_raw_parking_idfm, df_iris)
    df_museum_clean = clean_museum_data(df_raw_museum)
    df_museum = get_museum_visitors_per_iris(df_museum_clean, df_iris)
    df_metro = get_metro_rer_passengers_per_iris(df_raw_metro, df_iris)
    df_train = get_train_passengers_per_iris(df_raw_train, df_iris)
    df_shops = get_shops_per_iris(df_raw_shops, df_iris)
    df_schools = get_school_capacity_per_iris(df_raw_schools, df_iris)

    # Save primary data
    primary_root_filepath = get_data_root() / "primary"
    primary_datasets = {
        "iris": df_iris,
        "parking": df_parking,
        "parking_idfm": df_parking_idfm,
        "museum": df_museum,
        "metro": df_metro,
        "train": df_train,
        "shops": df_shops,
        "schools": df_schools,
    }
    for df_name, df in primary_datasets.items():
        if isinstance(df, gpd.GeoDataFrame):
            df.to_file(primary_root_filepath / f"{df_name}.geojson", driver="GeoJSON")
        elif isinstance(df, pd.DataFrame):
            df.to_csv(primary_root_filepath / f"{df_name}.csv")
        else:
            raise ValueError(
                f"Datatype {type(df)} of {df_name} dataset is not recognized."
            )

    print("Don't forget to push your changes to dvc with `dvc push`.")

    return primary_datasets

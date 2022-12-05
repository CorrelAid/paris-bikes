from functools import reduce
from pathlib import Path
from typing import Dict, Union

import geopandas as gpd
import pandas as pd

from paris_bikes.preprocess_data import *
from paris_bikes.utils import get_data_root


def primary_pipeline() -> Dict[str, Union[pd.DataFrame, gpd.GeoDataFrame]]:
    """Generate and save the primary datasets from the raw datasets.

    Returns:
        Dict[str, Union[pd.DataFrame, gpd.GeoDataFrame]]: Dictionary with
            primary datasets.
    """
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
    print("Reading raw data.")
    df_raw_census = gpd.read_file(raw_census_filepath)
    df_raw_parking = gpd.read_file(raw_parking_filepath)
    df_raw_parking_idfm = pd.read_csv(raw_parking_idfm_filepath, delimiter=";")
    df_raw_museum = pd.read_csv(raw_museum_filepath, delimiter=";")
    df_raw_train = pd.read_csv(raw_train_filepath, delimiter=";")
    df_raw_metro = pd.read_csv(raw_metro_filepath, delimiter=";")
    df_raw_shops = gpd.read_file(raw_shops_filepath)
    df_raw_schools = gpd.read_file(raw_schools_filepath)

    # Transform raw data into primary data
    print("Transforming raw data into primary data.")
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
    print("Saving primary data.")
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


def feature_pipeline(
    primary_datasets: Dict[str, Union[pd.DataFrame, gpd.GeoDataFrame]] = {}
) -> gpd.GeoDataFrame:
    """Create and save the feature table from the primary datasets.

    The feature table is a merge between all the primary datasets, and it
    includes the geometry of each IRIS.

    Args:
        primary_datasets
        (Dict[str, Union[pd.DataFrame, gpd.GeoDataFrame]], optional):
            Dictionary of primary datasets.
            It is the output of primary_pipeline. Defaults to {}.

    Returns:
        gpd.GeoDataFrame: Feature table.
    """
    # Load primary datasets if not passed as argument
    if primary_datasets == {}:
        primary_root_filepath = get_data_root() / "primary"
        primary_datasets = [
            gpd.read_file(primary_root_filepath / "iris.geojson"),
            pd.read_csv(primary_root_filepath / "parking.csv"),
            pd.read_csv(primary_root_filepath / "parking_idfm.csv"),
            pd.read_csv(primary_root_filepath / "museums.csv"),
            pd.read_csv(primary_root_filepath / "metro_rer.csv"),
            pd.read_csv(primary_root_filepath / "trains.csv"),
            pd.read_csv(primary_root_filepath / "shops.csv"),
            pd.read_csv(primary_root_filepath / "schools.csv"),
        ]
        for idx, _ in enumerate(primary_datasets):
            primary_datasets[idx] = primary_datasets[idx].set_index("iris")
    else:
        primary_datasets = primary_datasets.values()

    df_feature = reduce(
        lambda x, y: x.merge(y, how="outer", left_index=True, right_index=True),
        primary_datasets,
    )

    feature_root_filepath = get_data_root() / "feature"
    df_feature.to_file(feature_root_filepath / "feature.geojson", driver="GeoJSON")

    return df_feature


def create_parking_index(
    feature_dataset="",
    index_vars=[
        "nb_pop",
        "visitors",
        "nb_metro_rer_passengers",
        "nb_train_passengers",
        "shops_weighted",
        "school_capacity",
    ],
) -> gpd.GeoDataFrame:

    """Create parking index and save the dataset incl. the index

    Args:
        feature_dataset: gpd.GeoDataFrame:
            Feature Dataframe
        index_vars: List[str], optional:
            name of Variables that should be aggregated to create the parking index

    Returns:
        gpd.GeoDataFrame: Feature table incl. index.

    """
    #  Load feature dataset if not passed as argument
    if isinstance(feature_dataset, gpd.GeoDataFrame):
        pass
    else:
        feature_dataset_filepath = get_data_root() / "feature/feature.geojson"
        feature_dataset = gpd.read_file(feature_dataset_filepath)

    feature_dataset = feature_dataset.set_index("iris")
    df_aggr = feature_dataset[index_vars].copy()

    # normalize each variable
    for var in df_aggr.columns:
        df_aggr[var] = (df_aggr[var] - df_aggr[var].min()) / (
            df_aggr[var].max() - df_aggr[var].min()
        )

    # aggregate normalized variables to parking index
    df_aggr["parking_index"] = df_aggr.sum(axis=1)

    # add parking index to original geodataframe
    df_parking_index = feature_dataset.join(df_aggr[["parking_index"]])

    # normalize parking supply
    df_parking_index["parking_normalized"] = (
        df_parking_index["nb_parking_spots"]
        - df_parking_index["nb_parking_spots"].min()
    ) / (
        df_parking_index["nb_parking_spots"].max()
        - df_parking_index["nb_parking_spots"].min()
    )

    return df_parking_index

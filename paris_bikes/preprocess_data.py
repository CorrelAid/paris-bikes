import geopandas as gpd
import pandas as pd
from geopy.geocoders import Nominatim


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

def strip(sep, name):
    """Remove substring behind a separator.

    Args:
        sep (string): Separator.
        name (string): The string to be shortened.

    Returns:
        string: Substring of 'name' containing everything before the separator.
    """
    try:
        for s in sep:
            stripped = name.split(s, 1)[0]
            name = stripped
        return stripped
    except:
        return None

def my_geocoder(row, column, geolocator):
    """Return geocode for a string.

    Args:
        row (row of pd.DataFrame): Row of dataframe.
        column (string): Label of the column that contains the string to geocode.
        geolocator (Nominatim): Tool to geocode OpenStreetMap data.
    
    Returns:
        geopy.location.Location.point: Geolocation point for the input string.
    """
    try:
        location = geolocator.geocode(row[column])
        row["longitude"] = location.longitude
        row["latitude"] = location.latitude
        return row
    except:
        return None

def clean_museum_data(df_museum_raw):
    """Geocoding and cleaning museum frequentation data.

    Args:
        df (pd.Dataframe): Raw data with frequentation of national museums in Paris in years 2019 and 2020.

    Returns:
        gpd.GeoDataFrame: Clean museum dataset with geolocation (columns: name, type, visitors, year, geometry).
    """
    df = df_museum_raw.copy()
    geolocator = Nominatim(user_agent="correlaid-paris-bikes")
    
    # drop museums that are closed
    df = df[df["Note"].isna()]
    
    # if data for more than one year, keep only most recent one
    df.sort_values("Année", inplace=True)
    df = df[(~df['ID MUSEOFILE'].duplicated(keep="last")) | df['ID MUSEOFILE'].isna()]
    
    # manual replacement of museum names which geocoder cannot find
    df["name"] = df["NOM DU MUSEE"].str.replace("Établissement public du musée d'Orsay et du musée de l'Orangerie - Valéry Giscard d'Estaing - Musée d'Orsay", "Musée d'Orsay")
    df["name"] = df["name"].str.replace("Établissement public du musée d'Orsay et du musée de l'Orangerie - Valéry Giscard d'Estaing - Musée de l'Orangerie", "Musée de l'Orangerie")
    df["name"] = df["name"].str.replace("Musée de l'Ecole Nationale Supérieure des Beaux-Arts","Ecole Nationale Supérieure des Beaux-Arts")
    df["name"] = df["name"].str.replace("Musée National Auguste Rodin","Musée Rodin Paris")
    df["name"] = df["name"].str.replace("Musée d'Art Moderne de la ville de Paris","Musée d'Art Moderne de Paris")
    df["name"] = df["name"].str.replace("Établissement Public de la Porte Dorée","Palais de la Porte Dorée")
    df["name"] = df["name"].str.replace("Etablissement Public du Musée des Arts Asiatiques Guimet","Musée Guimet")
    df["name"] = df["name"].str.replace("Musée du 11 Conti","La Monnaie de Paris")
    df["name"] = df["name"].str.replace("Musée Yves Saint Laurent","Musée Yves Saint Laurent Paris")
    
    # remove anything after bracket, dash, or comma
    sep_list = [" ("," -",","]
    df["name"] = df.apply(lambda x: strip(sep_list, x["name"]), axis=1)
    
    # geolocate museums
    # df["geopoint"] = df.apply(lambda x: my_geocoder(x["name"], geolocator), axis=1)
    df = df.apply(lambda x: my_geocoder(x, "name", geolocator), axis=1)
    
    print("{}% of addresses were geocoded!".format(
   (1 - sum(pd.isnull(df["longitude"])) / len(df)) * 100))
    
    # prepare cleaned dataframe (select and rename columns, add "type" column, fix datatypes, reset index)
    df['type'] = "museum"
    df_museum = df[["name", "type", "TOTAL","Année","longitude", "latitude"]].rename({'TOTAL':'visitors','Année':'year'}, axis=1)

    df_museum[['visitors','year']] = df_museum[['visitors','year']].astype('Int64')
    df_museum = df_museum.reset_index(drop=True)

    # transform to GeoDataFrame and drop longitude and latitude columns
    gdf_museum = gpd.GeoDataFrame(
    df_museum, geometry=gpd.points_from_xy(df_museum.longitude, df_museum.latitude))
    gdf_museum = gdf_museum.drop(["longitude", "latitude"], axis=1)
    print(gdf_museum)
    
    return gdf_museum
    
    
def get_idfm_parkings_per_iris(df_idfm_raw: gpd.GeoDataFrame, df_iris: gpd.GeoDataFrame) -> pd.DataFrame:
    """Compute Île de France Mobilité parking spots (in train stations) per IRIS.
    Args:
        df_idfm_raw (gpd.GeoDataFrame): Raw data with location and number of parking spots in IDFM parking facilities.
        df_iris (gpd.GeoDataFrame): Raw data with location of all IRIS within the city.
    Returns:
        pd.DataFrame: Number of IDFM parking spots per IRIS.
    """
    # Select relevant variables and rename them
    df_idfm = df_idfm_raw[['zdcname', 'type', 'num_docks_available', 'insee_code', 'geometry']]
    df_idfm = df_idfm.rename(
        columns={
            "zdcname": "name",
            "num_docks_available": "nb_parking_spots"
        }
    )

    # Filter only IRIS in Paris
    df_idfm = df_idfm[df_idfm['insee_code'].between(75000, 75999)]

    # Identify the IRIS of each parking facility
    df_idfm = df_idfm.sjoin(df_iris.loc[:, ["geometry"]], how="inner")

    # Get the total number of parking spots per IRIS
    df_idfm = df_idfm.groupby("index_right")[["nb_parking_spots"]].sum()
    df_idfm.index.rename("iris", inplace=True)

    return df_idfm
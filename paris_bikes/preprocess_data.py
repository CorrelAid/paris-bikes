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

def geocode_from_location_name(df_in: pd.DataFrame, location_name_column):
    """Geocode locations based on a column with names of the locations.

    Args:
        df_in (pd.DataFrame): Dataframe with location names to be geocoded
        location_name_column (string): Name of column with the location names to be geocoded

    Returns:
        gpd.GeoDataFrame: Dataframe with geocoded locations
    """
    geolocator = Nominatim(user_agent="correlaid-paris-bikes")
    df = df_in.apply(lambda x: my_geocoder(x, location_name_column, geolocator), axis=1)

    print("{}% of rows were geocoded!".format((1 - sum(pd.isnull(df["longitude"])) / len(df)) * 100))

    # transform to GeoDataFrame and drop longitude and latitude columns
    gdf = gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df.longitude, df.latitude), crs="EPSG:4326")
    gdf = gdf.drop(["longitude", "latitude"], axis=1)

    return gdf

def clean_museum_data(df_museum_raw):
    """Geocoding and cleaning museum frequentation data.

    Args:
        df (pd.Dataframe): Raw data with frequentation of national museums in Paris in years 2019 and 2020.

    Returns:
        gpd.GeoDataFrame: Clean museum dataset with geolocation (columns: name, type, visitors, year, geometry).
    """
    df = df_museum_raw.copy()

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
    gdf = geocode_from_location_name(df, "name")

    # prepare cleaned dataframe (select and rename columns, add "type" column, fix datatypes, reset index)
    gdf['type'] = "museum"
    gdf_museum = gdf[["name", "type", "TOTAL","Année","longitude", "latitude"]].rename({'TOTAL':'visitors','Année':'year'}, axis=1)

    gdf_museum[['visitors','year']] = gdf_museum[['visitors','year']].astype('Int64')
    gdf_museum = gdf_museum.reset_index(drop=True)

    return gdf_museum

def get_metro_passengers_per_iris(df_metro_raw: pd.DataFrame, df_iris: gpd.GeoDataFrame) -> pd.DataFrame:
    """Compute number of metro passengers per IRIS.

    Args:
        df_metro_raw (pd.DataFrame): Raw data with number of metro passengers per station
        df_iris (gpd.GeoDataFrame): Raw data with location of all IRIS within the city.

    Returns:
        pd.DataFrame: Number of metro passengers per IRIS.
    """
    # Clean metro data
    # Include only Métro stations (assuming that RER are counted on the train dataset)
    # Include only stations in Paris
    # Include only relevant columns
    df_metro = (
        df_metro_raw
        .loc[
            df_metro_raw["Réseau"].isin(["Métro"]) &
            df_metro_raw["Ville"].isin(["Paris"]),
            ["Station", "Trafic"]
        ]
        .rename(columns={"Station": "station", "Trafic": "nb_metro_passengers"})
        .copy()
    )

    df_metro["station"] = df_metro["station"].str.lower()
    df_metro["station"] = df_metro["station"].str.replace("bibliotheque", "bibliotheque francois mitterand")

    # Add string ", station" to every station name, to avoid confusions with stations names that are too general
    # E.g. "Hotel de Ville" (city hall) exists in every city
    df_metro["station_city"] = df_metro["station"] + ", paris"

    # Geocode station names
    df_metro = (
        geocode_from_location_name(df_metro, "station_city")
        .drop(columns="station_city")
    )

    # TODO this could also be refactored into a separate function, since it's already used in other functions
    # Identify the IRIS of each station
    df_metro = df_metro.sjoin(df_iris.loc[:, ["geometry"]], how="inner")
    # Get the total number of metro passengers per IRIS
    df_metro = df_metro.groupby("index_right")[["nb_metro_passengers"]].sum()
    df_metro.index.rename("iris", inplace=True)

    return df_metro

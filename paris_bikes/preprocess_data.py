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
            "val_qn2": "school_capacity"
        }
    )

    # Filter only IRIS in Paris
    df_schools = df_schools[df_schools['insee_code'].between(75000, 75999)]

    # Filter only primary and secondary education institutions (other institutions have no info on capacity)
    df_schools = df_schools[(df_schools['school_type'] == 101) | (df_schools['school_type'] == 102)]

    # Impute missing values of school capacity with mean capacity of similar type
    df_schools['school_capacity'] = df_schools['school_capacity'].fillna(df_schools.groupby('school_subtype')['school_capacity'].transform('mean'))

    # Identify the IRIS of each school
    df_schools = df_schools.sjoin(df_iris.loc[:, ["geometry"]], how="inner")

    # Get the total school capacity per IRIS
    df_schools = df_schools.groupby("index_right")[["school_capacity"]].sum()
    df_schools.index.rename("iris", inplace=True)

    return df_schools

def get_shops_per_iris(df_shopping_raw: gpd.GeoDataFrame, df_iris: gpd.GeoDataFrame) -> pd.DataFrame:
    """Compute number of businesses per IRIS (weighed by shop size).

    Args:
        df_shopping_raw (gpd.GeoDataFrame): Raw data with location, size and
        type of Paris shops.

    Returns:
        pd.DataFrame: School capacity per IRIS.
    """

    # Select relevant variables
    df_shopping = df_shopping_raw.loc[:,('IRIS', 'LIBELLE_REGROUPEMENT_8_POSTES', 'SURFACE', 'geometry')]

    # Map quantifiable values to different surfaces
    surface_dict = {'moins de 300 m²':1, 'de 300 à 1.000 m²':2, '1.000 m² ou plus':3}
    df_shopping['surface_code'] = df_shopping['SURFACE'].map(surface_dict)

    # Filter out vacant shops
    df_shopping = df_shopping[df_shopping['LIBELLE_REGROUPEMENT_8_POSTES'] != 'Local vacant']

    # Identify the IRIS of each shop
    df_shopping = df_shopping.sjoin(df_iris.loc[:, ["geometry"]], how="inner")

    # Group by IRIS (weighted by shop size categories)
    df_shopping = df_shopping.groupby("index_right")[["surface_code"]].sum()
    df_shopping.index.rename("iris", inplace=True)
    df_shopping.rename(columns={'surface_code':'shops_weighted'}, inplace=True)

    return df_shopping

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


def get_metro_rer_passengers_per_iris(df_metro_raw: pd.DataFrame, df_iris: gpd.GeoDataFrame) -> pd.DataFrame:
    """Compute number of metro and RER passengers per IRIS.

    Args:
        df_metro_raw (pd.DataFrame): Raw data with number of metro passengers per station
        df_iris (gpd.GeoDataFrame): Raw data with location of all IRIS within the city.

    Returns:
        pd.DataFrame: Number of metro passengers per IRIS.
    """
    # Clean metro data
    # Include only stations in Paris
    # Include only relevant columns
    df_metro = (
        df_metro_raw
        .loc[
            df_metro_raw["Ville"].isin(["Paris"]),
            ["Station", "Trafic"]
        ]
        .rename(columns={"Station": "station", "Trafic": "nb_metro_rer_passengers"})
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

    # Identify the IRIS of each station
    df_metro = df_metro.sjoin(df_iris.loc[:, ["geometry"]], how="inner")

    # Get the total number of metro passengers per IRIS
    df_metro = df_metro.groupby("index_right")[["nb_metro_rer_passengers"]].sum()
    df_metro.index.rename("iris", inplace=True)

    return df_metro


def get_train_passengers_per_iris(df_train_raw: pd.DataFrame, df_iris: gpd.GeoDataFrame) -> pd.DataFrame:
    """Compute number of train passengers per IRIS.

    Args:
        df_train_raw (pd.DataFrame): Raw data with number of train passengers per station
        df_iris (gpd.GeoDataFrame): Raw data with location of all IRIS within the city.

    Returns:
        pd.DataFrame: Number of train passengers per IRIS.
    """
    # Clean train data
    # Get the most recent column with number of passengers
    nb_passengers_col = sorted([col for col in df_train_raw.columns if col.startswith("Total Voyageurs 2")], reverse=True)[0]

    # Include only stations in Paris (postal code starts with 75)
    # Include only relevant columns
    df_train = (
        df_train_raw
        .loc[
            df_train_raw["Code postal"].astype(str).str.startswith("75"),
            ["Nom de la gare", nb_passengers_col]
        ]
        .rename(columns={"Nom de la gare": "station", nb_passengers_col: "nb_train_passengers"})
        .copy()
    )

    # Add string ", station" to every station name, to avoid confusions with stations names that are too general
    # E.g. "Hotel de Ville" (city hall) exists in every city
    df_train["station_city"] = df_train["station"] + ", paris"

    # Geocode station names
    df_train = (
        geocode_from_location_name(df_train, "station_city")
        .drop(columns="station_city")
    )

    # Identify the IRIS of each station
    df_train = df_train.sjoin(df_iris.loc[:, ["geometry"]], how="inner")

    # Get the total number of metro passengers per IRIS
    df_train = df_train.groupby("index_right")[["nb_train_passengers"]].sum()
    df_train.index.rename("iris", inplace=True)

    return df_train

def get_museum_visitors_per_iris(df_museums_clean: gpd.GeoDataFrame, df_iris: gpd.GeoDataFrame) -> pd.DataFrame:
    """Compute yearly museum visitors per IRIS.
    Args:
        df_museums_clean (gpd.GeoDataFrame): Cleaned data with location and number of visitors in national museums per year.
        df_iris (gpd.GeoDataFrame): Raw data with location of all IRIS within the city.
    Returns:
        pd.DataFrame: Number of yearly museum visitors per IRIS.
    """
    # Identify the IRIS of each museum
    df_museums = df_museums_clean.sjoin(df_iris.loc[:, ["geometry"]], how="inner")

    # Get the total number of yearly visitors per IRIS
    df_museums = df_museums.groupby("index_right")[["visitors"]].sum()
    df_museums.index.rename("iris", inplace=True)

    return df_museums

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
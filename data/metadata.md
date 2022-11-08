# Data documentation

## Parking data

Filepath: data/raw/stationnement-voie-publique-emplacements.geojson

Source: https://opendata.paris.fr/explore/dataset/stationnement-voie-publique-emplacements

Metadata: https://opendata.paris.fr/explore/dataset/stationnement-voie-publique-emplacements

Notes:

- location of parking spots
- not the polygons, just the location. For polygons look for "emprises" on the same website

## Census data

Filepath: data/raw/RECENSEMENT_IRIS_POPULATION.geojson

Source: https://data-apur.opendata.arcgis.com/datasets/Apur::recensement-iris-population/about

Metadata: https://www.apur.org/open_data/Chiffres_cles_insee_2015_Liste_variables_niveau_iris.pdf

Notes:

- population, density, households, houses
- per age group, education level, children possession, employment status and type, car possession
- evolution over last 5/10 years
- area units: [IRIS](https://www.insee.fr/en/metadonnees/definition/c1523)

## Green spaces

Filepath: data/raw/espaces_verts.geojson

Source: https://opendata.paris.fr/explore/dataset/espaces_verts/information/

Metadata: https://opendata.paris.fr/explore/dataset/espaces_verts/information/

Notes:

- Not all parks are present (e.g. Tuileries, Luxembourg, Plantes, ...)

## Metro and RER stations

Filepath: data/raw/trafic-annuel-entrant-par-station-du-reseau-ferre-2021.csv

Source: https://data.ratp.fr/explore/dataset/trafic-annuel-entrant-par-station-du-reseau-ferre-2021/information/

Metadata: N/A

Notes:

- Only includes entries in the station, but not exchanges between lines

## Train stations

Filepath: data/raw/frequentation-gares.csv

Source: https://ressources.data.sncf.com/explore/dataset/frequentation-gares/information/

Metadata: https://ressources.data.sncf.com/explore/dataset/frequentation-gares/information/

## Museums

Filepath: data/raw/frequentation-des-musees-de-france.csv

Source: https://data.culture.gouv.fr/explore/dataset/frequentation-des-musees-de-france/table/?sort=annee&q=ville%3D%22PARIS%22

Metadata: https://data.culture.gouv.fr/explore/dataset/frequentation-des-musees-de-france/information/?sort=annee&q=ville%3D%22PARIS%22

Notes:

- Total visitors per year of state museums ("Musée de France")

## île de France Mobilité parking (in train stations)

Filepath: data/raw/parking-velos-ile-de-france-mobilites.csv

Source: https://prim.iledefrance-mobilites.fr/fr/donnees-statiques/parking-velos-ile-de-france-mobilites

Metadata: https://prim.iledefrance-mobilites.fr/fr/donnees-statiques/parking-velos-ile-de-france-mobilites

Notes:

- Parking spots in train stations by Île de France Mobilité
- Includes closed/secure parking accessible with local transport pass/pass Navigo (type="consigne"), as well as open parking (type="abri")

## Schools

Filepath: data/raw/EQUIPEMENT_PONCTUEL_ENSEIGNEMENT_EDUCATION.geojson

Source: https://opendata.apur.org/datasets/Apur::equipement-ponctuel-enseignement-education/about

## Shops

Filepath: data/raw/BDCOM_2020.geojson

Source: https://opendata.apur.org/datasets/Apur::bdcom-2020-1/about

Metadata: https://geocatalogue.apur.org/catalogue/srv/fre/catalog.search#/metadata/4dab9088-f018-4379-83ec-1b0383b7435a

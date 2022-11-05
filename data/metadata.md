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

Notes:

- Only includes entries in the station, but not exchanges between lines

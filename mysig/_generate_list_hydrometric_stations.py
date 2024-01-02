import requests
import geopandas as gpd

from myhubeau.collect import _get_dataframe


# collect list of hydrometric stations still operating as dataframe
df = _get_dataframe(
    endpoint="v1/hydrometrie",
    operation="referentiel/stations",
    parameters={
        'fields': 'code_station,longitude_station,latitude_station',
        'en_service': 'true',
        'size': 10000
    }
)

# convert dataframe to WGS84 geodataframe
gdf = gpd.GeoDataFrame(
    df,
    geometry=gpd.points_from_xy(
        df.longitude_station, df.latitude_station
    ),
    crs="EPSG:4326"
)

# retain only stations with streamflow data
streamflow = []
for code in gdf['code_station'].values:
    # query real-time API for hydrometry
    url = (
        f"https://hubeau.eaufrance.fr/api/v1/hydrometrie/observations_tr?"
        f"code_entite={code}&grandeur_hydro=Q"
    )
    r = requests.get(url)

    # check that query is a success
    if r.status_code in [200, 206]:
        # check that data field does contain some data
        if r.json()['data']:
            streamflow.append(code)

gdf = gdf[gdf['code_station'].isin(streamflow)]

# save as geoJSON file
with open('database/stations_hydro_hydroportail_en-service+Q.geojson', 'w') as f:
    f.write(gdf.to_json(drop_id=True, to_wgs84=True))

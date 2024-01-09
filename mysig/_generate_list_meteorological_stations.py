import os
import requests
import pandas as pd
import geopandas as gpd

from mymeteofrance.collect import (
    _set_and_get_meteorology_stations, _get_json,
    _meteorology_daily_variables
)


api_key = os.environ['MyMeteoFranceAPIKey']

# collect list of real-time public open meteorological stations
meteorology_stations = _set_and_get_meteorology_stations(
    api_key=api_key,
    station_types=(0, 1, 2),
    public_stations_only=True,
    open_stations_only=True
)

# collect relevant information about the stations
df = pd.DataFrame(
    {
        'RR': pd.Series(dtype='bool'),
        'ETPMON': pd.Series(dtype='bool'),
        'ETPGRILLE': pd.Series(dtype='bool'),
        'TM': pd.Series(dtype='bool'),
        'lat': pd.Series(dtype='float64'),
        'lon': pd.Series(dtype='float64'),
        'alt': pd.Series(dtype='float64')
     }
)
df = df.reindex(meteorology_stations)

for station_id in meteorology_stations:
    # collect information for station
    info = _get_json(
        'https://public-api.meteofrance.fr/public/DPClim/v1/'
        f'information-station?id-station={station_id}',
        api_key=api_key, success_code=200
    )[0]

    # collect list of available variables at station
    available_variables = [p['nom'] for p in info['parametres']]

    for var in ['RR', 'ETPMON', 'ETPGRILLE', 'TM']:
        df.loc[station_id, var] = (
            _meteorology_daily_variables[var] in available_variables
        )

    # collect position of station
    pos = info['positions'][-1]

    df.loc[station_id, 'lat'] = pos['latitude']
    df.loc[station_id, 'lon'] = pos['longitude']
    df.loc[station_id, 'alt'] = pos['altitude']

df = df.reset_index(drop=False, names='station_id')

# convert dataframe to WGS84 geodataframe
gdf = gpd.GeoDataFrame(
    df,
    geometry=gpd.points_from_xy(
        df.lon, df.lat
    ),
    crs="EPSG:4326"
)

# save as geoJSON file
with open('database/stations_meteo_meteofranceapi_temps-reel+publique+ouverte.geojson', 'w') as f:
    f.write(gdf.to_json(drop_id=True, to_wgs84=True))

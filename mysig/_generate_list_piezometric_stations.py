import requests
import pandas as pd
import geopandas as gpd

from myhubeau.collect import _get_dataframe


# collect list of piezometric stations as dataframe
df = None
for departement in (
        [f'{i:02}' for i in range(1, 96) if i != 20]
        + ['2A', '2B', '971', '972', '973', '974', '976']
):
    df = pd.concat(
        [
            df, _get_dataframe(
                endpoint="v1/niveaux_nappes",
                operation="stations",
                parameters={
                    'fields': 'code_bss,bss_id,x,y',
                    'code_departement': departement,
                    'size': 10000
                }
            )
        ]
    )

# convert dataframe to WGS84 geodataframe
gdf = gpd.GeoDataFrame(
    df,
    geometry=gpd.points_from_xy(
        df.x, df.y
    ),
    crs="EPSG:4326"
)

# retain only real-time stations
realtime = []
for code in gdf['code_bss'].values:
    # query real-time API for piezometry
    url = (
        f"https://hubeau.eaufrance.fr/api/v1/niveaux_nappes/chroniques_tr?"
        f"code_bss={code}"
    )
    r = requests.get(url)

    # check that query is a success
    if r.status_code in [200, 206]:
        # check that data field does contain some data
        if r.json()['data']:
            realtime.append(code)

gdf = gdf[gdf['code_bss'].isin(realtime)]

# save as geoJSON file
with open('database/stations_piezo_ades_real-time.geojson', 'w') as file:
    file.write(gdf.to_json(drop_id=True, to_wgs84=True))

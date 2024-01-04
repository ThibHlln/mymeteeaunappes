from mymeteofrance.collect import get_meteorology


key = 'paste your API key here'

df = get_meteorology(
    variables=['RR', 'ETPMON', 'TM'],
    station_id=20004002,
    start='2021-01-01 00:00:00', end='2022-12-31 00:00:00',
    check_station_id=False,
    api_key=key
)

print(df)

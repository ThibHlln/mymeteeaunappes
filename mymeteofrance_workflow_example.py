from mymeteofrance.collect import get_meteorology


key = 'paste your API key here'

df = get_meteorology(
    variables=['RR'],
    station_id=20004002,
    api_key=key
)

print(df)

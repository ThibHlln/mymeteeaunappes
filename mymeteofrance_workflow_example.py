from mymeteofrance.store import save_meteorology


key = 'paste your API key here'

working_dir = 'examples/my-example'

save_meteorology(
    variables=['RR', 'ETPMON', 'TM'],
    station_id=20004002,
    working_dir=working_dir, filename='demo-{}.prn',
    start='2021-01-01 00:00:00', end='2022-12-31 00:00:00',
    check_station_id=False,
    api_key=key
)

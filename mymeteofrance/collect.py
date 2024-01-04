import requests
import time
import io
import numpy as np
import pandas as pd
import datetime


# "global" (module-wide) variables for memoization
_meteorology_stations = None


def _get_json(
        url: str, api_key: str, success_code: int
) -> list | dict | None:
    r = requests.get(url, headers={'apikey': api_key})

    if r.status_code == success_code:
        return r.json()
    elif r.status_code == 429:
        # too many requests, so delay before trying again (50 requests per min)
        time.sleep(60)
        return _get_json(url, api_key, success_code)
    else:
        raise RuntimeError(
            f"JSON retrieval failed (code: {r.status_code}) "
            f"for query with URL {url}: {r.reason}"
        )


def _get_text(url: str, api_key: str) -> str | None:
    # request order
    r = requests.get(url, headers={'apikey': api_key})

    # retrieve order as text
    if r.status_code == 201:
        # file returned
        return r.text
    elif r.status_code == 204:
        # file still being processed
        time.sleep(1)
        return _get_text(url, api_key)
    elif r.status_code == 500:
        # order failed (most likely because empty slice)
        return None
    else:
        raise RuntimeError(
            f"TEXT retrieval failed (code: {r.status_code}) "
            f"for query with URL {url}: {r.reason}"
        )


def _get_data(station_id: int, start: str, end: str, api_key: str) -> str:
    # order data
    params = {
        'id-station': station_id,
        'date-deb-periode': start,
        'date-fin-periode': end
    }

    order_id = _get_json(
        'https://public-api.meteofrance.fr/public/DPClim/v1/'
        'commande-station/quotidienne?'
        + f"{'&'.join(['='.join([k, str(v)]) for k, v in params.items()])}",
        api_key=api_key, success_code=202
    )['elaboreProduitAvecDemandeResponse']['return']

    # collect order and return it
    return _get_text(
        'https://public-api.meteofrance.fr/public/DPClim/v1/'
        f'commande/fichier?id-cmde={order_id}',
        api_key=api_key
    )


def _get_dataframe(
        variables: list, station_id: int, start: str, end: str, api_key: str
) -> pd.DataFrame | None:
    # collect data
    data = _get_data(station_id, start, end, api_key)

    if data is not None:
        # convert text to dataframe
        df = pd.read_csv(
            io.StringIO(data),
            delimiter=';', decimal=",", header=0
        )

        # turn date column into proper datetime
        df['DATE'] = pd.to_datetime(df['DATE'], format='%Y%m%d')

        # eliminate potential variable duplicates
        variables = set(variables)

        # check all variables are available in dataframe
        if not variables.issubset(set(df.columns)):
            raise KeyError(
                f"{variables.difference(df.columns)} not available "
                f"for station {station_id}"
            )

        # subset dataframe to dates and requested variables only
        df = df[['DATE'] + list(variables)]

        print(
            f"collected data for station {station_id} "
            f"for period {start} to {end}"
        )

        return df
    else:
        print(
            f"failed to collect data for station {station_id} "
            f"for period {start} to {end}"
        )

        return None


def _set_and_get_meteorology_stations(
        api_key: str, station_types: tuple = None,
        open_stations_only: bool = True,
        public_stations_only: bool = True
) -> list:
    global _meteorology_stations

    # set list of available stations still in operation
    meteorology_stations = None
    for dpt in (
            [i for i in range(1, 96)]
            + ['971', '972', '973', '974', '975']
            + ['984', '985', '986', '987', '988']
    ):
        meteorology_stations = pd.concat(
            [
                meteorology_stations,
                pd.concat(
                    [
                        pd.DataFrame.from_dict(i, orient='index')
                        for i in _get_json(
                            'https://public-api.meteofrance.fr/'
                            'public/DPClim/v1/liste-stations/quotidienne?'
                            f'id-departement={dpt}',
                            api_key=api_key, success_code=200
                        )
                    ],
                    axis=1
                ).T
            ]
        )

    # check whether at least one station exists
    if meteorology_stations is not None:
        mask = np.ones(len(meteorology_stations), dtype=bool)

        if station_types:
            mask = mask & np.isin(
                meteorology_stations['typePoste'].values, station_types
            )
        if open_stations_only:
            mask = mask & meteorology_stations['posteOuvert'].values
        if public_stations_only:
            mask = mask & meteorology_stations['postePublic'].values

        _meteorology_stations = (
            meteorology_stations[mask]['id'].values.tolist()
        )
    else:
        _meteorology_stations = []

    return _meteorology_stations


def get_meteorology(
        variables: list, station_id: int, api_key: str,
        start: str = None, end: str = None,
        realtime_only: bool = False, public_only: bool = True,
        open_only: bool = True
):
    # collect list of meteorological stations (if not already collected)
    meteorology_stations = (
        _meteorology_stations if _meteorology_stations is not None
        else _set_and_get_meteorology_stations(
            api_key=api_key,
            station_types=(0, 1, 2) if realtime_only else None,
            public_stations_only=public_only,
            open_stations_only=open_only
        )
    )

    # check station ID is available
    if str(station_id) not in meteorology_stations:
        raise ValueError(
            f"station ID {repr(station_id)} is not "
            f"available from MeteoFrance API"
        )

    # collect opening (and potentially closing) dates for station
    info = _get_json(
        'https://public-api.meteofrance.fr/public/DPClim/v1/'
        f'information-station?id-station={station_id}',
        api_key=api_key, success_code=200
    )[0]

    open_date = pd.to_datetime(info['dateDebut'])
    if info['dateFin']:
        close_date = pd.to_datetime(info['dateFin'])
    else:
        now_date = pd.to_datetime('now')
        # previous day only available after 11:30am (French time)
        if now_date.time() > datetime.time(11, 30, 0, 0):
            close_date = (
                now_date.replace(hour=0, minute=0, second=0, microsecond=0)
                - pd.Timedelta(days=1)
            )
        else:
            close_date = (
                now_date.replace(hour=0, minute=0, second=0, microsecond=0)
                - pd.Timedelta(days=2)
            )

    # choose between user-provided period and station period
    if start:
        start_date = pd.to_datetime(start)
        # if sooner than opening date, use opening date instead
        if start_date < open_date:
            start_date = open_date
    else:
        start_date = open_date

    if end:
        end_date = pd.to_datetime(end)
        # if later than closing date, use closing date instead
        if end_date > close_date:
            end_date = close_date
    else:
        end_date = close_date

    # collect data one year at a time
    df = pd.DataFrame(
        {'DATE': pd.Series(dtype='datetime64[ns]')}
        | {var: pd.Series(dtype='float64') for var in list(set(variables))}
    )

    # first year
    df = pd.concat(
        [
            df,
            _get_dataframe(
                variables=variables, station_id=station_id,
                start=start_date.strftime('%Y-%m-%dT%H:%M:%SZ'),
                end=f'{start_date.year}-12-31T00:00:00Z',
                api_key=api_key
            )
        ]
    )

    # years in between
    for yr in range(start_date.year + 1, end_date.year):
        df = pd.concat(
            [
                df,
                _get_dataframe(
                    variables=variables, station_id=station_id,
                    start=f'{yr}-01-01T00:00:00Z',
                    end=f'{yr}-12-31T00:00:00Z',
                    api_key=api_key
                )
            ]
        )

    # last year
    df = pd.concat(
        [
            df,
            _get_dataframe(
                variables=variables, station_id=station_id,
                start=f'{end_date.year}-01-01T00:00:00Z',
                end=end_date.strftime('%Y-%m-%dT%H:%M:%SZ'),
                api_key=api_key
            )
        ]
    )

    return df.reset_index(drop=True)

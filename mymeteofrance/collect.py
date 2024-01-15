import requests
import time
import io
import numpy as np
import pandas as pd
import datetime


# "global" (module-wide) variables for memoization
_meteorology_stations = None

_meteorology_daily_variables = {
    "BA300": "HAUTEUR MINIMALE DE LA COUCHE >300M AVEC UNE NEBULOSITE MAXI > 4/8",
    "BROU": "OCCURRENCE DE BROUILLARD QUOTIDIENNE",
    "BRUME": "OCCURRENCE DE BRUME QUOTIDIENNE",
    "DG": "DUREE DE GEL QUOTIDIENNE",
    "DHUMEC": "DUREE HUMECTATION QUOTIDIENNE",
    "DHUMI40": "DUREE HUMIDITE <= 40% QUOTIDIENNE",
    "DHUMI80": "DUREE HUMIDITE >= 80% QUOTIDIENNE",
    "DIFT": "RAYONNEMENT DIFFUS QUOTIDIEN",
    "DIRT": "RAYONNEMENT DIRECT QUOTIDIEN",
    "DRR": "DUREE DES PRECIPITATIONS QUOTIDIENNES",
    "DXI": "DIRECTION VENT MAXI INSTANTANE QUOTIDIEN",
    "DXI2": "DIRECTION DU VENT INSTANTANE MAXI QUOTIDIEN A 2 M",
    "DXI3S": "DIRECTION DU VENT INSTANTANE SUR 3 SECONDES",
    "DXY": "DIRECTION VENT QUOTIDIEN MAXI MOYENNE SUR 10 MIN ",
    "ECLAIR": "OCCURRENCE ECLAIR QUOTIDIENNE",
    "ETPGRILLE": "ETP CALCULEE AU POINT DE GRILLE LE PLUS PROCHE",
    "ETPMON": "EVAPO-TRANSPIRATION MONTEITH QUOTIDIENNE",
    "FF2M": "MOYENNE DES VITESSES DU VENT A 2 METRES QUOTIDIENNE",
    "FFM": "MOYENNE DES VITESSES DU VENT A 10M QUOTIDIENNE",
    "FUMEE": "OCCURRENCE DE FUMEE QUOTIDIENNE",
    "FXI": "VITESSE VENT MAXI INSTANTANE QUOTIDIENNE",
    "FXI2": "VITESSE DU VENT INSTANTANE MAXI QUOTIDIEN A 2 M",
    "FXI3S": "VITESSE DU VENT INSTANTANE SUR 3 SECONDES, MAXI DANS L'HEURE",
    "FXY": "VITESSE VENT QUOTIDIEN MAXI MOYENNE SUR 10 MIN ",
    "GELEE": "OCCURRENCE DE GELEE QUOTIDIENNE",
    "GLOT": "RAYONNEMENT GLOBAL QUOTIDIEN",
    "GRELE": "OCCURRENCE DE GRELE QUOTIDIENNE",
    "GRESIL": "OCCURENCE DE GRESIL QUOTIDIENNE",
    "HNEIGEF": "HAUTEUR DE NEIGE TOMBEE EN 24H",
    "HTN": "HEURE DU TN SOUS ABRI QUOTIDIENNE",
    "HTX": "HEURE DU TX SOUS ABRI QUOTIDIENNE",
    "HUN": "HEURE DU MINI D'HUMIDITE QUOTIDIENNE",
    "HUX": "HEURE DU MAXI D'HUMIDITE QUOTIDIENNE",
    "HXI": "HEURE VENT MAXI INSTANTANE QUOTIDIEN",
    "HXI2": "HEURE DU VENT MAX INSTANTANE A 2 M QUOTIDIENNE",
    "HXI3S": "HEURE DU VENT INSTANTANE SUR 3 SECONDES",
    "HXY": "HEURE VENT QUOTIDIEN MAXI MOYENNE SUR 10 MIN ",
    "INFRART": "SOMME DES RAYONNEMENTS IR HORAIRE",
    "INST": "DUREE D'INSOLATION QUOTIDIENNE",
    "NB300": "NEBULOSITE MAXIMALE > 4/8 D'UNE COUCHE < 300 M",
    "NEIG": "OCCURRENCE DE NEIGE QUOTIDIENNE",
    "NEIGETOT06": "EPAISSEUR DE NEIGE TOTALE RELEVEE A 0600 FU",
    "NEIGETOTX": "MAXIMUM QUOTIDIEN DES EPAISSEURS DE NEIGE TOTALE HORAIRE",
    "ORAG": "OCCURRENCE D'ORAGE QUOTIDIENNE",
    "PMERM": "PRESSION MER MOYENNE QUOTIDIENNE",
    "PMERMIN": "PRESSION MER MINIMUM QUOTIDIENNE",
    "ROSEE": "OCCURRENCE DE ROSEE QUOTIDIENNE",
    "RR": "HAUTEUR DE PRECIPITATIONS QUOTIDIENNE",
    "SIGMA": "RAPPORT INSOLATION QUOTIDIEN",
    "SOLNEIGE": "OCCURRENCE DE SOL COUVERT DE NEIGE",
    "TAMPLI": "AMPLITUDE ENTRE TN ET TX QUOTIDIEN",
    "TM": "TEMPERATURE MOYENNE SOUS ABRI QUOTIDIENNE",
    "TMERMAX": "TEMPERATURE MAXIMALE QUOTIDIENNE DE L'EAU DE MER",
    "TMERMIN": "TEMPERATURE MINIMALE QUOTIDIENNE DE L'EAU DE MER",
    "TMNX": "TEMPERATURE MOYENNE SOUS ABRI QUOTIDIENNE A PARTIR DE (TN+TX)/2",
    "TN": "TEMPERATURE MINIMALE SOUS ABRI QUOTIDIENNE",
    "TN50": "TEMPERATURE MINI A +50CM QUOTIDIENNE",
    "TNSOL": "TEMPERATURE MINIMALE A +10CM QUOTIDIENNE",
    "TNTXM": "MOYENNE DE TN ET TX QUOTIDIEN",
    "TSVM": "TENSION DE VAPEUR MOYENNE QUOTIDIENNE",
    "TX": "TEMPER'ATURE MAXIMALE SOUS ABRI QUOTIDIENNE",
    "UM": "HUMIDITE RELATIVE MOYENNE",
    "UN": "HUMIDITE RELATIVE MINIMALE QUOTIDIENNE",
    "UV": "RAYONNEMENT ULTRA VIOLET QUOTIDIEN",
    "UV_INDICEX": "MAX DES INDICES UV HORAIRE",
    "UX": "HUMIDITE RELATIVE MAXIMALE QUOTIDIENNE",
    "VERGLAS": "OCCURRENCE DE VERGLAS"
}


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
        check_station_id: bool = True, realtime_only: bool = False,
        public_only: bool = True, open_only: bool = True
):
    """Collect record of meteorological data for a given MeteoFrance
    station ID.

    :Parameters:

        variables: `list`
            The list of variables to collect for the given meteorological
            station. The following table contains a subset of variables
            that can be collected via the MeteoFrance API:

            ==========  ========  ======================================
            variable    unit      description
            ==========  ========  ======================================
            RR          mm        daily rainfall depth
            ETPMON      mm        daily Monteith evapotranspiration
            TM          °C        mean daily air temperature
            ==========  ========  ======================================

            A full list of variables available via the MeteoFrance API
            can be found at: https://donneespubliques.meteofrance.fr/client/
            document/api_clim_table_parametres_quotidiens_20240103_354.csv.

        station_id: `str`
            The 8-digit ID for the meteorological station for which data
            is to be collected.

        api_key: `str`
            The API key generated on https://portail-api.meteofrance.fr.

        start: `str`, optional
            The start date to use for the data time series. The date must
            be specified in a string following the ISO 8601-1:2019 standard,
            i.e. “YYYY-MM-DD” (e.g. the 21st of May 2007 is “2007-05-21”).
            If not provided, the earliest date in the available data is used.

        end: `str`, optional
            The end date to use for the data time series. The date must
            be specified in a string following the ISO 8601-1:2019 standard,
            i.e. “YYYY-MM-DD” (e.g. the 21st of May 2007 is “2007-05-21”).
            If not provided, the latest date in the available data is used.

        check_station_id: `bool`, optional
            Whether to check if the station ID exists before collecting
            the data. If not provided, set to default value `True`.

        realtime_only: `bool`, optional
            Whether to check if the station ID corresponds to a real-time
            station. If not provided, set to default value `False`. This
            parameter is only relevant if *check_station_id* is `True`.

        open_only: `bool`, optional
            Whether to check if the station ID corresponds to a station
            still in operation. If not provided, set to default value
            `True`. This parameter is only relevant if *check_station_id*
            is `True`.

        public_only: `bool`, optional
            Whether to check if the station ID corresponds to a public
            station. If not provided, set to default value `True`. This
            parameter is only relevant if *check_station_id* is `True`.

    :Returns:

        `pandas.DataFrame` or `None`
            The dataframe containing the meteorological time series (one
            column *DATE* plus as many columns as they are *variables*).
            If no data is available on MeteoFrance, `None` is returned.
    """
    if check_station_id:
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

    # collect information on station
    info = _get_json(
        'https://public-api.meteofrance.fr/public/DPClim/v1/'
        f'information-station?id-station={station_id}',
        api_key=api_key, success_code=200
    )[0]

    # check availability of variables
    available_variables = [p['nom'] for p in info['parametres']]
    for var in variables:
        if _meteorology_daily_variables[var] not in available_variables:
            raise ValueError(
                f"variable {repr(var)} is not available from "
                f"MeteoFrance API for station {station_id}"
            )

    # collect opening (and potentially closing) dates for station
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

    # sanity check on dates
    if start_date > end_date:
        raise RuntimeError(
            f"start date cannot be later than end date "
            f"({start_date} > {end_date})"
        )

    # collect data one year at a time
    df = pd.DataFrame(
        {'DATE': pd.Series(dtype='datetime64[ns]')}
        | {var: pd.Series(dtype='float64') for var in list(set(variables))}
    )

    # check if period is over multiple calendar years
    if end_date.year > start_date.year:
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
    else:
        df = pd.concat(
            [
                df,
                _get_dataframe(
                    variables=variables, station_id=station_id,
                    start=start_date.strftime('%Y-%m-%dT%H:%M:%SZ'),
                    end=end_date.strftime('%Y-%m-%dT%H:%M:%SZ'),
                    api_key=api_key
                )
            ]
        )

    return df.reset_index(drop=True)

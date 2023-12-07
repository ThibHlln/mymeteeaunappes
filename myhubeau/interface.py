import requests
import pandas as pd
import numpy as np
import re


def _get_data(url, data):
    r = requests.get(url)

    if r.status_code == 200:
        data.extend(r.json()['data'])
        return data
    elif r.status_code == 206:
        data.extend(r.json()['data'])
        return _get_data(r.json()['next'], data)
    else:
        raise RuntimeError(
            f"data retrieval failed for query with URL {url}"
        )


def _get_dataframe(endpoint: str, operation: str, parameters: dict):
    _url = (
        f"https://hubeau.eaufrance.fr/api/{endpoint}/{operation}?"
        f"{'&'.join(['='.join([k, str(v)]) for k, v in parameters.items()])}"
    )

    data = []

    data = _get_data(_url, data)

    return pd.concat(
        [pd.DataFrame.from_dict(i, orient='index') for i in data],
        axis=1
    ).T


def get_hydrometry(code_station: str):
    # get list of available stations still on operation
    stations = _get_dataframe(
        endpoint="v1/hydrometrie",
        operation="referentiel/stations",
        parameters={
            'fields': 'code_station,en_service',
            'size': 10000
        }
    )

    # check code station is available
    if code_station not in stations['code_station'].values:
        raise ValueError(
            f"code station {repr(code_station)} is not "
            f"available in Hub'Eau hydrometry API"
        )

    # check station is still in operation
    if code_station not in (
            stations[stations['en_service']]['code_station'].values
    ):
        raise ValueError(
            f"code station {repr(code_station)} is not "
            f"in operation anymore"
        )

    # get elaborated data
    try:
        data_elab = _get_dataframe(
            endpoint="v1/hydrometrie",
            operation="obs_elab",
            parameters={
                'code_entite': code_station,
                'grandeur_hydro': 'Q',
                'fields': ','.join(
                    ['date_obs_elab', 'resultat_obs_elab', 'code_statut']
                ),
                'size': 10000
            }
        )
    except RuntimeError as e:
        raise RuntimeError(
            f"elaborated hydrometric data retrieval failed "
            f"for {code_station}"
        ) from e

    # check elaborated data quality
    data_elab['resultat_obs_elab'][
        np.isin(data_elab['code_statut'].values, ('16', '20'))
    ] = np.nan
    data_elab.drop(columns='code_statut', inplace=True)

    # get real time data
    try:
        data_tr = _get_dataframe(
            endpoint="v1/hydrometrie",
            operation="observations_tr",
            parameters={
                'code_entite': code_station,
                'grandeur_hydro': 'Q',
                'fields': ','.join(
                    ['date_obs', 'resultat_obs']
                ),
                'size': 10000
            }
        )
    except RuntimeError as e:
        raise RuntimeError(
            f"real-time hydrometric data retrieval failed "
            f"for {code_station}"
        ) from e

    # aggregate real-time data to mean daily values
    data_tr['date_obs'] = pd.to_datetime(
        data_tr['date_obs'], format='%Y-%m-%dT%H:%M:%SZ'
    )
    data_tr.set_index('date_obs', inplace=True)
    data_tr = data_tr.resample('D').agg('mean')
    data_tr.reset_index(inplace=True)

    # merge datasets
    data_elab['date_obs_elab'] = pd.to_datetime(
        data_elab['date_obs_elab'], format='%Y-%m-%d'
    )
    data_elab.columns = ['Date', 'Debit']
    data_tr.columns = ['Date', 'Debit']

    data = pd.concat([data_elab, data_tr])

    return data.reset_index(drop=True)


def get_piezometry(code_bss: str):
    # check code format
    if not re.compile(r'^\d{5}[A-Z]\d{4}/[-A-Z]+$').findall(code_bss):
        raise ValueError(
            "code_bss format is invalid"
        )

    return _get_dataframe(
        endpoint="v1/niveaux_nappes",
        operation="chroniques",
        parameters={
            'code_bss': code_bss,
            'size': 10000
        }
    )


def get_withdrawal(code_ouvrage: str):
    # check code format
    if not re.compile(r'^OPR\d{10}$').findall(code_ouvrage):
        raise ValueError(
            "code_ouvrage format is invalid"
        )

    return _get_dataframe(
        endpoint="v1/prelevements",
        operation="chroniques",
        parameters={
            'code_ouvrage': code_ouvrage,
            'size': 10000
        }
    )

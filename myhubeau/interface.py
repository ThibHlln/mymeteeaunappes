import requests
import pandas as pd
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

    _data = []

    _data = _get_data(_url, _data)

    return pd.concat(
        [pd.DataFrame.from_dict(i, orient='index') for i in _data],
        axis=1
    ).T


def get_hydrometry(code_entite: str):
    # check code format
    if not re.compile(r'^[A-Z]\d{9}$').findall(code_entite):
        raise ValueError(
            "code_entite format is invalid"
        )

    return _get_dataframe(
        endpoint="v1/hydrometrie",
        operation="observations_tr",
        parameters={
            'code_entite': code_entite,
            'grandeur_hydro': 'Q',
            'size': 10000
        }
    )


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

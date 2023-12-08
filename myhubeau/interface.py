import requests
import pandas as pd
import numpy as np
import re


# "global" (module-wide) variables for memoization
_hydrometry_stations = None


def _get_json_data(url: str, data: list) -> list:
    r = requests.get(url)

    if r.status_code == 200:
        data.extend(r.json()['data'])
        return data
    elif r.status_code == 206:
        data.extend(r.json()['data'])
        return _get_json_data(r.json()['next'], data)
    else:
        raise RuntimeError(
            f"data retrieval failed for query with URL {url}"
        )


def _get_dataframe(endpoint: str, operation: str, parameters: dict) -> pd.DataFrame or None:
    url = (
        f"https://hubeau.eaufrance.fr/api/{endpoint}/{operation}?"
        f"{'&'.join(['='.join([k, str(v)]) for k, v in parameters.items()])}"
    )

    data = _get_json_data(url, [])

    if data:
        return pd.concat(
            [pd.DataFrame.from_dict(i, orient='index') for i in data],
            axis=1
        ).T


def _set_and_get_hydrometry_stations() -> list:
    global _hydrometry_stations

    # set list of available stations still in operation
    hydrometry_stations = _get_dataframe(
        endpoint="v1/hydrometrie",
        operation="referentiel/stations",
        parameters={
            'fields': 'code_station',
            'en_service': 'true',
            'size': 10000
        }
    )

    # check whether at least one station exists
    if hydrometry_stations is not None:
        _hydrometry_stations = (
            hydrometry_stations['code_station'].values.tolist()
        )
    else:
        _hydrometry_stations = []

    return _hydrometry_stations


def get_hydrometry(code_station: str) -> pd.DataFrame or None:
    # collect list of hydrometric stations (if not already collected)
    hydrometry_stations = (
        _hydrometry_stations if _hydrometry_stations is not None
        else _set_and_get_hydrometry_stations()
    )

    # check code station is available
    if code_station not in hydrometry_stations:
        raise ValueError(
            f"code station {repr(code_station)} is not "
            f"available in Hub'Eau hydrometry API or "
            f"is not in operation anymore"
        )

    # ------------------------------------------------------------------
    # get elaborated data
    # ------------------------------------------------------------------
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

    if data_elab is not None:
        # check elaborated data quality
        data_elab['resultat_obs_elab'][
            np.isin(data_elab['code_statut'].values, ('16', '20'))
        ] = np.nan
        data_elab.drop(columns='code_statut', inplace=True)

        # convert to datetime
        data_elab['date_obs_elab'] = pd.to_datetime(
            data_elab['date_obs_elab'], format='%Y-%m-%d'
        )
        # rename headers
        data_elab.columns = ['Date', 'Debit']

    # ------------------------------------------------------------------
    # get real time data
    # ------------------------------------------------------------------
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

    if data_tr is not None:
        # aggregate real-time data to mean daily values
        data_tr['date_obs'] = pd.to_datetime(
            data_tr['date_obs'], format='%Y-%m-%dT%H:%M:%SZ'
        )
        data_tr.set_index('date_obs', inplace=True)
        data_tr = data_tr.resample('D').agg('mean')
        data_tr.reset_index(inplace=True)

        # rename headers
        data_tr.columns = ['Date', 'Debit']

    # ------------------------------------------------------------------
    # return potentially aggregated elaborated and/or real-time data
    # ------------------------------------------------------------------
    if (data_elab is not None) or (data_tr is not None):
        data = pd.concat([data_elab, data_tr]).reset_index(drop=True)
        return data



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

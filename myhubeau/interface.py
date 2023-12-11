import requests
import pandas as pd
import numpy as np
import re


# "global" (module-wide) variables for memoization
_hydrometry_stations = None
_piezometry_stations = None


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


def _get_dataframe(
        endpoint: str, operation: str, parameters: dict
) -> pd.DataFrame | None:
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


def _get_consolidated_dataframe(
        api_kind: str, api_endpoint: str, api_operation: str,
        station_field: str, station_code: str,
        date_field: str, date_format: str, date_label: str,
        measure_field: str, measure_label: str,
        quality_field: str, good_quality_values: list,
        extra_parameters: dict = None
) -> pd.DataFrame | None:
    try:
        data = _get_dataframe(
            endpoint=api_endpoint,
            operation=api_operation,
            parameters={
                station_field: station_code,
                'fields': ','.join(
                    [date_field, measure_field, quality_field]
                ),
                'size': 10000
            } | (extra_parameters if extra_parameters else {})
        )
    except RuntimeError as e:
        raise RuntimeError(
            f"consolidated {api_kind} data retrieval "
            f"failed for {station_code}"
        ) from e

    if data is not None:
        # check consolidated data quality
        data[measure_field][
            ~np.isin(data[quality_field].values, good_quality_values)
        ] = np.nan
        data = data.drop(columns=quality_field)

        # convert to datetime
        data[date_field] = pd.to_datetime(
            data[date_field], format=date_format
        )
        # rename headers
        data.columns = [date_label, measure_label]

        return data


def _get_realtime_dataframe(
        api_kind: str, api_endpoint: str, api_operation: str,
        station_field: str, station_code: str,
        date_field: str, date_format: str, date_label: str,
        measure_field: str, measure_label: str,
        extra_parameters: dict = None
) -> pd.DataFrame | None:
    try:
        data = _get_dataframe(
            endpoint=api_endpoint,
            operation=api_operation,
            parameters={
                station_field: station_code,
                'fields': ','.join(
                    [date_field, measure_field]
                ),
                'size': 10000
            } | (extra_parameters if extra_parameters else {})
        )
    except RuntimeError as e:
        raise RuntimeError(
            f"real-time {api_kind} data retrieval "
            f"failed for {station_code}"
        ) from e

    if data is not None:
        # aggregate real-time data to mean daily values
        data[date_field] = pd.to_datetime(
            data[date_field], format=date_format
        )
        data = data.set_index(date_field)
        data = data.resample('D').agg('mean')
        data.reset_index(inplace=True)

        # rename headers
        data.columns = [date_label, measure_label]

        return data


def _merge_consolidated_and_realtime_dataframe(
        data_cons: (pd.DataFrame | None), data_tr: (pd.DataFrame | None),
        date_label: str, measure_label: str
) -> pd.DataFrame | None:

    if (data_cons is not None) or (data_tr is not None):
        # merge along dates
        data = pd.merge(
            left=(
                data_cons if data_cons is not None
                else pd.DataFrame(columns=[date_label, measure_label])
            ),
            right=(
                data_tr if data_tr is not None
                else pd.DataFrame(columns=[date_label, measure_label])
            ),
            on=date_label, how='outer', suffixes=('_cons', '_tr')
        )

        # deal with overlap (favour consolidated)
        data[measure_label] = np.where(
            # could use dates as filter rather than NaN because, towards
            # the end of the time series, real-time data are included in
            # consolidated data before being given a quality value but
            # there is no reason to include real-time data (without
            # quality value) and not to include consolidated data
            # without quality value
            data[f'{measure_label}_cons'].isna(),
            data[f'{measure_label}_tr'], data[f'{measure_label}_cons']
        )

        return data.drop(
            columns=[f'{measure_label}_cons', f'{measure_label}_tr']
        )


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


def get_hydrometry(code_station: str) -> pd.DataFrame | None:
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

    # set headers for output dataframe
    date_label = 'Date'
    measure_label = 'Debit'

    # get elaborated data
    data_cons = _get_consolidated_dataframe(
        api_kind='hydrometry', api_endpoint='v1/hydrometrie',
        api_operation='obs_elab',
        station_field='code_entite', station_code=code_station,
        date_field='date_obs_elab', date_format='%Y-%m-%d',
        date_label=date_label,
        measure_field='resultat_obs_elab', measure_label=measure_label,
        quality_field='code_qualification', good_quality_values=[16, 20],
        extra_parameters={'grandeur_hydro': 'Q'}
    )

    # get real time data
    data_tr = _get_realtime_dataframe(
        api_kind='hydrometry', api_endpoint='v1/hydrometrie',
        api_operation='observations_tr',
        station_field='code_entite', station_code=code_station,
        date_field='date_obs', date_format='%Y-%m-%dT%H:%M:%SZ',
        date_label=date_label,
        measure_field='resultat_obs', measure_label=measure_label,
        extra_parameters={'grandeur_hydro': 'Q'}
    )

    # return potentially aggregated elaborated and/or real-time data
    return _merge_consolidated_and_realtime_dataframe(
        data_cons, data_tr, date_label, measure_label
    )


# get list of available stations still on operation
def _set_and_get_piezometry_stations() -> list:
    global _piezometry_stations

    # (loop through departements to bypass 20000 query size limit)
    piezometry_stations = None
    for departement in (
            [f'{i:02}' for i in range(1, 96) if i != 20]
            + ['2A', '2B', '971', '972', '973', '974', '976']
    ):
        piezometry_stations = pd.concat(
            [
                piezometry_stations, _get_dataframe(
                    endpoint="v1/niveaux_nappes",
                    operation="stations",
                    parameters={
                        'fields': 'code_bss',
                        'code_departement': departement,
                        'size': 10000
                    }
                )
            ]
        )

    # check whether at least one station exists
    if piezometry_stations is not None:
        _piezometry_stations = (
            piezometry_stations['code_bss'].values.tolist()
        )
    else:
        _piezometry_stations = []

    return _piezometry_stations


def get_piezometry(code_bss: str) -> pd.DataFrame | None:
    # collect list of piezometric stations (if not already collected)
    piezometry_stations = (
        _piezometry_stations if _piezometry_stations is not None
        else _set_and_get_piezometry_stations()
    )

    # check code BSS is available
    if code_bss not in piezometry_stations:
        raise ValueError(
            f"code BSS {repr(code_bss)} is not "
            f"available in Hub'Eau piezometry API"
        )

    # set headers for output dataframe
    date_label = 'Date'
    measure_label = 'Niveau'

    # get consolidated data
    data_cons = _get_consolidated_dataframe(
        api_kind='piezometry', api_endpoint='v1/niveaux_nappes',
        api_operation='chroniques',
        station_field='code_bss', station_code=code_bss,
        date_field='date_mesure', date_format='%Y-%m-%d',
        date_label=date_label,
        measure_field='niveau_nappe_eau', measure_label=measure_label,
        quality_field='qualification', good_quality_values=['Correcte']
    )

    # get real time data
    data_tr = _get_realtime_dataframe(
        api_kind='piezometry', api_endpoint='v1/niveaux_nappes',
        api_operation='chroniques_tr',
        station_field='code_bss', station_code=code_bss,
        date_field='date_mesure', date_format='%Y-%m-%dT%H:%M:%SZ',
        date_label=date_label,
        measure_field='niveau_eau_ngf', measure_label=measure_label
    )

    # return potentially merged consolidated and/or real-time data
    return _merge_consolidated_and_realtime_dataframe(
        data_cons, data_tr, date_label, measure_label
    )


def get_withdrawal(code_ouvrage: str) -> pd.DataFrame | None:
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

import numpy as np
import pandas as pd
import itertools

from ._read import read_prn_file


def _calc_r_pearson(a: np.ndarray, b: np.ndarray) -> float:
    a_mean = np.mean(a)
    b_mean = np.mean(b)

    r_num = np.sum(
        (a - a_mean) * (b - b_mean)
    )
    r_den = np.sqrt(
        np.sum((a - a_mean) ** 2)
        * np.sum((b - b_mean) ** 2)
    )

    r = r_num / r_den

    return r


def _calc_r_spearman(a: np.ndarray, b: np.ndarray) -> float:
    a_rank = np.argsort(np.argsort(a))
    b_rank = np.argsort(np.argsort(b))

    r_num = np.sum(
        (a_rank - np.mean(a_rank)) * (b_rank - np.mean(b_rank))
    )
    r_den = np.sqrt(
        np.sum((a_rank - np.mean(a_rank)) ** 2)
        * np.sum((b_rank - np.mean(b_rank)) ** 2)
    )

    r = r_num / r_den

    return r


def compute_correlation_matrix(
    correlation_coefficient: str,
    working_dir: str,
    rainfall_filename: str = None,
    pet_filename: str = None,
    streamflow_filename: str = None,
    piezo_level_filename: str = None
) -> pd.DataFrame:
    """Compute the correlation between the given observations time series.

    :Parameters:

        correlation_coefficient: `str`
            The correlation coefficient to use. It can either be 'pearson'
             or 'spearman'.

        working_dir: `str`
            The file path the working directory where the data is stored
            in the 'data' subdirectory.

        rainfall_filename: `str`, optional
            The name of the file containing the rainfall data. If not
            provided, no rainfall data entry will be included in the
            returned correlation matrix.

        pet_filename: `str`, optional
            The name of the file containing the potential evapotranspiration
            data. If not provided, no rainfall data entry will be included
            in the returned correlation matrix.

        streamflow_filename: `str`, optional
            The name of the file containing the streamflow data. If not
            provided, no rainfall data entry will be included in the
            returned correlation matrix.

        piezo_level_filename: `str`, optional
            The name of the file containing the piezometric level data.
            If not provided, no rainfall data entry will be included in
            the returned correlation matrix.

    :Returns:

        `pd.DataFrame`
            The dataFrame containing the correlation matrix.
    """
    # read in the data time series as dataframes
    variables = {}
    if rainfall_filename is not None:
        variables['P'] = read_prn_file(
            working_dir, rainfall_filename, 'Pluie', None
        )['Pluie'].values
    if pet_filename is not None:
        variables['ETP'] = read_prn_file(
            working_dir, pet_filename, 'ETP', None
        )['ETP'].values
    if streamflow_filename is not None:
        variables['Q'] = read_prn_file(
            working_dir, streamflow_filename, 'Debit', -2
        )['Debit'].values
    if piezo_level_filename is not None:
        variables['Z'] = read_prn_file(
            working_dir, piezo_level_filename, 'Niveau', 9999
        )['Niveau'].values

    variable_names = list(variables.keys())

    # create correlation matrix
    df = pd.DataFrame(
        np.zeros((len(variables),) * 2, dtype=float),
        index=variable_names, columns=variable_names
    )
    df[:] = np.nan

    # compute correlations
    for a, b in itertools.permutations(variable_names, 2):
        msk = ~np.isnan(variables[a]) & ~np.isnan(variables[b])
        if not (~msk).all():
            arr_a = variables[a][msk]
            arr_b = variables[b][msk]

            if correlation_coefficient == 'pearson':
                corr = _calc_r_pearson(arr_a, arr_b)
            elif correlation_coefficient == 'spearman':
                corr = _calc_r_spearman(arr_a, arr_b)
            else:
                raise ValueError('unsupported correlation type')

            df[a][b] = corr
            df[b][a] = corr

    for v in variable_names:
        df[v][v] = 1

    return df

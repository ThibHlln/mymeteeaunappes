import os
import numpy as np
import pandas as pd
from datetime import datetime

from .collect import get_hydrometry, get_piezometry, get_withdrawal


def _save_df_as_prn_file(
        df: pd.DataFrame, working_dir: str, measure_label: str,
        missing_value: float, filename: str = None,
        start: str = None, end: str = None, freq: str = 'D'
):
    # adjust period to match start and end dates if provided
    start = (
        df['Date'].iloc[0] if (start is None)
        else datetime.strptime(start, '%Y-%m-%d')
    )
    end = (
        df['Date'].iloc[-1] if (end is None)
        else datetime.strptime(end, '%Y-%m-%d')
    )

    df = df.set_index('Date')
    df = df.reindex(pd.date_range(start, end, freq=freq), fill_value=np.nan)
    df = df.reset_index(names='Date')

    # fill in missing data with missing value flag
    if df[measure_label].isna().any():
        df.loc[df[measure_label].isna(), measure_label] = missing_value

    # save as PRN file
    filename = (
        filename if filename else
        f"my-{measure_label.lower().replace(' ', '-')}.prn"
    )
    df.to_csv(
        os.sep.join(
            [working_dir, "data", filename]
        ),
        index=False, sep='\t'
    )


def save_hydrometry(
        code_station: str, working_dir: str,
        filename: str = None,
        start: str = None, end: str = None,
        include_realtime: bool = True
):
    """Generate a PRN file containing the observed hydrometric data
    for a given station.

    :Parameters:

        code_station: `str`
            The code of the hydrometric station for which streamflow
            data is requested from HydroPortail via Hub'Eau.

        working_dir: `str`
            The file path the working directory to use to store the data.

        filename: `str`, optional
            The custom file name to use for storing the data. If not
            provided, the filename is set 'my-debit.prn'.

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

        include_realtime: `bool`, optional
            Whether to include real-time data (if available) and
            aggregate it with consolidated data. If not provided,
            set to default value `True`.

    :Returns:

        `None`

    **Examples**

    Generating a PRN file named *my-debit.prn* in *examples/my_example/data*
    containing consolidated and real-time daily streamflow data for the
    hydrometric station 'M107302001':

    >>> save_hydrometry(
    ...     code_station='M107302001', working_dir='examples/my_example'
    ... )

    Generating a PRN file named *my-debit.prn* in *examples/my_example/data*
    containing only consolidated daily streamflow data for the hydrometric
    station 'M107302001':

    >>> save_hydrometry(
    ...     code_station='M107302001', working_dir='examples/my_example',
    ...     include_realtime=False
    ... )

    Generating a PRN file named *my-debit.prn* in *examples/my_example/data*
    containing consolidated and real-time daily streamflow data for the
    hydrometric station 'M107302001' for the period [1st Jan 1990,
    1st Dec 2023]:

    >>> save_hydrometry(
    ...     code_station='M107302001', working_dir='examples/my_example',
    ...     start='1990-01-01', end='2023-12-01'
    ... )

    Generating a PRN file named *debit-M107302001.prn* in
    *examples/my_example/data*  containing consolidated and real-time
    daily streamflow data for the hydrometric station 'M107302001':

    >>> save_hydrometry(
    ...     code_station='M107302001', working_dir='examples/my_example',
    ...     filename='debit-M107302001.prn'
    ... )
    """
    # collect data as dataframe
    df = get_hydrometry(code_station, include_realtime)

    # store as PRN file
    _save_df_as_prn_file(
        df, working_dir, 'Debit', -2, filename, start, end
    )


def save_piezometry(
        code_bss: str, working_dir: str,
        filename: str = None,
        start: str = None, end: str = None,
        include_realtime: bool = True
):
    """Generate a PRN file containing the observed piezometric data
    for a given station.

    :Parameters:

        code_bss: `str`
            The BSS code of the piezometric station for which groundwater
            level data is requested from ADES via Hub'Eau.

        working_dir: `str`
            The file path the working directory to use to store the data.

        filename: `str`, optional
            The custom file name to use for storing the data. If not
            provided, the filename is set 'my-niveau.prn'.

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

        include_realtime: `bool`, optional
            Whether to include real-time data (if available) and
            aggregate it with consolidated data. If not provided,
            set to default value `True`.

    :Returns:

        `None`

    **Examples**

    Generating a PRN file named *my-prelevement-.prn* in
    *examples/my_example/data*  containing consolidated and real-time
    daily groundwater level data for the  piezometric station '06301X0131/F':

    >>> save_hydrometry(
    ...     code_bss='06301X0131/F', working_dir='examples/my_example'
    ... )
    """
    # collect data as dataframe
    df = get_piezometry(code_bss, include_realtime)

    # store as PRN file
    _save_df_as_prn_file(
        df, working_dir, 'Niveau', 9999, filename, start, end
    )


def save_withdrawal(
        code_ouvrage: str, working_dir: str,
        filename: str = None,
        start: str = None, end: str = None
):
    """Generate a PRN file containing the observed piezometric data
    for a given station.

    :Parameters:

        code_bss: `str`
            The BSS code of the piezometric station for which groundwater
            level data is requested from ADES via Hub'Eau.

        working_dir: `str`
            The file path the working directory to use to store the data.

        filename: `str`, optional
            The custom file name to use for storing the data. If not
            provided, the filename is set 'my-niveau.prn'.

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

    :Returns:

        `None`

    **Examples**

    Generating a PRN file named *my-prelevement-souterrain.prn* in
    *examples/my_example/data* containing consolidated withdrawal data
    for the extraction point 'OPR0000000003':

    >>> save_hydrometry(
    ...     code_ouvrage='OPR0000000003', working_dir='examples/my_example'
    ... )
    """
    # collect data as dataframe
    df = get_withdrawal(code_ouvrage)
    measure_label = df.columns.drop('Date')[0]

    # resample to daily values
    df['Date'] = pd.period_range(
        start=df['Date'].iloc[0], end=df['Date'].iloc[-1], freq='A'
    )
    df = df.set_index('Date')
    df = df.resample('D', convention='start').asfreq().ffill()
    df = df / df.groupby(df.index.year).transform(len)
    df.index = df.index.to_timestamp()
    df = df.reset_index()

    # round to 3 decimals
    df[measure_label] = df[measure_label].round(3)

    # store as PRN file
    _save_df_as_prn_file(
        df, working_dir, measure_label, np.nan, filename, start, end
    )

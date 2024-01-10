import os
import pathlib
import numpy as np
import pandas as pd

from .collect import get_meteorology


_variable_mapping = {
    'RR': 'Pluie',
    'ETPMON': 'ETP',
    'ETPMONGRILLE': 'ETP',
    'TM': 'Temperature'
}


def _manage_working_directory(working_dir: str):
    # create working directory and 'data' subdirectory if they do not exist
    (
        pathlib.Path(os.sep.join([working_dir, 'data']))
        .mkdir(parents=True, exist_ok=True)
    )


def _save_df_as_prn_files(
        df: pd.DataFrame, variables: list, 
        working_dir: str, filename: str = None,
        start: str = None, end: str = None, freq: str = 'D'
) -> None:
    # deal with working directory
    _manage_working_directory(working_dir)

    # adjust period to match start and end dates if provided
    start = (
        df['DATE'].iloc[0] if (start is None)
        else pd.to_datetime(start)
    )
    end = (
        df['DATE'].iloc[-1] if (end is None)
        else pd.to_datetime(end)
    )

    df = df.set_index('DATE')
    df = df.reindex(pd.date_range(start, end, freq=freq), fill_value=np.nan)
    df = df.reset_index(names='Date')

    # convert to "excel" date for Gardenia
    df['Date'] = df['Date'].dt.strftime('%d/%m/%Y')

    # save each variable as a PRN file
    for var in variables:
        # try renaming variable to plain text
        v = _variable_mapping.get(var, var)
        df = df.rename(columns={var: v})

        # save to PRN file
        df[['Date', v]].to_csv(
            os.sep.join(
                [
                    working_dir, "data",
                    filename.format(var) if filename else f"my-{var}.prn"
                ]
            ),
            index=False, sep='\t'
        )


def save_meteorology(
        variables: list, station_id: int, api_key: str,
        working_dir: str, filename: str = None,  
        start: str = None, end: str = None,
        check_station_id: bool = True, realtime_only: bool = False,
        public_only: bool = True, open_only: bool = True
):
    """Generate PRN files containing the observed meteorological data
    for a given station and given variables.

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
            
        working_dir: `str`
            The file path the working directory to use to store the data.

        filename: `str`, optional
            The custom file name to use for storing the data. The file 
            name must contain curly braces {} at the position where each  
            variable name should be introduced. If not provided, the 
            filename is set 'my-*.prn' where * is replaced by the name 
            of each variable.

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
    """
    # check that filename contains curly braces
    if filename and ('{}' not in filename):
        raise RuntimeError(
            "filename is not valid, it must contains curly braces"
        )

    # collect data as dataframe
    df = get_meteorology(
        variables=variables, station_id=station_id, api_key=api_key,
        start=start, end=end,
        check_station_id=check_station_id, realtime_only=realtime_only,
        public_only=public_only, open_only=open_only
    )

    # store as PRN file(s)
    _save_df_as_prn_files(
        df=df, variables=variables, 
        working_dir=working_dir, filename=filename, 
        start=start, end=end
    )

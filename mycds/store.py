import os
import pathlib
from datetime import datetime
import pandas as pd
import numpy as np
import xarray as xr

from .collect import (
    get_total_precipitation, get_potential_evaporation, get_2m_air_temperature
)


def _manage_working_directory(working_dir: str):
    # create working directory and 'data' subdirectory if they do not exist
    (
        pathlib.Path(os.sep.join([working_dir, 'data']))
        .mkdir(parents=True, exist_ok=True)
    )


def _save_data_as_prn_file(
        da: xr.DataArray, var: str, variable: str,
        working_dir: str, filename: str = None,
        start: str = None, end: str = None
) -> None:
    # deal with working directory
    _manage_working_directory(working_dir)

    # convert to dataframe
    df = da.to_dataframe()
    df = df.reset_index()

    # keep only time and variables
    df = df[['valid_time', var]]
    df.columns = ['Date', variable]

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
    df = df.reindex(pd.date_range(start, end), fill_value=np.nan)
    df = df.reset_index(names='Date')

    # convert to "excel" date for Gardenia
    df['Date'] = df['Date'].dt.strftime('%d/%m/%Y')

    filename = (
        filename if filename
        else f"my-{variable.lower().replace(' ', '-')}.prn"
    )

    df.to_csv(
        os.sep.join([working_dir, "data", filename]),
        index=False, sep='\t'
    )


def save_total_precipitation(
        longitude: float, latitude: float, working_dir: str,
        filename: str = None,
        start: str = None, end: str = None
):
    """Generate a PRN file containing the daily mean total precipitation data
    in millimetres (cumulative midnight to midnight) for the given longitude
    and latitude coordinates. If the coordinates do not correspond precisely
    to an ERA5 grid box centroid, the nearest centroid is used.

    :Parameters:

         longitude: `float`
            The longitude of the location for which total precipitation
            data is requested. It must be provided in degrees East.

        latitude: `float`
            The latitude of the location for which total precipitation
            data is requested. It must be provided in degrees North.

        working_dir: `str`
            The file path the working directory to use to store the data.

        filename: `str`, optional
            The custom file name to use for storing the data. If not
            provided, the filename is set 'my-total-precipitation.prn'.

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

    Generating a PRN file named *my-total-precipitation.prn* in
    *examples/my_example/data* containing daily total precipitation
    data for location +50.3°N +2.2°E:

    >>> save_total_precipitation(
    ...     longitude=2.2, latitude=50.3, working_dir='examples/my_example'
    ... )
    """
    # collect data array
    da = get_total_precipitation(longitude=longitude, latitude=latitude)

    # convert [m] to [mm]
    da = da * 1000

    # aggregate hourly to daily values
    da = da.resample(valid_time='1D', origin='end_day').sum()

    # store as PRN file
    _save_data_as_prn_file(
        da, 'tp', 'Total precipitation', working_dir, filename, start, end
    )


def save_potential_evaporation(
        longitude: float, latitude: float, working_dir: str,
        filename: str = None,
        start: str = None, end: str = None
):
    """Generate a PRN file containing the daily potential evaporation data
    in millimetres for the given longitude and latitude coordinates. If
    the coordinates do not correspond precisely to an ERA5 grid box
    centroid, the nearest centroid is used.

    :Parameters:

         longitude: `float`
            The longitude of the location for which potential evaporation
            data is requested. It must be provided in degrees East.

        latitude: `float`
            The latitude of the location for which potential evaporation
            data is requested. It must be provided in degrees North.

        working_dir: `str`
            The file path the working directory to use to store the data.

        filename: `str`, optional
            The custom file name to use for storing the data. If not
            provided, the filename is set 'my-potential-evaporation.prn'.

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

    Generating a PRN file named *my-potential-evaporation.prn* in
    *examples/my_example/data* containing daily potential evaporation
    data for location +50.3°N +2.2°E:

    >>> save_potential_evaporation(
    ...     longitude=2.2, latitude=50.3, working_dir='examples/my_example'
    ... )
    """
    # collect data array
    da = get_potential_evaporation(longitude=longitude, latitude=latitude)

    # convert [m] to [mm]
    da = da * 1000

    # discard remaining negative values
    da = da.where(da >= 0, np.nan)

    # aggregate hourly to daily values
    da = da.resample(valid_time='1D', origin='end_day').sum()

    # store as PRN file
    _save_data_as_prn_file(
        da, 'pev', 'Potential evaporation', working_dir, filename, start, end
    )


def save_2m_air_temperature(
        longitude: float, latitude: float, working_dir: str,
        filename: str = None,
        start: str = None, end: str = None
):
    """Generate a PRN file containing the daily mean air temperature data
    in degrees Celsius for the given longitude and latitude coordinates.
    If the coordinates do not correspond precisely to an ERA5 grid box
    centroid, the nearest centroid is used.

    :Parameters:

         longitude: `float`
            The longitude of the location for which air temperature
            data is requested. It must be provided in degrees East.

        latitude: `float`
            The latitude of the location for which air temperature
            data is requested. It must be provided in degrees North.

        working_dir: `str`
            The file path the working directory to use to store the data.

        filename: `str`, optional
            The custom file name to use for storing the data. If not
            provided, the filename is set 'my-2m-air-temperature.prn'.

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

    Generating a PRN file named *my-2m-air-temperature.prn* in
    *examples/my_example/data* containing daily air temperature data
    for location +50.3°N +2.2°E:

    >>> save_2m_air_temperature(
    ...     longitude=2.2, latitude=50.3, working_dir='examples/my_example'
    ... )
    """
    # collect data array
    da = get_2m_air_temperature(longitude=longitude, latitude=latitude)

    # convert [K] to [degC]
    da = da - 273.15

    # aggregate hourly to daily values
    da = da.resample(valid_time='1D', origin='end_day').mean()

    # store as PRN file
    _save_data_as_prn_file(
        da, 't2m', '2m air temperature', working_dir, filename, start, end
    )

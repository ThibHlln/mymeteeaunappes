import os
import glob
from datetime import datetime
import cdsapi
import xarray as xr


def _collect_era5_land(year: float, month: float, filename: str) -> None:
    c = cdsapi.Client()

    # collect data as GRIB file
    grib_filename = filename.replace('.nc', '.grib')

    c.retrieve(
        'reanalysis-era5-land',
        {
            'variable': [
                '2m_temperature', 'potential_evaporation',
                'total_precipitation',
            ],
            'year': f"{year}",
            'month': f"{month:02}",
            'area': [
                51.5,  # North
                -5,  # West
                41,  # South
                10,  # East
            ],
            'time': [
                '00:00', '01:00', '02:00',
                '03:00', '04:00', '05:00',
                '06:00', '07:00', '08:00',
                '09:00', '10:00', '11:00',
                '12:00', '13:00', '14:00',
                '15:00', '16:00', '17:00',
                '18:00', '19:00', '20:00',
                '21:00', '22:00', '23:00',
            ],
            'day': [
                '01', '02', '03',
                '04', '05', '06',
                '07', '08', '09',
                '10', '11', '12',
                '13', '14', '15',
                '16', '17', '18',
                '19', '20', '21',
                '22', '23', '24',
                '25', '26', '27',
                '28', '29', '30',
                '31',
            ],
            'format': 'grib',
        },
        grib_filename
    )

    # collapse time and step dimensions into single valid_time dimension
    ds = xr.open_dataset(grib_filename, engine='cfgrib')
    ds = (
        ds.stack(datetime=("time", "step"))
        .reset_index('datetime')
        .set_index(datetime='valid_time')
        .rename_dims({"datetime": "valid_time"})
        .rename_vars({'datetime': 'valid_time'})
    )

    # drop 23 first hours and last hour of the month (as they are NaN)
    ds = ds.isel(valid_time=slice(23, -1))

    # store as netCDF
    ds.to_netcdf(filename)

    # remove GRIB file and its index (.idx)
    for f in glob.glob(grib_filename + '*'):
        os.remove(f)


def update_era5_database() -> None:
    current_dt = datetime.now()

    existing_files = sorted(
        glob.glob(
            os.sep.join(
                [os.path.dirname(__file__), "database",
                 "reanalysis-era5-land_*.nc"]
            )
        )
    )

    for year in range(1950, current_dt.year + 1):

        for month in range(1, 13):
            # stop if year/month is beyond current time
            if (year == current_dt.year) and (month > current_dt.month):
                break

            # check that file does not exist already (except latest one)
            # before collecting more data
            filename = os.sep.join(
                [os.path.dirname(__file__), "database",
                 f"reanalysis-era5-land_{year}{month:02}.nc"]
            )
            if filename not in existing_files[:-1]:
                # collect data
                _collect_era5_land(year, month, filename)


def _get_data_array(
        variable: str, longitude: float, latitude: float
) -> xr.DataArray:
    # gather entire ERA5 record from database as xarray dataset
    files = os.sep.join(
        [os.path.dirname(__file__), "database",
         "reanalysis-era5-land_*.nc"]
    )
    if glob.glob(files):
        ds = xr.open_mfdataset(files)
    else:
        raise RuntimeError(
            "ERA5 database is empty, consider updating it"
        )

    # select variable
    da = ds[variable]

    # return nearest ERA5 grid box
    return da.sel(latitude=latitude, longitude=longitude, method='nearest')


def get_total_precipitation(longitude: float, latitude: float):
    """Collect entire record of total precipitation data (in metres)
    for given longitude and latitude coordinates from local ERA5-land
    database. If the coordinates do not correspond precisely to an ERA5
    grid box centroid, the nearest centroid is used.

    :Parameters:

        longitude: `float`
            The longitude of the location for which precipitation data
            is requested. It must be provided in degrees East.

        latitude: `float`
            The latitude of the location for which precipitation data
            is requested. It must be provided in degrees North.

    :Returns:

        `xarray.DataArray`
            The data array containing the precipitation data.

    **Examples**

    >>> da = get_total_precipitation(longitude=2.2, latitude=50.3)
    >>> da.long_name
    'Total precipitation'
    >>> da.units
    'm'
    >>> da.values[:10]
    array([8.642673e-07, 0.000000e+00, 0.000000e+00, 7.785857e-07,
           7.785857e-07, 7.785857e-07, 7.748604e-07, 7.748604e-07,
           7.748604e-07, 7.748604e-07], dtype=float32)
    """
    return _get_data_array(
        'tp', longitude=longitude, latitude=latitude
    )


def get_potential_evaporation(longitude: float, latitude: float):
    """Collect entire record of potential evaporation data (in metres)
    for given longitude and latitude coordinates from local ERA5-land
    database. If the coordinates do not correspond precisely to an ERA5
    grid box centroid, the nearest centroid is used.

    :Parameters:

        longitude: `float`
            The longitude of the location for which potential evaporation
            data is requested. It must be provided in degrees East.

        latitude: `float`
            The latitude of the location for which potential evaporation
            data is requested. It must be provided in degrees North.

    :Returns:

        `xarray.DataArray`
            The data array containing the potential evaporation data.

    **Examples**

    >>> da = get_potential_evaporation(longitude=2.2, latitude=50.3)
    >>> da.long_name
    'Potential evaporation'
    >>> da.units
    'm'
    >>> da.values[:10]
    array([-1.5933067e-04,  6.1374158e-06,  1.3383105e-05,  2.3350120e-05,
            3.4790486e-05,  4.9889088e-05,  6.3095242e-05,  7.6122582e-05,
            8.7004155e-05,  8.6087734e-05], dtype=float32)
    """
    return _get_data_array(
        'pev', longitude=longitude, latitude=latitude
    )


def get_2m_air_temperature(longitude: float, latitude: float):
    """Collect entire record of 2-metre air temperature data (in metres)
    for given longitude and latitude coordinates from local ERA5-land
    database. If the coordinates do not correspond precisely to an ERA5
    grid box centroid, the nearest centroid is used.

    :Parameters:

        longitude: `float`
            The longitude of the location for which air temperature
            data is requested. It must be provided in degrees East.

        latitude: `float`
            The latitude of the location for which air temperature
            data is requested. It must be provided in degrees North.

    :Returns:

        `xarray.DataArray`
            The data array containing the air temperature data.

    **Examples**

    >>> da = get_2m_air_temperature(longitude=2.2, latitude=50.3)
    >>> da.long_name
    '2 metre temperature'
    >>> da.units
    'K'
    >>> da.values[:10]
    array([270.0835 , 271.05762, 272.77002, 274.09045, 274.79028, 275.19983,
           275.78226, 277.01   , 277.524  , 278.27942], dtype=float32)
    """
    return _get_data_array(
        't2m', longitude=longitude, latitude=latitude
    )

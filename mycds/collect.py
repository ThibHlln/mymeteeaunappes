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


def _update_era5_database() -> None:
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


def get_meteorology(
        latitude: float, longitude: float, update_era5_land=False
) -> xr.Dataset:
    if update_era5_land:
        _update_era5_database()

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

    # return nearest ERA5 grid box
    return ds.sel(latitude=latitude, longitude=longitude, method='nearest')

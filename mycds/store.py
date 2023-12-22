import os
from datetime import datetime
import pandas as pd
import numpy as np
import xarray as xr

from .collect import get_meteorology


def save_meteorology(
        latitude: float, longitude: float, working_dir: str,
        filename_prefix: str = None, start: str = None, end: str = None,
        update_era5_land: bool = False
) -> None:
    # collect dataset
    ds = get_meteorology(latitude, longitude, update_era5_land)

    # convert units
    ds['tp'] = ds['tp'] * 1000  # [m] to [mm]
    ds['pev'] = ds['pev'] * -1000  # [m] to [mm] + sign change
    ds['t2m'] = ds['t2m'] - 273.15  # [K] to [degC]

    # drop negative remaining PET negative values
    ds['pev'] = ds['pev'].where(ds['pev'] >= 0, np.nan)

    # resample hourly to daily values
    ds = xr.merge(
        [
            # total precipitation [tp]
            ds['tp'].resample(valid_time='1D', origin='end_day').sum(),
            # potential evaporation [pev]
            ds['pev'].resample(valid_time='1D', origin='end_day').sum(),
            # 2m air temperature [t2m]
            ds['t2m'].resample(valid_time='1D', origin='end_day').mean()
        ]
    )

    # convert to dataframe
    df = ds.to_dataframe()
    df = df.reset_index()

    # keep only time and variables
    df = df[['valid_time', 'tp', 'pev', 't2m']]
    df.columns = ['Date', 'Pluie', 'ETP', 'Temperature']

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

    prefix = filename_prefix if filename_prefix else 'my'
    for var in ['Pluie', 'ETP', 'Temperature']:
        df[['Date', var]].to_csv(
            os.sep.join(
                [working_dir, "data", f"{prefix}-{var.lower()}.prn"]
            ),
            index=False, sep='\t'
        )

import os
from datetime import datetime
import pandas as pd
import numpy as np

from .collect import get_meteorology


def save_meteorology(
        latitude: float, longitude: float, working_dir: str,
        start: str = None, end: str = None, update_era5_land=False
) -> None:
    # collect dataset
    ds = get_meteorology(latitude, longitude, update_era5_land)

    # convert to dataframe
    df = ds.to_dataframe()
    df = df.reset_index()

    # keep only time and variables
    df = df[['time', 'tp', 'pev', 't2m']]
    df.columns = ['Date', 'Pluie', 'ETP', 'Temperature']

    # convert units
    df['Pluie'] *= 1000  # m to mm
    df['ETP'] *= 1000  # m to mm
    df['Temperature'] -= 273.15  # K to degC

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

    # format date to "Excel date"
    df['Date'] = df['Date'].dt.strftime('%d/%m/%Y')

    for var in ['Pluie', 'ETP', 'Temperature']:
        df[['Date', var]].to_csv(
            os.sep.join(
                [working_dir, "data", f"my-{var.lower()}.prn"]
            ),
            index=False, sep='\t'
        )

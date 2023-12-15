import os

from .collect import get_meteorology


def save_meteorology(
        latitude: float, longitude: float, working_dir: str,
        update_era5_land=False
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

    # format date to "Excel date"
    df['Date'] = df['Date'].dt.strftime('%d/%m/%Y')

    for var in ['Pluie', 'ETP', 'Temperature']:
        df[['Date', var]].to_csv(
            os.sep.join(
                [working_dir, "data", f"my-{var.lower()}.prn"]
            ),
            index=False, sep='\t'
        )

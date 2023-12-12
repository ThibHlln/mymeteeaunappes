import os
import numpy as np
import pandas as pd

from .collect import get_hydrometry, get_piezometry, get_withdrawal


def _save_df_as_prn_file(
        df: pd.DataFrame, working_dir: str, measure_label: str,
        missing_value: float
):
    # format date to "Excel date"
    df['Date'] = df['Date'].dt.strftime('%m/%d/%Y')

    # fill in missing data with missing value flag
    if df[measure_label].isna().any():
        df[measure_label][df[measure_label].isna()] = missing_value

    # save as PRN file
    df.to_csv(
        os.sep.join(
            [working_dir, "data",
             f"my-{measure_label.lower().replace(' ', '-')}.prn"]
        ),
        index=False, sep='\t'
    )


def save_hydrometry(
        code_station: str, working_dir: str, include_realtime: bool = True
):
    # collect data as dataframe
    df = get_hydrometry(code_station, include_realtime)

    # store as PRN file
    _save_df_as_prn_file(df, working_dir, 'Debit', -2)


def save_piezometry(
        code_bss: str, working_dir: str, include_realtime: bool = True
):
    # collect data as dataframe
    df = get_piezometry(code_bss, include_realtime)

    # store as PRN file
    _save_df_as_prn_file(df, working_dir, 'Niveau', 9999)


def save_withdrawal(
        code_ouvrage: str, working_dir: str
):
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
    df = df.reset_index()

    # round to 3 decimals
    df[measure_label] = df[measure_label].round(3)

    # store as PRN file
    _save_df_as_prn_file(df, working_dir, measure_label, np.nan)

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

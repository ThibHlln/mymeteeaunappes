import os
import pandas as pd
import numpy as np


def read_prn_file(
        working_dir: str, filename: str,
        variable: str, missing_value: float = None
) -> pd.DataFrame:
    df = pd.read_csv(
        os.sep.join([working_dir, 'data', filename]),
        delimiter='\t', parse_dates=['Date'], date_format='%d/%m/%Y'
    )

    if missing_value is not None:
        df.loc[df[variable] == missing_value, variable] = np.nan

    return df

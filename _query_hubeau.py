import os
import numpy as np

from myhubeau.interface import (
    get_hydrometry, get_piezometry, get_withdrawal
)


def save_df_as_prn_file(
        df, working_dir, measure_label, date_format, missing_value
):
    # format date to "Excel date"
    df['Date'] = df['Date'].dt.strftime(date_format)

    # fill in missing data with missing value flag
    df[measure_label][df[measure_label].isna()] = missing_value

    # save as PRN file
    df.to_csv(
        os.sep.join(
            [working_dir, "data",
             f"my-{measure_label.lower().replace(' ', '-')}.prn"]
        ),
        index=False, sep='\t'
    )


_working_dir = 'examples/my-example'

df_streamflow = get_hydrometry(code_station='M107302001')
save_df_as_prn_file(
    df_streamflow, _working_dir, 'Debit', '%m/%d/%Y', -2
)


df_piezo_level = get_piezometry(code_bss='06301X0131/F')
save_df_as_prn_file(
    df_piezo_level, _working_dir, 'Niveau', '%m/%d/%Y', 9999
)

df_withdrawal = get_withdrawal(code_ouvrage='OPR0000000003')
save_df_as_prn_file(
    df_withdrawal, _working_dir, 'Prelevement souterrain', '%Y', np.nan
)

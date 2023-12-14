from myhubeau.store import (
    save_hydrometry, save_piezometry, save_withdrawal
)


working_dir = 'examples/my-example'

df_streamflow = save_hydrometry(
    code_station='M107302001', working_dir=working_dir
)

df_piezo_level = save_piezometry(
    code_bss='06301X0131/F', working_dir=working_dir
)

df_withdrawal = save_withdrawal(
    code_ouvrage='OPR0000000003', working_dir=working_dir
)

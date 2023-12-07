from myhubeau.interface import (
    get_hydrometry, get_piezometry, get_withdrawal
)

df_streamflow = get_hydrometry(code_station='M107302001')

df_piezo_level = get_piezometry(code_bss='06301X0131/F')

df_withdrawal = get_withdrawal(code_ouvrage='OPR0000000003')

from myhubeau.store import (
    save_hydrometry, save_piezometry, save_withdrawal
)


working_dir = 'examples/my-example'

save_hydrometry(
    code_station='E642601001', working_dir=working_dir,
    filename='debit-E642601001.prn',
    start='1985-01-01', end='2023-07-31'
)

save_piezometry(
    code_bss='00608X0028/S1', working_dir=working_dir,
    filename='niveau-00608X0028_S1.prn',
    start='1985-01-01', end='2023-07-31'
)

save_withdrawal(
    code_ouvrage='OPR0000041735', working_dir=working_dir,
    filename='prelevement-OPR0000041735.prn',
    start='1985-01-01', end='2023-07-31'
)

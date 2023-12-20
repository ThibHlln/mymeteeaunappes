from myhubeau.store import (
    save_hydrometry, save_piezometry, save_withdrawal
)


working_dir = 'examples/my-example'

save_hydrometry(
    code_station='M107302001', working_dir=working_dir,
    filename='debit-M107302001.prn',
    start='1990-01-01', end='2023-12-01'
)

save_piezometry(
    code_bss='06301X0131/F', working_dir=working_dir,
    filename='niveau-06301X0131_F.prn',
    start='1990-01-01', end='2023-12-01'
)

save_withdrawal(
    code_ouvrage='OPR0000000003', working_dir=working_dir,
    filename='prelevement-OPR0000000003.prn',
    start='1990-01-01', end='2023-12-01'
)

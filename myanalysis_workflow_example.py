from myanalysis.visualise import plot_time_series


plot_time_series(
    working_dir='examples/my-example',
    rainfall_filename='pluie.prn',
    pet_filename='etp.prn',
    streamflow_filename='debit.prn',
    piezo_level_filename='niveau.prn',
    rainfall_summary='A-JUL', pet_summary='A',
    plot_filename='test.pdf',
    start='1990-01-01', end='2000-01-01'
)

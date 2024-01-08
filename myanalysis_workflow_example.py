from myanalysis.visualise import plot_time_series
from myanalysis.compare import compute_correlation_matrix


plot_time_series(
    working_dir='examples/my-example',
    rainfall_filename='pluie.prn',
    pet_filename='etp.prn',
    streamflow_filename='debit.prn',
    piezo_level_filename='niveau.prn',
    plot_filename='my-observations.pdf',
    rainfall_secondary_frequency='A-JUL',
    pet_secondary_frequency='A',
    start='1990-01-01', end='2000-01-01'
)

df = compute_correlation_matrix(
    correlation_coefficient='pearson',
    working_dir='examples/my-example',
    rainfall_filename='pluie.prn',
    pet_filename='etp.prn',
    streamflow_filename='debit.prn',
    piezo_level_filename='niveau.prn'
)
print(df)

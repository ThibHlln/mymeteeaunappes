import os
import glob
import subprocess
import re
import pandas as pd
import evalhyd

from _format import (
    format_rga_file_content, format_gar_file_content
)


# ----------------------------------------------------------------------
# configure
# ----------------------------------------------------------------------
project_description = "test run"
basin_description = "selle morvillers"

config_dir = "config"
data_dir = "data"
output_dir = "output"

rga_file = config_dir + os.sep + "test.rga"
gar_file = config_dir + os.sep + "test.gar"

user_profile = '0'
execution_mode = 'D'

river_obs_weight = 5
piezo_obs_weight = 2

river_calc = True
piezo_calc = True

recharge_effective_rain_save = True
river_piezo_save = True
water_balance_save = False

computation_scheme = '0'

spin_up_years = 4
spin_up_cycles = 1
data_start_year = 1985
max_calib_iter = 250

# ----------------------------------------------------------------------
# clean up files from previous run
# ----------------------------------------------------------------------
for f in glob.glob(f'{os.getcwd()}{os.sep}{config_dir}{os.sep}*'):
    os.remove(f)

for f in glob.glob(f'{os.getcwd()}{os.sep}{output_dir}{os.sep}*'):
    os.remove(f)

for f in glob.glob(f'{os.getcwd()}{os.sep}*.*'):
    if not re.compile('_*.py').findall(f):
        os.remove(f)

# ----------------------------------------------------------------------
# generate *.rga file
# ----------------------------------------------------------------------
rain_file = data_dir + os.sep + 'pluv_moy_9_stat_selle_1985_2003.prn'
pet_file = data_dir + os.sep + 'etp_moy_9_stat_selle_1985_2003.prn'

q_file = data_dir + os.sep + 'debit_selle_plachy_1985_2003.prn'
z_file = data_dir + os.sep + 'niv_morvillers_00608X0028_1985_2003.prn'

air_temp_file = ''
snow_file = ''

rga_text = format_rga_file_content(
    project_description,
    gar_file,
    rain_file,
    pet_file,
    q_file,
    z_file,
    air_temp_file,
    snow_file
)

with open(rga_file, "w+") as f:
    f.writelines(rga_text)

# ----------------------------------------------------------------------
# generate *.gar file
# ----------------------------------------------------------------------
gar_text = format_gar_file_content(
    project_description,
    basin_description,
    user_profile,
    execution_mode,
    river_obs_weight,
    piezo_obs_weight,
    river_calc,
    piezo_calc,
    recharge_effective_rain_save,
    river_piezo_save,
    water_balance_save,
    computation_scheme,
    spin_up_years,
    spin_up_cycles,
    data_start_year,
    max_calib_iter
)

with open(gar_file, "w+") as f:
    f.writelines(gar_text)

# ----------------------------------------------------------------------
# run gardenia model
# ----------------------------------------------------------------------
msg = subprocess.run(
    [
        f"{os.environ['bin_Garden']}{os.sep}Gardenia.exe",
        rga_file
    ],
    stdout=subprocess.PIPE
).stdout.decode('windows-1252')

# ----------------------------------------------------------------------
# post-process outputs
# ----------------------------------------------------------------------
output_file = "gardesim.prn"

beg_river = None
end_river = None
beg_piezo = None
end_piezo = None

with open(output_file, 'r') as f:
    for i, line in enumerate(f):
        if re.compile(r'Fin :.*: Débit_Riv').findall(line):
            end_river = i
        elif re.compile(r': Débit_Riv').findall(line):
            beg_river = i + 1
        elif re.compile(r'Fin :.*: Niveau_Aquif').findall(line):
            end_piezo = i
        elif re.compile(r': Niveau_Aquif').findall(line):
            beg_piezo = i + 1

with open(output_file, 'r') as f:
    n_lines = len(f.readlines())

options = dict(
    encoding='windows-1252',
    engine='python',
    parse_dates=[0], date_format='%d/%m/%Y'
)

metrics = ['NSE', 'KGE']

if beg_river and end_river:
    df_river = pd.read_table(
        output_file,
        skiprows=beg_river, skipfooter=n_lines-end_river,
        names=['dt', 'river_sim', 'river_obs'],
        **options
    )
    df_river.to_csv(f"{output_dir}/river_sim_obs.csv", index=False)
    df_river = df_river[
        df_river['dt'] >= (
            df_river['dt'].iloc[0] + pd.offsets.DateOffset(years=spin_up_years)
        )
    ]

    print("river")

    values = evalhyd.evald(
        q_obs=df_river['river_obs'].values,
        q_prd=df_river['river_sim'].values,
        metrics=metrics
    )
    print(*[f"{metric} {value}" for metric, value in zip(metrics, values)])

if beg_piezo and end_piezo:
    df_piezo = pd.read_table(
        output_file,
        skiprows=beg_piezo, skipfooter=n_lines-end_piezo,
        names=['dt', 'piezo_sim', 'piezo_obs'],
        **options
    )
    df_piezo.to_csv(f"{output_dir}/piezo_sim_obs.csv", index=False)
    df_piezo = df_piezo[
        df_piezo['dt'] >= (
            df_piezo['dt'].iloc[0] + pd.offsets.DateOffset(years=spin_up_years)
        )
    ]

    print("piezo")

    values = evalhyd.evald(
        q_obs=df_piezo['piezo_obs'].values,
        q_prd=df_piezo['piezo_sim'].values,
        metrics=metrics
    )
    print(*[f"{metric} {value}" for metric, value in zip(metrics, values)])

import os
import glob
import re
import pandas as pd
import evalhyd

from mygardenia.configure import GardeniaTree
from mygardenia.simulate import GardeniaModel


# ----------------------------------------------------------------------
# configure
# ----------------------------------------------------------------------
working_dir = 'examples/my-example'

tree = GardeniaTree()

tree.update(
    {
        'data': {
            'simulation': {
                'rainfall': 'pluie.prn',
                'pet': 'etp.prn'
            },
            'observation': {
                'streamflow': 'debit.prn',
                'piezo-level': 'niveau.prn'
            }
        },
        'description': {
            'project': "example run",
            'basin': "example",
        },
        'general_settings': {
            'user_profile': '0',
            'execution_mode': 'M',
            'streamflow_obs_weight': 5,
            'piezo-level_obs_weight': 2,
            'calc_streamflow': True,
            'calc_piezo-level': True,
            'save_recharge_effective-rainfall': True,
            'save_streamflow_piezo-level': True,
            'save_water-balance': False,
            'computation_scheme': '0'
        },
        'basin_settings': {
            'model': {
                'initialisation': {
                    'spinup': {
                        'n_years': 4,
                        'n_cycles': 1
                    }
                },
                'calibration': {
                    'max_iterations': 250
                }
            },
            'time': {
                'simulation': {
                    'first_year': 1985
                }
            }
        },
        'physical_parameters': {
            'basin_area': {
                'val': 524
            }
        }
    }
)

# tree = GardeniaTree(
#     catchment=f'{working_dir}/config/_my-catchment.toml',
#     settings=f'{working_dir}/config/_my-settings.toml',
# )

model = GardeniaModel(tree, working_dir)

# ----------------------------------------------------------------------
# clean up files from previous run
# ----------------------------------------------------------------------
for f in glob.glob(f'{working_dir}{os.sep}config{os.sep}*'):
    if ('auto.gar' in f) or ('auto.rga' in f):
        os.remove(f)

for f in glob.glob(f'{working_dir}{os.sep}output{os.sep}*'):
    os.remove(f)

for f in glob.glob(f'{working_dir}{os.sep}*.*'):
    if not re.compile('_*.toml').findall(f):
        os.remove(f)

# ----------------------------------------------------------------------
# run gardenia model
# ----------------------------------------------------------------------
model.run()

# ----------------------------------------------------------------------
# analyse outputs
# ----------------------------------------------------------------------
options = dict(
    parse_dates=[0], date_format='%Y-%m-%d'
)

metrics = ['NSE', 'KGE']

spin_up_n_years = tree['basin_settings']['model']['initialisation']['spinup']['n_years']

df_river = pd.read_csv(f"{working_dir}/output/river_sim_obs.csv", **options)
df_river = df_river[
    df_river['dt'] >= (
        df_river['dt'].iloc[0] + pd.offsets.DateOffset(years=spin_up_n_years)
    )
]

print("river")

values = evalhyd.evald(
    q_obs=df_river['river_obs'].values,
    q_prd=df_river['river_sim'].values,
    metrics=metrics
)
print(*[f"{metric}:{value.squeeze()}" for metric, value in zip(metrics, values)])

df_piezo = pd.read_csv(f"{working_dir}/output/piezo_sim_obs.csv", **options)
df_piezo = df_piezo[
    df_piezo['dt'] >= (
        df_piezo['dt'].iloc[0] + pd.offsets.DateOffset(years=spin_up_n_years)
    )
]

print("piezo")

values = evalhyd.evald(
    q_obs=df_piezo['piezo_obs'].values,
    q_prd=df_piezo['piezo_sim'].values,
    metrics=metrics
)
print(*[f"{metric}:{value.squeeze()}" for metric, value in zip(metrics, values)])

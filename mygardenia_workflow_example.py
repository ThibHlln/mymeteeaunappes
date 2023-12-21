from mygardenia.configure import GardeniaTree
from mygardenia.simulate import GardeniaModel


# ----------------------------------------------------------------------
# configure
# ----------------------------------------------------------------------
working_dir = 'examples/my-example'

# --- EITHER via TOML files --------------------------------------------
# tree = GardeniaTree(
#     catchment=f'{working_dir}/config/_my-catchment.toml',
#     settings=f'{working_dir}/config/_my-settings.toml',
# )

# --- OR via nested dictionary -----------------------------------------
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
            },
            'pumping_groundwater_half-life_rise': {
                'val': 0.0,
                'opt': False,
                'min': 0.05,
                'max': 10.0
            }
        }
    }
)

# ----------------------------------------------------------------------

model = GardeniaModel(tree, working_dir)

# ----------------------------------------------------------------------
# run gardenia model
# ----------------------------------------------------------------------
model.run(execution_mode='M')

# ----------------------------------------------------------------------
# evaluate gardenia simulations
# ----------------------------------------------------------------------
print(
    '\t'.join(
        ['river',
         f"NSE:{model.evaluate(variable='streamflow', metric='NSE'):.2f}",
         f"KGE:{model.evaluate(variable='streamflow', metric='KGE'):.2f}"]
    )
)

print(
    '\t'.join(
        ['piezo',
         f"NSE:{model.evaluate(variable='piezo_level', metric='NSE'):.2f}",
         f"KGE:{model.evaluate(variable='piezo_level', metric='KGE'):.2f}"]
    )
)

# ----------------------------------------------------------------------
# visualise gardenia simulations
# ----------------------------------------------------------------------
model.visualise(
    variable='streamflow', filename='my-streamflow.pdf'
)

model.visualise(
    variable='piezo_level', filename='my-piezo-level.pdf'
)
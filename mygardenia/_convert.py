import re

# information on how to parse RGA/GAR files to populate a Gardenia tree
_rga_line_parsing = {
    1: {'description.project': ('=', 0)},
    4: {'data.simulation.rainfall': ('=', 0)},
    5: {'data.simulation.pet': ('=', 0)},
    6: {'data.observation.streamflow': ('=', 0)},
    7: {'data.observation.piezo-level': ('=', 0)},
    8: {'data.simulation.air-temp': ('=', 0)},
    9: {'data.simulation.snowfall': ('=', 0)},
    10: {'data.forecast.rainfall': ('=', 0)},
    11: {'data.forecast.pet': ('=', 0)},
    12: {'data.forecast.air-temp': ('=', 0)},
    13: {'data.forecast.snowfall': ('=', 0)},
    14: {'data.influence.pumping_or_injection': ('=', 0)},
    15: {'data.other.weather_tile_weights': ('=', 0)}
}

_gar_line_parsing = {
    1: {'description.project': ('=', 0)},
    4: {'general_settings.user_profile': ('=', 0)},
    5: {'general_settings.execution_mode': ('=', 0)},
    6: {'general_settings.computation_mode': ('=', 0)},
    8: {'general_settings.n_sites': ('=', 0)},
    9: {'general_settings.forecast_data_type': ('=', 0)},
    10: {'general_settings.streamflow_obs_weight': ('=', 0)},
    11: {'general_settings.piezo-level_obs_weight': ('=', 0)},
    12: {'general_settings.calc_streamflow': ('=', 0)},
    13: {'general_settings.calc_piezo-level': ('=', 0)},
    14: {'general_settings.save_recharge_effective-rainfall': ('=', 0)},
    15: {'general_settings.save_streamflow_piezo-level': ('=', 0)},
    16: {'general_settings.save_water-balance': ('=', 0)},
    17: {'general_settings.verbose': ('=', 0)},
    18: {'general_settings.computation_scheme': ('=', 0)},
    19: {'general_settings.draw_series': ('=', 0)},
    20: {'general_settings.transform_calibration_data': ('=', 0)},
    21: {'general_settings.minimise_streamflow_bias': ('=', 0)},
    22: {'general_settings.pumping_influencing_streamflow': ('=', 0)},
    23: {'general_settings.pumping_influencing_piezo-level': ('=', 0)},
    24: {'general_settings.forecast_run': ('=', 0)},
    25: {'general_settings.forecast_method': ('=', 0)},
    26: {'general_settings.underground_exchange_scheme': ('=', 0)},
    27: {'general_settings.daily_summary': ('=', 0)},
    28: {'general_settings.consider_snow': ('=', 0)},
    29: {'general_settings.snowfall_in_file': ('=', 0)},
    30: {'general_settings.data_per_hydro_year': ('=', 0)},
    31: {'general_settings.streamflow_loss': ('=', 0)},
    32: {'general_settings.sensitivity_analysis': ('=', 0)},
    33: {'general_settings.save_impulse_and_cumulative_response': ('=', 0)},
    34: {'general_settings.site_data_in_columns': ('=', 0)},
    35: {'general_settings.simulation_rainfall_column_number': ('=', 0)},
    36: {'general_settings.simulation_pet_column_number': ('=', 0)},
    37: {'general_settings.simulation_streamflow_column_number': ('=', 0)},
    38: {'general_settings.simulation_piezo-level_column_number': ('=', 0)},
    39: {'general_settings.simulation_air-temp_column_number': ('=', 0)},
    40: {'general_settings.simulation_snowfall_column_number': ('=', 0)},
    41: {'general_settings.simulation_pumping_column_number': ('=', 0)},
    42: {'general_settings.forecast_rainfall_column_number': ('=', 0)},
    43: {'general_settings.forecast_air-temp_column_number': ('=', 0)},
    44: {'general_settings.forecast_pet_column_number': ('=', 0)},
    45: {'general_settings.forecast_snowfall_column_number': ('=', 0)},
    46: {'general_settings.weather_data_weighting_per_time_step': ('=', 0)},
    47: {'general_settings.save_weather_data_weighting': ('=', 0)},
    48: {'general_settings.openpalm_coupling': ('=', 0)},
    50: {'time.rainfall_snowfall_pumping_timestep': ('=', 0)},
    51: {'time.rainfall_snowfall_pumping_format': ('=', 0)},
    53: {'time.air-temp_timestep': ('=', 0)},
    54: {'time.air-temp_format': ('=', 0)},
    56: {'time.pet_timestep': ('=', 0)},
    57: {'time.pet_format': ('=', 0)},
    59: {'time.streamflow_piezo-level_timestep': ('=', 0)},
    60: {'time.streamflow_piezo-level_format': ('=', 0)},
    62: {'time.non_standard_timestep_duration_unit': ('=', 0)},
    63: {'time.non_standard_timestep_duration': ('=', 0)},
    66: {'description.basin': ('=', 0)},
    67: {'filter_settings.observed_streamflow_to_consider.max': ('=', 0)},
    68: {'filter_settings.observed_streamflow_to_consider.min': ('=', 0)},
    69: {'filter_settings.observed_piezo-level_to_consider.max': ('=', 0)},
    70: {'filter_settings.observed_piezo-level_to_consider.min': ('=', 0)},
    71: {'forecast_settings.readjustment_factor': ('=', 0)},
    72: {'forecast_settings.standard_deviation_of_intermediate_reservoir': ('=', 0)},
    73: {'forecast_settings.standard_deviation_of_groundwater_reservoir_1': ('=', 0)},
    74: {'forecast_settings.standard_deviation_of_groundwater_reservoir_2': ('=', 0)},
    75: {'filter_settings.simulated_streamflow_lower_limit_to_apply': ('=', 0)},
    76: {'forecast_settings.standard_deviation_of_observed_piezo-level': ('=', 0)},
    77: {'forecast_settings.half-life_fall_streamflow_forecast': ('=', 0)},
    78: {'forecast_settings.half-life_fall_piezo-level_forecast': ('=', 0)},
    80: {'basin_settings.time.simulation.n_years_in_data': ('=', 0)},
    81: {'basin_settings.model.initialisation.spinup.n_years': ('=', 0)},
    82: {'basin_settings.model.initialisation.spinup.n_cycles': ('=', 0)},
    83: {'basin_settings.time.simulation.first_year': ('=', 0)},
    84: {'basin_settings.time.delay_in_rainfall_data': ('=', 0)},
    85: {'basin_settings.time.delay_in_streamflow_piezo-level_data': ('=', 0)},
    86: {'basin_settings.model.initialisation.antecedent_conditions': ('=', 0)},
    87: {'basin_settings.model.calibration.max_iterations': ('=', 0)},
    88: {'basin_settings.time.rainfall_mean_duration_within_timestep': ('=', 0)},
    89: {'basin_settings.model.structure.n_groundwater_reservoirs': ('=', 0)},
    90: {'basin_settings.model.structure.groundwater_reservoir_for_piezo-level': ('=', 0)},
    91: {'basin_settings.model.calibration.n_tail_years_to_trim': ('=', 0)},
    92: {'basin_settings.time.simulation.first_day': ('=', 0)},
    93: {'basin_settings.time.simulation.first_month': ('=', 0)},
    94: {'basin_settings.time.simulation.first_hour': ('=', 0)},
    95: {'basin_settings.time.simulation.first_minute': ('=', 0)},
    96: {'basin_settings.model.structure.intermediate_runoff_by_overspill': ('=', 0)},
    97: {'basin_settings.model.structure.intermediate_reservoir_evapotranspiration_decrease_only_when_half_empty': ('=', 0)},
    98: {'basin_settings.model.structure.constant_runoff_ratio_scheme': ('=', 0)},
    99: {'basin_settings.model.structure.storage_coefficient_computation_scheme': ('=', 0)},
    101: {'basin_settings.time.forecast.n_years_in_data': ('=', 0)},
    102: {'basin_settings.time.forecast.issue_day': ('=', 0)},
    103: {'basin_settings.time.forecast.issue_month': ('=', 0)},
    104: {'basin_settings.time.forecast.span': ('=', 0)},
    105: {'basin_settings.time.forecast.first_year': ('=', 0)},
    107: {'basin_settings.data.basin_column_number_in_data': ('=', 0)},
    109: {'physical_parameters.annual_effective-rainfall.val': ('=', 0)},
    110: {'physical_parameters.external_flow.val': ('=', 0),
          'physical_parameters.external_flow.opt': ('=', -1)},
    111: {'physical_parameters.basin_area.val': ('=', 0),
          'physical_parameters.basin_area.opt': ('=', -1)},
    112: {'physical_parameters.groundwater_base_level.val': ('=', 0),
          'physical_parameters.groundwater_base_level.opt': ('=', -1)},
    113: {'physical_parameters.rainfall_correction.val': ('=', 0),
          'physical_parameters.rainfall_correction.opt': ('=', -1)},
    114: {'physical_parameters.pet_correction.val': ('=', 0),
          'physical_parameters.pet_correction.opt': ('=', -1)},
    115: {'physical_parameters.thornthewaite_reservoir_capacity.val': ('=', 0),
          'physical_parameters.thornthewaite_reservoir_capacity.opt': ('=', -1)},
    116: {'physical_parameters.progressive_reservoir_capacity.val': ('=', 0),
          'physical_parameters.progressive_reservoir_capacity.opt': ('=', -1)},
    117: {'physical_parameters.intermediate_runoff_seepage.val': ('=', 0),
          'physical_parameters.intermediate_runoff_seepage.opt': ('=', -1)},
    118: {'physical_parameters.intermediate_half-life_seepage.val': ('=', 0),
          'physical_parameters.intermediate_half-life_seepage.opt': ('=', -1)},
    119: {'physical_parameters.groundwater_1_drainage.val': ('=', 0),
          'physical_parameters.groundwater_1_drainage.opt': ('=', -1)},
    120: {'physical_parameters.groundwater_1_2_exchange.val': ('=', 0),
          'physical_parameters.groundwater_1_2_exchange.opt': ('=', -1)},
    121: {'physical_parameters.groundwater_1_double_outflow_threshold.val': ('=', 0),
          'physical_parameters.groundwater_1_double_outflow_threshold.opt': ('=', -1)},
    122: {'physical_parameters.groundwater_2_drainage.val': ('=', 0),
          'physical_parameters.groundwater_2_drainage.opt': ('=', -1)},
    123: {'physical_parameters.time_of_concentration.val': ('=', 0),
          'physical_parameters.time_of_concentration.opt': ('=', -1)},
    124: {'physical_parameters.groundwater_external_exchange.val': ('=', 0),
          'physical_parameters.groundwater_external_exchange.opt': ('=', -1)},
    125: {'physical_parameters.thornthewaite_reservoir_initial_deficit.val': ('=', 0),
          'physical_parameters.thornthewaite_reservoir_initial_deficit.opt': ('=', -1)},
    126: {'physical_parameters.progressive_reservoir_initial_deficit.val': ('=', 0),
          'physical_parameters.progressive_reservoir_initial_deficit.opt': ('=', -1)},
    127: {'physical_parameters.intermediate_runoff_threshold.val': ('=', 0),
          'physical_parameters.intermediate_runoff_threshold.opt': ('=', -1)},
    128: {'physical_parameters.intermediate_half-life_runoff_by_overspill.val': ('=', 0),
          'physical_parameters.intermediate_half-life_runoff_by_overspill.opt': ('=', -1)},
    129: {'physical_parameters.intermediate_half-life_max_runoff_decrease.val': ('=', 0),
          'physical_parameters.intermediate_half-life_max_runoff_decrease.opt': ('=', -1)},
    130: {'physical_parameters.basin_area_correction.val': ('=', 0),
          'physical_parameters.basin_area_correction.opt': ('=', -1)},
    131: {'physical_parameters.groundwater_storage_coefficient.val': ('=', 0),
          'physical_parameters.groundwater_storage_coefficient.opt': ('=', -1)},
    133: {'physical_parameters.rainfall_correction.min': ('=', 0),
          'physical_parameters.rainfall_correction.max': ('=', -1)},
    134: {'physical_parameters.pet_correction.min': ('=', 0),
          'physical_parameters.pet_correction.max': ('=', -1)},
    135: {'physical_parameters.thornthewaite_reservoir_capacity.min': ('=', 0),
          'physical_parameters.thornthewaite_reservoir_capacity.max': ('=', -1)},
    136: {'physical_parameters.progressive_reservoir_capacity.min': ('=', 0),
          'physical_parameters.progressive_reservoir_capacity.max': ('=', -1)},
    137: {'physical_parameters.intermediate_runoff_seepage.min': ('=', 0),
          'physical_parameters.intermediate_runoff_seepage.max': ('=', -1)},
    138: {'physical_parameters.intermediate_half-life_seepage.min': ('=', 0),
          'physical_parameters.intermediate_half-life_seepage.max': ('=', -1)},
    139: {'physical_parameters.groundwater_1_drainage.min': ('=', 0),
          'physical_parameters.groundwater_1_drainage.max': ('=', -1)},
    140: {'physical_parameters.groundwater_1_2_exchange.min': ('=', 0),
          'physical_parameters.groundwater_1_2_exchange.max': ('=', -1)},
    141: {'physical_parameters.groundwater_1_double_outflow_threshold.min': ('=', 0),
          'physical_parameters.groundwater_1_double_outflow_threshold.max': ('=', -1)},
    142: {'physical_parameters.groundwater_2_drainage.min': ('=', 0),
          'physical_parameters.groundwater_2_drainage.max': ('=', -1)},
    143: {'physical_parameters.time_of_concentration.min': ('=', 0),
          'physical_parameters.time_of_concentration.max': ('=', -1)},
    144: {'physical_parameters.groundwater_external_exchange.min': ('=', 0),
          'physical_parameters.groundwater_external_exchange.max': ('=', -1)},
    145: {'physical_parameters.thornthewaite_reservoir_initial_deficit.min': ('=', 0),
          'physical_parameters.thornthewaite_reservoir_initial_deficit.max': ('=', -1)},
    146: {'physical_parameters.progressive_reservoir_initial_deficit.min': ('=', 0),
          'physical_parameters.progressive_reservoir_initial_deficit.max': ('=', -1)},
    147: {'physical_parameters.intermediate_runoff_threshold.min': ('=', 0),
          'physical_parameters.intermediate_runoff_threshold.max': ('=', -1)},
    148: {'physical_parameters.intermediate_half-life_runoff_by_overspill.min': ('=', 0),
          'physical_parameters.intermediate_half-life_runoff_by_overspill.max': ('=', -1)},
    149: {'physical_parameters.intermediate_half-life_max_runoff_decrease.min': ('=', 0),
          'physical_parameters.intermediate_half-life_max_runoff_decrease.max': ('=', -1)},
    150: {'physical_parameters.basin_area_correction.min': ('=', 0),
          'physical_parameters.basin_area_correction.max': ('=', -1)},
    151: {'physical_parameters.groundwater_storage_coefficient.min': ('=', 0),
          'physical_parameters.groundwater_storage_coefficient.max': ('=', -1)},
    153: {'physical_parameters.air-temp_correction.val': ('=', 0),
          'physical_parameters.air-temp_correction.opt': ('=', -1)},
    154: {'physical_parameters.snowfall_retention_factor.val': ('=', 0),
          'physical_parameters.snowfall_retention_factor.opt': ('=', -1)},
    155: {'physical_parameters.snow_evaporation_factor.val': ('=', 0),
          'physical_parameters.snow_evaporation_factor.opt': ('=', -1)},
    156: {'physical_parameters.snow_melt_correction_with_rainfall.val': ('=', 0),
          'physical_parameters.snow_melt_correction_with_rainfall.opt': ('=', -1)},
    157: {'physical_parameters.natural_snow_melting_threshold.val': ('=', 0),
          'physical_parameters.natural_snow_melting_threshold.opt': ('=', -1)},
    158: {'physical_parameters.snow_melt_degree_day_factor.val': ('=', 0),
          'physical_parameters.snow_melt_degree_day_factor.opt': ('=', -1)},
    159: {'physical_parameters.snow_melting_in_contact_with_soil.val': ('=', 0),
          'physical_parameters.snow_melting_in_contact_with_soil.opt': ('=', -1)},
    161: {'physical_parameters.air-temp_correction.min': ('=', 0),
          'physical_parameters.air-temp_correction.max': ('=', -1)},
    162: {'physical_parameters.snowfall_retention_factor.min': ('=', 0),
          'physical_parameters.snowfall_retention_factor.max': ('=', -1)},
    163: {'physical_parameters.snow_evaporation_factor.min': ('=', 0),
          'physical_parameters.snow_evaporation_factor.max': ('=', -1)},
    164: {'physical_parameters.snow_melt_correction_with_rainfall.min': ('=', 0),
          'physical_parameters.snow_melt_correction_with_rainfall.max': ('=', -1)},
    165: {'physical_parameters.natural_snow_melting_threshold.min': ('=', 0),
          'physical_parameters.natural_snow_melting_threshold.max': ('=', -1)},
    166: {'physical_parameters.snow_melt_degree_day_factor.min': ('=', 0),
          'physical_parameters.snow_melt_degree_day_factor.max': ('=', -1)},
    167: {'physical_parameters.snow_melting_in_contact_with_soil.min': ('=', 0),
          'physical_parameters.snow_melting_in_contact_with_soil.max': ('=', -1)},
    169: {'physical_parameters.pumping_river_influence_factor.val': ('=', 0),
          'physical_parameters.pumping_river_influence_factor.opt': ('=', -1)},
    170: {'physical_parameters.pumping_river_half-life_rise.val': ('=', 0),
          'physical_parameters.pumping_river_half-life_rise.opt': ('=', -1)},
    171: {'physical_parameters.pumping_river_half-life_fall.val': ('=', 0),
          'physical_parameters.pumping_river_half-life_fall.opt': ('=', -1)},
    172: {'physical_parameters.pumping_groundwater_influence_factor.val': ('=', 0),
          'physical_parameters.pumping_groundwater_influence_factor.opt': ('=', -1)},
    173: {'physical_parameters.pumping_groundwater_half-life_rise.val': ('=', 0),
          'physical_parameters.pumping_groundwater_half-life_rise.opt': ('=', -1)},
    174: {'physical_parameters.pumping_groundwater_half-life_fall.val': ('=', 0),
          'physical_parameters.pumping_groundwater_half-life_fall.opt': ('=', -1)},
    176: {'physical_parameters.pumping_river_half-life_rise.min': ('=', 0),
          'physical_parameters.pumping_river_half-life_rise.max': ('=', -1)},
    177: {'physical_parameters.pumping_river_half-life_fall.min': ('=', 0),
          'physical_parameters.pumping_river_half-life_fall.max': ('=', -1)},
    178: {'physical_parameters.pumping_groundwater_half-life_rise.min': ('=', 0),
          'physical_parameters.pumping_groundwater_half-life_rise.max': ('=', -1)},
    179: {'physical_parameters.pumping_groundwater_half-life_fall.min': ('=', 0),
          'physical_parameters.pumping_groundwater_half-life_fall.max': ('=', -1)}
}


def convert_to_rga_content(
        gar: str,
        description: dict,
        data: dict,
        **kwargs
) -> str:
    return f"""{description['project']}
 #<V8.2># --- Fin du texte libre --- ; Ne pas modifier/retirer cette ligne
{gar:<69} = Paramètres et Options
{('data/' if data['simulation']['rainfall'] else '') + data['simulation']['rainfall']:<69} = Pluies
{('data/' if data['simulation']['pet'] else '')  + data['simulation']['pet']:<69} = Évapo-Transpirations Potentielles (ETP)
{('data/' if data['observation']['streamflow'] else '')  + data['observation']['streamflow']:<69} = Débits de Rivière
{('data/' if data['observation']['piezo-level'] else '')  + data['observation']['piezo-level']:<69} = Niveaux de Nappe
{('data/' if data['simulation']['air-temp'] else '')  + data['simulation']['air-temp']:<69} = Températures de l'air
{('data/' if data['simulation']['snowfall'] else '')  + data['simulation']['snowfall']:<69} = Précipitations Neigeuses
{('data/' if data['forecast']['rainfall'] else '')  + data['forecast']['rainfall']:<69} = Pluies pour Prévision
{('data/' if data['forecast']['pet'] else '')  + data['forecast']['pet']:<69} = ETP pour Prévision
{('data/' if data['forecast']['air-temp'] else '')  + data['forecast']['air-temp']:<69} = Températures pour Prévision
{('data/' if data['forecast']['snowfall'] else '')  + data['forecast']['snowfall']:<69} = Précipitations neigeuses pour Prévision
{('data/' if data['influence']['pumping_or_injection'] else '')  + data['influence']['pumping_or_injection']:<69} = Injections/Pompages
{('data/' if data['other']['weather_tile_weights'] else '')  + data['other']['weather_tile_weights']:<69} = Mailles météo et Pondérations

"""


def convert_to_gar_content(
        description: dict,
        time: dict,
        general_settings: dict,
        filter_settings: dict,
        forecast_settings: dict,
        basin_settings: dict,
        physical_parameters: dict,
        **kwargs
) -> str:
    return f"""{description['project']}
 #<V8.8># --- Fin du texte libre --- ; Ne pas modifier/retirer cette ligne
 *** Pré-Options Générales           ***
{general_settings['user_profile']:>10}=Profil d'utilisation : 0=simple ; A=Avancé (Neige, Pompage, Prévi etc.)
{general_settings['execution_mode']:>10}=Mode d'exécution (C = Contrôle sur écran ; Déf=Rapide ; D=Direct ; M=Muet)
{general_settings['computation_mode']:>10}=Opération : Déf=Calcul ; A=Actualisation seule du fichier des paramètres
 *** Options Générales               ***
{general_settings['n_sites']:>10}=Nombre de Sites (Bassins) à modéliser successivement
{general_settings['forecast_data_type']:>10}=Type de donnée pour Prévision (0=Débits de Rivière , 1=Niveaux de Nappe)
{general_settings['streamflow_obs_weight']:>10}=Observations de Débits de Rivière : Importance (entier : 0 à 10 ;  0=Non)
{general_settings['piezo-level_obs_weight']:>10}=Observations de Niveaux de Nappe  : Importance (entier : 0 à 10 ;  0=Non)
{general_settings['calc_streamflow']:>10}=Calcul des Débits de Rivière : (0=Non  ;  1=Oui)
{general_settings['calc_piezo-level']:>10}=Calcul des Niveaux de Nappe  : (0=Non  ;  1=Oui)
{general_settings['save_recharge_effective-rainfall']:>10}=Sauvegarde de la Recharge et de la Pluie Efficace (0=Non  ;  1=Oui)
{general_settings['save_streamflow_piezo-level']:>10}=Sauvegarde des Débit/Niveaux simulés : (0=Non  ;  1=Oui)
{general_settings['save_water-balance']:>10}=Sauvegarde des termes du Bilan : (0=Non ; 1=Annuel ; 2=Mensuel ; 3=Tous les pas de temps)
{general_settings['verbose']:>10}=Allègement du Listing (0=Complet ; 1=Allégé ; 2=Supprimé)
{general_settings['computation_scheme']:>10}=Schéma de calcul (0=Gardénia ; 5=Ruissell,Drainage ; etc.)
{general_settings['draw_series']:>10}=Dessin de la série simulée (0=non ; 1=Oui ; 2=Oui avec décomposition)
{general_settings['transform_calibration_data']:>10}=Transformation du débit pour calibration (0=Non ; 99= Racine_Débit; 97= Logar_Débits ; etc.)
{general_settings['minimise_streamflow_bias']:>10}=Poids (%) de minimisation du biais de simulation des Débits Rivière (0 = Non ; 100 = 100 %)
{general_settings['pumping_influencing_streamflow']:>10}=Pompage influençant les Débits de Rivière (0=Non ; 1=Oui ; 2=Oui en rivière)
{general_settings['pumping_influencing_piezo-level']:>10}=Pompage influençant les Niveaux de Nappe (0=Non ; 1=Oui)
{general_settings['forecast_run']:>10}=Calcul avec Prévision (0=Non ; 1=Oui ; -1=Préparation uniquement) [3, 4 = Particulier]
{general_settings['forecast_method']:>10}=Méthode de Prévision (0=Ajustement Réservoirs ; 1=Décalage avec 1/2 vie)
{general_settings['underground_exchange_scheme']:>10}=Schéma d'échanges souterr. avec extérieur (0=% Débit Souterr. (++) ; 1=Facteur Niv_Souterr.)
{general_settings['daily_summary']:>10}=Bilan journalier même si pluie Décadaire ou Mensuelle (0=Non ; 1=Oui)
{general_settings['consider_snow']:>10}=Prise en compte de la Neige (0=Non  ;  1=Oui)
{general_settings['snowfall_in_file']:>10}=Précipitations neigeuses dans un fichier propre (0 = avec pluies ; 1 = fichier séparé)
{general_settings['data_per_hydro_year']:>10}=Données par années hydrologiques [début 1 août] (0=années Civiles ; 1=années Hydrologiques)
{general_settings['streamflow_loss']:>10}=Perte de Débit : 0=Non ; 1=Perd le Debit Souterrain le plus Lent ; -1=Perd le Ruissellement
{general_settings['sensitivity_analysis']:>10}=Analyse de Sensibilité (0=Non  ;  1=Oui uniquement analyse de Sensibilité)
{general_settings['save_impulse_and_cumulative_response']:>10}=Sauvegarde de la 'Réponse impulsionnelle' et de la 'Réponse Cumulée' (1=Oui)
{general_settings['site_data_in_columns']:>10}=Données de tous les sites dans différentes colonnes d'un même fichier (Déf=0)
{general_settings['simulation_rainfall_column_number']:>10}=Numéro de la 'colonne' des Pluies       : Déf=0 <=> 1ère colonne de données
{general_settings['simulation_pet_column_number']:>10}=Numéro de la 'colonne' des ETP          : Déf=0=Identique à la pluie
{general_settings['simulation_streamflow_column_number']:>10}=Numéro de la 'colonne' des Débits       : Déf=0=Identique à la pluie
{general_settings['simulation_piezo-level_column_number']:>10}=Numéro de la 'colonne' des Niveaux      : Déf=0=Identique à la pluie
{general_settings['simulation_air-temp_column_number']:>10}=Numéro de la 'colonne' des Températures : Déf=0=Identique à la pluie
{general_settings['simulation_snowfall_column_number']:>10}=Numéro de la 'colonne' de la Neige      : Déf=0=Identique à la pluie
{general_settings['simulation_pumping_column_number']:>10}=Numéro de la 'colonne' des Pompages     : Déf=0=Identique à la pluie
{general_settings['forecast_rainfall_column_number']:>10}=Numéro de la 'colonne' des Pluies pour Prévision  : Déf=0=Identique à la pluie
{general_settings['forecast_air-temp_column_number']:>10}=Numéro de la 'colonne' des Tempér. pour Prévision : Déf=0=Identique à la pluie
{general_settings['forecast_pet_column_number']:>10}=Numéro de la 'colonne' des ETP pour Prévision     : Déf=0=Identique à la pluie
{general_settings['forecast_snowfall_column_number']:>10}=Numéro de la 'colonne' de la Neige pour Prévision : Déf=0=Identique à la pluie
{general_settings['weather_data_weighting_per_time_step']:>10}=Météo (Pluie, ETP, ...) pondérée à chaque pas [1=Fich. annuels SAFRAN , 2=Fichier unique]
{general_settings['save_weather_data_weighting']:>10}=Sauvegarde de la météo pondérée => Fichier (futurs runs + rapides et portables) [1=Oui]
{general_settings['openpalm_coupling']:>10}=Couplage avec le coupleur OpenPalm (0=Non ; 1=Couplage Météo)
 *** Pas de temps du Fichier Pluie, Neige, Pompage    ***
{time['rainfall_snowfall_pumping_timestep']:>10}= Pas de temps :  0=Journalier 1=Pentadaire 2=Décadaire 3=Mensuel 4=Autre 5=5_Jours 7=7_Jours
{time['rainfall_snowfall_pumping_format']:>10}= Format : 0=Gardénia_Sequentiel  1=Gardénia_Annuaire  2=Libre  3=Excel
 *** Pas de temps du Fichier Température              ***
{time['air-temp_timestep']:>10}= Pas de temps :  0=Journalier 1=Pentadaire 2=Décadaire 3=Mensuel 4=Autre 5=5_Jours 7=7_Jours
{time['air-temp_format']:>10}= Format : 0=Gardénia_Sequentiel  1=Gardénia_Annuaire  2=Libre  3=Excel
 *** Pas de temps du Fichier ETP                      ***
{time['pet_timestep']:>10}= Pas de temps :  0=Journalier 1=Pentadaire 2=Décadaire 3=Mensuel 4=Autre 5=5_Jours 7=7_Jours
{time['pet_format']:>10}= Format : 0=Gardénia_Sequentiel  1=Gardénia_Annuaire  2=Libre  3=Excel
 *** Pas de temps du Fichier Débits, Niveaux Observés ***
{time['streamflow_piezo-level_timestep']:>10}= Pas de temps :  0=Journalier 1=Pentadaire 2=Décadaire 3=Mensuel 4=Autre 5=5_Jours 7=7_Jours
{time['streamflow_piezo-level_format']:>10}= Format : 0=Gardénia_Sequentiel  1=Gardénia_Annuaire  2=Libre  3=Excel
 *** Durée du pas de temps s'il est non-standard ***
{time['non_standard_timestep_duration_unit']:>10}=Unité de durée des Pas si non-standard (sec,min,heu,jou,moi,ann)
{time['non_standard_timestep_duration']:>10}=Durée du pas de temps (dans l'unité)
 *** >>>>>>>>>>>>>> Fin des données communes ] >>>>>
 *** <<<<<<<<<<<< Début des données du bassin [ <<<<<
{description['basin']}
{filter_settings['observed_streamflow_to_consider']['max']:10f}=Valeur Maximale du Débit de Rivière Observé prise en compte (0 = toutes)
{filter_settings['observed_streamflow_to_consider']['min']:10f}=Valeur Minimale du Débit de Rivière Observé prise en compte (0 = toutes)
{filter_settings['observed_piezo-level_to_consider']['max']:10f}=Valeur Maximale du Niveau de Nappe Observé prise en compte (0 = toutes)
{filter_settings['observed_piezo-level_to_consider']['min']:10f}=Valeur Minimale du Niveau de Nappe Observé prise en compte (0 = toutes)
{forecast_settings['readjustment_factor']:10f}=Coefficient de réajustement pour la prévision [0 à 1]
{forecast_settings['standard_deviation_of_intermediate_reservoir']:10f}=Écart-type de l'alimentation du Réservoir intermédiaire  (pour la prévision)
{forecast_settings['standard_deviation_of_groundwater_reservoir_1']:10f}=Écart-type de l'alimentation du Réservoir Souterrain n°1 (pour la prévision)
{forecast_settings['standard_deviation_of_groundwater_reservoir_2']:10f}=Écart-type de l'alimentation du Réservoir Souterrain n°2 (pour la prévision)
{filter_settings['simulated_streamflow_lower_limit_to_apply']:10f}=Débit Rivière réservé (valeur simulée minimale possible) (Déf=0)
{forecast_settings['standard_deviation_of_observed_piezo-level']:10f}=Écart-type des observations de niveau de nappe (pour la prévision)
{forecast_settings['half-life_fall_streamflow_forecast']:10f}=Temps de 1/2 vie de l'écart de prévision de Débit  de rivière (pas de temps)
{forecast_settings['half-life_fall_piezo-level_forecast']:10f}=Temps de 1/2 vie de l'écart de prévision de Niveau de Nappe   (pas de temps)
 *** Options du Bassin               ***
{basin_settings['time']['simulation']['n_years_in_data']:>10}=Nombre d'Années des séries de données (Pluie, ETP, Observations) [0 => Toutes]
{basin_settings['model']['initialisation']['spinup']['n_years']:>10}=Nombre d'Années démarrage (-n pour générer n année moy fictives de démarrage)
{basin_settings['model']['initialisation']['spinup']['n_cycles']:>10}=Nombre de cycles de démarrage (déf. = 1)
{basin_settings['time']['simulation']['first_year']:>10}=Date de la première année des données (par ex. 2017)
{basin_settings['time']['delay_in_rainfall_data']:>10}=Décalage dans la série des Pluies [+5 => Retarde de 5 pas ; -4 Avance de 4 pas]
{basin_settings['time']['delay_in_streamflow_piezo-level_data']:>10}=Décalage de la série des Débits/Niveaux observés [ex: -2 => Avance de 2 pas]
{basin_settings['model']['initialisation']['antecedent_conditions']:>10}=État initial : 0=Pluie Effic. moyenne ; -1=Réservoirs vides ; -2=RuMax vide aussi
{basin_settings['model']['calibration']['max_iterations']:>10}=Nombre maxi. d'itérations pour la calibration (0 = aucune itération, pas de calibrat.)
{basin_settings['time']['rainfall_mean_duration_within_timestep']:>10}=Durée des pluies en moyenne par pas (%) (utilisations avancées)[défaut = 100 %]
{basin_settings['model']['structure']['n_groundwater_reservoirs']:>10}=Nombre de réservoirs souterrains (1 ou 2 ou -1=Double + seuil)      [déf = 1]
{basin_settings['model']['structure']['groundwater_reservoir_for_piezo-level']:>10}=Numéro du réservoir souterr. <=> Niveau nappe (si 2 réserv. souterr.) [déf = 1]
{basin_settings['model']['calibration']['n_tail_years_to_trim']:>10}=Nombre d'années finales à ignorer pour la calibration (déf = 0) [< 0 => n° last ann]
{basin_settings['time']['simulation']['first_day']:>10}=Numéro du Jour initial [Déf=1] (si durée non-standard) ; ex. 31 pour 31 Déc.
{basin_settings['time']['simulation']['first_month']:>10}=Numéro du Mois initial [Déf=1] (si durée non-standard) ; ex. 12 pour 31 Déc.
{basin_settings['time']['simulation']['first_hour']:>10}=Heure initiale [Déf=0] (si durée non-standard) ; par ex. 15 pour 15h30
{basin_settings['time']['simulation']['first_minute']:>10}=Minute initiale [Déf=0] (si durée non-standard) ; Par ex. 30 pour 15h30
{basin_settings['model']['structure']['intermediate_runoff_by_overspill']:>10}=Perte du débit de Ruissellement par Débordement au-dessus du Seuil [0=Non ; 1=Perte ; 2 => Rés Sout]
{basin_settings['model']['structure']['intermediate_reservoir_evapotranspiration_decrease_only_when_half_empty']:>10}=Décroissance de l'évapotranspiration si saturation du réservoir sol < 50% (0=Non ; 1=Oui)
{basin_settings['model']['structure']['constant_runoff_ratio_scheme']:>10}=Schéma à taux de ruissellement constant (pour comparaison ; déconseillé) (0=Non ; 1=Oui)
{basin_settings['model']['structure']['storage_coefficient_computation_scheme']:>10}=Méthode de calcul du coeff. d'Emmagasinement [0 = Corrélation ; 1 = Optimis entre bornes]
 *** Paramètres de Prévision         ***
{basin_settings['time']['forecast']['n_years_in_data']:>10}=Nombre d'Années de données du fichier de pluies etc. pour la Prévision
{basin_settings['time']['forecast']['issue_day']:>10}=Jour d'émission de la prévision (1-31) si pas de temps journalier (sinon : 0)
{basin_settings['time']['forecast']['issue_month']:>10}=Numéro du Mois [si journalier ou mensuel] (ou n° du pas) d'émission de la prévision)
{basin_settings['time']['forecast']['span']:>10}=Portée de la Prévision (Nombre de pas de temps de la prévision)
{basin_settings['time']['forecast']['first_year']:>10}=Date de la Première Année des fichiers météo de prévision [si journalier] (déf = 0)
 *** Position des Données du bassin  ***
{basin_settings['data']['basin_column_number_in_data']:>10}=N° de la 'colonne' des données : (-1 => N° d'ordre du bassin) Déf=0 <=> Col. n°1
 *** Paramètres Hydroclimatiques            ***
{physical_parameters['annual_effective-rainfall']['val']:10f}=Pluie Eff. annuelle pour initialis. (0=équil.) (mm/an)
{physical_parameters['external_flow']['val']:10f}=Débit extérieur éventuel                        (m3/s) Opti= {physical_parameters['external_flow']['opt']:1}
{physical_parameters['basin_area']['val']:10f}=Superficie du bassin versant                     (km2) Opti= {physical_parameters['basin_area']['opt']:1}
{physical_parameters['groundwater_base_level']['val']:10f}=Niveau de base local de la nappe               (m NGF) Opti= {physical_parameters['groundwater_base_level']['opt']:1}
{physical_parameters['rainfall_correction']['val']:10f}=Correction globale des Pluies                      (%) Opti= {physical_parameters['rainfall_correction']['opt']:1}
{physical_parameters['pet_correction']['val']:10f}=Correction globale de l'ETP                        (%) Opti= {physical_parameters['pet_correction']['opt']:1}
{physical_parameters['thornthewaite_reservoir_capacity']['val']:10f}=Capacité du réservoir sol 'réserve utile'         (mm) Opti= {physical_parameters['thornthewaite_reservoir_capacity']['opt']:1}
{physical_parameters['progressive_reservoir_capacity']['val']:10f}=Capacité du réservoir sol progressif              (mm) Opti= {physical_parameters['progressive_reservoir_capacity']['opt']:1}
{physical_parameters['intermediate_runoff_seepage']['val']:10f}=Hauteur de répartition Ruissellement-Percolation  (mm) Opti= {physical_parameters['intermediate_runoff_seepage']['opt']:1}
{physical_parameters['intermediate_half-life_seepage']['val']:10f}=Temps de 1/2 percolation vers la nappe          (mois) Opti= {physical_parameters['intermediate_half-life_seepage']['opt']:1}
{physical_parameters['groundwater_1_drainage']['val']:10f}=Temps de 1/2 tarissement du débit souterr. n°1  (mois) Opti= {physical_parameters['groundwater_1_drainage']['opt']:1}
{physical_parameters['groundwater_1_2_exchange']['val']:10f}=Temps de 1/2 transfert vers la nappe profonde   (mois) Opti= {physical_parameters['groundwater_1_2_exchange']['opt']:1}
{physical_parameters['groundwater_1_double_outflow_threshold']['val']:10f}=Seuil d'écoulement souterrain n°1 (rés. double)   (mm) Opti= {physical_parameters['groundwater_1_double_outflow_threshold']['opt']:1}
{physical_parameters['groundwater_2_drainage']['val']:10f}=Temps de 1/2 tarissement du débit souterr. n°2  (mois) Opti= {physical_parameters['groundwater_2_drainage']['opt']:1}
{physical_parameters['time_of_concentration']['val']:10f}=Temps de réaction ('retard') du débit   (pas de temps) Opti= {physical_parameters['time_of_concentration']['opt']:1}
{physical_parameters['groundwater_external_exchange']['val']:10f}=Facteur d'échange souterrain externe               (%) Opti= {physical_parameters['groundwater_external_exchange']['opt']:1}
{physical_parameters['thornthewaite_reservoir_initial_deficit']['val']:10f}=Déficit initial du réservoir sol 'réserve utile'  (mm) Opti= {physical_parameters['thornthewaite_reservoir_initial_deficit']['opt']:1}
{physical_parameters['progressive_reservoir_initial_deficit']['val']:10f}=Déficit initial du réservoir sol progressif       (mm) Opti= {physical_parameters['progressive_reservoir_initial_deficit']['opt']:1}
{physical_parameters['intermediate_runoff_threshold']['val']:10f}=Seuil de ruissellement par débordement            (mm) Opti= {physical_parameters['intermediate_runoff_threshold']['opt']:1}
{physical_parameters['intermediate_half-life_runoff_by_overspill']['val']:10f}=Temps de 1/2 ruissell. par débordement  (Pas de temps) Opti= {physical_parameters['intermediate_half-life_runoff_by_overspill']['opt']:1}
{physical_parameters['intermediate_half-life_max_runoff_decrease']['val']:10f}=Temps de 1/2 décroiss. maximal du ruissellement (mois) Opti= {physical_parameters['intermediate_half-life_max_runoff_decrease']['opt']:1}
{physical_parameters['basin_area_correction']['val']:10f}=Facteur de correction de la superficie du bassin   (-) Opti= {physical_parameters['basin_area_correction']['opt']:1}
{physical_parameters['groundwater_storage_coefficient']['val']:10f}=Coefficient d'emmagasinement de la nappe           (%) Opti= {physical_parameters['groundwater_storage_coefficient']['opt']:1}
 *** Bornes des paramètres Hydroclimatiques ***
{physical_parameters['rainfall_correction']['min']:10f}=Min : Correction globale des Pluies                      (%) Max ={physical_parameters['rainfall_correction']['max']:10.5f}
{physical_parameters['pet_correction']['min']:10f}=Min : Correction globale de l'ETP                        (%) Max ={physical_parameters['pet_correction']['max']:10.5f}
{physical_parameters['thornthewaite_reservoir_capacity']['min']:10f}=Min : Capacité du réservoir sol 'réserve utile'         (mm) Max ={physical_parameters['thornthewaite_reservoir_capacity']['max']:10.5f}
{physical_parameters['progressive_reservoir_capacity']['min']:10f}=Min : Capacité du réservoir sol progressif              (mm) Max ={physical_parameters['progressive_reservoir_capacity']['max']:10.5f}
{physical_parameters['intermediate_runoff_seepage']['min']:10f}=Min : Hauteur de répartition Ruissellement-Percolation  (mm) Max ={physical_parameters['intermediate_runoff_seepage']['max']:10.5f}
{physical_parameters['intermediate_half-life_seepage']['min']:10f}=Min : Temps de 1/2 percolation vers la nappe          (mois) Max ={physical_parameters['intermediate_half-life_seepage']['max']:10.5f}
{physical_parameters['groundwater_1_drainage']['min']:10f}=Min : Temps de 1/2 tarissement du débit souterr. n°1  (mois) Max ={physical_parameters['groundwater_1_drainage']['max']:10.5f}
{physical_parameters['groundwater_1_2_exchange']['min']:10f}=Min : Temps de 1/2 transfert vers la nappe profonde   (mois) Max ={physical_parameters['groundwater_1_2_exchange']['max']:10.5f}
{physical_parameters['groundwater_1_double_outflow_threshold']['min']:10f}=Min : Seuil d'écoulement souterrain n°1 (rés. double)   (mm) Max ={physical_parameters['groundwater_1_double_outflow_threshold']['max']:10.5f}
{physical_parameters['groundwater_2_drainage']['min']:10f}=Min : Temps de 1/2 tarissement du débit souterr. n°2  (mois) Max ={physical_parameters['groundwater_2_drainage']['max']:10.5f}
{physical_parameters['time_of_concentration']['min']:10f}=Min : Temps de réaction ('retard') du débit   (pas de temps) Max ={physical_parameters['time_of_concentration']['max']:10.5f}
{physical_parameters['groundwater_external_exchange']['min']:10f}=Min : Facteur d'échange souterrain externe               (%) Max ={physical_parameters['groundwater_external_exchange']['max']:10.5f}
{physical_parameters['thornthewaite_reservoir_initial_deficit']['min']:10f}=Min : Déficit initial du réservoir sol 'réserve utile'  (mm) Max ={physical_parameters['thornthewaite_reservoir_initial_deficit']['max']:10.5f}
{physical_parameters['progressive_reservoir_initial_deficit']['min']:10f}=Min : Déficit initial du réservoir sol progressif       (mm) Max ={physical_parameters['progressive_reservoir_initial_deficit']['max']:10.5f}
{physical_parameters['intermediate_runoff_threshold']['min']:10f}=Min : Seuil de ruissellement par débordement            (mm) Max ={physical_parameters['intermediate_runoff_threshold']['max']:10.5f}
{physical_parameters['intermediate_half-life_runoff_by_overspill']['min']:10f}=Min : Temps de 1/2 ruissell. par débordement  (Pas de temps) Max ={physical_parameters['intermediate_half-life_runoff_by_overspill']['max']:10.5f}
{physical_parameters['intermediate_half-life_max_runoff_decrease']['min']:10f}=Min : Temps de 1/2 décroiss. maximal du ruissellement (mois) Max ={physical_parameters['intermediate_half-life_max_runoff_decrease']['max']:10.5f}
{physical_parameters['basin_area_correction']['min']:10f}=Min : Facteur de correction de la superficie du bassin   (-) Max ={physical_parameters['basin_area_correction']['max']:10.5f}
{physical_parameters['groundwater_storage_coefficient']['min']:10f}=Min : Coefficient d'emmagasinement de la nappe           (%) Max ={physical_parameters['groundwater_storage_coefficient']['max']:10.5f}
 *** Paramètres de Fonte de Neige           ***
{physical_parameters['air-temp_correction']['val']:10f}=Correction globale de la température              (°C) Opti= {physical_parameters['air-temp_correction']['opt']:1}
{physical_parameters['snowfall_retention_factor']['val']:10f}=Taux de rétention de la neige                      (%) Opti= {physical_parameters['snowfall_retention_factor']['opt']:1}
{physical_parameters['snow_evaporation_factor']['val']:10f}=Facteur d'évaporation de la neige                  (%) Opti= {physical_parameters['snow_evaporation_factor']['opt']:1}
{physical_parameters['snow_melt_correction_with_rainfall']['val']:10f}=Correction de fonte de la neige par la pluie       (%) Opti= {physical_parameters['snow_melt_correction_with_rainfall']['opt']:1}
{physical_parameters['natural_snow_melting_threshold']['val']:10f}=Température seuil de fonte naturelle de la neige  (°C) Opti= {physical_parameters['natural_snow_melting_threshold']['opt']:1}
{physical_parameters['snow_melt_degree_day_factor']['val']:10f}=Constante de fonte par la température     (mm/°C/jour) Opti= {physical_parameters['snow_melt_degree_day_factor']['opt']:1}
{physical_parameters['snow_melting_in_contact_with_soil']['val']:10f}=Fonte de la neige au contact du sol     (1/10 mm/jour) Opti= {physical_parameters['snow_melting_in_contact_with_soil']['opt']:1}
 *** Bornes des paramètres Neige            ***
{physical_parameters['air-temp_correction']['min']:10f}=Min : Correction globale de la température              (°C) Max ={physical_parameters['air-temp_correction']['max']:10.5f}
{physical_parameters['snowfall_retention_factor']['min']:10f}=Min : Taux de rétention de la neige                      (%) Max ={physical_parameters['snowfall_retention_factor']['max']:10.5f}
{physical_parameters['snow_evaporation_factor']['min']:10f}=Min : Facteur d'évaporation de la neige                  (%) Max ={physical_parameters['snow_evaporation_factor']['max']:10.5f}
{physical_parameters['snow_melt_correction_with_rainfall']['min']:10f}=Min : Correction de fonte de la neige par la pluie       (%) Max ={physical_parameters['snow_melt_correction_with_rainfall']['max']:10.5f}
{physical_parameters['natural_snow_melting_threshold']['min']:10f}=Min : Température seuil de fonte naturelle de la neige  (°C) Max ={physical_parameters['natural_snow_melting_threshold']['max']:10.5f}
{physical_parameters['snow_melt_degree_day_factor']['min']:10f}=Min : Constante de fonte par la température     (mm/°C/jour) Max ={physical_parameters['snow_melt_degree_day_factor']['max']:10.5f}
{physical_parameters['snow_melting_in_contact_with_soil']['min']:10f}=Min : Fonte de la neige au contact du sol     (1/10 mm/jour) Max ={physical_parameters['snow_melting_in_contact_with_soil']['max']:10.5f}
 *** Paramètres de Pompage           ***
{physical_parameters['pumping_river_influence_factor']['val']:10f}=Coefficient d'influence du pompage => Débit Rivière (-) Opti= {physical_parameters['pumping_river_influence_factor']['opt']:1}
{physical_parameters['pumping_river_half-life_rise']['val']:10f}=Temps de 1/2 montée du pompage infl. => Rivière  (mois) Opti= {physical_parameters['pumping_river_half-life_rise']['opt']:1}
{physical_parameters['pumping_river_half-life_fall']['val']:10f}=Temps de 1/2 stabilisation du pompage => Rivière (mois) Opti= {physical_parameters['pumping_river_half-life_fall']['opt']:1}
{physical_parameters['pumping_groundwater_influence_factor']['val']:10f}=Coefficient d'influence du pompage => Niveau Nappe  (-) Opti= {physical_parameters['pumping_groundwater_influence_factor']['opt']:1}
{physical_parameters['pumping_groundwater_half-life_rise']['val']:10f}=Temps de 1/2 montée du pompage infl. => Nappe    (mois) Opti= {physical_parameters['pumping_groundwater_half-life_rise']['opt']:1}
{physical_parameters['pumping_groundwater_half-life_fall']['val']:10f}=Temps de 1/2 stabilisation du pompage => Nappe   (mois) Opti= {physical_parameters['pumping_groundwater_half-life_fall']['opt']:1}
 *** Bornes des paramètres Pompage   ***
{physical_parameters['pumping_river_half-life_rise']['min']:10f}=Min : Temps de 1/2 montée du pompage infl. => Rivière  (mois) Max ={physical_parameters['pumping_river_half-life_rise']['max']:10.5f}
{physical_parameters['pumping_river_half-life_fall']['min']:10f}=Min : Temps de 1/2 stabilisation du pompage => Rivière (mois) Max ={physical_parameters['pumping_river_half-life_fall']['max']:10.5f}
{physical_parameters['pumping_groundwater_half-life_rise']['min']:10f}=Min : Temps de 1/2 montée du pompage infl. => Nappe    (mois) Max ={physical_parameters['pumping_groundwater_half-life_rise']['max']:10.5f}
{physical_parameters['pumping_groundwater_half-life_fall']['min']:10f}=Min : Temps de 1/2 stabilisation du pompage => Nappe   (mois) Max ={physical_parameters['pumping_groundwater_half-life_fall']['max']:10.5f}
 *** >>>>>>>>>>>>>> Fin des données du bassin ] >>>>>
 """


def _parse_file(file: str, parser: dict) -> dict:
    d = {}

    with open(file, 'r', encoding='cp1252') as f:
        # explore file line by line
        for ln, txt in enumerate(f, start=1):
            # if line number contained in parser, there is parsing to do
            if ln in parser:
                for key_path, (sep, idx) in parser[ln].items():
                    # key path features the keys separated by dots
                    # to use to navigate through the nested dictionary
                    keys = key_path.split('.')

                    # iteratively go down the nested dictionary and
                    # create dictionaries if necessary along the way
                    d_ = d
                    for key in keys[:-1]:
                        if key not in d_:
                            d_[key] = {}
                        d_ = d_[key]

                    # finally assign the value once in the right place
                    # in the nested dictionary
                    if (
                            re.compile(r'physical_parameters\..*\.(val|min|max)').findall(key_path)
                            or re.compile(r'filter_settings\..*').findall(key_path)
                            or re.compile(r'forecast_settings\..*').findall(key_path)
                    ):
                        d_[keys[-1]] = float(txt.split(sep)[idx].strip())
                    elif (
                            re.compile(r'physical_parameters\..*\.opt').findall(key_path)
                    ):
                        d_[keys[-1]] = bool(int(txt.split(sep)[idx].strip()))
                    else:
                        d_[keys[-1]] = txt.split(sep)[idx].strip()

    return d


def parse_rga_content(rga_file: str) -> dict:
    return _parse_file(rga_file, _rga_line_parsing)


def parse_gar_content(gar_file: str) -> dict:
    return _parse_file(gar_file, _gar_line_parsing)

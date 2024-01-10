

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
 {general_settings['user_profile']:>9}=Profil d'utilisation : 0=simple ; A=Avancé (Neige, Pompage, Prévi etc.)
 {general_settings['execution_mode']:>9}=Mode d'exécution (C = Contrôle sur écran ; Déf=Rapide ; D=Direct ; M=Muet)
 {general_settings['computation_mode']:>9}=Opération : Déf=Calcul ; A=Actualisation seule du fichier des paramètres
 *** Options Générales               ***
 {general_settings['n_sites']:>9}=Nombre de Sites (Bassins) à modéliser successivement
 {general_settings['forecast_data_type']:>9}=Type de donnée pour Prévision (0=Débits de Rivière , 1=Niveaux de Nappe)
 {general_settings['streamflow_obs_weight']:>9}=Observations de Débits de Rivière : Importance (entier : 0 à 10 ;  0=Non)
 {general_settings['piezo-level_obs_weight']:>9}=Observations de Niveaux de Nappe  : Importance (entier : 0 à 10 ;  0=Non)
 {general_settings['calc_streamflow']:>9}=Calcul des Débits de Rivière : (0=Non  ;  1=Oui)
 {general_settings['calc_piezo-level']:>9}=Calcul des Niveaux de Nappe  : (0=Non  ;  1=Oui)
 {general_settings['save_recharge_effective-rainfall']:>9}=Sauvegarde de la Recharge et de la Pluie Efficace (0=Non  ;  1=Oui)
 {general_settings['save_streamflow_piezo-level']:>9}=Sauvegarde des Débit/Niveaux simulés : (0=Non  ;  1=Oui)
 {general_settings['save_water-balance']:>9}=Sauvegarde des termes du Bilan : (0=Non ; 1=Annuel ; 2=Mensuel ; 3=Tous les pas de temps)
 {general_settings['verbose']:>9}=Allègement du Listing (0=Complet ; 1=Allégé ; 2=Supprimé)
 {general_settings['computation_scheme']:>9}=Schéma de calcul (0=Gardénia ; 5=Ruissell,Drainage ; etc.)
 {general_settings['draw_series']:>9}=Dessin de la série simulée (0=non ; 1=Oui ; 2=Oui avec décomposition)
 {general_settings['transform_calibration_data']:>9}=Transformation du débit pour calibration (0=Non ; 99= Racine_Débit; 97= Logar_Débits ; etc.)
 {general_settings['minimise_streamflow_bias']:>9}=Poids (%) de minimisation du biais de simulation des Débits Rivière (0 = Non ; 100 = 100 %)
 {general_settings['pumping_influencing_streamflow']:>9}=Pompage influençant les Débits de Rivière (0=Non ; 1=Oui ; 2=Oui en rivière)
 {general_settings['pumping_influencing_piezo-level']:>9}=Pompage influençant les Niveaux de Nappe (0=Non ; 1=Oui)
 {general_settings['forecast_run']:>9}=Calcul avec Prévision (0=Non ; 1=Oui ; -1=Préparation uniquement) [3, 4 = Particulier]
 {general_settings['forecast_method']:>9}=Méthode de Prévision (0=Ajustement Réservoirs ; 1=Décalage avec 1/2 vie)
 {general_settings['underground_exchange_scheme']:>9}=Schéma d'échanges souterr. avec extérieur (0=% Débit Souterr. (++) ; 1=Facteur Niv_Souterr.)
 {general_settings['daily_summary']:>9}=Bilan journalier même si pluie Décadaire ou Mensuelle (0=Non ; 1=Oui)
 {general_settings['consider_snow']:>9}=Prise en compte de la Neige (0=Non  ;  1=Oui)
 {general_settings['snowfall_in_file']:>9}=Précipitations neigeuses dans un fichier propre (0 = avec pluies ; 1 = fichier séparé)
 {general_settings['data_per_hydro_year']:>9}=Données par années hydrologiques [début 1 août] (0=années Civiles ; 1=années Hydrologiques)
 {general_settings['streamflow_loss']:>9}=Perte de Débit : 0=Non ; 1=Perd le Debit Souterrain le plus Lent ; -1=Perd le Ruissellement
 {general_settings['sensitivity_analysis']:>9}=Analyse de Sensibilité (0=Non  ;  1=Oui uniquement analyse de Sensibilité)
 {general_settings['save_impulse_and_cumulative_response']:>9}=Sauvegarde de la 'Réponse impulsionnelle' et de la 'Réponse Cumulée' (1=Oui)
 {general_settings['site_data_in_columns']:>9}=Données de tous les sites dans différentes colonnes d'un même fichier (Déf=0)
 {general_settings['simulation_rainfall_column_number']:>9}=Numéro de la 'colonne' des Pluies       : Déf=0 <=> 1ère colonne de données
 {general_settings['simulation_pet_column_number']:>9}=Numéro de la 'colonne' des ETP          : Déf=0=Identique à la pluie
 {general_settings['simulation_streamflow_column_number']:>9}=Numéro de la 'colonne' des Débits       : Déf=0=Identique à la pluie
 {general_settings['simulation_piezo-level_column_number']:>9}=Numéro de la 'colonne' des Niveaux      : Déf=0=Identique à la pluie
 {general_settings['simulation_air-temp_column_number']:>9}=Numéro de la 'colonne' des Températures : Déf=0=Identique à la pluie
 {general_settings['simulation_snowfall_column_number']:>9}=Numéro de la 'colonne' de la Neige      : Déf=0=Identique à la pluie
 {general_settings['simulation_pumping_column_number']:>9}=Numéro de la 'colonne' des Pompages     : Déf=0=Identique à la pluie
 {general_settings['forecast_rainfall_column_number']:>9}=Numéro de la 'colonne' des Pluies pour Prévision  : Déf=0=Identique à la pluie
 {general_settings['forecast_air-temp_column_number']:>9}=Numéro de la 'colonne' des Tempér. pour Prévision : Déf=0=Identique à la pluie
 {general_settings['forecast_pet_column_number']:>9}=Numéro de la 'colonne' des ETP pour Prévision     : Déf=0=Identique à la pluie
 {general_settings['forecast_snowfall_column_number']:>9}=Numéro de la 'colonne' de la Neige pour Prévision : Déf=0=Identique à la pluie
 {general_settings['weather_data_weighting_per_time_step']:>9}=Météo (Pluie, ETP, ...) pondérée à chaque pas [1=Fich. annuels SAFRAN , 2=Fichier unique]
 {general_settings['save_weather_data_weighting']:>9}=Sauvegarde de la météo pondérée => Fichier (futurs runs + rapides et portables) [1=Oui]
 {general_settings['openpalm_coupling']:>9}=Couplage avec le coupleur OpenPalm (0=Non ; 1=Couplage Météo)
 *** Pas de temps du Fichier Pluie, Neige, Pompage    ***
 {time['rainfall_snowfall_pumping_timestep']:>9}= Pas de temps :  0=Journalier 1=Pentadaire 2=Décadaire 3=Mensuel 4=Autre 5=5_Jours 7=7_Jours
 {time['rainfall_snowfall_pumping_format']:>9}= Format : 0=Gardénia_Sequentiel  1=Gardénia_Annuaire  2=Libre  3=Excel
 *** Pas de temps du Fichier Température              ***
 {time['air-temp_timestep']:>9}= Pas de temps :  0=Journalier 1=Pentadaire 2=Décadaire 3=Mensuel 4=Autre 5=5_Jours 7=7_Jours
 {time['air-temp_format']:>9}= Format : 0=Gardénia_Sequentiel  1=Gardénia_Annuaire  2=Libre  3=Excel
 *** Pas de temps du Fichier ETP                      ***
 {time['pet_timestep']:>9}= Pas de temps :  0=Journalier 1=Pentadaire 2=Décadaire 3=Mensuel 4=Autre 5=5_Jours 7=7_Jours
 {time['pet_format']:>9}= Format : 0=Gardénia_Sequentiel  1=Gardénia_Annuaire  2=Libre  3=Excel
 *** Pas de temps du Fichier Débits, Niveaux Observés ***
 {time['streamflow_piezo-level_timestep']:>9}= Pas de temps :  0=Journalier 1=Pentadaire 2=Décadaire 3=Mensuel 4=Autre 5=5_Jours 7=7_Jours
 {time['streamflow_piezo-level_format']:>9}= Format : 0=Gardénia_Sequentiel  1=Gardénia_Annuaire  2=Libre  3=Excel
 *** Durée du pas de temps s'il est non-standard ***
 {time['non_standard_timestep_duration_unit']:>9}=Unité de durée des Pas si non-standard (sec,min,heu,jou,moi,ann)
 {time['non_standard_timestep_duration']:>9}=Durée du pas de temps (dans l'unité)
 *** >>>>>>>>>>>>>> Fin des données communes ] >>>>>
 *** <<<<<<<<<<<< Début des données du bassin [ <<<<<
{description['basin']}
 {filter_settings['observed_streamflow_to_consider']['max']:9.5f}=Valeur Maximale du Débit de Rivière Observé prise en compte (0 = toutes)
 {filter_settings['observed_streamflow_to_consider']['min']:9.5f}=Valeur Minimale du Débit de Rivière Observé prise en compte (0 = toutes)
 {filter_settings['observed_piezo-level_to_consider']['max']:9.5f}=Valeur Maximale du Niveau de Nappe Observé prise en compte (0 = toutes)
 {filter_settings['observed_piezo-level_to_consider']['min']:9.5f}=Valeur Minimale du Niveau de Nappe Observé prise en compte (0 = toutes)
 {forecast_settings['readjustment_factor']:9.5f}=Coefficient de réajustement pour la prévision [0 à 1]
 {forecast_settings['standard_deviation_of_intermediate_reservoir']:9.5f}=Écart-type de l'alimentation du Réservoir intermédiaire  (pour la prévision)
 {forecast_settings['standard_deviation_of_groundwater_reservoir_1']:9.5f}=Écart-type de l'alimentation du Réservoir Souterrain n°1 (pour la prévision)
 {forecast_settings['standard_deviation_of_groundwater_reservoir_2']:9.5f}=Écart-type de l'alimentation du Réservoir Souterrain n°2 (pour la prévision)
 {filter_settings['simulated_streamflow_lower_limit_to_apply']:9.5f}=Débit Rivière réservé (valeur simulée minimale possible) (Déf=0)
 {forecast_settings['standard_deviation_of_observed_piezo-level']:9.5f}=Écart-type des observations de niveau de nappe (pour la prévision)
 {forecast_settings['half-life_fall_streamflow_forecast']:9.5f}=Temps de 1/2 vie de l'écart de prévision de Débit  de rivière (pas de temps)
 {forecast_settings['half-life_fall_piezo-level_forecast']:9.5f}=Temps de 1/2 vie de l'écart de prévision de Niveau de Nappe   (pas de temps)
 *** Options du Bassin               ***
 {basin_settings['time']['simulation']['n_years_in_data']:>9}=Nombre d'Années des séries de données (Pluie, ETP, Observations) [0 => Toutes]
 {basin_settings['model']['initialisation']['spinup']['n_years']:>9}=Nombre d'Années démarrage (-n pour générer n année moy fictives de démarrage)
 {basin_settings['model']['initialisation']['spinup']['n_cycles']:>9}=Nombre de cycles de démarrage (déf. = 1)
 {basin_settings['time']['simulation']['first_year']:>9}=Date de la première année des données (par ex. 2017)
 {basin_settings['time']['delay_in_rainfall_data']:>9}=Décalage dans la série des Pluies [+5 => Retarde de 5 pas ; -4 Avance de 4 pas]
 {basin_settings['time']['delay_in_streamflow_piezo-level_data']:>9}=Décalage de la série des Débits/Niveaux observés [ex: -2 => Avance de 2 pas]
 {basin_settings['model']['initialisation']['antecedent_conditions']:>9}=État initial : 0=Pluie Effic. moyenne ; -1=Réservoirs vides ; -2=RuMax vide aussi
 {basin_settings['model']['calibration']['max_iterations']:>9}=Nombre maxi. d'itérations pour la calibration (0 = aucune itération, pas de calibrat.)
 {basin_settings['time']['rainfall_mean_duration_within_timestep']:>9}=Durée des pluies en moyenne par pas (%) (utilisations avancées)[défaut = 100 %]
 {basin_settings['model']['structure']['n_groundwater_reservoirs']:>9}=Nombre de réservoirs souterrains (1 ou 2 ou -1=Double + seuil)      [déf = 1]
 {basin_settings['model']['structure']['groundwater_reservoir_for_piezo-level']:>9}=Numéro du réservoir souterr. <=> Niveau nappe (si 2 réserv. souterr.) [déf = 1]
 {basin_settings['model']['calibration']['n_tail_years_to_trim']:>9}=Nombre d'années finales à ignorer pour la calibration (déf = 0) [< 0 => n° last ann]
 {basin_settings['time']['simulation']['first_day']:>9}=Numéro du Jour initial [Déf=1] (si durée non-standard) ; ex. 31 pour 31 Déc.
 {basin_settings['time']['simulation']['first_month']:>9}=Numéro du Mois initial [Déf=1] (si durée non-standard) ; ex. 12 pour 31 Déc.
 {basin_settings['time']['simulation']['first_hour']:>9}=Heure initiale [Déf=0] (si durée non-standard) ; par ex. 15 pour 15h30
 {basin_settings['time']['simulation']['first_minute']:>9}=Minute initiale [Déf=0] (si durée non-standard) ; Par ex. 30 pour 15h30
 {basin_settings['model']['structure']['intermediate_runoff_by_overspill']:>9}=Perte du débit de Ruissellement par Débordement au-dessus du Seuil [0=Non ; 1=Perte ; 2 => Rés Sout]
 {basin_settings['model']['structure']['intermediate_reservoir_evapotranspiration_decrease_only_when_half_empty']:>9}=Décroissance de l'évapotranspiration si saturation du réservoir sol < 50% (0=Non ; 1=Oui)
 {basin_settings['model']['structure']['constant_runoff_ratio_scheme']:>9}=Schéma à taux de ruissellement constant (pour comparaison ; déconseillé) (0=Non ; 1=Oui)
 {basin_settings['model']['structure']['storage_coefficient_computation_scheme']:>9}=Méthode de calcul du coeff. d'Emmagasinement [0 = Corrélation ; 1 = Optimis entre bornes]
 *** Paramètres de Prévision         ***
 {basin_settings['time']['forecast']['n_years_in_data']:>9}=Nombre d'Années de données du fichier de pluies etc. pour la Prévision
 {basin_settings['time']['forecast']['issue_day']:>9}=Jour d'émission de la prévision (1-31) si pas de temps journalier (sinon : 0)
 {basin_settings['time']['forecast']['issue_month']:>9}=Numéro du Mois [si journalier ou mensuel] (ou n° du pas) d'émission de la prévision)
 {basin_settings['time']['forecast']['span']:>9}=Portée de la Prévision (Nombre de pas de temps de la prévision)
 {basin_settings['time']['forecast']['first_year']:>9}=Date de la Première Année des fichiers météo de prévision [si journalier] (déf = 0)
 *** Position des Données du bassin  ***
 {basin_settings['data']['basin_column_number_in_data']:>9}=N° de la 'colonne' des données : (-1 => N° d'ordre du bassin) Déf=0 <=> Col. n°1
 *** Paramètres Hydroclimatiques            ***
 {physical_parameters['annual_effective-rainfall']['val']:9.5f}=Pluie Eff. annuelle pour initialis. (0=équil.) (mm/an)
 {physical_parameters['external_flow']['val']:9.5f}=Débit extérieur éventuel                        (m3/s) Opti= {physical_parameters['external_flow']['opt']:1}
 {physical_parameters['basin_area']['val']:9.5f}=Superficie du bassin versant                     (km2) Opti= {physical_parameters['basin_area']['opt']:1}
 {physical_parameters['groundwater_base_level']['val']:9.5f}=Niveau de base local de la nappe               (m NGF) Opti= {physical_parameters['groundwater_base_level']['opt']:1}
 {physical_parameters['rainfall_correction']['val']:9.5f}=Correction globale des Pluies                      (%) Opti= {physical_parameters['rainfall_correction']['opt']:1}
 {physical_parameters['pet_correction']['val']:9.5f}=Correction globale de l'ETP                        (%) Opti= {physical_parameters['pet_correction']['opt']:1}
 {physical_parameters['thornthewaite_reservoir_capacity']['val']:9.5f}=Capacité du réservoir sol 'réserve utile'         (mm) Opti= {physical_parameters['thornthewaite_reservoir_capacity']['opt']:1}
 {physical_parameters['progressive_reservoir_capacity']['val']:9.5f}=Capacité du réservoir sol progressif              (mm) Opti= {physical_parameters['progressive_reservoir_capacity']['opt']:1}
 {physical_parameters['intermediate_runoff_seepage']['val']:9.5f}=Hauteur de répartition Ruissellement-Percolation  (mm) Opti= {physical_parameters['intermediate_runoff_seepage']['opt']:1}
 {physical_parameters['intermediate_half-life_seepage']['val']:9.5f}=Temps de 1/2 percolation vers la nappe          (mois) Opti= {physical_parameters['intermediate_half-life_seepage']['opt']:1}
 {physical_parameters['groundwater_1_drainage']['val']:9.5f}=Temps de 1/2 tarissement du débit souterr. n°1  (mois) Opti= {physical_parameters['groundwater_1_drainage']['opt']:1}
 {physical_parameters['groundwater_1_2_exchange']['val']:9.5f}=Temps de 1/2 transfert vers la nappe profonde   (mois) Opti= {physical_parameters['groundwater_1_2_exchange']['opt']:1}
 {physical_parameters['groundwater_1_double_outflow_threshold']['val']:9.5f}=Seuil d'écoulement souterrain n°1 (rés. double)   (mm) Opti= {physical_parameters['groundwater_1_double_outflow_threshold']['opt']:1}
 {physical_parameters['groundwater_2_drainage']['val']:9.5f}=Temps de 1/2 tarissement du débit souterr. n°2  (mois) Opti= {physical_parameters['groundwater_2_drainage']['opt']:1}
 {physical_parameters['time_of_concentration']['val']:9.5f}=Temps de réaction ('retard') du débit   (pas de temps) Opti= {physical_parameters['time_of_concentration']['opt']:1}
 {physical_parameters['groundwater_external_exchange']['val']:9.5f}=Facteur d'échange souterrain externe               (%) Opti= {physical_parameters['groundwater_external_exchange']['opt']:1}
 {physical_parameters['thornthewaite_reservoir_initial_deficit']['val']:9.5f}=Déficit initial du réservoir sol 'réserve utile'  (mm) Opti= {physical_parameters['thornthewaite_reservoir_initial_deficit']['opt']:1}
 {physical_parameters['progressive_reservoir_initial_deficit']['val']:9.5f}=Déficit initial du réservoir sol progressif       (mm) Opti= {physical_parameters['progressive_reservoir_initial_deficit']['opt']:1}
 {physical_parameters['intermediate_runoff_threshold']['val']:9.5f}=Seuil de ruissellement par débordement            (mm) Opti= {physical_parameters['intermediate_runoff_threshold']['opt']:1}
 {physical_parameters['intermediate_half-life_runoff_by_overspill']['val']:9.5f}=Temps de 1/2 ruissell. par débordement  (Pas de temps) Opti= {physical_parameters['intermediate_half-life_runoff_by_overspill']['opt']:1}
 {physical_parameters['intermediate_half-life_max_runoff_decrease']['val']:9.5f}=Temps de 1/2 décroiss. maximal du ruissellement (mois) Opti= {physical_parameters['intermediate_half-life_max_runoff_decrease']['opt']:1}
 {physical_parameters['basin_area_correction']['val']:9.5f}=Facteur de correction de la superficie du bassin   (-) Opti= {physical_parameters['basin_area_correction']['opt']:1}
 {physical_parameters['groundwater_storage_coefficient']['val']:9.5f}=Coefficient d'emmagasinement de la nappe           (%) Opti= {physical_parameters['groundwater_storage_coefficient']['opt']:1}
 *** Bornes des paramètres Hydroclimatiques ***
 {physical_parameters['rainfall_correction']['min']:9.5f}=Min : Correction globale des Pluies                      (%) Max ={physical_parameters['rainfall_correction']['max']:10.5f}
 {physical_parameters['pet_correction']['min']:9.5f}=Min : Correction globale de l'ETP                        (%) Max ={physical_parameters['pet_correction']['max']:10.5f}
 {physical_parameters['thornthewaite_reservoir_capacity']['min']:9.5f}=Min : Capacité du réservoir sol 'réserve utile'         (mm) Max ={physical_parameters['thornthewaite_reservoir_capacity']['max']:10.5f}
 {physical_parameters['progressive_reservoir_capacity']['min']:9.5f}=Min : Capacité du réservoir sol progressif              (mm) Max ={physical_parameters['progressive_reservoir_capacity']['max']:10.5f}
 {physical_parameters['intermediate_runoff_seepage']['min']:9.5f}=Min : Hauteur de répartition Ruissellement-Percolation  (mm) Max ={physical_parameters['intermediate_runoff_seepage']['max']:10.5f}
 {physical_parameters['intermediate_half-life_seepage']['min']:9.5f}=Min : Temps de 1/2 percolation vers la nappe          (mois) Max ={physical_parameters['intermediate_half-life_seepage']['max']:10.5f}
 {physical_parameters['groundwater_1_drainage']['min']:9.5f}=Min : Temps de 1/2 tarissement du débit souterr. n°1  (mois) Max ={physical_parameters['groundwater_1_drainage']['max']:10.5f}
 {physical_parameters['groundwater_1_2_exchange']['min']:9.5f}=Min : Temps de 1/2 transfert vers la nappe profonde   (mois) Max ={physical_parameters['groundwater_1_2_exchange']['max']:10.5f}
 {physical_parameters['groundwater_1_double_outflow_threshold']['min']:9.5f}=Min : Seuil d'écoulement souterrain n°1 (rés. double)   (mm) Max ={physical_parameters['groundwater_1_double_outflow_threshold']['max']:10.5f}
 {physical_parameters['groundwater_2_drainage']['min']:9.5f}=Min : Temps de 1/2 tarissement du débit souterr. n°2  (mois) Max ={physical_parameters['groundwater_2_drainage']['max']:10.5f}
 {physical_parameters['time_of_concentration']['min']:9.5f}=Min : Temps de réaction ('retard') du débit   (pas de temps) Max ={physical_parameters['time_of_concentration']['max']:10.5f}
 {physical_parameters['groundwater_external_exchange']['min']:9.5f}=Min : Facteur d'échange souterrain externe               (%) Max ={physical_parameters['groundwater_external_exchange']['max']:10.5f}
 {physical_parameters['thornthewaite_reservoir_initial_deficit']['min']:9.5f}=Min : Déficit initial du réservoir sol 'réserve utile'  (mm) Max ={physical_parameters['thornthewaite_reservoir_initial_deficit']['max']:10.5f}
 {physical_parameters['progressive_reservoir_initial_deficit']['min']:9.5f}=Min : Déficit initial du réservoir sol progressif       (mm) Max ={physical_parameters['progressive_reservoir_initial_deficit']['max']:10.5f}
 {physical_parameters['intermediate_runoff_threshold']['min']:9.5f}=Min : Seuil de ruissellement par débordement            (mm) Max ={physical_parameters['intermediate_runoff_threshold']['max']:10.5f}
 {physical_parameters['intermediate_half-life_runoff_by_overspill']['min']:9.5f}=Min : Temps de 1/2 ruissell. par débordement  (Pas de temps) Max ={physical_parameters['intermediate_half-life_runoff_by_overspill']['max']:10.5f}
 {physical_parameters['intermediate_half-life_max_runoff_decrease']['min']:9.5f}=Min : Temps de 1/2 décroiss. maximal du ruissellement (mois) Max ={physical_parameters['intermediate_half-life_max_runoff_decrease']['max']:10.5f}
 {physical_parameters['basin_area_correction']['min']:9.5f}=Min : Facteur de correction de la superficie du bassin   (-) Max ={physical_parameters['basin_area_correction']['max']:10.5f}
 {physical_parameters['groundwater_storage_coefficient']['min']:9.5f}=Min : Coefficient d'emmagasinement de la nappe           (%) Max ={physical_parameters['groundwater_storage_coefficient']['max']:10.5f}
 *** Paramètres de Fonte de Neige           ***
 {physical_parameters['air-temp_correction']['val']:9.5f}=Correction globale de la température              (°C) Opti= {physical_parameters['air-temp_correction']['opt']:1}
 {physical_parameters['snowfall_retention_factor']['val']:9.5f}=Taux de rétention de la neige                      (%) Opti= {physical_parameters['snowfall_retention_factor']['opt']:1}
 {physical_parameters['snow_evaporation_factor']['val']:9.5f}=Facteur d'évaporation de la neige                  (%) Opti= {physical_parameters['snow_evaporation_factor']['opt']:1}
 {physical_parameters['snow_melt_correction_with_rainfall']['val']:9.5f}=Correction de fonte de la neige par la pluie       (%) Opti= {physical_parameters['snow_melt_correction_with_rainfall']['opt']:1}
 {physical_parameters['natural_snow_melting_threshold']['val']:9.5f}=Température seuil de fonte naturelle de la neige  (°C) Opti= {physical_parameters['natural_snow_melting_threshold']['opt']:1}
 {physical_parameters['snow_melt_degree_day_factor']['val']:9.5f}=Constante de fonte par la température     (mm/°C/jour) Opti= {physical_parameters['snow_melt_degree_day_factor']['opt']:1}
 {physical_parameters['snow_melting_in_contact_with_soil']['val']:9.5f}=Fonte de la neige au contact du sol     (1/10 mm/jour) Opti= {physical_parameters['snow_melting_in_contact_with_soil']['opt']:1}
 *** Bornes des paramètres Neige            ***
 {physical_parameters['air-temp_correction']['min']:9.5f}=Min : Correction globale de la température              (°C) Max ={physical_parameters['air-temp_correction']['max']:10.5f}
 {physical_parameters['snowfall_retention_factor']['min']:9.5f}=Min : Taux de rétention de la neige                      (%) Max ={physical_parameters['snowfall_retention_factor']['max']:10.5f}
 {physical_parameters['snow_evaporation_factor']['min']:9.5f}=Min : Facteur d'évaporation de la neige                  (%) Max ={physical_parameters['snow_evaporation_factor']['max']:10.5f}
 {physical_parameters['snow_melt_correction_with_rainfall']['min']:9.5f}=Min : Correction de fonte de la neige par la pluie       (%) Max ={physical_parameters['snow_melt_correction_with_rainfall']['max']:10.5f}
 {physical_parameters['natural_snow_melting_threshold']['min']:9.5f}=Min : Température seuil de fonte naturelle de la neige  (°C) Max ={physical_parameters['natural_snow_melting_threshold']['max']:10.5f}
 {physical_parameters['snow_melt_degree_day_factor']['min']:9.5f}=Min : Constante de fonte par la température     (mm/°C/jour) Max ={physical_parameters['snow_melt_degree_day_factor']['max']:10.5f}
 {physical_parameters['snow_melting_in_contact_with_soil']['min']:9.5f}=Min : Fonte de la neige au contact du sol     (1/10 mm/jour) Max ={physical_parameters['snow_melting_in_contact_with_soil']['max']:10.5f}
 *** Paramètres de Pompage           ***
 {physical_parameters['pumping_river_influence_factor']['val']:9.5f}=Coefficient d'influence du pompage => Débit Rivière (-) Opti= {physical_parameters['pumping_river_influence_factor']['opt']:1}
 {physical_parameters['pumping_river_half-life_rise']['val']:9.5f}=Temps de 1/2 montée du pompage infl. => Rivière  (mois) Opti= {physical_parameters['pumping_river_half-life_rise']['opt']:1}
 {physical_parameters['pumping_river_half-life_fall']['val']:9.5f}=Temps de 1/2 stabilisation du pompage => Rivière (mois) Opti= {physical_parameters['pumping_river_half-life_fall']['opt']:1}
 {physical_parameters['pumping_groundwater_influence_factor']['val']:9.5f}=Coefficient d'influence du pompage => Niveau Nappe  (-) Opti= {physical_parameters['pumping_groundwater_influence_factor']['opt']:1}
 {physical_parameters['pumping_groundwater_half-life_rise']['val']:9.5f}=Temps de 1/2 montée du pompage infl. => Nappe    (mois) Opti= {physical_parameters['pumping_groundwater_half-life_rise']['opt']:1}
 {physical_parameters['pumping_groundwater_half-life_fall']['val']:9.5f}=Temps de 1/2 stabilisation du pompage => Nappe   (mois) Opti= {physical_parameters['pumping_groundwater_half-life_fall']['opt']:1}
 *** Bornes des paramètres Pompage   ***
 {physical_parameters['pumping_river_half-life_rise']['min']:9.5f}=Min : Temps de 1/2 montée du pompage infl. => Rivière  (mois) Max ={physical_parameters['pumping_river_half-life_rise']['max']:10.5f}
 {physical_parameters['pumping_river_half-life_fall']['min']:9.5f}=Min : Temps de 1/2 stabilisation du pompage => Rivière (mois) Max ={physical_parameters['pumping_river_half-life_fall']['max']:10.5f}
 {physical_parameters['pumping_groundwater_half-life_rise']['min']:9.5f}=Min : Temps de 1/2 montée du pompage infl. => Nappe    (mois) Max ={physical_parameters['pumping_groundwater_half-life_rise']['max']:10.5f}
 {physical_parameters['pumping_groundwater_half-life_fall']['min']:9.5f}=Min : Temps de 1/2 stabilisation du pompage => Nappe   (mois) Max ={physical_parameters['pumping_groundwater_half-life_fall']['max']:10.5f}
 *** >>>>>>>>>>>>>> Fin des données du bassin ] >>>>>
 """

import os
import glob
import subprocess
import re
import pandas as pd


project_description = "test run"

config_dir = "config"
data_dir = "data"
output_dir = "output"

rga_file = config_dir + os.sep + "test.rga"
gar_file = config_dir + os.sep + "test.gar"

# ----------------------------------------------------------------------
# clean up files from previous run
# ----------------------------------------------------------------------
for f in glob.glob(f'{os.getcwd()}{os.sep}{config_dir}{os.sep}*'):
    os.remove(f)

for f in glob.glob(f'{os.getcwd()}{os.sep}{output_dir}{os.sep}*'):
    os.remove(f)

for f in glob.glob(f'{os.getcwd()}{os.sep}*.*'):
    if f != __file__:
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

rga_text = f"""{project_description}
 #<V8.2># --- Fin du texte libre --- ; Ne pas modifier/retirer cette ligne
{gar_file:<69} = Paramètres et Options
{rain_file:<69} = Pluies
{pet_file:<69} = Évapo-Transpirations Potentielles (ETP)
{q_file:<69} = Débits de Rivière
{z_file:<69} = Niveaux de Nappe
{air_temp_file:<69} = Températures de l'air
{snow_file:<69} = Précipitations Neigeuses
                                                                      = Pluies pour Prévision
                                                                      = ETP pour Prévision
                                                                      = Températures pour Prévision
                                                                      = Précipitations neigeuses pour Prévision
                                                                      = Injections/Pompages
                                                                      = Mailles météo et Pondérations

"""

with open(rga_file, "w+") as f:
    f.writelines(rga_text)

# ----------------------------------------------------------------------
# generate *.gar file
# ----------------------------------------------------------------------
user_profile = '0'
execution_mode = 'D'

river_obs_weight = '5'
piezo_obs_weight = '2'

river_calc = '1'
piezo_calc = '1'

recharge_effective_rain_save = '0'
river_piezo_save = '1'
water_balance_save = '0'

computation_scheme = '0'

gar_text = f"""{project_description}
 #<V8.8># --- Fin du texte libre --- ; Ne pas modifier/retirer cette ligne
 *** Pré-Options Générales           ***
 {user_profile:>9}=Profil d'utilisation : 0=simple ; A=Avancé (Neige, Pompage, Prévi etc.)
 {execution_mode:>9}=Mode d'exécution (C = Contrôle sur écran ; Déf=Rapide ; D=Direct ; M=Muet)
          =Opération : Déf=Calcul ; A=Actualisation seule du fichier des paramètres
 *** Options Générales               ***
         1=Nombre de Sites (Bassins) à modéliser successivement
         0=Type de donnée pour Prévision (0=Débits de Rivière , 1=Niveaux de Nappe)
 {river_obs_weight:>9}=Observations de Débits de Rivière : Importance (entier : 0 à 10 ;  0=Non)
 {piezo_obs_weight:>9}=Observations de Niveaux de Nappe  : Importance (entier : 0 à 10 ;  0=Non)
 {river_calc:>9}=Calcul des Débits de Rivière : (0=Non  ;  1=Oui)
 {piezo_calc:>9}=Calcul des Niveaux de Nappe  : (0=Non  ;  1=Oui)
 {recharge_effective_rain_save:>9}=Sauvegarde de la Recharge et de la Pluie Efficace (0=Non  ;  1=Oui)
 {river_piezo_save:>9}=Sauvegarde des Débit/Niveaux simulés : (0=Non  ;  1=Oui)
 {water_balance_save:>9}=Sauvegarde des termes du Bilan : (0=Non ; 1=Annuel ; 2=Mensuel ; 3=Tous les pas de temps)
         0=Allègement du Listing (0=Complet ; 1=Allégé ; 2=Supprimé)
 {computation_scheme:>9}=Schéma de calcul (0=Gardénia ; 5=Ruissell,Drainage ; etc.)
         2=Dessin de la série simulée (0=non ; 1=Oui ; 2=Oui avec décomposition)
         0=Pondération pour calibration (0=Non ; 2= ++Étiages ; 99= Racine_Débit; 97= Logar_Débits)
         0=Minimisation du biais de simulation des Débits Rivière (0 = Non ; 100 = 100 %)
         0=Pompage influençant les Débits de Rivière (0=Non ; 1=Oui ; 2=Oui en rivière)
         0=Pompage influençant les Niveaux de Nappe (0=Non ; 1=Oui)
         0=Calcul avec Prévision (0=Non ; 1=Oui ; -1=Préparation uniquement) [3, 4 = Particulier]
         0=Méthode de Prévision (0=Ajustement Réservoirs ; 1=Décalage simple ; 2=Décalage avec 1/2 vie)
         0=Schéma d'échanges souterr. avec extérieur (0=% Débit Souterr. (++) ; 1=Facteur Niv_Souterr.)
         0=Bilan journalier même si pluie Décadaire ou Mensuelle (0=Non ; 1=Oui)
         0=Prise en compte de la Neige (0=Non  ;  1=Oui)
         0=Précipitations neigeuses dans un fichier propre (0 = avec pluies ; 1 = fichier séparé)
         0=Données par années hydrologiques [début 1 août] (0=années Civiles ; 1=années Hydrologiques)
         0=Perte de Débit : 0=Non ; 1=Perd le Debit Souterrain le plus Lent ; -1=Perd le Ruissellement
         0=Analyse de Sensibilité (0=Non  ;  1=Oui uniquement analyse de Sensibilité)
         0=Sauvegarde de la 'Réponse impulsionnelle' et de la 'Réponse Cumulée' (1=Oui)
         0=Données de tous les sites dans différentes colonnes d'un même fichier (Déf=0)
         0=Numéro de la 'colonne' des Pluies       : Déf=0 <=> 1ère colonne de données
         0=Numéro de la 'colonne' des ETP          : Déf=0=Identique à la pluie
         0=Numéro de la 'colonne' des Débits       : Déf=0=Identique à la pluie
         0=Numéro de la 'colonne' des Niveaux      : Déf=0=Identique à la pluie
         0=Numéro de la 'colonne' des Températures : Déf=0=Identique à la pluie
         0=Numéro de la 'colonne' de la Neige      : Déf=0=Identique à la pluie
         0=Numéro de la 'colonne' des Pompages     : Déf=0=Identique à la pluie
         0=Numéro de la 'colonne' des Pluies pour Prévision  : Déf=0=Identique à la pluie
         0=Numéro de la 'colonne' des Tempér. pour Prévision : Déf=0=Identique à la pluie
         0=Numéro de la 'colonne' des ETP pour Prévision     : Déf=0=Identique à la pluie
         0=Numéro de la 'colonne' de la Neige pour Prévision : Déf=0=Identique à la pluie
         0=Météo (Pluie, ETP, ...) pondérée à chaque pas [1=Fich. annuels SAFRAN , 2=Fichier unique]
         0=Sauvegarde de la météo pondérée => Fichier (futurs runs + rapides et portables) [1=Oui]
         0=Couplage avec le coupleur OpenPalm (0=Non ; 1=Couplage Météo)
 *** Pas de temps du Fichier Pluie, Neige, Pompage    ***
         0= Pas de temps :  0=Journalier 1=Pentadaire 2=Décadaire 3=Mensuel 4=Autre 5=5_Jours 7=7_Jours
         3= Format : 0=Gardénia_Sequentiel  1=Gardénia_Annuaire  2=Libre  3=Excel
 *** Pas de temps du Fichier Température              ***
         0= Pas de temps :  0=Journalier 1=Pentadaire 2=Décadaire 3=Mensuel 4=Autre 5=5_Jours 7=7_Jours
         1= Format : 0=Gardénia_Sequentiel  1=Gardénia_Annuaire  2=Libre  3=Excel
 *** Pas de temps du Fichier ETP                      ***
         0= Pas de temps :  0=Journalier 1=Pentadaire 2=Décadaire 3=Mensuel 4=Autre 5=5_Jours 7=7_Jours
         3= Format : 0=Gardénia_Sequentiel  1=Gardénia_Annuaire  2=Libre  3=Excel
 *** Pas de temps du Fichier Débits, Niveaux Observés ***
         0= Pas de temps :  0=Journalier 1=Pentadaire 2=Décadaire 3=Mensuel 4=Autre 5=5_Jours 7=7_Jours
         3= Format : 0=Gardénia_Sequentiel  1=Gardénia_Annuaire  2=Libre  3=Excel
 *** Durée du pas de temps s'il est non-standard ***
  Standard=Unité de durée des Pas si non-standard (sec,min,heu,jou,moi,ann)
     1.000=Durée du pas de temps (dans l'unité)
 *** >>>>>>>>>>>>>> Fin des données communes ] >>>>>
 *** <<<<<<<<<<<< Début des données du bassin [ <<<<<
 Selle à Plachy + Piézo Morvillers : 00608X0028) (Lame moyenne 9 Postes)
   0.00000=Valeur Maximale du Débit de Rivière Observé prise en compte (0 = toutes)
   0.00000=Valeur Minimale du Débit de Rivière Observé prise en compte (0 = toutes)
   0.00000=Valeur Maximale du Niveau de Nappe Observé prise en compte (0 = toutes)
   0.00000=Valeur Minimale du Niveau de Nappe Observé prise en compte (0 = toutes)
   0.00000=Coefficient de réajustement pour la prévision [0 à 1]
   0.00000=Écart-type de l'alimentation du Réservoir intermédiaire  (pour la prévision)
   0.00000=Écart-type de l'alimentation du Réservoir Souterrain n°1 (pour la prévision)
   0.00000=Écart-type de l'alimentation du Réservoir Souterrain n°2 (pour la prévision)
   0.00000=Débit Rivière réservé (valeur simulée minimale possible) (Déf=0)
   0.00000=Écart-type des observations de niveau de nappe (pour la prévision)
   0.00000=Temps de 1/2 vie de l'écart de prévision de Débit  de rivière (pas de temps)
   0.00000=Temps de 1/2 vie de l'écart de prévision de Niveau de Nappe   (pas de temps)
 *** Options du Bassin               ***
         0=Nombre d'Années des séries de données (Pluie, ETP, Observations) [0 => Toutes]
         4=Nombre d'Années démarrage (-n pour générer n année moy fictives de démarrage)
         0=Nombre de cycles de démarrage (déf. = 1)
      1985=Date de la première année des données (par ex. 2017)
         0=Décalage dans la série des Pluies [+5 => Retarde de 5 pas ; -4 Avance de 4 pas]
         0=Décalage de la série des Débits/Niveaux observés [ex: -2 => Avance de 2 pas]
         0=État initial : 0=Pluie Effic. moyenne ; -1=Réservoirs vides ; -2=RuMax vide aussi
       250=Nombre maxi. d'itérations pour la calibration (0 = aucune itération, pas de calibrat.)
         0=Durée des pluies en moyenne par pas (%) (utilisations avancées)[défaut = 100 %]
         0=Nombre de réservoirs souterrains (1 ou 2 ou -1=Double + seuil)      [déf = 1]
         0=Numéro du réservoir souterr. <=> Niveau nappe (si 2 réserv. souterr.) [déf = 1]
         0=Nombre d'années finales à ignorer pour la calibration (déf = 0) [< 0 => n° last ann]
         0=Numéro du Jour initial [Déf=1] (si durée non-standard) ; ex. 31 pour 31 Déc.
         0=Numéro du Mois initial [Déf=1] (si durée non-standard) ; ex. 12 pour 31 Déc.
         0=Heure initiale [Déf=0] (si durée non-standard) ; par ex. 15 pour 15h30
         0=Minute initiale [Déf=0] (si durée non-standard) ; Par ex. 30 pour 15h30
         0=Perte du débit de Ruissellement par Débordement au-dessus du Seuil [0=Non ; 1=Perte ; 2 => Rés Sout]
         0=Décroissance de l'évapotranspiration si saturation du réservoir sol < 50% (0=Non ; 1=Oui)
         0=Schéma à taux de ruissellement constant (pour comparaison ; déconseillé) (0=Non ; 1=Oui)
         0=Méthode de calcul du coeff. d'Emmagasinement [0 = Corrélation ; 1 = Optimis entre bornes]
 *** Paramètres de Prévision         ***
         0=Nombre d'Années de données du fichier de pluies etc. pour la Prévision
         0=Jour d'émission de la prévision (1-31) si pas de temps journalier (sinon : 0)
         0=Numéro du Mois [si journalier ou mensuel] (ou n° du pas) d'émission de la prévision)
         0=Portée de la Prévision (Nombre de pas de temps de la prévision)
         0=Date de la Première Année des fichiers météo de prévision [si journalier] (déf = 0)
 *** Position des Données du bassin  ***
         0=N° de la 'colonne' des données : (-1 => N° d'ordre du bassin) Déf=0 <=> Col. n°1
 *** Paramètres Hydroclimatiques            ***
   0.00000=Pluie Eff. annuelle pour initialis. (0=équil.) (mm/an)
   0.00000=Débit extérieur éventuel                        (m3/s) Opti= 0
 524.00000=Superficie du bassin versant                     (km2) Opti= 0
 125.00000=Niveau de base local de la nappe               (m NGF) Opti= 1
   0.00000=Correction globale des Pluies                      (%) Opti= 0
   0.00000=Correction globale de l'ETP                        (%) Opti= 0
   0.00000=Capacité du réservoir sol 'réserve utile'         (mm) Opti= 0
 180.00000=Capacité du réservoir sol progressif              (mm) Opti= 1
 600.00000=Hauteur de répartition Ruissellement-Percolation  (mm) Opti= 1
   5.00000=Temps de 1/2 percolation vers la nappe          (mois) Opti= 1
  20.00000=Temps de 1/2 tarissement du débit souterr. n°1  (mois) Opti= 1
   0.15000=Temps de 1/2 transfert vers la nappe profonde   (mois) Opti= 0
   0.00000=Seuil d'écoulement souterrain n°1 (rés. double)   (mm) Opti= 0
   0.15000=Temps de 1/2 tarissement du débit souterr. n°2  (mois) Opti= 0
   0.00000=Temps de réaction ('retard') du débit   (pas de temps) Opti= 0
   0.00000=Facteur d'échange souterrain externe               (%) Opti= 0
   0.00000=Déficit initial du réservoir sol 'réserve utile'  (mm) Opti= 0
   0.00000=Déficit initial du réservoir sol progressif       (mm) Opti= 0
   0.00000=Seuil de ruissellement par débordement            (mm) Opti= 0
   0.00000=Temps de 1/2 ruissell. par débordement  (Pas de temps) Opti= 0
   0.00000=Temps de 1/2 décroiss. maximal du ruissellement (mois) Opti= 0
   1.00000=Facteur de correction de la superficie du bassin   (-) Opti= 0
   1.00000=Coefficient d'emmagasinement de la nappe           (%) Opti= 1
 *** Bornes des paramètres Hydroclimatiques ***
   0.00000=Min : Correction globale des Pluies                      (%) Max =   0.00000
   0.00000=Min : Correction globale de l'ETP                        (%) Max =   0.00000
   0.00000=Min : Capacité du réservoir sol 'réserve utile'         (mm) Max = 350.00000
   0.00000=Min : Capacité du réservoir sol progressif              (mm) Max = 650.00000
   5.00000=Min : Hauteur de répartition Ruissellement-Percolation  (mm) Max =9998.00000
   0.15000=Min : Temps de 1/2 percolation vers la nappe          (mois) Max =  25.00000
   6.00000=Min : Temps de 1/2 tarissement du débit souterr. n°1  (mois) Max =  70.00000
   0.15000=Min : Temps de 1/2 transfert vers la nappe profonde   (mois) Max =  50.00000
   0.15000=Min : Seuil d'écoulement souterrain n°1 (rés. double)   (mm) Max =  50.00000
   0.15000=Min : Temps de 1/2 tarissement du débit souterr. n°2  (mois) Max =  50.00000
   0.00000=Min : Temps de réaction ('retard') du débit   (pas de temps) Max =  10.00000
 -50.00000=Min : Facteur d'échange souterrain externe               (%) Max =  50.00000
   0.00000=Min : Déficit initial du réservoir sol 'réserve utile'  (mm) Max =   0.00000
   0.00000=Min : Déficit initial du réservoir sol progressif       (mm) Max =   0.00000
   0.00000=Min : Seuil de ruissellement par débordement            (mm) Max = 999.00000
   0.06000=Min : Temps de 1/2 ruissell. par débordement  (Pas de temps) Max =  30.00000
   0.00000=Min : Temps de 1/2 décroiss. maximal du ruissellement (mois) Max =   0.00000
   0.02000=Min : Facteur de correction de la superficie du bassin   (-) Max =  50.00000
   0.02000=Min : Coefficient d'emmagasinement de la nappe           (%) Max =  50.00000
 *** Paramètres de Fonte de Neige           ***
   0.00000=Correction globale de la température              (°C) Opti= 0
   0.00000=Taux de rétention de la neige                      (%) Opti= 0
   0.00000=Facteur d'évaporation de la neige                  (%) Opti= 0
   0.00000=Correction de fonte de la neige par la pluie       (%) Opti= 0
   0.00000=Température seuil de fonte naturelle de la neige  (°C) Opti= 0
   0.00000=Constante de fonte par la température     (mm/°C/jour) Opti= 0
   0.00000=Fonte de la neige au contact du sol     (1/10 mm/jour) Opti= 0
 *** Bornes des paramètres Neige            ***
   0.00000=Min : Correction globale de la température              (°C) Max =   0.00000
   0.00000=Min : Taux de rétention de la neige                      (%) Max =   0.00000
   0.00000=Min : Facteur d'évaporation de la neige                  (%) Max =   0.00000
   0.00000=Min : Correction de fonte de la neige par la pluie       (%) Max =   0.00000
   0.00000=Min : Température seuil de fonte naturelle de la neige  (°C) Max =   0.00000
   0.00000=Min : Constante de fonte par la température     (mm/°C/jour) Max =   0.00000
   0.00000=Min : Fonte de la neige au contact du sol     (1/10 mm/jour) Max =   0.00000
 *** Paramètres de Pompage           ***
   1.00000=Coefficient d'influence du pompage => Débit Rivière (-) Opti= 0
   0.20000=Temps de 1/2 montée du pompage infl. => Rivière  (mois) Opti= 0
   0.20000=Temps de 1/2 stabilisation du pompage => Rivière (mois) Opti= 0
   1.00000=Coefficient d'influence du pompage => Niveau Nappe  (-) Opti= 0
   0.30000=Temps de 1/2 montée du pompage infl. => Nappe    (mois) Opti= 0
   0.30000=Temps de 1/2 stabilisation du pompage => Nappe   (mois) Opti= 0
 *** Bornes des paramètres Pompage   ***
   0.05000=Min : Temps de 1/2 montée du pompage infl. => Rivière  (mois) Max =   3.00000
   0.05000=Min : Temps de 1/2 stabilisation du pompage => Rivière (mois) Max =   3.00000
   0.07000=Min : Temps de 1/2 montée du pompage infl. => Nappe    (mois) Max =   4.00000
   0.07000=Min : Temps de 1/2 stabilisation du pompage => Nappe   (mois) Max =   4.00000
 *** >>>>>>>>>>>>>> Fin des données du bassin ] >>>>>
"""

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
    shell=True, stdout=subprocess.PIPE
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

if beg_river and end_river:
    df_river = pd.read_table(
        output_file,
        skiprows=beg_river, skipfooter=n_lines-end_river,
        names=['dt', 'river_sim', 'river_obs'],
        **options
    )
    df_river.to_csv(f"{output_dir}/river_sim_obs.csv", index=False)

if beg_piezo and end_piezo:
    df_piezo = pd.read_table(
        output_file,
        skiprows=beg_piezo, skipfooter=n_lines-end_piezo,
        names=['dt', 'piezo_sim', 'piezo_obs'],
        **options
    )
    df_piezo.to_csv(f"{output_dir}/piezo_sim_obs.csv", index=False)

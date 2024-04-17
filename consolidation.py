import pickle
from datetime import datetime
import pandas as pd
import numpy as np



# Needed functions

def map_activity(row):
    if row['ACTIVITY_CODE_VERSION'] == 'NAP':
        return dic_version_1973.get(row['MAIN_ACTIVITY_LEVEL_5'])
    elif row['ACTIVITY_CODE_VERSION'] == 'NAF1993':
        return dic_version_1993.get(row['MAIN_ACTIVITY_LEVEL_5'])
    elif row['ACTIVITY_CODE_VERSION'] == 'NAFRev1':
        return dic_version_2003.get(row['MAIN_ACTIVITY_LEVEL_5'])
    elif row['ACTIVITY_CODE_VERSION'] == 'NAFRev2':
        return dic_version_2008.get(row['MAIN_ACTIVITY_LEVEL_5'])
    else:
        return np.nan


def map_levels(row, level, levels_list):
    try:
        if row['ACTIVITY_CODE_VERSION'] == 'NAP':
            return levels_list[0].loc[row['MAIN_ACTIVITY_LEVEL_5'], level]
        elif row['ACTIVITY_CODE_VERSION'] == 'NAF1993':
            return levels_list[1].loc[row['MAIN_ACTIVITY_LEVEL_5'], level]
        elif row['ACTIVITY_CODE_VERSION'] == 'NAFRev1':
            return levels_list[2].loc[row['MAIN_ACTIVITY_LEVEL_5'], level]
        elif row['ACTIVITY_CODE_VERSION'] == 'NAFRev2':
            return levels_list[3].loc[row['MAIN_ACTIVITY_LEVEL_5'], level]
        else:
            return np.nan
    except:
        return np.nan


def remplace_nan_date(data):
    if data is pd.NaT:
        return datetime.strptime('2023-12-31', format_date)


def extract_first_9_chars(s):
    return str(s)[:9]


def find_departement(data):
    try:
        if data[:2] != '97':
            return data[:2]
        else:
            return data[:3]
    except:
        return pd.NA


def apply_dict_epci_cae(row):
    digits = row['ID_BOAMP_AWARD'][0:2]
    if int(digits) < 15:
        digits = '15'
    year = '20' + digits
    return dict_epci_by_year[year].get(row['CAE_EPCI'], pd.NA)

def apply_dict_communes_cae(row):
    digits = row['ID_BOAMP_AWARD'][0:2]
    if int(digits) < 15:
        digits = '15'
    year = '20' + digits
    return dict_communes_by_year[year].get(row['CAE_CITY_CODE'], pd.NA)

def apply_dict_epci_win(row):
    digits = row['ID_BOAMP_AWARD'][0:2]
    if int(digits) < 15:
        digits = '15'
    year = '20' + digits
    return dict_epci_by_year[year].get(row['WIN_EPCI'], pd.NA)

def apply_dict_communes_win(row):
    digits = row['ID_BOAMP_AWARD'][0:2]
    if int(digits) < 15:
        digits = '15'
    year = '20' + digits
    return dict_communes_by_year[year].get(row['WIN_CITY_CODE'], pd.NA)


def assign_name(row):
    if pd.notna(row['CAE_SIREN']) and row['CAE_SIREN'] in df_institutions.index:
        row['CAE_SIREN_NAME'] = df_institutions.loc[row['CAE_SIREN'], 'NAME']
    if pd.notna(row['WIN_SIREN']) and row['WIN_SIREN'] in df_institutions.index:
        row['WIN_SIREN_NAME'] = df_institutions.loc[row['WIN_SIREN'], 'NAME']
    return row


def assign_city(row):
    if pd.notna(row['CAE_SIRET']) and row['CAE_SIRET'] in agencies.index:
        row['CAE_TOWN'] = agencies.loc[row['CAE_SIRET'], 'CITY']
    if pd.notna(row['WIN_SIRET']) and row['WIN_SIRET'] in agencies.index:
        row['WIN_TOWN'] = agencies.loc[row['WIN_SIRET'], 'CITY']
    return row


def assign_zipcode(row):
    if pd.notna(row['CAE_SIRET']) and row['CAE_SIRET'] in agencies.index:
        row['CAE_ZIP_CODE'] = agencies.loc[row['CAE_SIRET'], 'ZIP_CODE']
    if pd.notna(row['WIN_SIRET']) and row['WIN_SIRET'] in agencies.index:
        row['WIN_ZIP_CODE'] = agencies.loc[row['WIN_SIRET'], 'ZIP_CODE']
    return row


# Importing the table with the estimated sirets

with open('table_with_sirets.pkl', 'rb') as f:
    df = pickle.load(f)


# Getting a list of unique identifiers in the table

siret_list = list(set(pd.concat([df['CAE_SIRET'], df['WIN_SIRET']]).dropna().tolist()))
siren_list = list(set(pd.concat([df['CAE_SIRET'].str.slice(0, 9), df['WIN_SIRET'].str.slice(0, 9)]).dropna().tolist()))


# Reading files of official classifications

legal_status = pd.read_csv('legal_status.csv', sep=';', encoding='latin1', dtype='str')
dictionnaire_legal = legal_status.set_index('categorie_juridique_insee')['libelle'].to_dict()

staff_status = pd.read_csv('staff_status.csv', sep=';')
dictionnaire_staff = staff_status.set_index('code')['size'].to_dict()

codes_1973 = pd.read_csv('Level_names_1973.csv', sep=';')
codes_1993 = pd.read_csv('Level_names_1993.csv', sep=';')
codes_2003 = pd.read_csv('Level_names_2003.csv', sep=';')
codes_2008 = pd.read_csv('Level_names_2008.csv', sep=';')

dic_version_1973 = codes_1973.set_index('code')['name'].to_dict()
dic_version_1993 = codes_1993.set_index('code')['name'].to_dict()
dic_version_2003 = codes_2003.set_index('code')['name'].to_dict()
dic_version_2008 = codes_2008.set_index('code')['name'].to_dict()

levels_1973 = pd.read_csv('Levels_1973.csv', sep=';')
levels_1993 = pd.read_csv('Levels_1993.csv', sep=';')
levels_2003 = pd.read_csv('Levels_2003.csv', sep=';')
levels_2008 = pd.read_csv('Levels_2008.csv', sep=';')

levels_list = [levels_1973, levels_1993, levels_2003, levels_2008]
for i in range(len(levels_list)):
    levels_list[i] = levels_list[i].astype(str)
    levels_list[i] = levels_list[i].set_index('NIV5')


# Read data on institutions

format_date = '%Y-%m-%d'
date_debut = datetime.strptime('2015-01-01', format_date)

institution_history = pd.read_csv('StockUniteLegaleHistorique_utf8.csv',
                 usecols=['siren',
                          'dateDebut',
                          'dateFin',
                          'caractereEmployeurUniteLegale'],
                 dtype=str)
institution_history = institution_history[institution_history['siren'].isin(siren_list)]
institution_history.loc[:, 'dateFin'] = pd.to_datetime(arg=institution_history['dateFin'])
institution_history.loc[:, 'dateFin'] = institution_history['dateFin'].apply(remplace_nan_date)
institution_history = institution_history[institution_history['dateFin'] > date_debut]
institution_history = institution_history.drop(columns='dateFin')

institutions = pd.read_csv('StockUniteLegale_utf8.csv',
                 usecols=[
                        'denominationUniteLegale',
                        'siren',
                        'dateCreationUniteLegale',
                        'trancheEffectifsUniteLegale',
                        'categorieEntreprise',
                        'societeMissionUniteLegale',
                        'etatAdministratifUniteLegale',
                        'categorieJuridiqueUniteLegale',
                        'activitePrincipaleUniteLegale',
                        'economieSocialeSolidaireUniteLegale',
                        'nomenclatureActivitePrincipaleUniteLegale'
                        ],
                 low_memory=False,
                 dtype=str)
institutions = institutions[institutions['siren'].isin(siren_list)]

df_institutions = institution_history.merge(right=institutions, 
                                            how='outer', 
                                            on='siren')

# Releasing memory

del institutions
del institution_history


# Processing the data on institutions

column_names_institutions = {'etatAdministratifUniteLegale': 'STILL_ACTIVE', 
                         'categorieJuridiqueUniteLegale': 'LEGAL_STATUS',
                         'activitePrincipaleUniteLegale': 'MAIN_ACTIVITY_LEVEL_5',
                         'economieSocialeSolidaireUniteLegale': 'SSE',
                         'societeMissionUniteLegale': 'MISSION',
                         'caractereEmployeurUniteLegale': 'EMPLOYER',
                         'dateCreationUniteLegale': 'CREATION_DATE',
                         'trancheEffectifsUniteLegale': 'STAFF',
                         'categorieEntreprise': 'SIZE',
                         'nomenclatureActivitePrincipaleUniteLegale': 'ACTIVITY_CODE_VERSION',
                         'denominationUniteLegale': 'NAME'
                         }
df_institutions = df_institutions.rename(columns=column_names_institutions)

df_institutions['EMPLOYER'] = df_institutions['EMPLOYER'].replace({"O": True, "N": False})
df_institutions['SSE'] = df_institutions['SSE'].replace({"O": True, "N": False})
df_institutions['MISSION'] = df_institutions['MISSION'].replace({"O": True, "N": False})
df_institutions['STILL_ACTIVE'] = df_institutions['STILL_ACTIVE'].replace({"A": True, "C": False})
df_institutions['LEGAL_STATUS_NAME'] = df_institutions['LEGAL_STATUS'].map(dictionnaire_legal)
df_institutions['STAFF'] = pd.to_numeric(df_institutions['STAFF'], errors='coerce').astype('Int64')
df_institutions['STAFF'] = df_institutions['STAFF'].map(dictionnaire_staff)
df_institutions['MAIN_ACTIVITY_NAME'] = df_institutions.apply(map_activity, axis=1)

df_institutions['MAIN_ACTIVITY_LEVEL_1'] = df_institutions.apply(map_levels, args=('NIV1', levels_list), axis=1)
df_institutions['MAIN_ACTIVITY_LEVEL_2'] = df_institutions.apply(map_levels, args=('NIV2', levels_list), axis=1)
df_institutions['MAIN_ACTIVITY_LEVEL_3'] = df_institutions.apply(map_levels, args=('NIV3', levels_list), axis=1)
df_institutions['MAIN_ACTIVITY_LEVEL_4'] = df_institutions.apply(map_levels, args=('NIV4', levels_list), axis=1)

translation_versions = {
    'NAP': '1973',
    'NAF1993': '1993',
    'NAFRev1': '2003',
    'NAFRev2': '2008'}
df_institutions['ACTIVITY_CODE_VERSION'] = df_institutions['ACTIVITY_CODE_VERSION'].replace(translation_versions)

df_institutions = df_institutions.set_index('siren')

df['CAE_SIREN'] = df['CAE_SIRET'].str[:9]
df['WIN_SIREN'] = df['WIN_SIRET'].str[:9]

df = df.apply(assign_name, axis=1)

df['CAE_LEGAL_STATUS'] = df['CAE_SIREN'].map(df_institutions['LEGAL_STATUS'])
df['CAE_LEGAL_STATUS_NAME'] = df['CAE_SIREN'].map(df_institutions['LEGAL_STATUS_NAME'])
df['CAE_EMPLOYER'] = df['CAE_SIREN'].map(df_institutions['EMPLOYER'])
df['CAE_STAFF'] = df['CAE_SIREN'].map(df_institutions['STAFF'])
df['CAE_MAIN_ACTIVITY'] = df['CAE_SIREN'].map(df_institutions['MAIN_ACTIVITY_NAME'])
df['CAE_SSE'] = df['CAE_SIREN'].map(df_institutions['SSE'])
df['CAE_CREATION'] = df['CAE_SIREN'].map(df_institutions['CREATION_DATE'])
df['CAE_MAIN_ACTIVITY_CODE'] = df['CAE_SIREN'].map(df_institutions['MAIN_ACTIVITY_LEVEL_5'])
df['CAE_ACTIVITY_VERSION'] = df['CAE_SIREN'].map(df_institutions['ACTIVITY_CODE_VERSION'])

df['WIN_LEGAL_STATUS'] = df['WIN_SIREN'].map(df_institutions['LEGAL_STATUS'])
df['WIN_LEGAL_STATUS_NAME'] = df['WIN_SIREN'].map(df_institutions['LEGAL_STATUS_NAME'])
df['WIN_EMPLOYER'] = df['WIN_SIREN'].map(df_institutions['EMPLOYER'])
df['WIN_STAFF'] = df['WIN_SIREN'].map(df_institutions['STAFF'])
df['WIN_SSE'] = df['WIN_SIREN'].map(df_institutions['SSE'])
df['WIN_MISSION'] = df['WIN_SIREN'].map(df_institutions['MISSION'])
df['WIN_STILL_ACTIVE'] = df['WIN_SIREN'].map(df_institutions['STILL_ACTIVE'])
df['WIN_ACTIVITY_VERSION'] = df['WIN_SIREN'].map(df_institutions['ACTIVITY_CODE_VERSION'])
df['WIN_ACTIVITY_LEVEL_1'] = df['WIN_SIREN'].map(df_institutions['MAIN_ACTIVITY_LEVEL_1'])
df['WIN_ACTIVITY_LEVEL_2'] = df['WIN_SIREN'].map(df_institutions['MAIN_ACTIVITY_LEVEL_2'])
df['WIN_ACTIVITY_LEVEL_3'] = df['WIN_SIREN'].map(df_institutions['MAIN_ACTIVITY_LEVEL_3'])
df['WIN_ACTIVITY_LEVEL_4'] = df['WIN_SIREN'].map(df_institutions['MAIN_ACTIVITY_LEVEL_4'])
df['WIN_ACTIVITY_LEVEL_5'] = df['WIN_SIREN'].map(df_institutions['MAIN_ACTIVITY_LEVEL_5'])
df['WIN_MAIN_ACTIVITY'] = df['WIN_SIREN'].map(df_institutions['MAIN_ACTIVITY_NAME'])
df['WIN_CREATION_DATE'] = df['WIN_SIREN'].map(df_institutions['CREATION_DATE'])

del df_institutions


# Read data on establishments

agencies = pd.read_csv('StockEtablissement_utf8.csv',
                 usecols=[
                          'siret',
                          'dateCreationEtablissement',
                          'trancheEffectifsEtablissement',
                          'caractereEmployeurEtablissement',
                          'nomenclatureActivitePrincipaleEtablissement',
                          'activitePrincipaleEtablissement',
                          'etablissementSiege',
                          'numeroVoieEtablissement',
                          'codePostalEtablissement',
                          'libelleCommuneEtablissement',
                          ],
                 low_memory=False,
                 dtype=str)
agencies = agencies[agencies['siret'].isin(siret_list)]

column_names_agencies = {'activitePrincipaleEtablissement': 'MAIN_ACTIVITY_LEVEL_5', 
                          'dateCreationEtablissement': 'CREATION_DATE',
                          'trancheEffectifsEtablissement': 'STAFF',
                          'caractereEmployeurEtablissement': 'EMPLOYER',
                          'nomenclatureActivitePrincipaleEtablissement': 'ACTIVITY_CODE_VERSION',
                          'etablissementSiege': 'HEADQUARTERS',
                          'codePostalEtablissement': 'ZIP_CODE',
                          'libelleCommuneEtablissement': 'CITY'
                          }
agencies = agencies.rename(columns=column_names_agencies)


agencies['STAFF'] = pd.to_numeric(agencies['STAFF'], errors='coerce').astype('Int64')
agencies['STAFF'] = agencies['STAFF'].map(dictionnaire_staff)
agencies['MAIN_ACTIVITY_NAME'] = agencies.apply(map_activity, axis=1)
agencies['EMPLOYER'] = agencies['EMPLOYER'].replace({"O": True, "N": False})
agencies['HEADQUARTERS'] = agencies['HEADQUARTERS'].replace({"true": True, "false": False})

agencies['MAIN_ACTIVITY_LEVEL_1'] = agencies.apply(map_levels, args=('NIV1', levels_list), axis=1)
agencies['MAIN_ACTIVITY_LEVEL_2'] = agencies.apply(map_levels, args=('NIV2', levels_list), axis=1)
agencies['MAIN_ACTIVITY_LEVEL_3'] = agencies.apply(map_levels, args=('NIV3', levels_list), axis=1)
agencies['MAIN_ACTIVITY_LEVEL_4'] = agencies.apply(map_levels, args=('NIV4', levels_list), axis=1)


localisations = pd.read_csv('géolocalisation.csv',
                            dtype=str, 
                            sep=';',
                            usecols=[
                                'siret',
                                'plg_code_commune',
                                'y_latitude',
                                'x_longitude'])

localisations = localisations[localisations['siret'].isin(siret_list)]
localisations = localisations.set_index('siret')

agencies['LONGITUDE'] = agencies['siret'].map(localisations['x_longitude'])
agencies['LATITUDE'] = agencies['siret'].map(localisations['y_latitude'])
agencies['CITY_CODE']= agencies['siret'].map(localisations['plg_code_commune'])

del localisations


agencies = agencies.set_index('siret')
df = df.apply(assign_zipcode, axis=1)
df = df.apply(assign_city, axis=1)


df['CAE_AGENCY_EMPLOYER'] = df['CAE_SIRET'].map(agencies['EMPLOYER'])
df['CAE_AGENCY_STAFF'] = df['CAE_SIRET'].map(agencies['STAFF'])
df['CAE_AGENCY_MAIN_ACTIVITY'] = df['CAE_SIRET'].map(agencies['MAIN_ACTIVITY_NAME'])
df['CAE_AGENCY_CREATION'] = df['CAE_SIRET'].map(agencies['CREATION_DATE'])
df['CAE_AGENCY_MAIN_ACTIVITY_CODE'] = df['CAE_SIRET'].map(agencies['MAIN_ACTIVITY_LEVEL_5'])
df['CAE_AGENCY_ACTIVITY_VERSION'] = df['CAE_SIRET'].map(agencies['ACTIVITY_CODE_VERSION'])
df['CAE_HEADQUARTERS'] = df['CAE_SIRET'].map(agencies['HEADQUARTERS'])
df['CAE_CITY_CODE'] = df['CAE_SIRET'].map(agencies['CITY_CODE'])
df['CAE_GPS'] = df['CAE_SIRET'].apply(lambda x: (agencies['LATITUDE'].get(x), agencies['LONGITUDE'].get(x)))
df['CAE_DEPARTEMENT'] = df['CAE_ZIP_CODE'].apply(find_departement)

df['WIN_EMPLOYER'] = df['WIN_SIRET'].map(agencies['EMPLOYER'])
df['WIN_STAFF'] = df['WIN_SIRET'].map(agencies['STAFF'])
df['WIN_AGENCY_ACTIVITY_LEVEL_1'] = df['WIN_SIRET'].map(agencies['MAIN_ACTIVITY_LEVEL_1'])
df['WIN_AGENCY_ACTIVITY_LEVEL_2'] = df['WIN_SIRET'].map(agencies['MAIN_ACTIVITY_LEVEL_2'])
df['WIN_AGENCY_ACTIVITY_LEVEL_3'] = df['WIN_SIRET'].map(agencies['MAIN_ACTIVITY_LEVEL_3'])
df['WIN_AGENCY_ACTIVITY_LEVEL_4'] = df['WIN_SIRET'].map(agencies['MAIN_ACTIVITY_LEVEL_4'])
df['WIN_AGENCY_ACTIVITY_LEVEL_5'] = df['WIN_SIRET'].map(agencies['MAIN_ACTIVITY_LEVEL_5'])
df['WIN_AGENCY_ACTIVITY_VERSION'] = df['WIN_SIRET'].map(agencies['ACTIVITY_CODE_VERSION'])
df['WIN_AGENCY_MAIN_ACTIVITY'] = df['WIN_SIRET'].map(agencies['MAIN_ACTIVITY_NAME'])
df['WIN_AGENCY_CREATION_DATE'] = df['WIN_SIRET'].map(agencies['CREATION_DATE'])
df['WIN_HEADQUARTERS'] = df['WIN_SIRET'].map(agencies['HEADQUARTERS'])
df['WIN_CITY_CODE'] = df['WIN_SIRET'].map(agencies['CITY_CODE'])
df['WIN_GPS'] = df['WIN_SIRET'].apply(lambda x: (agencies['LATITUDE'].get(x), agencies['LONGITUDE'].get(x)))
df['WIN_DEPARTEMENT'] = df['WIN_ZIP_CODE'].apply(find_departement)

del agencies


# Add information about municipalities, départements and régions

years = range(2015, 2024)
dict_epci_by_year = {}
dict_communes_by_year = {}

for year in years:
    year = str(year)
    filename = f'liste_EPCI_{year}.csv'
    epci = pd.read_csv(filename, dtype=str, sep=';')
    dict_epci = epci.set_index('EPCI')['NATURE_EPCI'].to_dict()
    dict_epci_by_year[year] = dict_epci

for year in years:
    year = str(year)
    filename = f'liste_communes_{year}.csv'
    communes = pd.read_csv(filename, dtype=str, sep=';', usecols=['CODGEO', 'EPCI'])
    dict_communes = communes.set_index('CODGEO')['EPCI'].to_dict()
    dict_communes_by_year[year] = dict_communes

df['CAE_EPCI'] = df.apply(apply_dict_communes_cae, axis=1)
df['WIN_EPCI'] = df.apply(apply_dict_communes_win, axis=1)
df['CAE_EPCI_TYPE'] = df.apply(apply_dict_epci_cae, axis=1)
df['WIN_EPCI_TYPE'] = df.apply(apply_dict_epci_win, axis=1)

regions = pd.read_csv('régions.csv', sep=';')
regions_dict = regions.set_index('Département')['Région'].to_dict()
df['WIN_REGION'] = df['WIN_DEPARTEMENT'].map(regions_dict)
df['CAE_REGION'] = df['CAE_DEPARTEMENT'].map(regions_dict)

with open('consolidated_table.pkl', 'wb') as f:
    pickle.dump(df, f)

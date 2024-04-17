import pickle
import numpy as np

with open('siretisation_partielle.pkl', 'rb') as f:
    df = pickle.load(f)

df['OBSERVATION'] = df.index
df['OBSERVATION'] = df['OBSERVATION'].astype(str)

colonnes_acheteurs = [
    'CAE_NAME',
    'CAE_ADDRESS',
    'CAE_TOWN',
    'CAE_ZIP_CODE',
    'DATE_AWARD_NOTICE',
    ]

acheteurs = df[df['CAE_NATIONALID'].isna()]
acheteurs = acheteurs[colonnes_acheteurs]
acheteurs['CAE_COUNTRY_CODE'] = np.array('FR')
acheteurs = acheteurs.groupby(colonnes_acheteurs[:4],as_index=False,dropna=False).agg({'CAE_NAME':'first','CAE_ADDRESS':'first','CAE_TOWN':'first','CAE_ZIP_CODE':'first', 'DATE_AWARD_NOTICE':'first'})
acheteurs.to_csv('cae_list.csv', encoding='utf-8')


colonnes_titulaires = [
    'WIN_NAME',
    'WIN_ADDRESS',
    'WIN_TOWN',
    'WIN_ZIP_CODE',
    'DATE_AWARD_NOTICE',
    'OBSERVATION']

titulaires = df[df['WIN_NATIONALID'].isna()]
titulaires = titulaires[colonnes_titulaires]
titulaires = titulaires.groupby(colonnes_titulaires[:4],as_index=False,dropna=False).agg({'WIN_NAME':'first','WIN_ADDRESS':'first','WIN_TOWN':'first','WIN_ZIP_CODE':'first', 'DATE_AWARD_NOTICE':'first'})
titulaires.to_csv('win_list.csv', encoding='utf-8')

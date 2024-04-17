import pandas as pd
import pickle

with open('processed_table.pkl', 'rb') as f:
    df = pickle.load(f)

siret = pd.read_csv('estimated_sirets.csv', low_memory=False, sep=';', dtype=str, encoding='utf-8')

mapping = {}
for _, row in siret.iterrows():
    ids = map(int, row['OBSERVATION'].split('-'))
    for id in ids:
        mapping[id] = row['siret']
for id, row in df.iterrows():
    if id in mapping:
        df.loc[id, 'WIN_SIRET'] = mapping[id]

df['WIN_SIRET'] = df['WIN_SIRET'].replace('0', pd.NA)

with open('table_with_sirets.pkl', 'wb') as f:
    pickle.dump(df, f)

import pandas as pd
import pickle
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter
import numpy as np

with open('consolidated_table.pkl', 'rb') as f:
    df = pickle.load(f)


geolocator = Nominatim(user_agent="User_BeauAMP", timeout=10)
geocode = RateLimiter(geolocator.geocode, min_delay_seconds=2)
gps_countries = pd.read_csv('gps_countries.csv')


def update_geolocation_from_city(row):
    if pd.notna(row['WIN_ADDRESS']):
        try:
            information = row['WIN_ADDRESS'] + ' ' + row['WIN_TOWN']
            location = geocode(information)
            if location:
                return (location.latitude, location.longitude)
        except:
            pass
    return (None, None)


def update_geolocation_from_country(row):
    if pd.notna(row['WIN_COUNTRY_CODE']):
        country_code = row['WIN_COUNTRY_CODE']
        if country_code in gps_countries['Alpha-2 code'].values:
            country_row = gps_countries[gps_countries['Alpha-2 code'] == country_code]
            return (country_row['Latitude (average)'].values[0], country_row['Longitude (average)'].values[0])
    return (None, None)



# Attempt to geolocate the foreign company with its stated address

df[['WIN_GPS_1', 'WIN_GPS_2']] = pd.DataFrame(df['WIN_GPS'].tolist(), index=df.index)
mask = (~df['WIN_COUNTRY_CODE'].isin(['FR', 'NONE']) & df['WIN_COUNTRY_CODE'].notna()) & df['WIN_GPS_1'].isna()  & df['WIN_GPS_2'].isna()
df.loc[mask, 'WIN_GPS'] = df.loc[mask].apply(update_geolocation_from_city, axis=1)
df = df.drop(['WIN_GPS_1', 'WIN_GPS_2'], axis=1)


# Geolocation with the average GPS position of the country if the first try has failed

df['WIN_GPS'] = df['WIN_GPS'].apply(lambda x: np.nan if x == (None, None) else x)
mask = ((~df['WIN_COUNTRY_CODE'].isin(['FR', 'NONE'])) & (~df['WIN_COUNTRY_CODE'].isna()) & (df['WIN_GPS'].isna()))
df.loc[mask, 'WIN_GPS'] = df.loc[mask].apply(update_geolocation_from_country, axis=1)


with open('consolidated_geolocated_table.pkl', 'wb') as f:
    pickle.dump(df, f)

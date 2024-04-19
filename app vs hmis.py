from tqdm import tqdm
import pandas as pd

dfAppReport = pd.read_csv('App Report Jan 2024.csv')
dfAppReport = dfAppReport[['HMIS ID','Service']]
dfAppReport = dfAppReport.dropna(subset=['HMIS ID', 'Service'])

rows = []

for _, row in dfAppReport.iterrows():
    for service in row['Service'].split('\n'):
        service_name, service_info = service.split(' (')
        date, count = service_info.rstrip(')').split(') : ')
        #print(row['HMIS ID'], service_name, date, count)
        for _ in range(int(count)):
            rows.append([row['HMIS ID'], service_name, date])

# Creating a new dataframe from the processed rows
df_transformed = pd.DataFrame(rows, columns=['HMIS ID', 'Service', 'Service Date'])
df_transformed['Service Date'] = pd.to_datetime(df_transformed['Service Date'])
df_transformed.to_csv('App Report 2023.csv', index=False)

dfServicesOct = pd.read_csv('Services Apr2021 - Jan2024.csv')
dfServicesCovidSep = dfServicesOct.copy()
dfServicesCovidSep['Service Date'] = pd.to_datetime(dfServicesCovidSep['Service Date'])
dfServicesCovidSep = dfServicesCovidSep[(dfServicesCovidSep['Service Date'] >= '2024-01-01') & (dfServicesCovidSep['Service Date'] <= '2024-01-31')]

#pint date ranges
print('HMIS Date Range: ', dfServicesCovidSep['Service Date'].min(), ' - ', dfServicesCovidSep['Service Date'].max())
print('APP Date Range: ', df_transformed['Service Date'].min(), ' - ', df_transformed['Service Date'].max())
print('\n')

dfServicesCovidSep['org'] = dfServicesCovidSep['Provider'].fillna(dfServicesCovidSep['Associated Program'])

dfServicesCovidSep = dfServicesCovidSep.dropna(subset=['org'])
dfServicesCovidSep = dfServicesCovidSep[dfServicesCovidSep['org'].str.contains('SALT')]

dfServicesCovidSep = dfServicesCovidSep[['Client ID', 'Service', 'Service Date']]

dfServicesCovidSep['Client ID'] = dfServicesCovidSep['Client ID'].astype(str)

df_transformed = df_transformed[df_transformed['Service'].isin(['Laundry', 'Shower', 'Case Management'])]
dfServicesCovidSep = dfServicesCovidSep[dfServicesCovidSep['Service'].isin(['Laundry', 'Shower', 'Case Management'])]

print("App ['Laundry', 'Shower', 'Case Management'] services:", len(df_transformed['HMIS ID']))
print("App Unique Clients: ", len(df_transformed['HMIS ID'].unique()))
print('\n')
print("Client Track ['Laundry', 'Shower', 'Case Management'] services:", len(dfServicesCovidSep['Client ID']))
print("Client Track Unique Clients: ", len(dfServicesCovidSep['Client ID'].unique()))
print('\n')

df_transformed = df_transformed.rename(columns={'HMIS ID': 'Client ID'})
df_transformed['Client ID'] = df_transformed['Client ID'].astype(str)
df_transformed['Service'] = df_transformed['Service'].astype(str)

dfServicesCovidSep['Client ID'] = dfServicesCovidSep['Client ID'].astype(str)
dfServicesCovidSep['Service'] = dfServicesCovidSep['Service'].astype(str)

#######
#services mising in app and client track
df_transformedEXACT = df_transformed.copy()
dfServicesCovidSepEXACT = dfServicesCovidSep.copy()

df_transformedEXACT = df_transformedEXACT.sort_values(by=['Client ID', 'Service', 'Service Date'], ascending=False)
dfServicesCovidSepEXACT = dfServicesCovidSepEXACT.sort_values(by=['Client ID', 'Service', 'Service Date'], ascending=False)

print(df_transformedEXACT)
print(dfServicesCovidSepEXACT)

transformed = df_transformedEXACT.values.tolist()
services = dfServicesCovidSepEXACT.values.tolist()

for i in reversed(range(len(transformed))):
    s = transformed[i]
    try:
        services.pop(services.index(s))
        transformed.pop(i)
    except:
        pass

print('SERVICES EXACT_AppNotClientTrack: ', len(transformed))
print('SERVICES EXACT_ClientTrackNotApp: ', len(services))

df_transformedEXACT = pd.DataFrame(transformed, columns=['Client ID', 'Service', 'Service Date'])
dfServicesCovidSepEXACT = pd.DataFrame(services, columns=['Client ID', 'Service', 'Service Date'])

df_transformedEXACT.to_csv('SERVICES EXACT_AppNotClientTrack - JAN 2024.csv', index=False)
dfServicesCovidSepEXACT.to_csv('SERVICES EXACT_ClientTrackNotApp - JAN 2024.csv', index=False)

#######


df_transformed = df_transformed[['Client ID', 'Service']]
dfServicesCovidSep = dfServicesCovidSep[['Client ID', 'Service']]


transformed = df_transformed.values.tolist()
services = dfServicesCovidSep.values.tolist()

for i in reversed(range(len(transformed))):
    s = transformed[i]
    try:
        services.pop(services.index(s))
        transformed.pop(i)
    except:
        pass

df_transformed = pd.DataFrame(transformed, columns=['Client ID', 'Service'])
dfServicesCovidSep = pd.DataFrame(services, columns=['Client ID', 'Service'])

print('SERVICES_Not exact_AppNotClientTrack: ', len(df_transformed))
print('SERVICES_Not exact_ClientTrackNotApp: ', len(dfServicesCovidSep))

#df_transformed.to_csv('SERVICES_Not exact_AppNotClientTrack - JAN 2024.csv', index=False)
#dfServicesCovidSep.to_csv('SERVICES_Not exact_ClientTrackNotApp - JAN 2024.csv', index=False)
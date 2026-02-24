import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os

#set directory
os.chdir('hydroinformatics')

#Load data from data folder
reservoir_gauge = pd.read_csv('data/reservoir_gauge.csv')
headwater_gauge = pd.read_csv('data/headwater_gauge.csv')
uinta_river_gauge = pd.read_csv('data/uinta_river_gauge.csv')
ashley_creek_gauge = pd.read_csv('data/ashley_creek_gauge.csv')
#Visualize data headers, checkout dataframe
# print(reservoir_gauge.head())
# print(reservoir_gauge.describe())

# print(headwater_gauge.head())
# print(headwater_gauge.describe())

# print(uinta_river_gauge.head())
# print(uinta_river_gauge.describe())

# print(ashley_creek_gauge.head())
# print(ashley_creek_gauge.describe())

#No negative valuess or 0s

#Change datettime column to datetime format
def convert_to_datetime(df):
    df['datetime'] = pd.to_datetime(df['datetime'])
    df.set_index('datetime', inplace=True,drop=True)
    return df
reservoir_gauge = convert_to_datetime(reservoir_gauge)
headwater_gauge = convert_to_datetime(headwater_gauge)
uinta_river_gauge = convert_to_datetime(uinta_river_gauge)
ashley_creek_gauge = convert_to_datetime(ashley_creek_gauge)

def edit_columns(df):
    df['discharge_cfs'] = df['00060_Mean']
    df = df.drop(columns=['site_no', '00060_Mean_cd','00060_Mean'], inplace=False)
    return df
reservoir_gauge = edit_columns(reservoir_gauge)
headwater_gauge = edit_columns(headwater_gauge)
uinta_river_gauge = edit_columns(uinta_river_gauge)
ashley_creek_gauge = edit_columns(ashley_creek_gauge)

#Check post edit_columns:
#print(reservoir_gauge.head())
#print(reservoir_gauge.describe())

# print(headwater_gauge.head())
# print(headwater_gauge.describe())

# print(uinta_river_gauge.head())
# print(uinta_river_gauge.describe())

# print(ashley_creek_gauge.head())
# print(ashley_creek_gauge.describe())


#Concentate the data to find 6 years matching 
reservoir_gauge = reservoir_gauge.rename(columns={'discharge_cfs': 'discharge_reservoir'})
headwater_gauge = headwater_gauge.rename(columns={'discharge_cfs': 'discharge_headwater'})
uinta_river_gauge = uinta_river_gauge.rename(columns={'discharge_cfs': 'discharge_uinta_river'})
ashley_creek_gauge = ashley_creek_gauge.rename(columns={'discharge_cfs': 'discharge_ashley_creek'})

merged_df = reservoir_gauge.merge(headwater_gauge, on='datetime', how='outer')
merged_df = merged_df.merge(uinta_river_gauge, on='datetime', how='outer')
merged_df = merged_df.merge(ashley_creek_gauge, on='datetime', how='outer')

print(merged_df.columns)
#All of our gauges are in here
print(merged_df.isnull().sum())
#No nans in our data, yay!
#Lets visualize this data
fig, axes = plt.subplots(2, 2, figsize=(15, 10))
fig.suptitle('Discharge Comparison of Gauges (2019-2025)')

axes[0,0].plot(merged_df.index, merged_df['discharge_reservoir'], label='Reservoir Gauge',color ='blue')
axes[0,0].set_title('Reservoir Gauge Discharge')
axes[0,0].set_xlabel('Date')
axes[0,0].set_ylabel('Discharge (cfs)')
axes[0,1].plot(merged_df.index, merged_df['discharge_headwater'], label='Headwater Gauge', color='green')
axes[0,1].set_title('Headwater Gauge Discharge')
axes[0,1].set_xlabel('Date')
axes[0,1].set_ylabel('Discharge (cfs)')
axes[1,0].plot(merged_df.index, merged_df['discharge_uinta_river'], label='Uinta River Gauge', color='pink')
axes[1,0].set_title('Uinta River Gauge Discharge')
axes[1,0].set_xlabel('Date')
axes[1,0].set_ylabel('Discharge (cfs)')
axes[1,1].plot(merged_df.index, merged_df['discharge_ashley_creek'], label='Ashley Creek Gauge', color='purple')
axes[1,1].set_xlabel('Date')
axes[1,1].set_ylabel('Discharge (cfs)')
axes[1,1].set_title('Ashley Creek Gauge Discharge')
plt.tight_layout()
plt.show()


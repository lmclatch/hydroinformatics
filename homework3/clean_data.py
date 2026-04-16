import numpy as np
import pandas as pd
import os

#os.chdir("hydroinformatics/hydroinformatics/homework3")
#Bring in all data
#streamflow data
little_susitna_streamflow = pd.read_csv('data/little_susitna_streamflow.csv')
ship_creek_streamflow = pd.read_csv('data/ship_creek_streamflow.csv')
manatuska_river_gauge = pd.read_csv('data/manatuska_river_gauge.csv')
campbell_creek_gauge = pd.read_csv('data/campbell_creek_gauge.csv')

#all daymet data
daymet_data = pd.read_csv('data/daymet_api_output/alaska_basins_weather_master.csv')

#catchment attribute data
catchment_attributes = pd.read_csv('data/catchment_attributes.csv')

#clean daymet
daymet_data = pd.read_csv('data/daymet_api_output/alaska_basins_weather_master.csv')
# 1. Cast all streamflow gauge_ids to string
little_susitna_streamflow['gauge_id'] = little_susitna_streamflow['gauge_id'].astype(str)
ship_creek_streamflow['gauge_id'] = ship_creek_streamflow['gauge_id'].astype(str)
manatuska_river_gauge['gauge_id'] = manatuska_river_gauge['gauge_id'].astype(str)
campbell_creek_gauge['gauge_id'] = campbell_creek_gauge['gauge_id'].astype(str)

# 2. Cast Daymet gauge_id to string
daymet_data['gauge_id'] = daymet_data['gauge_id'].astype(str)

# 3. Cast Catchment Attributes gauge_id to string
catchment_attributes['gauge_id'] = catchment_attributes['gauge_id'].astype(str)
# 1. Clean Daymet: Convert the existing 'year'/'yday' to a 'date' column
daymet_data['date'] = pd.to_datetime(
    daymet_data['year'].astype(str) + '-' + daymet_data['yday'].astype(str), 
    format='%Y-%j'
).dt.normalize()

# 2. Stack Streamflow: Ensure 'datetime' or 'date' is a column
streamflow_master = pd.concat([
    little_susitna_streamflow, 
    ship_creek_streamflow, 
    manatuska_river_gauge, 
    campbell_creek_gauge
])

# Most USGS/StreamStats CSVs name the time column 'datetime'. 
# Let's standardize it to 'date' to match daymet.
if 'datetime' in streamflow_master.columns:
    streamflow_master = streamflow_master.rename(columns={'datetime': 'date'})

streamflow_master['date'] = pd.to_datetime(streamflow_master['date']).dt.tz_localize(None).dt.normalize()

# 3. Merge on the columns directly (No reset_index needed)
combined_dynamic = pd.merge(
    daymet_data, 
    streamflow_master, 
    on=['date', 'gauge_id'], 
    how='inner'
).drop(columns=['year', 'yday'], errors='ignore')

# 4. Final Join with Attributes
catchment_attributes['gauge_id'] = catchment_attributes['gauge_id'].astype(str)
combined_dynamic['gauge_id'] = combined_dynamic['gauge_id'].astype(str)

final_df = pd.merge(combined_dynamic, catchment_attributes, on='gauge_id', how='left')

# 5. Set index at the very end
final_df = final_df.set_index('date').sort_index()

print(final_df.head())

print("Columns in final_df:", final_df.columns.tolist())
print(final_df[['gauge_id']].nunique())

# print("Daymet IDs:", daymet_data['gauge_id'].unique())
# print("Little Susitna ID:", little_susitna_streamflow['gauge_id'].unique())
# print("Ship Creek ID:", ship_creek_streamflow['gauge_id'].unique())
# print("Matanuska ID:", manatuska_river_gauge['gauge_id'].unique())
# print("Campbell Creek ID:", campbell_creek_gauge['gauge_id'].unique())
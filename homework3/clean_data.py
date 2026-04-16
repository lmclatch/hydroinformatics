import numpy as np
import pandas as pd

#Bring in all data
#streamflow data
little_susitna_streamflow = pd.read_csv('data/little_susitna_streamflow.csv', index_col=0)
ship_creek_streamflow = pd.read_csv('data/ship_creek_streamflow.csv', index_col=0)
manatuska_river_gauge = pd.read_csv('data/manatuska_river_gauge.csv', index_col=0)
campbell_creek_gauge = pd.read_csv('data/campbell_creek_gauge.csv', index_col=0)

#all daymet data
daymet_data = pd.read_csv('data/daymet_api_putput/alaska_basins_weather_master.csv', index_col=0)

#catchment attribute data
catchment_attributes = pd.read_csv('data/catchment_attributes.csv', index_col=0)

#Make dyamet have a "datetime" index
daymet_data.index = pd.to_datetime(daymet_data['year'].astype(str) + '-' + daymet_data['yday'].astype(str), format='%Y-%j')
# Ensure it is 'naive' (no timezone) and normalized to midnight to match your gauge data
daymet_data.index = daymet_data.index.normalize()



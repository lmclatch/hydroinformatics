import pandas as pd
from dataretrieval import nwis
import os

''' This script downloads all relevant daily discharge values for the 4 selected streamflow gauges in the Anchorage area, and saves them as csv files in the data folder.
The 4 streamflow gauges are:
- Little Susitina, 15290000
- Ship Creek, 15276000
- Matanuska River, 15284000
- Campbell Creek, 15274600
'''
#Little Susitina, 15290000
site_id = "15290000"
start_date = "1990-09-30"
end_date = "2025-10-01"
parameter_code = "00060" #daily discharge
little_susitna_streamflow = nwis.get_record(sites=site_id, service='dv', parameterCd=parameter_code, 
start=start_date, end=end_date)

#Ship Creek, 15276000
site_id = "15276000"
start_date = "1990-09-30"
end_date = "2025-10-01"
parameter_code = "00060" #daily discharge
ship_creek_streamflow = nwis.get_record(sites=site_id, service='dv', parameterCd=parameter_code, 
start=start_date, end=end_date)

#-	Matanuska River, 15284000
site_id = "15284000"
start_date = "1990-09-30"
end_date = "2025-10-01"
parameter_code = "00060" #daily discharge
manatuska_river_gauge = nwis.get_record(sites=site_id, service='dv', parameterCd=parameter_code, 
start=start_date, end=end_date)

#Campbell Creek, 15274600
site_id = "15274600"
start_date = "1990-09-30"
end_date = "2025-10-01"
parameter_code = "00060" #daily discharge
campbell_creek_gauge = nwis.get_record(sites=site_id, service='dv', parameterCd=parameter_code, 
start=start_date, end=end_date)

#set directory
#os.chdir('hydroinformatics/hydroinformatics/homework3')

#Clean streamflow data !!!
little_susitna_streamflow = little_susitna_streamflow.rename(columns={'00060_Mean': 'flow_cfs'})
ship_creek_streamflow = ship_creek_streamflow.rename(columns={'00060_Mean': 'flow_cfs'})
manatuska_river_gauge = manatuska_river_gauge.rename(columns={'00060_Mean': 'flow_cfs'})
campbell_creek_gauge = campbell_creek_gauge.rename(columns={'00060_Mean': 'flow_cfs'})

little_susitna_streamflow['flow_cms'] = little_susitna_streamflow['flow_cfs'] * 0.0283168
ship_creek_streamflow['flow_cms'] = ship_creek_streamflow['flow_cfs'] * 0.0283168
manatuska_river_gauge['flow_cms'] = manatuska_river_gauge['flow_cfs'] * 0.0283168
campbell_creek_gauge['flow_cms'] = campbell_creek_gauge['flow_cfs'] * 0.0283168

little_susitna_streamflow.drop(columns=['flow_cfs'], inplace=True)
ship_creek_streamflow.drop(columns=['flow_cfs'], inplace=True)
manatuska_river_gauge.drop(columns=['flow_cfs'], inplace=True)
campbell_creek_gauge.drop(columns=['flow_cfs'], inplace=True)

#change index to datetime
little_susitna_streamflow.index = pd.to_datetime(little_susitna_streamflow.index)
ship_creek_streamflow.index = pd.to_datetime(ship_creek_streamflow.index)
manatuska_river_gauge.index = pd.to_datetime(manatuska_river_gauge.index)
campbell_creek_gauge.index = pd.to_datetime(campbell_creek_gauge.index)
#remove hour/minutes/seconds:
campbell_creek_gauge.index = campbell_creek_gauge.index.tz_localize(None).normalize()
little_susitna_streamflow.index = little_susitna_streamflow.index.tz_localize(None).normalize()
ship_creek_streamflow.index = ship_creek_streamflow.index.tz_localize(None).normalize()
manatuska_river_gauge.index = manatuska_river_gauge.index.tz_localize(None).normalize()
#make site_no to gauge_id to match other data
little_susitna_streamflow = little_susitna_streamflow.rename(columns={'site_no': 'gauge_id'})
ship_creek_streamflow = ship_creek_streamflow.rename(columns={'site_no': 'gauge_id'})
manatuska_river_gauge = manatuska_river_gauge.rename(columns={'site_no': 'gauge_id'})
campbell_creek_gauge = campbell_creek_gauge.rename(columns={'site_no': 'gauge_id'})

little_susitna_streamflow.drop(columns=['00060_Mean_cd'], inplace=True)
ship_creek_streamflow.drop(columns=['00060_Mean_cd'], inplace=True)
manatuska_river_gauge.drop(columns=['00060_Mean_cd'], inplace=True)
campbell_creek_gauge.drop(columns=['00060_Mean_cd'], inplace=True)

print(little_susitna_streamflow.head())
print(ship_creek_streamflow.head())
print(manatuska_river_gauge.head())
print(campbell_creek_gauge.head())

#Save data to respective data folder
little_susitna_streamflow.to_csv('data/little_susitna_streamflow.csv')
ship_creek_streamflow.to_csv('data/ship_creek_streamflow.csv')
manatuska_river_gauge.to_csv('data/manatuska_river_gauge.csv')
campbell_creek_gauge.to_csv('data/campbell_creek_gauge.csv')
import dataretrieval as dr
from dataretrieval import nwis
import pandas as pd


# Selected basin:
#Alaska: USGS, 15274600 SNOTEL: 1070

#Pull streamflow data
site_id = '15290000' # L Susitna R NR Palmer AK - USGS-15290000
start_date = "1980-10-01"
end_date = "2025-09-30"

Ak_streamflow_data,meta = nwis.get_dv(sites=site_id,
                           parameterCd="00060",
                           start=start_date,
                           end=end_date)
#print(Ak_streamflow_data.head())

#Clean streamflow
Ak_streamflow_data.index = pd.to_datetime(Ak_streamflow_data.index)
Ak_streamflow_data = Ak_streamflow_data.rename(columns={'00060_Mean': 'streamflow (cfs)'})
Ak_streamflow_data.drop(columns=['00060_Mean_cd'], inplace=True)
print(Ak_streamflow_data.head())

Ak_streamflow_data.to_csv('data/streamflow_data.csv', index=True)
import pandas as pd
from dataretrieval import nwis
import os

#Load NWIS data, study site Utah, utilize nwis dataretrivel package to access USGS NWIS data, daily discharge (parameter code 00060) for the following gauges:

#Little Susitina, 190205051202
site_id = "190205051202"
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

#Campbell Creek
site_id = "09266500"
start_date = "1990-09-30"
end_date = "2025-10-01"

parameter_code = "00060" #daily discharge
campbell_creek_gauge = nwis.get_record(sites=site_id, service='dv', parameterCd=parameter_code, 
start=start_date, end=end_date)

#set directory
os.chdir('hydroinformatics/homework3')

#Save data to respective data folder
little_susitna_streamflow.to_csv('data/little_susitna_streamflow.csv')
ship_creek_streamflow.to_csv('data/ship_creek_streamflow.csv')
manatuska_river_gauge.to_csv('data/manatuska_river_gauge.csv')
campbell_creek_gauge.to_csv('data/campbell_creek_gauge.csv')
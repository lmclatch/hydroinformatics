import pandas as pd
from dataretrieval import nwis
import os

#Load NWIS data, study site Utah, utilize nwis dataretrivel package to access USGS NWIS data, daily discharge (parameter code 00060) for the following gauges:

#Reservoir gauge: 09288180
site_id = "09288180"
start_date = "2019-09-30"
end_date = "2025-10-01"
parameter_code = "00060" #daily discharge
reservoir_gauge = nwis.get_record(sites=site_id, service='dv', parameterCd=parameter_code, 
start=start_date, end=end_date)

#Headwater gauge: 09292000
site_id = "09292000"
start_date = "2019-09-30"
end_date = "2025-10-01"
parameter_code = "00060" #daily discharge
headwater_gauge_gauge = nwis.get_record(sites=site_id, service='dv', parameterCd=parameter_code, 
start=start_date, end=end_date)

#Uinta river gauge: 09301500
site_id = "09301500"
start_date = "2019-09-30"
end_date = "2025-10-01"
parameter_code = "00060" #daily discharge
uinta_river_gauge = nwis.get_record(sites=site_id, service='dv', parameterCd=parameter_code, 
start=start_date, end=end_date)

#Ashley Creek: 09266500
site_id = "09266500"
start_date = "2019-09-30"
end_date = "2025-10-01"

parameter_code = "00060" #daily discharge
ashley_creek_gauge = nwis.get_record(sites=site_id, service='dv', parameterCd=parameter_code, 
start=start_date, end=end_date)

#set directory
os.chdir('hydroinformatics')

#Save data to respective data folder
reservoir_gauge.to_csv('data/reservoir_gauge.csv')
headwater_gauge_gauge.to_csv('data/headwater_gauge.csv')
uinta_river_gauge.to_csv('data/uinta_river_gauge.csv')
ashley_creek_gauge.to_csv('data/ashley_creek_gauge.csv')

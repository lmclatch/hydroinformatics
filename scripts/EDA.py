import pandas as pd
import numpy as np
from dataretrieval import nwis

#Load NWIS data, study site Utah

#Reservoir gauge: 09288180
site_id = "09288180"
start_date = "2020-01-01"
end_date = "2020-12-31"
parameter_code = "00060" #daily discharge

#Headwater gauge: 09292000

#Uinta river gauge: 09301500


import pandas as pd
import numpy as np

'''
attributes taken directly from stream stats for each basin, formatted into a dataframe and saved as a csv file in the data folder. Attributes include:
- Drainage area (sqaure km)
- Mean Basin elevation (m)
- Percent Glaciers
- Percent Lakes and Ponds
- LC01BARE
- Percent_Forest_from_NLCD2001
- LC01WETLND
'''

campbell_creek_static_attributes = {
    "gauge_id": "15274600",
    "Drainage Area (square km)": 175,
    "Mean Basin elevation (m)": 539,
    "Percent Glaciers": 0, 
    "Percent Lakes and Ponds": 1,
    "LC01BARE": 12,
    "Percent_Forest_from_NLCD2001": 21,
    "LC01WETLND": 2
}
little_susitna_static_attributes = {
    "gauge_id": "15290000",
    "Drainage Area (square km)": 160,
    "Mean Basin elevation (m)": 1112,
    "Percent Glaciers": 1,
    "Percent Lakes and Ponds": 0,
    "LC01BARE": 34,
    "Percent_Forest_from_NLCD2001": 1,
    "LC01WETLND": 0
}
ship_creek_static_attributes = {
    "gauge_id": "15276000",
    "Drainage Area (square km)": 232,
    "Mean Basin elevation (m)": 905,
    "Percent Glaciers": 0,
    "Percent Lakes and Ponds": 0,
    "LC01BARE": 18,
    "Percent_Forest_from_NLCD2001": 8,
    "LC01WETLND": 0
}

manatuska_river_static_attributes = {
    "gauge_id": "15284000",
    "Drainage Area (square km)": 5335,
    "Mean Basin elevation (m)": 1298,
    "Percent Glaciers": 11,
    "Percent Lakes and Ponds": 0,  
    "LC01BARE": 42,
    "Percent_Forest_from_NLCD2001": 13,
    "LC01WETLND": 1
}

attributes_df = pd.DataFrame([campbell_creek_static_attributes, little_susitna_static_attributes, ship_creek_static_attributes, manatuska_river_static_attributes],
                                index=["Campbell Creek", "Little Susitna", "Ship Creek", "Matanuska River"])
attributes_df.to_csv('data/catchment_attributes.csv')

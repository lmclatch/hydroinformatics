import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

#Load data from data folder
reservoir_gauge = pd.read_csv('data/reservoir_gauge.csv')
headwater_gauge = pd.read_csv('data/headwater_gauge.csv')
uinta_river_gauge = pd.read_csv('data/uinta_river_gauge.csv')
ashley_creek_gauge = pd.read_csv('data/ashley_creek_gauge.csv')
#Visualize data headers, checkout dataframe
print(reservoir_gauge.head())
print(reservoir_gauge.describe())

print(headwater_gauge.head())
print(headwater_gauge.describe())

print(uinta_river_gauge.head())
print(uinta_river_gauge.describe())

print(ashley_creek_gauge.head())
print(ashley_creek_gauge.describe())

#Change datettime column to datetime format
def convert_to_datetime(df):
    df['datetime'] = pd.to_datetime(df['datetime'])
    return df
reservoir_gauge = convert_to_datetime(reservoir_gauge)
headwater_gauge = convert_to_datetime(headwater_gauge)
uinta_river_gauge = convert_to_datetime(uinta_river_gauge)
ashley_creek_gauge = convert_to_datetime(ashley_creek_gauge)

#Concentate the data to find 6 years matching 
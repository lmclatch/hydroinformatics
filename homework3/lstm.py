import math
import random
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
import joblib

from utils import LSTM_helper

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
print(f"Using device: {device}")

# Set random seeds for reproducibility
SEED = 42
random.seed(SEED)
np.random.seed(SEED)
torch.manual_seed(SEED)


# Data parameters
FILE_PATH = "data/final_lstm_data.csv" #path to cleaned and merged data file, with streamflow, daymet, and catchment attributes
DATE_COL = "datetime"
TARGET_COL = "flow_cms"

# Hyperparameters
LOOKBACK_DAYS = 90 #number of past time steps to use for prediction
BATCH_SIZE = 64 #number of samples per batch for training
EPOCHS = 50 #number of times to iterate over the entire training dataset
PATIENCE = 10 #number of epochs to wait for improvement in validation loss before stopping training
LEARNING_RATE = 1e-3 #step size for updating model parameters during training

# Testing/training on one basin, so we can use the same date ranges for all basins
TRAIN_START_YEAR = 1990
TRAIN_END_YEAR = 2014
VAL_START_YEAR = 2015
VAL_END_YEAR = 2018
TEST_START_YEAR = 2019
TEST_END_YEAR = 2021

# Load and preprocess the data
df = pd.read_csv(FILE_PATH)

# Clean column names, removing spaces and special characters
clean_cols = []
for c in df.columns:
    c = str(c).strip().replace('"', '')
    c = ''.join(ch if ch.isalnum() else '_' for ch in c)
    while '__' in c:
        c = c.replace('__', '_')
    c = c.strip('_')
    clean_cols.append(c)
df.columns = clean_cols

# Convert date column to datetime and sort by date
df[DATE_COL] = pd.to_datetime(df[DATE_COL])
df = df.sort_values(DATE_COL).reset_index(drop=True)

print('Rows:', len(df))
print('Date range:', df[DATE_COL].min().date(), 'to', df[DATE_COL].max().date())
print('Years:', sorted(df[DATE_COL].dt.year.unique()))
df.head()

# Identify numeric feature columns, excluding target and date columns
exclude_cols = {TARGET_COL, DATE_COL, 'site_no', 'station_id', 'Unnamed_0'}

# We want to include only numeric columns as features, and exclude any non-numeric or irrelevant columns
numeric_cols = [c for c in df.columns if pd.api.types.is_numeric_dtype(df[c])]
feature_cols = [c for c in numeric_cols if c not in exclude_cols]

print('Target column:', TARGET_COL)
print('Number of features:', len(feature_cols))
print(feature_cols)

feature_cols =['TUM_SWE_cm', 'DAN_SWE_cm', 'SLI_SWE_cm']
cols = feature_cols + [TARGET_COL]

#select these columns from the dataframe
df = df[[DATE_COL] + cols]
df.head()
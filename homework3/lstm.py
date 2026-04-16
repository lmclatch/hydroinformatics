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
FILE_PATH = "data"
DATE_COL = "Date"
TARGET_COL = "flow_cms"

# Hyperparameters
LOOKBACK_DAYS = 90 #number of past time steps to use for prediction
BATCH_SIZE = 64 #number of samples per batch for training
EPOCHS = 50 #number of times to iterate over the entire training dataset
PATIENCE = 8 #number of epochs to wait for improvement in validation loss before stopping training
LEARNING_RATE = 1e-3 #step size for updating model parameters during training

# Testing/training on one basin, so we can use the same date ranges for all basins
TRAIN_START_YEAR = 1990
TRAIN_END_YEAR = 2014
VAL_START_YEAR = 2015
VAL_END_YEAR = 2018
TEST_START_YEAR = 2019
TEST_END_YEAR = 2021
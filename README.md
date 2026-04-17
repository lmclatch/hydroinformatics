# Hydroinformatics
CVEEN 6920 at the University of Utah
# Assignment #3
Goal: Predicting daily streamflow in southcentral Alaska basins using a Long Short-Term Memory (LSTM) neural network trained on Daymet climate forcings and catchment attributes.

Study Basins
Four USGS-gauged basins in the Matanuska-Susitna and Anchorage area were selected, covering a range of basin sizes and hydrological regimes:
Little Susitna River (15290000), Ship Creek near Anchorage (15276000), the Matanuska River at Palmer (15284000), and Campbell Creek near Spenard (15274600).

Model
A two-layer LSTM with hidden size 64 and dropout 0.2 was trained to predict next-day streamflow from a 90-day lookback window. Static catchment attributes were concatenated with dynamic climate forcings at each time step. 
Train/val/test split:

Training: Matanuska, Little Susitna, Campbell Creek — 1990 through 2016
Validation: Matanuska, Little Susitna, Campbell Creek — 2017 onward
Test: Ship Creek (held out entirely — zero-shot basin generalization)

Evaluation metrics: MAE, RMSE, R², Nash-Sutcliffe Efficiency (NSE)

Relevant streamstats deliniated files can be found in /data
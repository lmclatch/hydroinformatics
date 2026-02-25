import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os

#set directory
os.chdir('hydroinformatics')

#Load data from data folder
reservoir_gauge = pd.read_csv('data/reservoir_gauge.csv')

headwater_gauge = pd.read_csv('data/headwater_gauge.csv')
uinta_river_gauge = pd.read_csv('data/uinta_river_gauge.csv')
ashley_creek_gauge = pd.read_csv('data/ashley_creek_gauge.csv')
#Visualize data headers, checkout dataframe
# print(reservoir_gauge.head())
# print(reservoir_gauge.describe())

# print(headwater_gauge.head())
# print(headwater_gauge.describe())

# print(uinta_river_gauge.head())
# print(uinta_river_gauge.describe())

# print(ashley_creek_gauge.head())
# print(ashley_creek_gauge.describe())

#No negative valuess or 0s

#Change datettime column to datetime format
def convert_to_datetime(df):
    df['datetime'] = pd.to_datetime(df['datetime'])
    df.set_index('datetime', inplace=True,drop=True)
    return df
reservoir_gauge = convert_to_datetime(reservoir_gauge)
headwater_gauge = convert_to_datetime(headwater_gauge)
uinta_river_gauge = convert_to_datetime(uinta_river_gauge)
ashley_creek_gauge = convert_to_datetime(ashley_creek_gauge)

def edit_columns(df):
    df['discharge_cfs'] = df['00060_Mean']
    df = df.drop(columns=['site_no', '00060_Mean_cd','00060_Mean'], inplace=False)
    return df
reservoir_gauge = edit_columns(reservoir_gauge)
headwater_gauge = edit_columns(headwater_gauge)
uinta_river_gauge = edit_columns(uinta_river_gauge)
ashley_creek_gauge = edit_columns(ashley_creek_gauge)

#Check post edit_columns:
#print(reservoir_gauge.head())
#print(reservoir_gauge.describe())

# print(headwater_gauge.head())
# print(headwater_gauge.describe())

# print(uinta_river_gauge.head())
# print(uinta_river_gauge.describe())

# print(ashley_creek_gauge.head())
# print(ashley_creek_gauge.describe())


#Concentate the data to find 6 years matching 
reservoir_gauge = reservoir_gauge.rename(columns={'discharge_cfs': 'discharge_reservoir'})
headwater_gauge = headwater_gauge.rename(columns={'discharge_cfs': 'discharge_headwater'})
uinta_river_gauge = uinta_river_gauge.rename(columns={'discharge_cfs': 'discharge_uinta_river'})
ashley_creek_gauge = ashley_creek_gauge.rename(columns={'discharge_cfs': 'discharge_ashley_creek'})

merged_df = reservoir_gauge.merge(headwater_gauge, on='datetime', how='outer')
merged_df = merged_df.merge(uinta_river_gauge, on='datetime', how='outer')
merged_df = merged_df.merge(ashley_creek_gauge, on='datetime', how='outer')

#print(merged_df.columns)
#All of our gauges are in here
#print(merged_df.isnull().sum())
#No nans in our data, yay!
#Lets visualize this data
fig, axes = plt.subplots(2, 2, figsize=(15, 10))
fig.suptitle('Discharge Comparison of Gauges (2019-2025)')

axes[0,0].plot(merged_df.index, merged_df['discharge_reservoir'], label='Reservoir Gauge',color ='blue')
axes[0,0].set_title(' Strawberry River (reservoir) Discharge')
axes[0,0].set_xlabel('Date')
axes[0,0].set_ylabel('Discharge (cfs)')
axes[0,1].plot(merged_df.index, merged_df['discharge_headwater'], label='Headwater Gauge', color='green')
axes[0,1].set_title('Yellowstone River (headwater) Discharge')
axes[0,1].set_xlabel('Date')
axes[0,1].set_ylabel('Discharge (cfs)')
axes[1,0].plot(merged_df.index, merged_df['discharge_uinta_river'], label='Uinta River Gauge', color='pink')
axes[1,0].set_title('Uinta River Discharge')
axes[1,0].set_xlabel('Date')
axes[1,0].set_ylabel('Discharge (cfs)')
axes[1,1].plot(merged_df.index, merged_df['discharge_ashley_creek'], label='Ashley Creek Gauge', color='purple')
axes[1,1].set_xlabel('Date')
axes[1,1].set_ylabel('Discharge (cfs)')
axes[1,1].set_title('Ashley Creek Discharge')
for ax in axes.flat:
    ax.set_ylim(0, 2000)
plt.tight_layout()
plt.show()

#Resample data
# Weekly mean
reservoir_weekly = reservoir_gauge.resample('W').mean()
headwaters_weekly = headwater_gauge.resample('W').mean()
ashley_creek_weekly = ashley_creek_gauge.resample('W').mean()
uinta_river_weekly = uinta_river_gauge.resample('W').mean()

#combine
weekly_df = reservoir_weekly.join([headwaters_weekly, uinta_river_weekly, ashley_creek_weekly], how='outer')
print(weekly_df.head())

# Monthly volumetric (cfs to acre-feet)
# mean cfs * 86400 sec/day * ~30.44 days/month / 43560 ft^2 = acre-feet
def cfs_to_acre_feet_monthly(df):
    return df.resample('ME').apply(lambda x: x.mean() * 86400 * len(x) / 43560)

reservoir_monthly = cfs_to_acre_feet_monthly(reservoir_gauge)
headwaters_monthly = cfs_to_acre_feet_monthly(headwater_gauge)
ashley_creek_monthly = cfs_to_acre_feet_monthly(ashley_creek_gauge)
uinta_river_monthly = cfs_to_acre_feet_monthly(uinta_river_gauge)

monthly_df = reservoir_monthly.join([headwaters_monthly, uinta_river_monthly, ashley_creek_monthly], how='outer')
print(monthly_df.head())

# 4-panel figure
colors = {
    'discharge_reservoir': 'blue',
    'discharge_headwater': 'green',
    'discharge_uinta_river': 'pink',
    'discharge_ashley_creek': 'purple'
}
labels = {
    'discharge_reservoir': 'Reservoir',
    'discharge_headwater': 'Headwater',
    'discharge_uinta_river': 'Uinta River',
    'discharge_ashley_creek': 'Ashley Creek'
}

fig, axes = plt.subplots(2, 2, figsize=(16, 10))
fig.suptitle('Discharge: Raw, Monthly Volume, Weekly Average', fontsize=14)

# Panel A - Daily raw
for col in colors:
    axes[0,0].plot(merged_df.index, merged_df[col], color=colors[col], label=labels[col], linewidth=0.8)
axes[0,0].set_title('Daily (Raw)')
axes[0,0].set_ylabel('Discharge (cfs)')
axes[0,0].set_xlabel('Date')

# Panel B - Weekly mean
for col in colors:
    axes[0,1].plot(weekly_df.index, weekly_df[col], color=colors[col], label=labels[col], linewidth=0.8)
axes[0,1].set_title('Weekly Mean')
axes[0,1].set_ylabel('Discharge (cfs)')
axes[0,1].set_xlabel('Date')

# Panel C - Monthly volumetric
for col in colors:
    axes[1,0].plot(monthly_df.index, monthly_df[col], color=colors[col], label=labels[col], linewidth=0.8)
axes[1,0].set_title('Monthly Volume')
axes[1,0].set_ylabel('Volume (acre-feet)')
axes[1,0].set_xlabel('Date')

# Panel D - Legend only
axes[1,1].axis('off')
handles, lbls = axes[0,0].get_legend_handles_labels()
axes[1,1].legend(handles, lbls, loc='center', fontsize=12, title='Stream Gauges', title_fontsize=13)
axes[1,1].set_title('Panel D: Legend')

plt.tight_layout()
plt.show()

#Analysis:
# Timing - peak flow day of year for each stream
print("Peak DOY (daily data):")
print("Reservoir:  ", merged_df['discharge_reservoir'].idxmax().dayofyear)
print("Headwater:  ", merged_df['discharge_headwater'].idxmax().dayofyear)
print("Uinta River:", merged_df['discharge_uinta_river'].idxmax().dayofyear)
print("Ashley Creek:", merged_df['discharge_ashley_creek'].idxmax().dayofyear)

# Magnitude - basic stats for each stream
print("\nMean discharge (cfs):")
print(merged_df.mean().round(1))

print("\nMax discharge (cfs):")
print(merged_df.max().round(1))

# Resampling comparison - how weekly smoothing changes the picture
print("\nWeekly mean - overall mean per stream:")
print(weekly_df.mean().round(1))

# Monthly volume totals across all years
print("\nMonthly volume - total across record (acre-feet):")
print("Reservoir:  ", reservoir_monthly['discharge_reservoir'].sum().round(0))
print("Headwater:  ", headwaters_monthly['discharge_headwater'].sum().round(0))
print("Uinta River:", uinta_river_monthly['discharge_uinta_river'].sum().round(0))
print("Ashley Creek:", ashley_creek_monthly['discharge_ashley_creek'].sum().round(0))

#Wet and dry year analysis 
#Wet and dry year analysis
#Based on annual volumetric totals: 2023 = wet year, 2021 = dry year
#Locations: Strawberry River (below reservoir), Yellowstone River (headwater)
#Wet and dry year analysis
#Based on annual volumetric totals: 2023 = wet year, 2021 = dry year
#Locations: Strawberry River (below reservoir), Yellowstone River (headwater)

def to_water_year_doy(dates):
    doy = []
    for d in dates:
        if d.month >= 10:
            start = pd.Timestamp(f'{d.year}-10-01', tz=d.tzinfo)
        else:
            start = pd.Timestamp(f'{d.year-1}-10-01', tz=d.tzinfo)
        doy.append((d - start).days + 1)
    return doy

def filter_water_year(df, water_year):
    start = pd.Timestamp(f'{water_year-1}-10-01', tz='UTC')
    end = pd.Timestamp(f'{water_year}-09-30', tz='UTC')
    return df.loc[start:end].copy()

wet_year = 2023
dry_year = 2021

# Filter by water year
res_wet  = filter_water_year(reservoir_gauge, wet_year)
res_dry  = filter_water_year(reservoir_gauge, dry_year)
head_wet = filter_water_year(headwater_gauge, wet_year)
head_dry = filter_water_year(headwater_gauge, dry_year)

# Assign water year DOY as index
for df in [res_wet, res_dry, head_wet, head_dry]:
    df.index = to_water_year_doy(df.index)

# Build envelope using water year DOY
def get_doy_envelope(gauge_df, col):
    tmp = pd.DataFrame({
        'doy': to_water_year_doy(gauge_df.index),
        'value': gauge_df[col].values
    })
    return tmp.groupby('doy')['value'].agg(['min', 'max', 'mean'])

res_envelope  = get_doy_envelope(reservoir_gauge, 'discharge_reservoir')
head_envelope = get_doy_envelope(headwater_gauge, 'discharge_headwater')

# Plotting function
def plot_flow(ax, envelope, target, col, target_year, year_type, color, title):
    ax.fill_between(envelope.index, envelope['min'], envelope['max'],
                    alpha=0.2, color=color, label='Min/Max range (all years)')
    ax.plot(envelope.index, envelope['mean'],
            color=color, linewidth=1.2, linestyle='--', label='Mean (all years)')
    ax.plot(target.index, target[col],
            color=color, linewidth=2, label=f'{target_year} ({year_type} year)')
    ax.set_title(title)
    ax.set_xlabel('Day of Water Year (Oct 1 = Day 1)')
    ax.set_ylabel('Discharge (cfs)')
    ax.legend(fontsize=8)

# Wet year figure
fig, axes = plt.subplots(1, 2, figsize=(14, 5))
fig.suptitle(f'Wet Year (WY{wet_year}) — Daily Flow with Min/Max Range', fontsize=13)

plot_flow(axes[0], res_envelope, res_wet, 'discharge_reservoir',
          wet_year, 'Wet', 'blue', 'Strawberry River (Below Reservoir)')
plot_flow(axes[1], head_envelope, head_wet, 'discharge_headwater',
          wet_year, 'Wet', 'green', 'Yellowstone River (Headwater)')

plt.tight_layout()
plt.show()

# Dry year figure
fig, axes = plt.subplots(1, 2, figsize=(14, 5))
fig.suptitle(f'Dry Year (WY{dry_year}) — Daily Flow with Min/Max Range', fontsize=13)

plot_flow(axes[0], res_envelope, res_dry, 'discharge_reservoir',
          dry_year, 'Dry', 'blue', 'Strawberry River (Below Reservoir)')
plot_flow(axes[1], head_envelope, head_dry, 'discharge_headwater',
          dry_year, 'Dry', 'green', 'Yellowstone River (Headwater)')

plt.tight_layout()
plt.show()

# Peak flow timing
print("Reservoir peak Water Year DOY:", res_wet['discharge_reservoir'].idxmax(), "(wet)", res_dry['discharge_reservoir'].idxmax(), "(dry)")
print("Headwater peak Water Year DOY:", head_wet['discharge_headwater'].idxmax(), "(wet)", head_dry['discharge_headwater'].idxmax(), "(dry)")
print("Reservoir peak DOY:", res_wet['discharge_reservoir'].idxmax(), "(wet)", res_dry['discharge_reservoir'].idxmax(), "(dry)")
print("Headwater peak DOY:", head_wet['discharge_headwater'].idxmax(), "(wet)", head_dry['discharge_headwater'].idxmax(), "(dry)")
print(res_dry.index.min())
print(res_dry.index.max())


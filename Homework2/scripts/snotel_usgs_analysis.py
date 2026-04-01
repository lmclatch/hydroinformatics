import os
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import os
import pandas as pd
import matplotlib.dates as mdates

#Load data
snotel_data = pd.read_csv('data/snotel_data.csv')
snotel_data['datetime'] = pd.to_datetime(snotel_data['datetime'])
#Clip to WY 2021-2025
snotel_data = snotel_data[(snotel_data['datetime'] >= '2021-10-01') & (snotel_data['datetime'] <= '2025-09-30')]
#Convert meters to ft for SWE
snotel_data['WTEQ_ft'] = snotel_data['WTEQ'] * 3.28084

#### Adapted from Ryan's SNOTEL.ipynb

# ── Config ────────────────────────────────────────────────────────────────────
SITE_NAME        = 'Indpedence Mine SNOTEL'  # For plot titles and filenames
WATERSHED        = 'Little Susitna River'    # For plot titles and filenames
WATER_YEARS      = [2021, 2022, 2023, 2024, 2025]
 
# ── Add water year and MM-DD columns ──────────────────────────────────────────
snotel_data['WY']    = snotel_data['datetime'].apply(
    lambda dt: dt.year + 1 if dt.month >= 10 else dt.year)
snotel_data['MM-DD'] = snotel_data['datetime'].dt.strftime('%m-%d')
 
# ── Pivot to wide format (index = MM-DD, columns = water year) ────────────────
pivot = snotel_data.pivot_table(index='MM-DD', columns='WY',
                                values='WTEQ_ft', aggfunc='mean')
 
# Sort index chronologically Oct -> Sep
months    = [f'{m:02d}' for m in list(range(10, 13)) + list(range(1, 10))]
day_order = [f'{m}-{d:02d}' for m in months for d in range(1, 32)
             if f'{m}-{d:02d}' in pivot.index]
pivot = pivot.reindex(day_order)
 
# ── Compute percentiles across all water years ────────────────────────────────
stats = pd.DataFrame(index=pivot.index)
stats['min']    = pivot.min(axis=1)
stats['Q10']    = pivot.quantile(0.10, axis=1)
stats['Q25']    = pivot.quantile(0.25, axis=1)
stats['median'] = pivot.median(axis=1)
stats['Q75']    = pivot.quantile(0.75, axis=1)
stats['Q90']    = pivot.quantile(0.90, axis=1)
stats['max']    = pivot.max(axis=1)
 
# ── Plot — one subplot per water year ─────────────────────────────────────────
opacity  = 0.25
n        = len(WATER_YEARS)
x        = range(len(stats))
 
fig, axes = plt.subplots(1, n, figsize=(5 * n, 6), sharey=True)
fig.suptitle(f'Snow Water Equivalent – {SITE_NAME} | {WATERSHED}',
             fontsize=13, fontweight='bold', y=1.01)
 
# x-axis tick positions (shared)
step           = max(1, len(stats) // 6)
tick_positions = list(range(0, len(stats), step))
tick_labels    = [stats.index[i] for i in tick_positions]
 
for ax, WY in zip(axes, WATER_YEARS):
 
    # Percentile bands
    ax.fill_between(x, stats['max'],  stats['Q90'], color='slateblue', alpha=opacity)
    ax.fill_between(x, stats['Q90'],  stats['Q75'], color='cyan',      alpha=opacity)
    ax.fill_between(x, stats['Q75'],  stats['Q25'], color='green',     alpha=opacity)
    ax.fill_between(x, stats['Q25'],  stats['Q10'], color='yellow',    alpha=opacity)
    ax.fill_between(x, stats['Q10'],  stats['min'], color='red',       alpha=opacity)
 
    # Stat lines
    ax.plot(x, stats['max'],    color='slateblue', linewidth=0.8)
    ax.plot(x, stats['median'], color='green',     linewidth=1.2)
    ax.plot(x, stats['min'],    color='red',       linewidth=0.8)
 
    # Current WY line
    if WY in pivot.columns:
        ax.plot(x, pivot[WY], color='black', linewidth=2, label=f'WY {WY}')
    else:
        ax.text(0.5, 0.5, 'No Data', transform=ax.transAxes,
                ha='center', va='center', fontsize=11, color='gray')
 

    # x-axis ticks
    ax.set_xticks(tick_positions)
    ax.set_xticklabels(tick_labels, rotation=45, ha='right', fontsize=7)
    ax.set_title(f'WY {WY}', fontweight='bold')
    ax.set_xlabel('Date (MM-DD)', fontsize=8)
 
    # Peak SWE text box
    if WY in pivot.columns:
        wy_series = pivot[WY].dropna()
        if not wy_series.empty:
            peak_val    = wy_series.max()
            peak_day    = wy_series.idxmax()
            textstr     = f"Peak SWE: {peak_val:.2f} ft\n{WY}-{peak_day}"
            props       = dict(boxstyle='round', facecolor='white', alpha=0.6)
            ax.text(0.03, 0.97, textstr, transform=ax.transAxes, fontsize=8,
                    verticalalignment='top', bbox=props, family='monospace')
 
axes[0].set_ylabel('SWE (ft)', fontsize=9)
 
# ── Shared legend ─────────────────────────────────────────────────────────────
legend_elements = [
    mpatches.Patch(color='slateblue', alpha=0.6,  label='Q90–Max'),
    mpatches.Patch(color='cyan',      alpha=0.6,  label='Q75–Q90'),
    mpatches.Patch(color='green',     alpha=0.6,  label='Q25–Q75'),
    mpatches.Patch(color='yellow',    alpha=0.6,  label='Q10–Q25'),
    mpatches.Patch(color='red',       alpha=0.6,  label='Min–Q10'),
    plt.Line2D([0], [0], color='green',     linewidth=1.2, label='Median'),
    plt.Line2D([0], [0], color='black',     linewidth=2,   label='Water Year'),
    #plt.Line2D([0], [0], color='black',     linewidth=1, linestyle='--', label=f'DOI {DATE_OF_INTEREST}'),
]
fig.legend(handles=legend_elements, loc='lower center', ncol=8,
           bbox_to_anchor=(0.5, -0.08), fontsize=8, frameon=True)
 
plt.tight_layout()
 
os.makedirs('Figures', exist_ok=True)
fig.savefig(f"Figures/{SITE_NAME.replace(' ', '_')}_WY2021-2025_snotelanalysis.png",
            dpi=300, bbox_inches='tight')
plt.show()
 

#USGS Analysis
usgs_data = pd.read_csv('data/streamflow_data.csv')
#Plot USGS streamflow data:April, May, June, July, August, and September
usgs_data['datetime'] = pd.to_datetime(usgs_data['datetime'])
usgs_data['month'] = usgs_data['datetime'].dt.month
usgs_data['year'] = usgs_data['datetime'].dt.year  # ← add this here

#Create an April dataframe
usgs_april = usgs_data[usgs_data['month'] == 4]
print(usgs_april.tail())
#May dataframe
usgs_may = usgs_data[usgs_data['month'] == 5]
print(usgs_may.tail())

#June dataframe
usgs_june = usgs_data[usgs_data['month'] == 6]
print(usgs_june.tail())

#July dataframe
usgs_july = usgs_data[usgs_data['month'] == 7]
print(usgs_july.tail())

#August dataframe
usgs_august = usgs_data[usgs_data['month'] == 8]
print(usgs_august.tail())

#September dataframe
usgs_september = usgs_data[usgs_data['month'] == 9]
print(usgs_september.tail())

#Subplot for each month


fig, axes = plt.subplots(2, 3, figsize=(18, 12), sharey=True)
fig.suptitle('Streamflow for USGS-15290000: Little Susitna River, Palmer AK by Month')

#make y axis all the same for comparability 
ymin = 0
ymax = 4000

#Coloring for each month
month_data = [
    (usgs_april, 'April', 'lightblue'),
    (usgs_may, 'May', 'green'),
    (usgs_june, 'June', 'orange'),
    (usgs_july, 'July', 'pink'),
    (usgs_august, 'August', 'purple'),
    (usgs_september, 'September', 'brown')
]

#Plotting code for each month
for ax, (df, month, color) in zip(axes.flat, month_data):
    ax.plot(df['datetime'], df['streamflow (cfs)'], color=color)
    ax.set_title(month)
    ax.set_ylim(ymin, ymax)
    ax.xaxis.set_major_locator(mdates.YearLocator(5))
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
    ax.tick_params(axis='x', labelrotation=0)

# Only left column gets y-label
axes[0, 0].set_ylabel('Streamflow (cfs)')
axes[1, 0].set_ylabel('Streamflow (cfs)')

# Only bottom row gets x-label
axes[1, 0].set_xlabel('Year')
axes[1, 1].set_xlabel('Year')
axes[1, 2].set_xlabel('Year')

# Hide year numbers on the top row
for ax in axes[0, :]:
    ax.tick_params(axis='x', labelbottom=False)

plt.subplots_adjust(wspace=0.25, hspace=0.3)
plt.tight_layout()
plt.savefig('Figures/usgs_streamflow_by_month.png')
plt.show()

#Peak SWE parity plots for April, May, June, July, August, and September streamflow
#Calculate Peak SWE per Year
snotel_data['year'] = snotel_data['datetime'].dt.year
peak_swe = snotel_data.groupby('year')['WTEQ_ft'].max().reset_index()
print(peak_swe.head())

#Calc cummulative streamflow for each month of interest from 2021-2025
usgs_filtered = usgs_data[(usgs_data['year'] >= 2021) & (usgs_data['year'] <= 2025)]
 
months_of_interest = [4, 5, 6, 7, 8, 9] 
month_names = {4: 'April', 5: 'May', 6: 'June', 7: 'July', 8: 'August', 9: 'September'}
 
cumulative_flow = usgs_filtered.groupby(['year', 'month'])['streamflow (cfs)'].sum().reset_index()
cumulative_flow.columns = ['year', 'month', 'cumulative_cfs']
 
# ── Peak SWE per water year ────────────────────────────────────────────────────
snotel_data['WY'] = snotel_data['datetime'].apply(
    lambda dt: dt.year + 1 if dt.month >= 10 else dt.year)
peak_swe = snotel_data.groupby('WY')['WTEQ_ft'].max().reset_index()
peak_swe.columns = ['year', 'peak_swe_ft']
 
# ── Merge peak SWE with cumulative streamflow ──────────────────────────────────
parity_df = cumulative_flow.merge(peak_swe, on='year')
 
# ── Parity scatter plots — one per month ──────────────────────────────────────
fig, axes = plt.subplots(2, 3, figsize=(15, 10))
fig.suptitle('Peak SWE vs. Cumulative Monthly Streamflow (WY 2021–2025)',
             fontsize=13, fontweight='bold')
 
month_colors = {4: 'lightblue', 5: 'green', 6: 'orange',
                7: 'pink',      8: 'purple', 9: 'brown'}
 
for ax, month in zip(axes.flat, months_of_interest):
    df_month = parity_df[parity_df['month'] == month]
 
    ax.scatter(df_month['peak_swe_ft'], df_month['cumulative_cfs'],
               color=month_colors[month], edgecolors='black', s=80, zorder=3)
 
    # Label each point with the year
    for _, row in df_month.iterrows():
        ax.annotate(str(int(row['year'])),
                    xy=(row['peak_swe_ft'], row['cumulative_cfs']),
                    xytext=(4, 4), textcoords='offset points', fontsize=8)
 
    ax.set_title(month_names[month], fontweight='bold')
    ax.set_xlabel('Peak SWE (ft)')
    ax.set_ylabel('Cumulative Streamflow (cfs)')
    ax.grid(True, linestyle='--', alpha=0.5)
 
plt.tight_layout()
plt.savefig('Figures/usgs_parity_plots.png', dpi=300, bbox_inches='tight')
plt.show()

#check out april 1st stats
# check out april 1st stats
april1_swe = snotel_data[snotel_data['MM-DD'] == '04-01']['WTEQ_ft']
print(f"Median April 1st SWE (WY 2021-2025): {april1_swe.median():.2f} ft")

april1_2025_swe = snotel_data[(snotel_data['MM-DD'] == '04-01') & (snotel_data['year'] == 2025)]['WTEQ_ft']
print(f"April 1st SWE in WY 2025: {april1_2025_swe.values[0]:.2f} ft")

# Median April 1st streamflow (2021-2025)
april1_flow = usgs_filtered[(usgs_filtered['month'] == 4) & (usgs_filtered['datetime'].dt.day == 1)]['streamflow (cfs)']
print(f"Median April 1st streamflow (2021-2025): {april1_flow.median():,.0f} cfs")

april1_2025_flow = usgs_filtered[(usgs_filtered['month'] == 4) & (usgs_filtered['datetime'].dt.day == 1) & (usgs_filtered['year'] == 2025)]['streamflow (cfs)']
print(f"April 1st streamflow in 2025: {april1_2025_flow.values[0]:,.0f} cfs")
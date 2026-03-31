
import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
from shapely.geometry import Point

# -----------------------------
# 1. StreamStats De;inated Basin for USGS Gage 15276000
# -----------------------------
geojson_path = r"C:\Users\Liza\Downloads\data (1).geojson"

# -----------------------------
# 2. Coordinates!
# -----------------------------
# USGS gage
lat_usgs = 61.70973581374065
lon_usgs = -149.23196347225957

# SNOTEL
lat_snotel = 61.79
lon_snotel = -149.28

# Load basin
basin = gpd.read_file(geojson_path)

if basin.crs is None:
    basin = basin.set_crs("EPSG:4326")

# Create points
points_df = pd.DataFrame({
    "site": ["USGS Gage", "SNOTEL"],
    "lat": [lat_usgs, lat_snotel],
    "lon": [lon_usgs, lon_snotel]
})

points_gdf = gpd.GeoDataFrame(
    points_df,
    geometry=[Point(xy) for xy in zip(points_df["lon"], points_df["lat"])],
    crs="EPSG:4326"
)

# Reproject to Alaska Albers
basin_ak = basin.to_crs("EPSG:3338")
points_ak = points_gdf.to_crs("EPSG:3338")

# Split into two layers
usgs_point = points_ak[points_ak["site"] == "USGS Gage"]
snotel_point = points_ak[points_ak["site"] == "SNOTEL"]

# Plot
fig, ax = plt.subplots(figsize=(10, 10))

basin_ak.plot(ax=ax, color="lightblue", edgecolor="black", alpha=0.5)
usgs_point.plot(ax=ax, markersize=90, color="purple", label="USGS Gage")
snotel_point.plot(ax=ax, markersize=90, color="pink", label="SNOTEL")

# Labels
for x, y, label in zip(points_ak.geometry.x, points_ak.geometry.y, points_ak["site"]):
    ax.text(x, y, label, fontsize=9, ha="right", va="bottom")

ax.set_title("Delinated USGS Watershed and Point Locations", fontsize=14)
ax.set_axis_off()
#ax.legend()

plt.show()

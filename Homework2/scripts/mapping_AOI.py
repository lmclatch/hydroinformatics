import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from shapely.geometry import Point
import contextily as ctx

# -----------------------------
# 1. StreamStats Delineated Basin for USGS Gage 15276000
# -----------------------------
geojson_path = r"C:\Users\Liza\Downloads\data (1).geojson"

# -----------------------------
# 2. Coordinates
# -----------------------------
lat_usgs   = 61.70973581374065
lon_usgs   = -149.23196347225957
lat_snotel = 61.79
lon_snotel = -149.28

# Load basin
basin = gpd.read_file(geojson_path)
if basin.crs is None:
    basin = basin.set_crs("EPSG:4326")

# Create points
points_df = pd.DataFrame({
    "site": ["USGS Gage", "SNOTEL"],
    "lat":  [lat_usgs, lat_snotel],
    "lon":  [lon_usgs, lon_snotel]
})
points_gdf = gpd.GeoDataFrame(
    points_df,
    geometry=[Point(xy) for xy in zip(points_df["lon"], points_df["lat"])],
    crs="EPSG:4326"
)

# Reproject to Web Mercator for contextily basemap
basin_wm  = basin.to_crs("EPSG:3857")
points_wm = points_gdf.to_crs("EPSG:3857")

# Keep WGS84 copy for lat/lon tick labels
basin_wgs  = basin.to_crs("EPSG:4326")
points_wgs = points_gdf  # already 4326

usgs_point   = points_wm[points_wm["site"] == "USGS Gage"]
snotel_point = points_wm[points_wm["site"] == "SNOTEL"]

# ── Plot ──────────────────────────────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(10, 10))

basin_wm.plot(ax=ax, color="lightblue", edgecolor="black", alpha=0.4, zorder=2)
usgs_point.plot(ax=ax, markersize=90, color="purple", label="USGS Gage", zorder=4)
snotel_point.plot(ax=ax, markersize=90, color="pink",   label="SNOTEL",   zorder=4)

# Point labels
for x, y, label in zip(points_wm.geometry.x, points_wm.geometry.y, points_wm["site"]):
    ax.annotate(label, xy=(x, y), xytext=(8, 8), textcoords="offset points",
                fontsize=9, fontweight='bold', ha="left", va="bottom")

# Basemap (OpenStreetMap)
ctx.add_basemap(ax, source=ctx.providers.OpenStreetMap.Mapnik, zoom=12, zorder=1)

# ── Lat/lon tick labels ───────────────────────────────────────────────────────
# Get current axis extent in Web Mercator, convert to WGS84 for labeling
from pyproj import Transformer
transformer = Transformer.from_crs("EPSG:3857", "EPSG:4326", always_xy=True)

xmin, xmax = ax.get_xlim()
ymin, ymax = ax.get_ylim()

# Generate ~5 evenly spaced ticks on each axis in Web Mercator
x_ticks_wm = [xmin + i * (xmax - xmin) / 4 for i in range(5)]
y_ticks_wm = [ymin + i * (ymax - ymin) / 4 for i in range(5)]

# Convert tick positions to lat/lon for labels
x_lons = [transformer.transform(x, (ymin + ymax) / 2)[0] for x in x_ticks_wm]
y_lats = [transformer.transform((xmin + xmax) / 2, y)[1] for y in y_ticks_wm]

ax.set_xticks(x_ticks_wm)
ax.set_yticks(y_ticks_wm)
ax.set_xticklabels([f"{lon:.3f}°W" if lon < 0 else f"{lon:.3f}°E" for lon in x_lons], fontsize=8)
ax.set_yticklabels([f"{lat:.3f}°N" if lat > 0 else f"{lat:.3f}°S" for lat in y_lats], fontsize=8)

ax.set_xlabel("Longitude", fontsize=10)
ax.set_ylabel("Latitude",  fontsize=10)
ax.set_title("Delineated USGS Watershed and Point Locations", fontsize=14)
ax.legend(loc="lower right")

plt.tight_layout()
plt.savefig("Figures/watershed_map.png", dpi=300, bbox_inches="tight")
plt.show()
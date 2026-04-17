"""
Study area map: Southcentral Alaska basins with USGS gauges.

Reads each StreamStats GeoJSON and overlays on a basemap using contextily.
Gauge coordinates retrieved from USGS Water Data for the Nation
(https://waterdata.usgs.gov/) — WGS84 decimal degrees.
"""

import geopandas as gpd
import matplotlib.pyplot as plt
import contextily as cx
import pandas as pd


# ---- configuration ---------------------------------------------------------
BASINS = {
    "Little Susitna": {
        "file":     "data/littlesu_streamstats.geojson",
        "gauge_id": "15290000",
        "lat":      61.70973581,
        "lon":     -149.23196347,
    },
    "Matanuska": {
        "file":     "data/manatuska_streamstats.geojson",
        "gauge_id": "15284000",
        "lat":      61.60862507,
        "lon":     -149.07306388,
    },
    "Ship Creek": {
        "file":     "data/shipcreek_streamstats.geojson",
        "gauge_id": "15276000",
        "lat":      61.22555600,
        "lon":     -149.63500000,
    },
    "Campbell Creek": {
        "file":     "data/campbellcreek_streamstats.geojson",
        "gauge_id": "15274600",
        "lat":      61.13944400,
        "lon":     -149.92333300,
    },
}

# one color per basin
COLORS = {
    "Little Susitna": "#1f77b4",
    "Matanuska":      "#d62728",
    "Ship Creek":     "#2ca02c",
    "Campbell Creek": "#ff7f0e",
}


# ---- load all basins into one GeoDataFrame --------------------------------
basins_list = []
gauges_list = []

for name, info in BASINS.items():
    gdf = gpd.read_file(info["file"]).to_crs("EPSG:4326")
    # keep only the polygon (drop any point/line features if present)
    gdf = gdf[gdf.geometry.geom_type.isin(["Polygon", "MultiPolygon"])].copy()
    gdf["basin_name"] = name
    gdf["gauge_id"]   = info["gauge_id"]
    basins_list.append(gdf[["basin_name", "gauge_id", "geometry"]])

    gauges_list.append({"basin_name": name, "gauge_id": info["gauge_id"],
                        "lat": info["lat"], "lon": info["lon"]})
    print(f"✓ {name:16s} gauge {info['gauge_id']} at "
          f"({info['lat']:.4f}, {info['lon']:.4f})")

basins = pd.concat(basins_list, ignore_index=True)
basins = gpd.GeoDataFrame(basins, geometry="geometry", crs="EPSG:4326")
gauges = gpd.GeoDataFrame(
    gauges_list,
    geometry=gpd.points_from_xy([g["lon"] for g in gauges_list],
                                 [g["lat"] for g in gauges_list]),
    crs="EPSG:4326"
)

# ---- reproject to Web Mercator for the basemap ----------------------------
basins_wm = basins.to_crs(epsg=3857)
gauges_wm = gauges.to_crs(epsg=3857)


# ---- plot -----------------------------------------------------------------
fig, ax = plt.subplots(figsize=(11, 9))

# basin polygons — colored outlines with light fills
for name in BASINS.keys():
    sub = basins_wm[basins_wm["basin_name"] == name]
    sub.plot(ax=ax, facecolor=COLORS[name], alpha=0.30,
             edgecolor=COLORS[name], linewidth=2, label=name)

# gauge locations — gold stars
gauges_wm.plot(ax=ax, marker="*", color="gold", edgecolor="black",
               markersize=320, linewidth=1.2, zorder=5, label="USGS gauge")

# label each gauge with its ID
for _, row in gauges_wm.iterrows():
    ax.annotate(row["gauge_id"],
                xy=(row.geometry.x, row.geometry.y),
                xytext=(10, 8), textcoords="offset points",
                fontsize=9, fontweight="bold",
                bbox=dict(boxstyle="round,pad=0.3", fc="white",
                          ec="gray", alpha=0.85))

# basemap (CartoDB Positron is clean and light; won't fight colored polygons)
cx.add_basemap(ax, source=cx.providers.CartoDB.Positron, zoom=9)

ax.set_axis_off()
ax.set_title("Study Area: Southcentral Alaska Basins",
             fontsize=14, fontweight="bold", pad=12)
ax.legend(loc="lower left", fontsize=10, frameon=True,
          facecolor="white", edgecolor="gray")

plt.tight_layout()
plt.savefig("study_area_map.png", dpi=200, bbox_inches="tight")
plt.show()
print("\nSaved → study_area_map.png")
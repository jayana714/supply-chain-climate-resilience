import numpy as np
import pandas as pd
import pystac_client
import planetary_computer
import rioxarray

from state_centroids import STATE_CENTROIDS

catalog = pystac_client.Client.open(
    "https://planetarycomputer.microsoft.com/api/stac/v1",
    modifier=planetary_computer.sign_inplace,
)

NDVI_SCALE = 0.0001
FILL_VALUE = -3000
BBOX_PAD = 0.5  # degrees around each state centroid

def get_mean_ndvi(lat, lon, datetime_range):
    bbox = [lon - BBOX_PAD, lat - BBOX_PAD, lon + BBOX_PAD, lat + BBOX_PAD]
    try:
        search = catalog.search(
            collections=["modis-13A1-061"],
            bbox=bbox,
            datetime=datetime_range,
        )
        items = list(search.items())
        if not items:
            return None

        item = items[0]
        href = item.assets["500m_16_days_NDVI"].href

        da = rioxarray.open_rasterio(href)
        clipped = da.rio.clip_box(*bbox, crs="EPSG:4326")
        values = clipped.values.astype(float)
        values[values == FILL_VALUE] = np.nan
        ndvi = values * NDVI_SCALE
        mean_ndvi = np.nanmean(ndvi)
        return round(float(mean_ndvi), 4) if not np.isnan(mean_ndvi) else None
    except Exception as e:
        print(f"  Error: {e}")
        return None

results = []
for fips, (lat, lon) in STATE_CENTROIDS.items():
    print(f"Processing state_fips={fips}...")
    current = get_mean_ndvi(lat, lon, "2026-06-01/2026-07-31")
    baseline = get_mean_ndvi(lat, lon, "2020-06-01/2020-07-31")
    anomaly = (current - baseline) if (current is not None and baseline is not None) else None
    results.append({
        "state_fips": fips,
        "ndvi_current": current,
        "ndvi_baseline_2020": baseline,
        "ndvi_anomaly": anomaly,
    })

df = pd.DataFrame(results)
df.to_csv("raw/modis_ndvi_by_state.csv", index=False)
print("\nSaved to raw/modis_ndvi_by_state.csv")
print(df)
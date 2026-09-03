import pystac_client
import planetary_computer
import rioxarray
import numpy as np
import matplotlib.pyplot as plt

catalog = pystac_client.Client.open(
    "https://planetarycomputer.microsoft.com/api/stac/v1",
    modifier=planetary_computer.sign_inplace,
)

LOCATIONS = {
    "houston_tx": [-95.55, 29.60, -95.15, 29.95],
    "honolulu_hi": [-157.95, 21.20, -157.75, 21.40],
    "los_angeles_ca": [-118.45, 33.85, -118.05, 34.15],
}

def crop_to_landscape(arr, max_aspect=1.4):
    h, w = arr.shape[0], arr.shape[1]
    if h / w > max_aspect:
        new_h = int(w * max_aspect)
        start = (h - new_h) // 2
        arr = arr[start:start + new_h, :]
    return arr

for name, bbox in LOCATIONS.items():
    print(f"Computing NDVI for {name}...")
    search = catalog.search(
        collections=["sentinel-2-l2a"],
        bbox=bbox,
        datetime="2025-01-01/2026-07-31",
        query={"eo:cloud_cover": {"lt": 15}},
    )
    items = list(search.items())
    if not items:
        print(f"  No scenes found for {name}, skipping.")
        continue
    items.sort(key=lambda i: i.properties.get("eo:cloud_cover", 100))

    saved = False
    for item in items[:8]:
        try:
            red_href = item.assets["B04"].href  # red band
            nir_href = item.assets["B08"].href  # near-infrared band

            red = rioxarray.open_rasterio(red_href).rio.clip_box(*bbox, crs="EPSG:4326")
            nir = rioxarray.open_rasterio(nir_href).rio.clip_box(*bbox, crs="EPSG:4326")

            red_arr = red.values[0].astype(float)
            nir_arr = nir.values[0].astype(float)

            valid_fraction = ((red_arr > 0) & (nir_arr > 0)).mean()
            if valid_fraction < 0.85:
                print(f"  Scene {item.id[:40]}... only {valid_fraction:.0%} covered, trying next...")
                continue

            with np.errstate(divide="ignore", invalid="ignore"):
                ndvi = (nir_arr - red_arr) / (nir_arr + red_arr)
            ndvi = np.clip(ndvi, -1, 1)
            ndvi = crop_to_landscape(ndvi)

            fig, ax = plt.subplots(figsize=(10, 8))
            im = ax.imshow(ndvi, cmap="RdYlGn", vmin=-0.2, vmax=0.8)
            ax.set_title(f"NDVI - {name.replace('_', ' ').title()}")
            ax.axis("off")
            plt.colorbar(im, ax=ax, label="NDVI (vegetation health)")
            out_path = f"docs/ndvi_{name}.png"
            plt.savefig(out_path, dpi=150, bbox_inches="tight")
            plt.close(fig)

            print(f"  Saved {out_path} (cloud: {item.properties.get('eo:cloud_cover'):.1f}%, coverage: {valid_fraction:.0%})")
            saved = True
            break
        except Exception as e:
            print(f"  Error with scene: {e}")
            continue

    if not saved:
        print(f"  Could not compute NDVI for {name}.")

print("\nDone.")
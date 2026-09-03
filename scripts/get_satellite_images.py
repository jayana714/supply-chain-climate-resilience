import pystac_client
import planetary_computer
import rioxarray
import numpy as np
from PIL import Image

catalog = pystac_client.Client.open(
    "https://planetarycomputer.microsoft.com/api/stac/v1",
    modifier=planetary_computer.sign_inplace,
)

LOCATIONS = {
    "houston_tx": [-95.55, 29.60, -95.15, 29.95],
    "honolulu_hi": [-157.95, 21.20, -157.75, 21.40],
    "los_angeles_ca": [-118.45, 33.85, -118.05, 34.15],
}

MIN_VALID_FRACTION = 0.85  # scene must cover at least 85% of the box to be accepted

for name, bbox in LOCATIONS.items():
    print(f"Searching for {name}...")
    search = catalog.search(
        collections=["sentinel-2-l2a"],
        bbox=bbox,
        datetime="2025-01-01/2026-07-31",
        query={"eo:cloud_cover": {"lt": 15}},
    )
    items = list(search.items())
    if not items:
        print(f"  No low-cloud scenes found for {name}, skipping.")
        continue

    items.sort(key=lambda i: i.properties.get("eo:cloud_cover", 100))

    saved = False
    for item in items[:8]:
        try:
            href = item.assets["visual"].href
            da = rioxarray.open_rasterio(href)
            clipped = da.rio.clip_box(*bbox, crs="EPSG:4326")
            arr = np.transpose(clipped.values, (1, 2, 0))

            valid_fraction = (arr.sum(axis=-1) > 0).mean()

            if valid_fraction < MIN_VALID_FRACTION:
                print(f"  Scene {item.id[:40]}... only {valid_fraction:.0%} covered, trying next...")
                continue

            arr = np.clip(arr, 0, 255).astype(np.uint8)
            img = Image.fromarray(arr)
            out_path = f"docs/satellite_{name}.png"
            img.save(out_path)
            print(f"  Saved {out_path} (cloud: {item.properties.get('eo:cloud_cover'):.1f}%, coverage: {valid_fraction:.0%})")
            saved = True
            break
        except Exception as e:
            print(f"  Error with scene: {e}")
            continue

    if not saved:
        print(f"  Could not find a fully-covered scene for {name}.")

print("\nDone.")
import pystac_client
import planetary_computer

catalog = pystac_client.Client.open(
    "https://planetarycomputer.microsoft.com/api/stac/v1",
    modifier=planetary_computer.sign_inplace,
)

# Texas centroid, a small bounding box around it
bbox = [-98.06, 30.80, -97.06, 31.80]

search = catalog.search(
    collections=["modis-13A1-061"],
    bbox=bbox,
    datetime="2025-07-01/2025-07-31",
)

items = list(search.items())
print(f"Found {len(items)} MODIS items for Texas, July 2025")

if items:
    item = items[0]
    print("\nItem ID:", item.id)
    print("\nAvailable assets:")
    for key, asset in item.assets.items():
        print(f"  {key}: {asset.title}")
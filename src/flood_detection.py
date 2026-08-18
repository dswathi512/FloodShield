import ee
import config as c
from . import data_fetch as d
import geopandas as gpd
def detect_floods():
    """Detect newly flooded pixels by comparing before/after Sentinel-1 VH imagery,
    excluding permanent water bodies using the JRC Global Surface Water dataset."""

    # Fetch two real, comparable radar composites of the same area — one from
    # before the event window, one from after (dates come from config.py)
    before_image,after_image=d.get_before_after_image()

    # Per-pixel change in radar echo strength between the two dates.
    # A pixel that turned into water shows a sharp drop (land echoes stronger
    # than water), while normal day-to-day noise stays small.
    diff=after_image.subtract(before_image)

    # How much of a drop counts as "likely flooded" — in decibels.
    # Tunable: lower threshold = more sensitive, but more false positives.
    threshold=7

    # Naive flood flag: True wherever the drop exceeds the threshold.
    # Note: use .lt(), not Python's "<" — plain comparison operators don't
    # work correctly on Earth Engine Image objects.
    mask=diff.lt(-threshold)

    # Reference dataset: how often each pixel has historically been water,
    # based on decades of satellite history (not something we compute ourselves).
    jrc=ee.Image("JRC/GSW1_4/GlobalSurfaceWater").select("occurrence")

    # Pixels that are water more than 90% of the time = permanent water
    # (rivers, lakes) — not new flooding, even if the diff looks similar.
    permanent_water=jrc.gt(90)

    # Hide permanent water pixels from the result entirely. This matters
    # because water surfaces aren't perfectly stable between two dates
    # (wind ripples, water-level changes, radar speckle noise), so the
    # threshold step alone can occasionally misflag a lake as "new flood".
    flood_mask=mask.updateMask(permanent_water.Not())
    return flood_mask

def get_flood_polygon(flood_mask):
    """Convert the flood mask to a GeoDataFrame of polygons for further analysis."""
    flood_vectors=flood_mask.reduceToVectors(
        geometry=c.AOI_CORDS,
        scale=30,
        geometryType='polygon',
        maxPixels=1e9
    )
    flood_geojson=flood_vectors.getInfo()
    flood_gdf=gpd.GeoDataFrame.from_features(flood_geojson['features'])
    flood_polygon=flood_gdf.geometry.unary_all
    return flood_polygon
if __name__ == "__main__":
    mask = detect_floods()
    print("Mask band Names:", mask.bandNames().getInfo())

    aoi = ee.Geometry.Rectangle(c.AOI_CORDS)
    vis_params = {'min': 0, 'max': 1, 'palette': ['black', 'white'], 'dimensions': 512, 'region': aoi}
    url = mask.getThumbURL(vis_params)
    print(url)

    import urllib.request
    urllib.request.urlretrieve(url, 'flood_mask_check.png')
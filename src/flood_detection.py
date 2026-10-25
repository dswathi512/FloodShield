import ee
import config as c
from . import data_fetch as d
import geopandas as gpd


def detect_floods(before_image=None, after_image=None):
    """Return a mask where only flooded pixels exist (value 1); everything else is masked out."""
    aoi = ee.Geometry.Rectangle(c.AOI_CORDS)
    if before_image is None or after_image is None:
        before_image, after_image = d.get_before_after_image()

    diff = after_image.subtract(before_image)
    flood = diff.lt(-c.THRESHOLD_DB)

    # Remove permanent water (rivers, lakes)
    jrc = ee.Image("JRC/GSW1_4/GlobalSurfaceWater").select("occurrence")
    permanent_water = jrc.gt(c.PERMANENT_WATER_MIN).unmask(0)
    flood = flood.updateMask(permanent_water.Not())

    # KEY FIX: keep ONLY the flooded pixels (drop the 0s)
    flood = flood.selfMask()

    # Drop tiny isolated specks (likely radar noise)
    connected = flood.connectedPixelCount(maxSize=100, eightConnected=True)
    flood = flood.updateMask(connected.gte(c.MIN_PATCH_PIXELS))

    return flood.clip(aoi)


def get_flood_polygon(flood_mask):
    """Convert flooded pixels into one merged polygon. Returns None if nothing is flooded."""
    aoi = ee.Geometry.Rectangle(c.AOI_CORDS)
    vectors = flood_mask.reduceToVectors(
        geometry=aoi,
        scale=30,
        geometryType='polygon',
        maxPixels=1e9,
        bestEffort=True
    )
    features = vectors.getInfo()['features']
    if not features:
        return None
    gdf = gpd.GeoDataFrame.from_features(features, crs='EPSG:4326')
    return gdf.geometry.union_all()


if __name__ == "__main__":
    mask = detect_floods()
    aoi = ee.Geometry.Rectangle(c.AOI_CORDS)
    vis = {'min': 0, 'max': 1, 'palette': ['red'], 'dimensions': 512, 'region': aoi}
    import urllib.request
    urllib.request.urlretrieve(mask.getThumbURL(vis), 'flood_check.png')
    print("Saved flood_check.png")
import ee
import config as c
from . import data_fetch as d

from . import flood_detection as fd

flood = fd.detect_floods()
jrc = ee.Image("JRC/GSW1_4/GlobalSurfaceWater").select("occurrence")
aoi = ee.Geometry.Rectangle(c.AOI_CORDS)

print(jrc.updateMask(flood).reduceRegion(
    ee.Reducer.percentile([5, 25, 50, 75, 95]), aoi, 30,
    maxPixels=1e9, bestEffort=True).getInfo())

before, after = d.get_before_after_image()
diff = after.subtract(before)

# 1. How big are the changes at all?
pct = diff.reduceRegion(
    reducer=ee.Reducer.percentile([1, 5, 25, 50, 75, 95, 99]),
    geometry=aoi, scale=30, maxPixels=1e9, bestEffort=True
).getInfo()
print("Change in VH (dB), percentiles:", pct)

# 2. Where do pixels disappear?
jrc = ee.Image("JRC/GSW1_4/GlobalSurfaceWater").select("occurrence")
perm = jrc.gt(c.PERMANENT_WATER_MIN).unmask(0)

def count(img):
    return img.reduceRegion(
        ee.Reducer.sum(), aoi, 30, maxPixels=1e9, bestEffort=True
    ).getInfo()

print("threshold | raw flagged | after water mask | after patch filter")
for t in [2, 3, 4, 5, 6, 7]:
    raw = diff.lt(-t)
    masked = raw.updateMask(perm.Not()).selfMask()
    conn = masked.connectedPixelCount(100, True)
    filtered = masked.updateMask(conn.gte(c.MIN_PATCH_PIXELS))
    print(t, count(raw), count(masked), count(filtered))
import ee
import config as c
from . import data_fetch  # this import also runs ee.Initialize()

aoi = ee.Geometry.Rectangle(c.AOI_CORDS)

lake = ee.Geometry.Point([78.4740, 17.4239]).buffer(300)
jrc = ee.Image("JRC/GSW1_4/GlobalSurfaceWater").select("occurrence")

print(jrc.reduceRegion(
    ee.Reducer.percentile([5, 25, 50, 95]), lake, 30, maxPixels=1e9
).getInfo())

for name, s, e in [("before", c.BEFORE_START, c.BEFORE_END), ("after", c.AFTER_START, c.AFTER_END)]:
    col = (ee.ImageCollection('COPERNICUS/S1_GRD').filterBounds(aoi)
           .filterDate(s, e).filter(ee.Filter.eq('instrumentMode', 'IW')))
    print(name,
          col.aggregate_array('system:time_start').map(lambda t: ee.Date(t).format('YYYY-MM-dd HH:mm')).getInfo(),
          col.aggregate_array('orbitProperties_pass').getInfo(),
          col.aggregate_array('relativeOrbitNumber_start').getInfo())
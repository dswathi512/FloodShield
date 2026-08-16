import ee
import config as c
from . import data_fetch as d
def detect_floods():
    before_image,after_image=d.get_before_after_image()
    diff=after_image.subtract(before_image)
    threshold=7
    mask=diff.lt(-threshold)
    jrc=ee.Image("JRC/GSW1_4/GlobalSurfaceWater").select("occurrence")
    permanent_water=jrc.gt(90)
    flood_mask=mask.updateMask(permanent_water.Not())
    return flood_mask
if __name__ == "__main__":
    mask = detect_floods()
    print("Mask band Names:", mask.bandNames().getInfo())

    aoi = ee.Geometry.Rectangle(c.AOI_CORDS)
    vis_params = {'min': 0, 'max': 1, 'palette': ['black', 'white'], 'dimensions': 512, 'region': aoi}
    url = mask.getThumbURL(vis_params)
    print(url)

    import urllib.request
    urllib.request.urlretrieve(url, 'flood_mask_check.png')
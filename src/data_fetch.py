import ee
import config as c 
ee.Initialize(project=c.PROJECT_ID)
def get_before_after_image():
    aoi = ee.Geometry.Rectangle(c.AOI_CORDS)

    before_collection = (ee.ImageCollection('COPERNICUS/S1_GRD')
            .filterBounds(aoi)
            .filterDate(c.BEFORE_START, c.BEFORE_END)
            .filter(ee.Filter.eq('instrumentMode', 'IW'))
            .select('VH'))

    after_collection = (ee.ImageCollection('COPERNICUS/S1_GRD')
           .filterBounds(aoi)
           .filterDate(c.AFTER_START, c.AFTER_END)
           .filter(ee.Filter.eq('instrumentMode', 'IW'))
           .select('VH'))

    before_count = before_collection.size().getInfo()   # .size() on the COLLECTION, before converting
    after_count = after_collection.size().getInfo()

    if before_count == 0 or after_count == 0:
        raise ValueError(f"No images found — before: {before_count}, after: {after_count}")

    print(f"Found {before_count} images for before period and {after_count} images for after period")

    before_image = before_collection.median().focal_mean(radius=50, units='meters')
    after_image = after_collection.median().focal_mean(radius=50, units='meters')
    print(before_image.bandNames().getInfo())

    return before_image, after_image
if __name__=="__main__":
    """For testing whether the images are fetched correctly, you can run this script and it will print the band names of the before and after images."""
    before,after=get_before_after_image()
    print("Before Image Bands",before.bandNames().getInfo())
    print("After Image Bands",after.bandNames().getInfo())
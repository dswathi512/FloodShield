import ee
import config as c 
ee.Initialize(project=c.PROJECT_ID)
def get_before_after_image():
    """This function fetches the before and after images from the Sentinel-1 GRD collection based on the AOI and date ranges specified in the config file. It returns the median images for both periods. """
    aoi=ee.Geometry.Rectangle(c.AOI_CORDS)
    before=(ee.ImageCollection('COPERNICUS/S1_GRD')
            .filterBounds(aoi)
            .filterDate(c.BEFORE_START,c.BEFORE_END)
            .filter(ee.Filter.eq('instrumentMode','IW'))
            .select('VH'))
    after=(ee.ImageCollection('COPERNICUS/S1_GRD')
           .filterBounds(aoi)
           .filterDate(c.AFTER_START,c.AFTER_END)
           .filter(ee.Filter.eq('instrumentMode','IW'))
           .select('VH'))
    before_count=before.size().getInfo()
    after_count=after.size().getInfo()
    if (before_count==0 or after_count==0):
        raise ValueError(f" No images found for before period: {before_count}, after period: {after_count} ")
    print(f"Found {before_count} images for before period and {after_count} images for after period")
    return before.median(),after.median()
if __name__=="__main__":
    """For testing whether the images are fetched correctly, you can run this script and it will print the band names of the before and after images."""
    before,after=get_before_after_image()
    print("Before Image Bands",before.bandNames().getInfo())
    print("After Image Bands",after.bandNames().getInfo())
import ee
import urllib.request
import matplotlib.pyplot as plt
import matplotlib.image as mpimg

ee.Initialize(project='floodshield-504714')

aoi = ee.Geometry.Rectangle([78.30, 17.30, 78.60, 17.50])

collection = (ee.ImageCollection('COPERNICUS/S1_GRD')
              .filterBounds(aoi)
              .filterDate('2026-06-01', '2026-07-01')
              .filter(ee.Filter.eq('instrumentMode', 'IW')))

image = collection.first()
"""vv = image.select('VV').clip(aoi)

url = vv.getThumbURL({'min': -25, 'max': 0, 'dimensions': 512, 'region': aoi})
print(url)

urllib.request.urlretrieve(url, 'vv_image.png')

img = mpimg.imread('vv_image.png')
plt.imshow(img, cmap='gray')
plt.title('Sentinel-1 VV - Hyderabad')
plt.colorbar()
plt.show()"""

vis_params = {
    'bands': ['VV', 'VH', 'VV'],  # assign bands to R, G, B slots for viewing
    'min': -25,
    'max': 0,
    'dimensions': 512,
    'region': aoi
}

url = image.getThumbURL(vis_params)
print(url)

urllib.request.urlretrieve(url, 'combined_image.png')

img = mpimg.imread('combined_image.png')
plt.imshow(img)
plt.title('Sentinel-1 VV+VH combined - Hyderabad')
plt.show()
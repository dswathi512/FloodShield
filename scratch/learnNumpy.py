""""
import numpy as np
import matplotlib.pyplot as plt

image=np.array([[1,2,3],[4,5,6]])
plt.imshow(image,cmap='gray')
plt.colorbar()
plt.show()


grid1 = np.array([[0, 0, 0], [255, 255, 255]])
grid2 = np.array([[255, 255, 255], [0, 0, 0]])

plt.imshow(grid1, cmap='gray')
plt.title("Grid 1")
plt.show()

plt.imshow(grid2, cmap='gray')
plt.title("Grid 2")
plt.show()

import rasterio

dataset = rasterio.open('sample.tif')

print(dataset.width)
print(dataset.height)
print(dataset.count)
"""
import matplotlib.pyplot as plt
import rasterio

dataset = rasterio.open('sample.tif')
array = dataset.read()
""""
print(array.shape)

fig, axes = plt.subplots(1, 3)

axes[0].imshow(array[0], cmap='gray')
axes[0].set_title("Band 1 (Red)")

axes[1].imshow(array[1], cmap='gray')
axes[1].set_title("Band 2 (Green)")

axes[2].imshow(array[2], cmap='gray')
axes[2].set_title("Band 3 (Blue)")

plt.show()
diff = array[0].astype(int) - array[2].astype(int)  # Red minus Blue

plt.imshow(diff, cmap='gray')
plt.colorbar()
plt.title("Red minus Blue")
plt.show()

before = array[0][:400, :390]
after = array[0][:400, 390:780]

print(before.shape, after.shape)

diff = after.astype(int) - before.astype(int)

threshold = 30
change_mask = diff < -threshold  # big drop in brightness = "new water"

plt.subplot(1, 3, 1)
plt.imshow(before, cmap='gray')
plt.title("Before")

plt.subplot(1, 3, 2)
plt.imshow(after, cmap='gray')
plt.title("After")

plt.subplot(1, 3, 3)
plt.imshow(change_mask, cmap='gray')
plt.title("Detected change")

plt.show()

print("Flagged pixels:", change_mask.sum())
"""
red_band = array[0]  # just the first grid — remember, bands come first
print(red_band.shape)

import matplotlib.pyplot as plt
plt.imshow(red_band, cmap='gray')
plt.colorbar()
plt.show()
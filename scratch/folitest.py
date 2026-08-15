import folium
import config as c

west, south, east, north = c.AOI_CORDS

m = folium.Map(location=[(south + north) / 2, (west + east) / 2], zoom_start=11)

folium.Rectangle(
    bounds=[[south, west], [north, east]],
    color='red',
    fill=True,
    fill_opacity=0.1
).add_to(m)

m.save('aoi_check.html')
print("Saved aoi_check.html")
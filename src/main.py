from . import flood_detection as fd
from . import road_analysis as ra
from . import visualization as v
import config as c

flood_mask = fd.detect_floods()
roads = ra.get_roads()
affected_roads, total_km = ra.analyze_road_impact(roads, flood_mask)

print(f"Affected segments: {len(affected_roads)} of {len(roads)}")
print(f"Total flooded road length: {total_km:.2f} km")

west, south, east, north = c.AOI_CORDS

aoi_center = [
    (south + north) / 2,
    (west + east) / 2
]
dashboard = v.create_flood_dashboard(flood_mask, affected_roads, aoi_center)
dashboard.save('Floodshield_dashboard.html')
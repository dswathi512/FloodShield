from . import flood_detection as fd
from . import road_analysis as ra
from . import visualization as v

flood_mask = fd.detect_floods()
roads = ra.get_roads()
affected_roads, total_km = ra.analyze_road_impact(roads, flood_mask)

print(f"Affected segments: {len(affected_roads)} of {len(roads)}")
print(f"Total flooded road length: {total_km:.2f} km")

hyderabad_center = [17.4375, 78.4483]
dashboard = v.create_flood_dashboard(flood_mask, affected_roads, hyderabad_center)
dashboard.save('geoshield_dashboard.html')
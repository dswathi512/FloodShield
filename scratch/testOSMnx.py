"""from shapely.geometry import LineString, Polygon

# Pretend this is a road — just a straight line between two points
road = LineString([(0, 0), (10, 10)])

# Pretend this is a flooded area — a simple square
flood_zone = Polygon([(3, 3), (7, 3), (7, 7), (3, 7)])

# Does the road cross the flood zone at all?
print(road.intersects(flood_zone))

# What's the actual overlapping piece?
overlap = road.intersection(flood_zone)
print(overlap)

print("Length of road:", road.length)
print("Length of flooded portion:", overlap.length)"""
import geopandas as gpd
from shapely.geometry import LineString

data = {
    'name': ['Main Road', 'Ring Road', 'Side Street'],
    'road_type': ['primary', 'primary', 'residential'],
    'geometry': [
        LineString([(0, 0), (5, 5)]),
        LineString([(2, 8), (9, 8)]),
        LineString([(1, 1), (1, 6)])
    ]
}

roads = gpd.GeoDataFrame(data)
print(roads)
print(roads.geometry.length)
from shapely.geometry import Polygon

flood_zone = Polygon([(1, 2), (6, 2), (6, 9), (1, 9)])

roads['intersects_flood'] = roads.geometry.intersects(flood_zone)
roads['overlap_length'] = roads.geometry.intersection(flood_zone).length

print(roads)
total_flooded_road_length = roads['overlap_length'].sum()
print(total_flooded_road_length)
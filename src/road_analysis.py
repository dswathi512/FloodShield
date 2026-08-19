import ee
import osmnx as ox
import config as c
from . import flood_detection as fd
import geopandas as gpd
ox.settings.log_console = False
def get_roads():
    """Fetch road data from OpenStreetMap for the area of interest defined in config.py."""
    graph=ox.graph_from_bbox(c.AOI_CORDS,network_type='drive')
    roads_gdf=ox.graph_to_gdfs(graph,nodes=False,edges=True)
    roads_gdf=roads_gdf.reset_index()
    return roads_gdf

def analyze_road_impact(roads):
    flood_mask=fd.detect_floods()
    flood_polygon=fd.get_flood_polygon(flood_mask)
    roads_projected = roads.to_crs(epsg=32644)
    flood_polygon_gdf = gpd.GeoDataFrame(geometry=[flood_polygon], crs='EPSG:4326').to_crs(epsg=32644)
    flood_polygon_projected = flood_polygon_gdf.geometry.iloc[0]
    roads_projected['intersects_flood'] = roads_projected.geometry.intersects(flood_polygon_projected)
    affected_roads = roads_projected[roads_projected['intersects_flood']]
    total_affected_length_m = roads_projected.geometry.intersection(flood_polygon_projected).length.sum()
    total_affected_length_km = total_affected_length_m / 1000
    return affected_roads, total_affected_length_km

if __name__ == "__main__":
    print("Starting data fetch...")
    roads = get_roads()
    affected, total = analyze_road_impact(roads)
    print(f"Affected road segments: {len(affected)}")
    print(f"Total affected length: {total}")


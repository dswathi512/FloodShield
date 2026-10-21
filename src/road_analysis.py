import osmnx as ox
import config as c
from . import flood_detection as fd
import geopandas as gpd

ox.settings.log_console = False


def get_roads():
    graph = ox.graph_from_bbox(c.AOI_CORDS, network_type='drive')
    roads = ox.graph_to_gdfs(graph, nodes=False, edges=True).reset_index()

    # Two-way streets appear twice (A->B and B->A); keep one copy of each
    roads['a'] = roads[['u', 'v']].min(axis=1)
    roads['b'] = roads[['u', 'v']].max(axis=1)
    roads = roads.drop_duplicates(subset=['a', 'b', 'key']).drop(columns=['a', 'b'])
    return roads


def analyze_road_impact(roads, flood_mask):
    """Takes the flood mask as input (no recomputation). Returns affected roads and total km."""
    roads_projected = roads.to_crs(epsg=32644)

    flood_polygon = fd.get_flood_polygon(flood_mask)
    if flood_polygon is None or flood_polygon.is_empty:
        return roads_projected.iloc[0:0], 0.0

    flood_projected = gpd.GeoSeries([flood_polygon], crs='EPSG:4326').to_crs(epsg=32644).iloc[0]

    affected = roads_projected[roads_projected.geometry.intersects(flood_projected)].copy()
    total_km = affected.geometry.intersection(flood_projected).length.sum() / 1000
    return affected, total_km


if __name__ == "__main__":
    roads = get_roads()
    flood_mask = fd.detect_floods()
    affected, total_km = analyze_road_impact(roads, flood_mask)
    print(f"Affected segments: {len(affected)} of {len(roads)} ({len(affected)/len(roads)*100:.2f}%)")
    print(f"Total flooded road length: {total_km:.2f} km")
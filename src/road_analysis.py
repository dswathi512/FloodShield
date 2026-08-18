import osmnx as ox
import config as c
ox.settings.log_console = True
def get_roads():
    """Fetch road data from OpenStreetMap for the area of interest defined in config.py."""
    graph=ox.graph_from_bbox(c.AOI_CORDS,network_type='drive')
    roads_gdf=ox.graph_to_gdfs(graph,nodes=False,edges=True)
    roads_gdf=roads_gdf.reset_index()
    return roads_gdf
if __name__=="__main__":
    print("Starting data fetch...")
    roads=get_roads()
    print(roads.head())
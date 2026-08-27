import ee
import folium


# ---------------------------------------------------------------------------
# Adapter function: lets a folium.Map display an Earth Engine image as a layer.
# EE images live on Google's servers as computation graphs, not normal files,
# so Folium can't display them directly — this bridges the two.
# ---------------------------------------------------------------------------
def add_ee_layer(self, ee_image_object, vis_params, name):
    # Ask Earth Engine to render this image into map tiles (like Google Maps
    # tiles) using the given visualization settings (color, min/max, etc.)
    map_id_dict = ee.Image(ee_image_object).getMapId(vis_params)

    # Wrap those tiles in a standard Folium TileLayer, same mechanism Folium
    # uses to show the base map itself
    folium.raster_layers.TileLayer(
        tiles=map_id_dict['tile_fetcher'].url_format,
        attr='Google Earth Engine',   # required attribution text
        name=name,                    # label shown in the layer toggle box
        overlay=True,                 # sits on top of the base map
        control=True                  # shows as a toggleable checkbox
    ).add_to(self)


# Attach add_ee_layer onto folium.Map itself, so it behaves like a built-in
# method — e.g. m.add_ee_layer(...) instead of add_ee_layer(m, ...)
folium.Map.add_ee_layer = add_ee_layer


# ---------------------------------------------------------------------------
# Builds the full dashboard: flood mask + affected roads, on one toggleable map
# ---------------------------------------------------------------------------
def create_flood_dashboard(flood_mask, affected_roads_gdf, center_coords, zoom=13):
    # Base map, centered on the area of interest (e.g. Hyderabad)
    m = folium.Map(location=center_coords, zoom_start=zoom)

    # Visualization settings for the flood layer — render flood pixels in red
    flood_vis = {'min': 0, 'max': 1, 'palette': ['red']}
    m.add_ee_layer(flood_mask, flood_vis, 'Flood Extent')

    # Add affected roads as their own layer, only if any were found —
    # avoids crashing on an empty GeoDataFrame
    if affected_roads_gdf is not None and len(affected_roads_gdf) > 0:
        # .explore() is a GeoPandas method that auto-converts road geometry
        # into a Folium layer — no manual per-road looping needed
        affected_roads_gdf.explore(
            m=m,
            color='blue',
            name='Affected Roads',
            style_kwds={'weight': 4}
        )

    # Adds the on/off toggle box (top-right corner) for each named layer
    folium.LayerControl().add_to(m)

    return m
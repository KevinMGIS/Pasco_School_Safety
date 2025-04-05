import geopandas as gpd

# Read the existing buffer file (make sure the path and file name are correct)
school_buffers = gpd.read_file("Data/All_School_Buffers_Analyzed.geojson")
# Reproject the data to WGS84 (EPSG:4326) for use in Leaflet
buffers_4326 = school_buffers.to_crs(epsg=4326)
buffers_4326.to_file("Data/All_School_Buffers_Analyzed_4326.geojson", driver="GeoJSON")
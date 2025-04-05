#!/usr/bin/env python
"""
Pasco School Isochrone Generation Script
This script processes the Pasco Schools GeoJSON along with the road network for 
Pasco County (downloaded from OSM using OSMnx). For each school, it computes a network 
isochrone (area reachable within a specified travel time, here 5 minutes) based on an 
assumed driving speed. The results are exported as a GeoJSON file for use in WebGIS 
applications and dashboards.
This project is intended solely as a coding exercise.

Author: Kevin M
Date: March, 2025
"""

import osmnx as ox
import networkx as nx
import geopandas as gpd
from shapely.geometry import MultiPoint

# -------------------------------
# 1. Download and Prepare the Road Network
# -------------------------------
place_name = "Pasco County, Florida, USA"
network_type = "drive"

print("Downloading network graph for", place_name)
# Download the network graph for the defined area
G = ox.graph_from_place(place_name, network_type=network_type)

# Project the graph to a suitable projected CRS (e.g., Web Mercator, EPSG:3857)
G = ox.project_graph(G)

# -------------------------------
# 2. Add Travel Time to Each Edge
# -------------------------------
# Assume an average driving speed (e.g., 25 mph)
speed_mph = 25
speed_mps = speed_mph * 0.44704  # convert mph to meters per second

print("Calculating travel times for each edge...")
for u, v, k, data in G.edges(keys=True, data=True):
    if 'length' in data and data['length']:
        data['travel_time'] = data['length'] / speed_mps
    else:
        data['travel_time'] = 0

# -------------------------------
# 3. Load and Reproject Schools Data
# -------------------------------
schools_fp = "data/Pasco_Schools.geojson"
schools = gpd.read_file(schools_fp)

# Reproject schools to the network's CRS
schools = schools.to_crs(G.graph['crs'])

# Determine the correct school identifier column.
if 'name' in schools.columns:
    id_col = 'name'
elif 'NAME' in schools.columns:
    id_col = 'NAME'
else:
    raise KeyError("Neither 'name' nor 'NAME' found in schools columns. Available columns: " + str(schools.columns))

# -------------------------------
# 4. Isochrone Generation Function
# -------------------------------
def generate_isochrone(G, center_node, travel_time_limit):
    """
    Generate an isochrone polygon for nodes reachable within travel_time_limit (in seconds)
    from a given center_node in the graph G.
    """
    # Compute shortest travel times from the center node using Dijkstra's algorithm.
    travel_times = nx.single_source_dijkstra_path_length(G, center_node, weight='travel_time')
    # Select nodes reachable within the travel time limit.
    reachable_nodes = [node for node, t in travel_times.items() if t <= travel_time_limit]
    
    # Get node geometries from the graph
    nodes = ox.graph_to_gdfs(G, nodes=True, edges=False)
    reachable_points = nodes.loc[reachable_nodes]['geometry']
    
    # Create a MultiPoint and compute its convex hull as the isochrone polygon.
    multipoint = MultiPoint(list(reachable_points))
    if multipoint.is_empty:
        return None
    else:
        return multipoint.convex_hull

# -------------------------------
# 5. Loop Over Schools to Generate Isochrones
# -------------------------------
# Define the travel time threshold (e.g., 5 minutes = 300 seconds)
threshold_seconds = 5 * 60

isochrone_features = []

print("Generating isochrones for each school...")
for idx, school in schools.iterrows():
    # Determine the school identifier
    school_id = school[id_col]
    # Get the school's geometry (assumed to be a point)
    point = school.geometry
    # Find the nearest node in the network
    center_node = ox.distance.nearest_nodes(G, point.x, point.y)
    # Generate the isochrone polygon for the specified travel time threshold
    poly = generate_isochrone(G, center_node, threshold_seconds)
    if poly is not None:
        isochrone_features.append({
            'school_id': school_id,
            'travel_time': threshold_seconds,
            'geometry': poly
        })

# Create a GeoDataFrame from the isochrone features
if isochrone_features:
    isochrone_gdf = gpd.GeoDataFrame(isochrone_features, crs=G.graph['crs'])
else:
    raise ValueError("No isochrone features were generated.")

# -------------------------------
# 6. Reproject and Export Isochrone Data
# -------------------------------
# Reproject the GeoDataFrame to WGS84 (EPSG:4326) for use in Leaflet
isochrone_gdf = isochrone_gdf.to_crs(epsg=4326)

# Export the isochrones as a GeoJSON file
output_fp = "Data/isochrones_all.geojson"
isochrone_gdf.to_file(output_fp, driver="GeoJSON")
print("Exported isochrone polygons for all schools to", output_fp)
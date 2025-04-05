#!/usr/bin/env python
"""
Network Analysis with OSMnx for Pasco School Safety Project

This script downloads the road network for Pasco County, Florida using OSMnx,
computes travel times for each edge based on an assumed driving speed,
and generates isochrone polygons (areas reachable within specified travel times)
for a selected school from the Pasco Schools dataset.

The output GeoJSON file containing the isochrone polygons can be used in your
WebGIS application to compare network-based accessibility with Euclidean buffers.

Author: Your Name
Date: YYYY-MM-DD
"""

import osmnx as ox
import networkx as nx
import geopandas as gpd
from shapely.geometry import MultiPoint
import matplotlib.pyplot as plt

# -------------------------------
# 1. Define Parameters and Settings
# -------------------------------

# Define the geographic area for network analysis using a place name.
place_name = "Pasco County, Florida, USA"

# Specify the type of network to download (e.g., "drive" for vehicle travel).
network_type = "drive"

# Define an average driving speed (in miles per hour) to compute travel times.
speed_mph = 25  # average speed in mph
speed_mps = speed_mph * 0.44704  # convert mph to meters per second

# Define isochrone thresholds in minutes (e.g., 5, 10, 15 minutes).
isochrone_thresholds = [5, 10, 15]
# Convert thresholds to seconds for travel time calculations.
thresholds_seconds = [t * 60 for t in isochrone_thresholds]

# -------------------------------
# 2. Download and Prepare the Network
# -------------------------------

print("Downloading network graph for", place_name)
# Download the network graph for the defined area.
G = ox.graph_from_place(place_name, network_type=network_type)

# Note: The graph is already simplified by osmnx, so no need to call ox.simplify_graph(G) again.

# Project the graph to a suitable projected CRS (e.g., UTM) for accurate distance measurements.
G = ox.project_graph(G)

# Add a 'travel_time' attribute to each edge using the edge length and average speed.
# The length is in meters; travel time (in seconds) = length / speed_mps.
print("Adding travel time to each edge...")
for u, v, k, data in G.edges(keys=True, data=True):
    if data.get('length', 0) > 0:
        data['travel_time'] = data['length'] / speed_mps
    else:
        data['travel_time'] = 0

# -------------------------------
# 3. Select a School for Isochrone Analysis
# -------------------------------

# Load the Pasco Schools GeoJSON file.
schools_fp = "data/Pasco_Schools.geojson"
schools = gpd.read_file(schools_fp)

# Get the CRS of the network graph (projected CRS) and convert schools to this CRS.
graph_nodes = ox.graph_to_gdfs(G, nodes=True, edges=False)
graph_crs = graph_nodes.crs
schools = schools.to_crs(graph_crs)

# For demonstration, select the first school from the dataset.
selected_school = schools.iloc[0]
school_name = selected_school.get("name", "Selected School")
school_point = selected_school.geometry

print(f"Selected school for analysis: {school_name}")

# -------------------------------
# 4. Find the Nearest Network Node to the Selected School
# -------------------------------

# Extract the x and y coordinates from the school's geometry.
school_x, school_y = school_point.x, school_point.y

# Use OSMnx to find the nearest node in the graph to the school's location.
center_node = ox.distance.nearest_nodes(G, school_x, school_y)
print("Nearest network node for the selected school:", center_node)

# -------------------------------
# 5. Generate Isochrone Polygons
# -------------------------------

def generate_isochrone(G, center_node, travel_time_limit):
    """
    Generate an isochrone polygon for a given network graph, center node, and travel time limit.
    
    Parameters:
        G (networkx.MultiDiGraph): The network graph with a 'travel_time' attribute.
        center_node (int): The node ID representing the center (e.g., a school).
        travel_time_limit (float): The maximum travel time (in seconds) for the isochrone.
        
    Returns:
        shapely.geometry.Polygon or None: A convex hull polygon of all nodes reachable
        within the travel time limit, or None if no nodes are reachable.
    """
    # Compute shortest travel times from the center node to all other nodes using Dijkstra's algorithm.
    travel_times = nx.single_source_dijkstra_path_length(G, center_node, weight='travel_time')
    
    # Filter for nodes that can be reached within the travel time limit.
    reachable_nodes = [node for node, t in travel_times.items() if t <= travel_time_limit]
    
    # Retrieve node coordinates from the graph as a GeoDataFrame.
    nodes = ox.graph_to_gdfs(G, nodes=True, edges=False)
    reachable_points = nodes.loc[reachable_nodes]['geometry']
    
    # Combine the reachable points into a MultiPoint object.
    multipoint = MultiPoint(list(reachable_points))
    
    # Generate and return the convex hull of the points as the isochrone polygon.
    if multipoint.is_empty:
        return None
    else:
        return multipoint.convex_hull

# Dictionary to store the isochrone polygons for each threshold.
isochrones = {}

for t_seconds in thresholds_seconds:
    print(f"Generating isochrone for {t_seconds/60} minutes...")
    poly = generate_isochrone(G, center_node, t_seconds)
    isochrones[t_seconds] = poly

# -------------------------------
# 6. Export Isochrone Polygons as GeoJSON
# -------------------------------

# Convert the isochrone polygons into a GeoDataFrame for export.
isochrone_gdf = gpd.GeoDataFrame(columns=['travel_time', 'geometry'], crs=graph_crs)

for t_seconds, poly in isochrones.items():
    if poly is not None:
        # Append each isochrone with its corresponding travel time (in seconds) using _append (since append is deprecated).
        isochrone_gdf = isochrone_gdf._append({'travel_time': t_seconds, 'geometry': poly}, ignore_index=True)

# Specify the output file path for the isochrone GeoJSON.
isochrone_output_fp = "data/isochrones.geojson"
isochrone_gdf.to_file(isochrone_output_fp, driver="GeoJSON")
print("Isochrone polygons exported to", isochrone_output_fp)

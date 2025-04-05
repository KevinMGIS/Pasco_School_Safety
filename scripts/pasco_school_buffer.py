#!/usr/bin/env python
"""
School Safety Proximity Analysis Script
This script processes GeoJSON data for Pasco Schools, Police Stations, Fire Stations, 
and County Boundaries. It creates multiple buffer zones around each school, calculates 
the distance to the nearest police and fire stations, and exports the processed data.
This code-based workflow is ideal for showcasing reproducibility and technical proficiency.

Author: Your Name
Date: YYYY-MM-DD
"""

import geopandas as gpd

# -------------------------------
# 1. SETUP AND DATA LOADING
# -------------------------------

# Define file paths for the data files in the 'Data' folder.
schools_fp = "data/Pasco_Schools.geojson"
police_fp = "data/Pasco_Police_Stations.geojson"
fire_fp = "data/Pasco_Fire_Stations.geojson"
county_fp = "data/Pasco_County_Boundary.geojson"

# Load the GeoJSON files into GeoDataFrames using GeoPandas.
schools = gpd.read_file(schools_fp)
police = gpd.read_file(police_fp)
fire = gpd.read_file(fire_fp)
county = gpd.read_file(county_fp)

# -------------------------------
# 2. CRS CHECK AND REPROJECTION
# -------------------------------
# Ensure all layers use the same Coordinate Reference System (CRS) for accurate spatial analysis.
# For buffer and distance calculations, a projected CRS is preferred.
# Here, we assume the data may be in WGS84 (EPSG:4326) and convert to EPSG:3857 (Web Mercator),
# which uses meters as its unit.

target_crs = "EPSG:3857"

if schools.crs != target_crs:
    schools = schools.to_crs(target_crs)
if police.crs != target_crs:
    police = police.to_crs(target_crs)
if fire.crs != target_crs:
    fire = fire.to_crs(target_crs)
if county.crs != target_crs:
    county = county.to_crs(target_crs)

# -------------------------------
# 3. BUFFER CREATION
# -------------------------------
# Define buffer distances in miles and convert to meters.
# Conversion: 1 mile = 1609.34 meters.
buffer_distances = {
    "0.5_mile": 0.5 * 1609.34,
    "1_mile": 1 * 1609.34,
    "1.5_mile": 1.5 * 1609.34
}

# Create buffers for each school at different distances.
# We create separate GeoDataFrames for each buffer scenario.
schools_buffer_0_5 = schools.copy()
schools_buffer_0_5["geometry"] = schools_buffer_0_5.geometry.buffer(buffer_distances["0.5_mile"])

schools_buffer_1 = schools.copy()
schools_buffer_1["geometry"] = schools_buffer_1.geometry.buffer(buffer_distances["1_mile"])

schools_buffer_1_5 = schools.copy()
schools_buffer_1_5["geometry"] = schools_buffer_1_5.geometry.buffer(buffer_distances["1.5_mile"])

# Export the buffer layers as GeoJSON files for the WebGIS application.
schools_buffer_0_5.to_file("Data/Schools_Buffer_0.5_Mile.geojson", driver="GeoJSON")
schools_buffer_1.to_file("Data/Schools_Buffer_1_Mile.geojson", driver="GeoJSON")
schools_buffer_1_5.to_file("Data/Schools_Buffer_1.5_Mile.geojson", driver="GeoJSON")

# -------------------------------
# 4. DISTANCE ANALYSIS
# -------------------------------
# Calculate the nearest police station and fire station distances for each school.
# We use GeoPandas' sjoin_nearest function (available in GeoPandas 0.10+), which performs a spatial join 
# and adds a column with the computed distance.
# The distance values are in the CRS units (meters for EPSG:3857).

# Calculate distance to the nearest police station.
schools_with_police = schools.sjoin_nearest(
    police[['geometry']],
    how="left",
    distance_col="dist_to_police"
)

# Drop 'index_right' column to avoid conflicts in subsequent joins
schools_with_police = schools_with_police.drop(columns=['index_right'], errors='ignore')

# Calculate distance to the nearest fire station by joining the fire GeoDataFrame.
# We perform the join on the result from the previous join to retain the police distance column.
schools_with_fire = schools_with_police.sjoin_nearest(
    fire[['geometry']],
    how="left",
    distance_col="dist_to_fire"
)

# The 'schools_with_fire' GeoDataFrame now contains two new columns:
# 'dist_to_police' and 'dist_to_fire' representing the nearest distances (in meters).
print("Sample of schools with computed distances:")
print(schools_with_fire.head())

# -------------------------------
# 5. EXPORT PROCESSED DATA
# -------------------------------
# Export the processed schools layer, which now includes the distance calculations,
# to a new GeoJSON file for use in the WebGIS application.
schools_with_fire.to_file("Data/Processed_Schools.geojson", driver="GeoJSON")
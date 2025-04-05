#!/usr/bin/env python
"""
School Safety Proximity Analysis Script (Pivot Version)
This script processes GeoJSON data for Pasco Schools, Police Stations, Fire Stations, 
and County Boundaries. It creates a buffer for each school (storing the school name with the buffer),
then performs spatial analysis to count the number of police and fire stations within each buffer.
The resulting data is exported as a GeoJSON file for use in a WebGIS application and dashboards.
This project is intended solely as a coding exercise.

Author: Your Name
Date: YYYY-MM-DD
"""

import geopandas as gpd

# -------------------------------
# 1. SETUP AND DATA LOADING
# -------------------------------
schools_fp = "data/Pasco_Schools.geojson"
police_fp = "data/Pasco_Police_Stations.geojson"
fire_fp = "data/Pasco_Fire_Stations.geojson"
county_fp = "data/Pasco_County_Boundary.geojson"

schools = gpd.read_file(schools_fp)
police = gpd.read_file(police_fp)
fire = gpd.read_file(fire_fp)
county = gpd.read_file(county_fp)

# -------------------------------
# 2. CRS CHECK AND REPROJECTION
# -------------------------------
# For buffer and spatial analysis, we use a projected CRS (Web Mercator)
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
# 3. BUFFER CREATION FOR ALL SCHOOLS
# -------------------------------
# Define the buffer distance for analysis (1 mile in meters)
buffer_distance_meters = 1 * 1609.34

# Create a buffer for each school.
schools['buffer'] = schools.geometry.buffer(buffer_distance_meters)

# Determine the correct school identifier column.
if 'name' in schools.columns:
    id_col = 'name'
elif 'NAME' in schools.columns:
    id_col = 'NAME'
elif 'school_name' in schools.columns:
    id_col = 'school_name'
else:
    raise KeyError("Neither 'name', 'NAME', nor 'school_name' found in schools columns. Available columns: " + str(schools.columns))

# Create a GeoDataFrame from the buffers, retaining the school identifier.
school_buffers = schools[[id_col, 'buffer']].copy()
# Rename the identifier column to 'school_id' and 'buffer' to 'geometry'
school_buffers = school_buffers.rename(columns={'buffer': 'geometry', id_col: 'school_id'})
school_buffers = school_buffers.set_geometry('geometry')

# -------------------------------
# 4. SPATIAL ANALYSIS: COUNT NEARBY STATIONS
# -------------------------------
# Count police stations within each school's buffer.
police_in_buffer = gpd.sjoin(police, school_buffers, how='inner', predicate='within')
# Count fire stations within each school's buffer.
fire_in_buffer = gpd.sjoin(fire, school_buffers, how='inner', predicate='within')

# Aggregate counts by school_id.
police_counts = police_in_buffer.groupby('school_id').size().reset_index(name='police_count')
fire_counts = fire_in_buffer.groupby('school_id').size().reset_index(name='fire_count')

# Merge the counts into the school_buffers GeoDataFrame using 'school_id'.
school_buffers = school_buffers.merge(police_counts, on='school_id', how='left')
school_buffers = school_buffers.merge(fire_counts, on='school_id', how='left')

# Replace NaN values with 0.
school_buffers['police_count'] = school_buffers['police_count'].fillna(0).astype(int)
school_buffers['fire_count'] = school_buffers['fire_count'].fillna(0).astype(int)

# -------------------------------
# 5. EXPORT PROCESSED DATA
# -------------------------------
# Export the analyzed school buffers with counts as a GeoJSON file.
output_fp = "Data/All_School_Buffers_Analyzed.geojson"
school_buffers.to_file(output_fp, driver="GeoJSON")

print("Exported analyzed school buffers with station counts to", output_fp)
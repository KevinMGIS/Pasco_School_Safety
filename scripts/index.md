---
layout: default
title: Pasco School Safety Proximity Analysis
---

# Pasco School Safety Proximity Analysis

> **Disclaimer:**  
> **This project and the data used are strictly for demonstration and coding exercise purposes. They should not be used for any real analysis or decision-making.**

## Project Overview

This project demonstrates an end-to-end GIS workflow that examines the proximity of schools to emergency services (police and fire stations) in Pasco County. The focus is on showcasing a coding-based spatial analysis workflow and creating an interactive WebGIS application. The data used (Schools, Police Stations, and Fire Stations) were obtained for Pasco County, Florida, and are used here solely as sample data.

The project integrates:
- **Euclidean Analysis:**  
  Buffer creation and straight-line distance measurements between schools and emergency services.
- **Network Analysis:**  
  Realistic travel time computation using the OpenStreetMap (OSM) network and OSMnx, along with isochrone generation.
- **Interactive Mapping:**  
  A Leaflet-based map that overlays the various layers (schools, police, fire, and isochrones) on an OpenStreetMap basemap.
- **Dashboard Elements:**  
  (Planned) A dashboard that further summarizes key metrics and provides interactive filtering options.

---

## Project Phases

### Phase 1: Planning & Data Collection
- **Objectives & Scope:**  
  Define the project goals to analyze school safety proximity using spatial data. The focus is on demonstrating a reproducible coding workflow.
- **Data Sources:**  
  - **Pasco Schools**
  - **Pasco Police Stations**
  - **Pasco Fire Stations**
  - (Optional) County boundaries for contextual reference.
  
*Note: The data used are for demonstration only and should not be relied on for any critical decisions.*

### Phase 2: Data Preparation & Spatial Analysis
- **Data Inspection and CRS Alignment:**  
  All GeoJSON files were loaded in QGIS and reprojected to a common coordinate reference system for accurate measurements.
- **Buffer Creation and Distance Calculations:**  
  Using Python (GeoPandas and Shapely), we generated multiple buffers (0.5, 1, and 1.5 miles) around each school and calculated the Euclidean distances to the nearest police and fire stations.

**Example Code Snippet: Buffer Creation**

```python
# Define buffer distances (in meters, 1 mile ≈ 1609.34 meters)
buffer_distances = {
    "0.5_mile": 0.5 * 1609.34,
    "1_mile": 1 * 1609.34,
    "1.5_mile": 1.5 * 1609.34
}

# Create buffer layers for schools
schools_buffer_1 = schools.copy()
schools_buffer_1["geometry"] = schools_buffer_1.geometry.buffer(buffer_distances["1_mile"])
```

### Phase 3: Code-Based Workflow Documentation
- **Transition from QGIS to Code:**  
  The entire spatial analysis process was automated using Python scripts. This allows for reproducibility and easy modifications.
- **Documentation and Version Control:**  
  All steps, including data loading, buffer creation, and distance analysis, are well-commented in the scripts. The full chat history for this project was used as the foundation for documenting the workflow.

### Phase 4: Network Analysis with OSMnx
- **Downloading the Road Network:**  
  Using OSMnx, we downloaded the road network for Pasco County and computed realistic travel times based on an assumed driving speed.
- **Isochrone Generation:**  
  For a selected school, isochrone polygons were generated to visualize areas reachable within specified travel times (e.g., 5, 10, and 15 minutes).

**Example Code Snippet: Isochrone Generation Function**

```python
def generate_isochrone(G, center_node, travel_time_limit):
    """
    Generate an isochrone polygon for nodes reachable within travel_time_limit.
    """
    travel_times = nx.single_source_dijkstra_path_length(G, center_node, weight='travel_time')
    reachable_nodes = [node for node, t in travel_times.items() if t <= travel_time_limit]
    nodes = ox.graph_to_gdfs(G, nodes=True, edges=False)
    reachable_points = nodes.loc[reachable_nodes]['geometry']
    multipoint = MultiPoint(list(reachable_points))
    return multipoint.convex_hull if not multipoint.is_empty else None
```

### Phase 5: WebGIS Application & Dashboard Development
- **Interactive Map:**  
  The map is built using Leaflet (in `map.html`), which loads the processed GeoJSON layers. Users can toggle layers to view schools, emergency services, and isochrones.
- **Dashboard Integration:**  
  Future plans include adding dashboard elements (using Plotly Dash or Streamlit) to provide summary statistics and interactive filtering options.

**Example Code Snippet: Basic Leaflet Map Initialization**

```html
<script>
  var map = L.map('map').setView([28.2465, -82.6925], 11);
  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 19,
    attribution: '&copy; OpenStreetMap contributors'
  }).addTo(map);
</script>
```

---

## Conclusion

This project demonstrates an integrated GIS workflow combining data collection, spatial analysis, network analysis using OSMnx, and interactive visualization with Leaflet. While the project is intended solely as a coding exercise, it provides a robust framework that showcases advanced GIS techniques and reproducible coding practices.


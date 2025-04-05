---
layout: "default"
title: "Pasco School Safety Proximity Analysis"
---

# Pasco School Safety Proximity Analysis

> **Disclaimer:**  
> **This project and the data used are strictly for demonstration and coding exercise purposes. They should not be used for any real analysis or decision-making.**

[View Interactive Map](map.html)

## Project Overview

This project demonstrates an end-to-end GIS workflow that examines the proximity of schools to emergency services (police and fire stations) in Pasco County. Originally, the focus was on generating simple Euclidean buffers and network isochrones for selected schools. However, we have pivoted to a more comprehensive approach:

- **Buffer & Spatial Analysis Pivot:**  
  We now generate buffers for every school in Pasco County, storing each school's identifier with its buffer. These buffers are then used to perform spatial analysis to count the number of police and fire stations that fall within each buffer, providing an indicator of service coverage for each school.
- **Network Analysis:**  
  Alongside the Euclidean buffers, we compute network isochrones using the road network from OpenStreetMap (via OSMnx) to assess realistic travel times to emergency services.
- **Interactive Mapping & Dashboards:**  
  The processed data is integrated into a WebGIS application (using Leaflet) that displays schools, police, and fire stations. Additionally, dashboards summarize key metrics such as:
  - The number of schools covered by police and fire services within the Euclidean and network isochrone buffers.
  - Average distances and travel times from schools to emergency services.
  - A breakdown of coverage percentages across schools.

---

## Project Phases

### Phase 1: Planning & Data Collection
- **Objectives & Scope:**  
  Define project goals to analyze school safety proximity using spatial data and demonstrate a reproducible coding workflow.
- **Data Sources:**  
  - **Pasco Schools**
  - **Pasco Police Stations**
  - **Pasco Fire Stations**
  - (Optional) County boundaries for context.
  
*Note: The data are for demonstration only and should not be used for any critical decisions.*

### Phase 2: Data Preparation & Spatial Analysis (Pivot)
- **CRS Alignment & Data Loading:**  
  All GeoJSON files are loaded and reprojected to a common metric CRS (EPSG:3857) for accurate spatial analysis.
- **Buffer Generation for All Schools:**  
  Instead of creating buffers for a single school, we loop over all schools in Pasco County, creating a 1-mile buffer for each school. Each buffer is tagged with the school’s identifier.
- **Spatial Join Analysis:**  
  Using these buffers, we perform spatial joins with the police and fire station layers to count how many stations fall within each school’s buffer. These counts provide a quantitative measure of emergency service coverage.

**Example Code Snippet: Generating Buffers and Counting Stations**

```python
# Create a 1-mile buffer for every school and attach the school name
buffer_distance_meters = 1 * 1609.34
schools['buffer'] = schools.geometry.buffer(buffer_distance_meters)

# Use the appropriate identifier column (e.g., 'NAME' or 'name')
id_col = 'NAME' if 'NAME' in schools.columns else 'name'
school_buffers = schools[[id_col, 'buffer']].copy()
school_buffers = school_buffers.rename(columns={id_col: 'school_id', 'buffer': 'geometry'})
school_buffers = school_buffers.set_geometry('geometry')

# Perform spatial join to count nearby police stations
police_in_buffer = gpd.sjoin(police, school_buffers, how='inner', predicate='within')
police_counts = police_in_buffer.groupby('school_id').size().reset_index(name='police_count')

# Similarly for fire stations
fire_in_buffer = gpd.sjoin(fire, school_buffers, how='inner', predicate='within')
fire_counts = fire_in_buffer.groupby('school_id').size().reset_index(name='fire_count')

# Merge counts back into the buffers GeoDataFrame
school_buffers = school_buffers.merge(police_counts, on='school_id', how='left')
school_buffers = school_buffers.merge(fire_counts, on='school_id', how='left')
school_buffers['police_count'] = school_buffers['police_count'].fillna(0).astype(int)
school_buffers['fire_count'] = school_buffers['fire_count'].fillna(0).astype(int)
```

### Phase 3: Code-Based Workflow Documentation
- **Automation & Reproducibility:**  
  The spatial analysis process is entirely automated with Python scripts. All steps—from data loading to buffer generation and spatial joins—are fully documented in the code, ensuring reproducibility.
- **Version Control:**  
  All scripts and changes have been tracked, and the full project history is available as a reference.

### Phase 4: Network Analysis with OSMnx
- **Road Network Download & Travel Time Calculation:**  
  The road network for Pasco County is downloaded using OSMnx and reprojected to a metric CRS. Travel times for each network edge are computed using an assumed average speed.
- **Isochrone Generation:**  
  For each school, an isochrone polygon is generated representing the area reachable within a specified travel time (e.g., 5 minutes). This adds a realistic perspective to the analysis.

**Example Code Snippet: Isochrone Generation**

```python
def generate_isochrone(G, center_node, travel_time_limit):
    travel_times = nx.single_source_dijkstra_path_length(G, center_node, weight='travel_time')
    reachable_nodes = [node for node, t in travel_times.items() if t <= travel_time_limit]
    nodes = ox.graph_to_gdfs(G, nodes=True, edges=False)
    reachable_points = nodes.loc[reachable_nodes]['geometry']
    multipoint = MultiPoint(list(reachable_points))
    return multipoint.convex_hull if not multipoint.is_empty else None
```

### Phase 5: WebGIS Application & Dashboard Development
- **Interactive Map:**  
  The map (built with Leaflet) displays the following layers:
  - Schools
  - Police Stations
  - Fire Stations
- **Dashboard Integration:**  
  A side panel hosts multiple dashboard components:
  - **Coverage Count Dashboard:** Displays the number of schools with police and fire stations within the Euclidean and network isochrone buffers.
  - **Average Distance / Travel Time Dashboard:** Compares average distances and travel times from schools to the nearest emergency services.
  - **Coverage Breakdown Dashboard:** Shows a breakdown (via pie chart) of the percentage of schools with different levels of service coverage.
  
These dashboards provide quantitative insights and interactive filtering capabilities.

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

This pivot refines our approach by generating buffers for every school and incorporating spatial joins to count nearby emergency services, alongside generating network isochrones for a realistic measure of accessibility. The result is a robust, integrated GIS workflow that demonstrates advanced spatial analysis techniques and provides interactive, dashboard-driven insights into school safety proximity in Pasco County.


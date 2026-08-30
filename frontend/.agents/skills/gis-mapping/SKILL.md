---
name: gis-mapping
description: Build interactive geospatial visualizations for satellite oil spill detection, oil slick polygons and AIS vessel trajectories.
---

# GIS Mapping Skill

The application visualizes satellite-derived oil spill detections and AIS vessel data.

## Primary map requirements

The map should support:

- satellite imagery
- oil slick polygons
- oil spill locations
- AIS vessel markers
- AIS vessel trajectories
- candidate vessel highlighting
- selected vessel highlighting
- vessel movement paths
- map legends
- layer controls
- popups
- zoom controls
- time-based visualization where supported
- GeoJSON data

## React mapping

Prefer React-compatible mapping architecture.

If the existing project does not specify another solution, consider:

- Leaflet
- React-Leaflet
- GeoJSON

Do not introduce Mapbox or another paid mapping service without checking project requirements first.

## Oil slick visualization

Oil spill polygons should be clearly distinguishable from other map layers.

When backend data provides:

- polygon geometry
- detection confidence
- detection time
- area
- coordinates

display appropriate information on the map or in a details panel.

Never invent geographic coordinates.

## AIS visualization

AIS vessel data may contain:

- MMSI
- vessel name
- latitude
- longitude
- timestamp
- heading
- speed
- course

Render vessel positions accurately.

Render trajectory lines from actual coordinates.

Do not connect unrelated points incorrectly.

## Candidate vessels

When the backend supplies vessel attribution candidates, visualize:

- vessel name
- MMSI
- confidence score
- proximity
- temporal match
- trajectory match
- AIS gap status

Allow the user to select a candidate and highlight its trajectory.

## Dark vessel / AIS gap

If the backend identifies an AIS gap:

Display a clear warning.

Example:

"AIS signal gap detected"

Do not independently declare a vessel responsible for the spill from frontend logic.

The backend is responsible for attribution calculations.

## Map performance

Large GeoJSON/AIS datasets can be expensive.

Use appropriate:

- filtering
- memoization
- viewport-based rendering
- clustering where appropriate
- simplified visualization

Avoid unnecessary rerenders.

## Map UX

Provide:

- legend
- layer toggles
- selected-object state
- loading indicator
- error state
- empty state

The map must remain understandable even when many vessels are present.
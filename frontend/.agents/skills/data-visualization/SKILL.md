---
name: data-visualization
description: Create clear technical dashboards and visualizations for oil spill detection, vessel attribution and confidence analysis.
---

# Data Visualization Skill

The application must make complex oil spill and AIS attribution results easy to understand.

## Dashboard

Use real backend data for:

- detected spills
- active detections
- candidate vessels
- high-confidence matches
- AIS gaps
- recent detections

Never invent statistics.

## Vessel attribution

Display candidate vessels as ranked results.

Each candidate may show:

- vessel name
- MMSI
- overall confidence
- spatial/proximity score
- temporal score
- trajectory score
- AIS gap status

Use visual hierarchy to make the highest-ranked candidate obvious without claiming certainty.

## Confidence

Confidence must be presented as a score supplied by the backend.

Do not calculate attribution confidence independently in the frontend unless explicitly required.

## Charts

Use a React-compatible chart library already present in the project.

If none exists, use a lightweight library such as Recharts only when appropriate.

Possible visualizations:

- confidence distribution
- vessel ranking
- spill detections over time
- vessel activity over time
- AIS signal gaps
- detection statistics

## Chart rules

Charts must have:

- meaningful labels
- readable axes
- tooltips
- empty states
- loading states
- responsive sizing

Avoid charts that do not communicate useful information.

## Evidence

When evidence is available, show it alongside attribution results.

Example:

Detection
→ Vessel
→ Time correlation
→ Spatial correlation
→ Trajectory correlation
→ AIS gap
→ Confidence

The UI should make this reasoning understandable.
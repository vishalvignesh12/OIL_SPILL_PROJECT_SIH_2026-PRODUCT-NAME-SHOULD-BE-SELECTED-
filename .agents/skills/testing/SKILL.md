---
name: testing
description: Test and verify the React frontend, API integration, maps, dashboards and user workflows for the oil spill detection system.
---

# Testing Skill

Test functionality after implementation.

## React checks

Verify:

- application starts
- application builds
- routes work
- components render
- no obvious console errors

## API checks

Verify:

- API requests use correct endpoints
- loading state works
- successful response works
- error response works
- empty response works
- authentication behavior works

## Map checks

Verify:

- map loads
- oil slick polygons render
- GeoJSON is handled correctly
- vessel markers render
- AIS trajectories render
- candidate selection works
- selected vessel highlighting works
- layer controls work
- map remains responsive

## Attribution UI

Verify:

- candidates are ranked correctly according to backend response
- confidence scores display correctly
- AIS gap status displays correctly
- evidence information displays correctly

Do not independently change backend attribution logic.

## Responsive testing

Check:

- desktop
- laptop
- tablet
- mobile

Pay special attention to:

- navigation
- map
- tables
- candidate cards
- charts

## Error testing

Test:

- backend unavailable
- invalid API response
- empty data
- missing optional fields
- authentication failure

The UI should fail gracefully.

## Final check

Before declaring a task complete:

1. Run the application.
2. Check console.
3. Check network/API requests.
4. Test the affected workflow.
5. Verify no unrelated files were modified.
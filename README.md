# ITS Path Walk

A desktop route-finding application for pedestrian navigation inside the ITS campus area, built with Python and Tkinter.

The app visualizes campus points on a map, lets users choose a start and destination, then computes a route using either:
- A* Search
- Uniform Cost Search (UCS)

It also estimates:
- Distance (`km`)
- Calories burned (`kal`)
- Travel time (`minutes` and `seconds`)

## Features

- Interactive map rendered with `tkinter.Canvas`
- Selectable start and goal points from dropdown menus
- Algorithm switch between A* and UCS
- Visual route overlay on top of campus map
- Click-to-inspect grid coordinates on the map
- Route summary popup with distance, calories, and time

## Project Structure

- `walk_route.py`: Main application source (graph model, search algorithms, UI)
- `map_its.png`: Background campus map image used by the app
- `image/`: Screenshot assets for documentation

## Requirements

- Python 3.8+
- Tkinter (usually included with standard Python installations)

## How To Run

1. Ensure `walk_route.py` and `map_its.png` are in the same directory.
2. Run:

```bash
python walk_route.py
```

If your system uses `python3`:

```bash
python3 walk_route.py
```

## How To Use

1. Launch the app.
2. Pick a start point from **Select Start Point**.
3. Pick a destination from **Select Goal Point**.
4. Choose algorithm: **A*** or **Uniform Cost Search**.
5. Click **Find Route**.
6. View:
- Blue line path on the map
- Popup summary for distance, calories, and travel time

## Screenshots

1. Initial app view

![Initial app view](image/Screenshot%20from%202026-03-19%2018-23-53.png)

2. Route selection and path visualization

![Route selection and path visualization](image/Screenshot%20from%202026-03-19%2018-24-20.png)

3. Route result popup (distance, calories, and time)

![Route result popup](image/Screenshot%20from%202026-03-19%2018-24-34.png)

## Search Algorithm Notes

### A* Search

- Uses path cost so far (`g`) + heuristic estimate to goal (`h`)
- Heuristic is straight-line distance between nodes
- Typically faster in practice when heuristic is informative

### Uniform Cost Search

- Expands the lowest cumulative-cost path first
- Does not use heuristic
- Guarantees optimal path for non-negative edge costs

## Cost and Metric Calculation

- Edge distance in the graph is computed from point coordinates and scaled in `Graph.add_path`
- Route display summary uses these approximations from `find_path`:
- Distance: accumulated segment distance divided by `550`
- Calories: `distance * 60`
- Time: `distance * 15` (minutes)

These values are estimation-oriented and can be recalibrated as needed.

## Known Limitations

- Node coordinates and path links are currently hardcoded in source code
- Duplicate location entries exist for some labels (for example: `Geomatika`, `FDKBD`)
- Obstacle support exists in data model but is not actively configured in the current path list
- Requires local image asset (`map_its.png`) to render correctly

## Potential Improvements

- Move locations/paths into external config (JSON/CSV)
- Add obstacle toggling from UI
- Add zoom/pan support for map navigation
- Add path details per segment and total route cost breakdown
- Add automated tests for graph and search behavior

## License

No license file is currently provided in this repository.

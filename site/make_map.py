"""Turn the us-atlas state outlines into SVG path strings for the map on the index page.

    python3 site/make_map.py --topojson <states-albers-10m.json> --out site/us_states.json

Source: https://cdn.jsdelivr.net/npm/us-atlas@3.0.1/states-albers-10m.json (US Census Bureau
outlines, already projected to a 975 x 610 drawing). Output: {state name: SVG path}, with
coordinates rounded to whole units. The District of Columbia is left out (no senators).
"""
import argparse
import json

parser = argparse.ArgumentParser()
parser.add_argument("--topojson", required=True)
parser.add_argument("--out", required=True)
args = parser.parse_args()

topo = json.load(open(args.topojson))
(kx, ky), (dx, dy) = topo["transform"]["scale"], topo["transform"]["translate"]
arcs = []
for arc in topo["arcs"]:  # each arc is a list of steps from the previous point
    x = y = 0
    points = []
    for step in arc:
        x, y = x + step[0], y + step[1]
        points.append((round(x * kx + dx), round(y * ky + dy)))
    arcs.append(points)


def ring(indexes):
    points = []
    for i in indexes:
        part = arcs[i] if i >= 0 else arcs[~i][::-1]  # a negative index means the arc runs backwards
        points += part[1:] if points else part
    out = [points[0]]
    for p in points[1:]:
        if p != out[-1]:
            out.append(p)
    return "M" + "L".join(f"{x},{y}" for x, y in out) + "Z"


paths = {}
for g in topo["objects"]["states"]["geometries"]:
    name = g["properties"]["name"]
    if name == "District of Columbia":
        continue
    polygons = g["arcs"] if g["type"] == "MultiPolygon" else [g["arcs"]]
    paths[name] = "".join(ring(r) for polygon in polygons for r in polygon)
assert len(paths) == 50, len(paths)
with open(args.out, "w") as f:
    json.dump(paths, f, separators=(",", ":"), sort_keys=True)
print(len(paths), "states,", sum(len(p) for p in paths.values()), "characters")

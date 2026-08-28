"""
gpx_to_trail.py
Converts a GPX track file (downloaded from Wikiloc, AllTrails, Strava, or
any GPS app) into trail.js for the Huellas map.

USAGE:
    1. Download a .gpx file for your route (see README.md for where).
    2. Save it in this folder, e.g. as "rio-ramos.gpx"
    3. Run:  python3 gpx_to_trail.py rio-ramos.gpx
    4. This writes trail.js. Open index.html to see the trail drawn.

If your GPX file has named waypoints (many Wikiloc routes do, for things
like "Charco de las Víboras"), those become labeled landmark pins.
If it has none, the script still draws the full trail line — you can add
landmark labels afterward by opening trail-builder.html (it will show your
imported trail as a reference line you can click landmarks onto).

Requires no extra libraries — just Python 3.
"""

import sys
import json
import xml.etree.ElementTree as ET

MAX_LINE_POINTS = 400  # keeps the map smooth without being enormous


def strip_ns(tag):
    return tag.split("}")[-1] if "}" in tag else tag


def parse_gpx(path):
    tree = ET.parse(path)
    root = tree.getroot()

    trkpts = []
    waypoints = []

    for elem in root.iter():
        tag = strip_ns(elem.tag)
        if tag == "trkpt":
            lat = elem.get("lat")
            lon = elem.get("lon")
            if lat is not None and lon is not None:
                trkpts.append((float(lat), float(lon)))
        elif tag == "wpt":
            lat = elem.get("lat")
            lon = elem.get("lon")
            if lat is None or lon is None:
                continue
            name = None
            for child in elem:
                if strip_ns(child.tag) == "name":
                    name = child.text
            waypoints.append({
                "lat": round(float(lat), 6),
                "lng": round(float(lon), 6),
                "label": (name or "").strip() or "Point",
            })

    return trkpts, waypoints


def downsample(points, max_points):
    if len(points) <= max_points:
        return points
    step = len(points) / max_points
    sampled = [points[int(i * step)] for i in range(max_points)]
    if points[-1] != sampled[-1]:
        sampled.append(points[-1])
    return sampled


def main(gpx_path):
    try:
        trkpts, waypoints = parse_gpx(gpx_path)
    except ET.ParseError:
        print(f"❌ Couldn't read '{gpx_path}' — is it a valid GPX file?")
        return
    except FileNotFoundError:
        print(f"❌ Couldn't find '{gpx_path}'. Check the filename and try again.")
        return

    if not trkpts:
        print("❌ No track points found in this file. It may only contain "
              "waypoints, or may not be a track-type GPX file.")
        return

    line_points = downsample(trkpts, MAX_LINE_POINTS)

    with open("trail.js", "w", encoding="utf-8") as f:
        f.write(
            "// Imported by gpx_to_trail.py from a downloaded GPS track.\n"
            "// TRAIL_LINE draws the path itself (many points, for a smooth line).\n"
            "// TRAIL_LANDMARKS are named pins along it (from the GPX's waypoints,\n"
            "// if it had any). Add or edit landmarks any time with trail-builder.html\n"
            "// — it will show this imported line as a reference to click along.\n"
        )
        f.write("const TRAIL_LINE = ")
        f.write(json.dumps([[lat, lng] for lat, lng in line_points], indent=2))
        f.write(";\n\n")
        f.write("const TRAIL_LANDMARKS = ")
        f.write(json.dumps(waypoints, indent=2, ensure_ascii=False))
        f.write(";\n")

    print(f"✅ Imported {len(trkpts)} track points ({len(line_points)} kept for the line)")
    if waypoints:
        print(f"✅ Found {len(waypoints)} named waypoint(s): " + ", ".join(w["label"] for w in waypoints))
    else:
        print("ℹ️  No named waypoints in this file — the trail line is in, "
              "but you'll want to add landmark labels via trail-builder.html.")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 gpx_to_trail.py your-file.gpx")
    else:
        main(sys.argv[1])

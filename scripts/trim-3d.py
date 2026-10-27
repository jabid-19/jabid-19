"""Keep only the 3D buildings from the github-profile-3d-contrib SVG.

The generator always draws a radar chart, a language donut and a stats line
next to the calendar. This drops those, removes the solid background so the
graph blends into GitHub's light or dark theme, and crops the canvas tightly
around the buildings. Animations are untouched.

Usage: python3 scripts/trim-3d.py path/to/profile-3d-contrib.svg
"""

import re
import sys
import xml.etree.ElementTree as ET

SVG_NS = "http://www.w3.org/2000/svg"
ET.register_namespace("", SVG_NS)

PADDING = 12
TOP_OVERHANG = 24  # roofs of the tallest buildings sit above their anchor
CELL_WIDTH = 40  # top face of one building, with a little slack
BOTTOM_OVERHANG = 24  # front faces of the last row hang below their anchor


def tag(el):
    return el.tag.split("}")[-1]


def main(path):
    tree = ET.parse(path)
    root = tree.getroot()
    children = list(root)

    groups = [c for c in children if tag(c) == "g"]
    if not groups:
        sys.exit("No graph group found, leaving the file alone.")
    calendar = groups[0]  # the 3D calendar is always drawn first

    for child in children:
        if child is calendar or tag(child) in ("style", "defs"):
            continue
        root.remove(child)

    xs, ys = [], []
    for cell in calendar.iter():
        if tag(cell) != "g":
            continue
        m = re.match(r"translate\(([-\d.]+)[ ,]+([-\d.]+)\)", cell.get("transform", ""))
        if m:
            xs.append(float(m.group(1)))
            ys.append(float(m.group(2)))
    if not xs:
        sys.exit("Could not read building positions, leaving the file alone.")

    height = float(root.get("height", "850"))
    min_x = min(xs) - PADDING
    min_y = min(ys) - TOP_OVERHANG - PADDING
    max_x = max(xs) + CELL_WIDTH + PADDING
    max_y = height + BOTTOM_OVERHANG

    w, h = max_x - min_x, max_y - min_y
    root.set("viewBox", f"{min_x:.0f} {min_y:.0f} {w:.0f} {h:.0f}")
    root.set("width", f"{w:.0f}")
    root.set("height", f"{h:.0f}")

    tree.write(path, encoding="utf-8", xml_declaration=False)


if __name__ == "__main__":
    for p in sys.argv[1:]:
        main(p)

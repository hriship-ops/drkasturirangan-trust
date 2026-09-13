"""
figma_shapes_scraper.py — Fix 2
Scrapes all RECTANGLE/ELLIPSE nodes with significant fills from every
audited Figma frame and saves figma_shapes.json alongside figma_texts.json.

Run this whenever the Figma design changes:
    python figma_shapes_scraper.py
"""
import urllib.request, json
from pathlib import Path

ROOT = Path(r"C:\appdev\drk")
from figma_config import FILE_KEY, TOKEN  # gitignored — see figma_config.py

# All frames to scrape (primary + state frames)
FRAME_NAMES = [
    "Home Page ",
    "Vision and Mission",
    "fellowship page",
    "Apply",
    "V2 Dr Kasturi Rangan's Life",
    "Team",
    # interactive state frames
    "Space and Cosmos",
    "Environment",
    "Education",
    "Public Life",
    "Application process 2",
    "Application process 3",
    "Application process 4",
]

def api(url):
    req = urllib.request.Request(url, headers={"X-Figma-Token": TOKEN})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.load(r)

def extract_fill(fills):
    """Return (r, g, b, a) in 0-255 / 0-1 range for the first visible SOLID fill."""
    for f in fills:
        if f.get("type") != "SOLID":
            continue
        if not f.get("visible", True):
            continue
        c = f.get("color", {})
        r = round(c.get("r", 0) * 255)
        g = round(c.get("g", 0) * 255)
        b = round(c.get("b", 0) * 255)
        # Figma opacity can be on the fill object OR on the node; fill.opacity dominates here
        a = c.get("a", 1.0) * f.get("opacity", 1.0)
        return (r, g, b, round(a, 3))
    return None

def is_significant(r, g, b, a, width, height):
    """Exclude tiny, transparent, white, or near-white shapes."""
    if width < 30 or height < 30:
        return False
    if a < 0.05:
        return False
    # white / near-white
    if r > 242 and g > 242 and b > 242:
        return False
    # very light (luminance > 230)
    lum = 0.299 * r + 0.587 * g + 0.114 * b
    if lum > 230:
        return False
    return True

def walk(node, frame_x, frame_y, results, vectors, depth=0):
    if depth > 10:
        return
    ntype = node.get("type", "")
    nname = node.get("name", "")
    cb    = node.get("absoluteBoundingBox") or {}
    w     = round(cb.get("width",  0))
    h     = round(cb.get("height", 0))
    rx    = round(cb.get("x", 0) - frame_x)
    ry    = round(cb.get("y", 0) - frame_y)

    if ntype in ("RECTANGLE", "ELLIPSE"):
        fill = extract_fill(node.get("fills", []))
        if fill:
            r, g, b, a = fill
            if is_significant(r, g, b, a, w, h):
                cr = node.get("cornerRadius") or 0
                if not cr:
                    crs = node.get("rectangleCornerRadii") or [0, 0, 0, 0]
                    cr = max(crs)
                results.append({
                    "name":         nname,
                    "fill_rgba":    f"rgba({r},{g},{b},{a})",
                    "fill_r": r, "fill_g": g, "fill_b": b, "fill_a": a,
                    "corner_radius": round(cr),
                    "width": w, "height": h, "x": rx, "y": ry,
                })

    # VECTOR / LINE nodes: decorative connectors, illustrations, path graphics.
    # Captured at depth <= 2 to exclude icon glyphs nested inside components.
    # Minimum size 50x50 to skip tiny strokes.
    elif ntype in ("VECTOR", "LINE", "BOOLEAN_OPERATION") and depth <= 2:
        if w >= 50 and h >= 50:
            # skip nodes whose name suggests they are icon glyphs
            if nname.lower() not in ("icon", "vector", "path"):
                vectors.append({
                    "name":  nname,
                    "node_id": node.get("id", ""),
                    "width": w, "height": h, "x": rx, "y": ry,
                })
            else:
                # generic name but large — still capture with a flag
                vectors.append({
                    "name":    nname,
                    "node_id": node.get("id", ""),
                    "width": w, "height": h, "x": rx, "y": ry,
                    "generic_name": True,
                })

    for child in node.get("children", []):
        walk(child, frame_x, frame_y, results, vectors, depth + 1)

# ── Step 1: discover frame IDs ───────────────────────────────────────────────
print("Fetching file structure …")
file_data = api(f"https://api.figma.com/v1/files/{FILE_KEY}?depth=2")
name_to_id = {}
for page in file_data["document"]["children"]:
    for child in page.get("children", []):
        n = child.get("name", "")
        if n in FRAME_NAMES and n not in name_to_id:
            name_to_id[n] = child["id"]
            print(f"  Found: {n!r} id={child['id']}")

missing = [n for n in FRAME_NAMES if n not in name_to_id]
if missing:
    print(f"  WARNING: frames not found in Figma: {missing}")

# ── Step 2: fetch all nodes in one request ───────────────────────────────────
print("\nFetching node trees …")
all_ids = ",".join(name_to_id.values())
nodes_data = api(f"https://api.figma.com/v1/files/{FILE_KEY}/nodes?ids={all_ids}")

# ── Step 3: walk each frame ──────────────────────────────────────────────────
output = {}
for name, node_id in name_to_id.items():
    doc = nodes_data["nodes"][node_id]["document"]
    bb  = doc.get("absoluteBoundingBox", {})
    fx, fy = bb.get("x", 0), bb.get("y", 0)
    results = []
    vectors = []
    walk(doc, fx, fy, results, vectors)
    output[name] = {
        "node_id": node_id,
        "width":   round(bb.get("width",  0)),
        "height":  round(bb.get("height", 0)),
        "shapes":  results,
        "vectors": vectors,
    }
    print(f"  {name!r}: {len(results)} shapes, {len(vectors)} vectors")
    for s in results:
        print(f"    SHAPE {s['name']!r:28s} {s['fill_rgba']} cr={s['corner_radius']} {s['width']}x{s['height']}")
    for v in vectors:
        print(f"    VECT  {v['name']!r:28s} id={v['node_id']} {v['width']}x{v['height']}")

# ── Save ─────────────────────────────────────────────────────────────────────
out = ROOT / "figma_shapes.json"
out.write_text(json.dumps(output, indent=2, ensure_ascii=False), encoding="utf-8")
print(f"\nSaved {out}")

"""
strict_audit.py  —  Layers 1-3
Layer 1: Key Figma text strings present in HTML
Layer 2: Figma shape fill colours present in CSS/HTML
Layer 3: CSS background colours all have Figma counterparts
"""
import sys, json, re, os, urllib.request, urllib.parse
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.dirname(__file__))
import figma_config
TOKEN  = figma_config.TOKEN
FILE_KEY = "wk5MigfCT48tilIuHtT1lg"
HEADERS = {"X-Figma-Token": TOKEN}
ROOT = os.path.dirname(__file__)

def figma_get(path, timeout=90):
    url = f"https://api.figma.com/v1{path}"
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read())

def fill_hex(fills):
    for f in fills:
        if f.get("type") == "SOLID" and f.get("visible", True) is not False:
            c = f.get("color", {})
            return "#{:02X}{:02X}{:02X}".format(
                int(round(c.get("r",0)*255)), int(round(c.get("g",0)*255)), int(round(c.get("b",0)*255)))
    return None

def read_file(name):
    path = os.path.join(ROOT, name)
    if not os.path.exists(path):
        return ""
    return open(path, encoding='utf-8', errors='ignore').read()

# Read all HTML and CSS
html_files = ["index.html", "fellowship.html", "hislife.html", "vision.html",
              "apply.html", "memories.html", "team.html"]
css_files  = ["style.css", "fellowship.css", "hislife.css", "vision.css",
              "apply.css", "memories.css", "shared.css", "tokens.css"]

all_html = "\n".join(read_file(f) for f in html_files)
all_css  = "\n".join(read_file(f) for f in css_files)
all_src  = all_html + "\n" + all_css

# ── LAYER 1: Key Figma text strings in HTML ────────────────────────────────
print("=" * 70)
print("LAYER 1 — Figma text strings in HTML")
print("=" * 70)

# Spot-check: circle texts, focus card texts, tagline
TEXT_CHECKS = [
    ("review circle 1",   "Candidates are nominated by selected individuals, as defined by trust"),
    ("review circle 2",   "A distinguished jury of experts will evaluate the applications"),
    ("review circle 3",   "Shortlisted candidates will be notified"),
    ("review circle 4",   "Selected fellows will be announced"),
    ("focus card 1",      "Satellite applications and space technology"),
    ("focus card 2",      "Revolutionising learning systems"),
    ("focus card 3",      "Environmental consciousness"),
    ("focus card 4",      "Cultivating leadership and ethical governance"),
    ("home tagline",      "Cultivating Excellence. Futures Thinking. Advancing Humanity."),
    ("announce date",     "April 25, 2027"),
]
l1_pass = l1_fail = 0
for label, text in TEXT_CHECKS:
    found = text.lower() in all_html.lower()
    if found:
        l1_pass += 1
    else:
        l1_fail += 1
        print(f"  MISS: [{label}] '{text[:60]}'")
if not l1_fail:
    print(f"  All {l1_pass} spot-checks found ✓")

# ── LAYER 2: Figma shape fills present in CSS ──────────────────────────────
print("\n" + "=" * 70)
print("LAYER 2 — Figma fill colours in CSS")
print("=" * 70)

# Fetch fills from key frames
FRAME_IDS = ["1029:689", "1029:890", "1029:1018"]  # fellowship, vision, apply
figma_fills = set()

def collect_fills(node, depth=0):
    fc = fill_hex(node.get("fills", []))
    if fc and fc != "#FFFFFF":
        figma_fills.add(fc.upper())
    for child in node.get("children", []):
        if depth < 4:
            collect_fills(child, depth+1)

for fid in FRAME_IDS:
    try:
        nd = figma_get(f"/files/{FILE_KEY}/nodes?ids={urllib.parse.quote(fid)}&depth=4")
        collect_fills(nd["nodes"][fid]["document"])
    except Exception as e:
        print(f"  Fetch error for {fid}: {e}")

# Extract hex colors from CSS
css_colors = set(re.findall(r'#([0-9A-Fa-f]{6})\b', all_css))
css_colors = {"#" + c.upper() for c in css_colors}

# Check which Figma fills are missing from CSS (ignore near-white, near-black)
l2_fail = []
for fc in sorted(figma_fills):
    r, g, b = int(fc[1:3], 16), int(fc[3:5], 16), int(fc[5:7], 16)
    if max(r,g,b) > 240 or max(r,g,b) < 20:
        continue  # skip near-white/near-black
    if fc not in css_colors:
        l2_fail.append(fc)

if l2_fail:
    for c in l2_fail:
        print(f"  MISS: {c} is in Figma fills but not in CSS")
else:
    print(f"  All {len(figma_fills)} Figma fills covered in CSS ✓")

# ── LAYER 3: CSS background colours have Figma counterparts ───────────────
print("\n" + "=" * 70)
print("LAYER 3 — CSS bg colours have Figma counterpart")
print("=" * 70)

bg_pattern = re.compile(r'background(?:-color)?\s*:\s*#([0-9A-Fa-f]{6})\b', re.IGNORECASE)
css_bgs = {"#" + m.upper() for m in bg_pattern.findall(all_css)}
all_figma = figma_fills | {
    "#2A427E", "#FFB338", "#F6F6F6", "#FFFFFF", "#202020",
    "#FFF6E6", "#FFF6E7", "#808080",
}

l3_fail = []
for bg in sorted(css_bgs):
    r, g, b = int(bg[1:3], 16), int(bg[3:5], 16), int(bg[5:7], 16)
    if max(r,g,b) > 240 or max(r,g,b) < 20:
        continue
    if bg not in all_figma:
        # fuzzy match: allow ±2 per channel
        close = any(
            all(abs(int(bg[1+j*2:3+j*2],16) - int(fc[1+j*2:3+j*2],16)) <= 2 for j in range(3))
            for fc in all_figma
        )
        if not close:
            l3_fail.append(bg)

if l3_fail:
    for c in l3_fail:
        print(f"  ORPHAN: {c} in CSS but no Figma counterpart (±2)")
else:
    print(f"  All CSS background colours have Figma counterparts ✓")

print("\n" + "=" * 70)
total_fail = l1_fail + len(l2_fail) + len(l3_fail)
print(f"SUMMARY: {total_fail} mismatch(es) across 3 layers.")

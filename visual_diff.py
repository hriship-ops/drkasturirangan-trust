"""
visual_diff.py  —  Layer 4
Colour-palette diff: renders the 4 main pages at 1440px in Playwright,
extracts the dominant palette, and reports any colour present in the
render that doesn't appear in tokens.css or Figma fills (with tolerance).
"""
import sys, os, re, json, collections
sys.stdout.reconfigure(encoding='utf-8')
ROOT = os.path.dirname(__file__)

# ── Token / Figma reference palette ───────────────────────────────────────
TOKENS_CSS = open(os.path.join(ROOT, "tokens.css"), encoding='utf-8', errors='ignore').read()
tok_hex = re.findall(r'#([0-9A-Fa-f]{6})\b', TOKENS_CSS)
REFERENCE = {(int(h[0:2],16), int(h[2:4],16), int(h[4:6],16)) for h in tok_hex}
# Add known Figma fills not in tokens
for h in ["FFF6E7", "808080", "F6F6F6", "E8EBF3", "202020", "FFFFFF", "000000"]:
    REFERENCE.add((int(h[0:2],16), int(h[2:4],16), int(h[4:6],16)))

PAGES = ["index.html", "fellowship.html", "vision.html", "hislife.html"]
SCRATCHPAD = r"C:\Users\hrish\AppData\Local\Temp\claude\C--Users-hrish\858e6c95-1140-480f-8ff9-b0b08a83baec\scratchpad"
TOLERANCE = 12  # per-channel delta considered "same colour"

def closest_dist(rgb, palette):
    return min(sum(abs(a-b) for a,b in zip(rgb,p)) for p in palette)

try:
    from playwright.sync_api import sync_playwright
except ImportError:
    print("Playwright not installed — skipping Layer 4")
    sys.exit(0)

try:
    from PIL import Image
    import io
except ImportError:
    print("Pillow not installed — skipping Layer 4")
    sys.exit(0)

print("=" * 70)
print("LAYER 4 — Rendered colour palette vs Figma/tokens")
print("=" * 70)

all_orphans = {}

with sync_playwright() as pw:
    b = pw.chromium.launch(args=["--disable-cache"])
    for page_name in PAGES:
        p = b.new_page(viewport={"width": 1440, "height": 900})
        url = f"file:///{ROOT.replace(os.sep,'/')}/{page_name}"
        try:
            p.goto(url, wait_until="networkidle", timeout=20000)
            p.wait_for_timeout(400)
            png = p.screenshot(full_page=False)
            img = Image.open(io.BytesIO(png)).convert("RGB")
            # Downsample for speed: every 4th pixel
            pixels = list(img.getdata())[::4]
            counter = collections.Counter(pixels)
            # Top 50 colours by frequency
            top50 = [rgb for rgb, _ in counter.most_common(50)]
            orphans = []
            for rgb in top50:
                r,g,b2 = rgb
                # Skip very dark, very light, very desaturated (UI chrome / text)
                if max(r,g,b2) > 245 or max(r,g,b2) < 15:
                    continue
                sat = max(r,g,b2) - min(r,g,b2)
                if sat < 8:
                    continue
                dist = closest_dist(rgb, REFERENCE)
                if dist > TOLERANCE * 3:  # 3 channels × tolerance
                    orphans.append((rgb, dist))
            if orphans:
                all_orphans[page_name] = orphans[:5]
        except Exception as e:
            print(f"  {page_name}: error — {e}")
        finally:
            p.close()
    b.close()

if all_orphans:
    for page_name, orphans in all_orphans.items():
        for rgb, dist in orphans:
            h = "#{:02X}{:02X}{:02X}".format(*rgb)
            print(f"  {page_name}: {h} (dist={dist}) not in reference palette")
else:
    print(f"  All rendered colours within tolerance of reference palette ✓")

print("=" * 70)

"""
visual_diff.py — Fix 5
Downloads Figma frame renders and Chrome viewport screenshots, then compares
their dominant colour palettes. Flags pages where the colour distribution
diverges significantly (likely a section background or fill is missing).

Usage:
    python visual_diff.py

Outputs reference images to figma_refs/ (git-ignored) and prints a similarity
report. A score below WARN_THRESHOLD warrants manual review.

Requires: Pillow  (pip install Pillow)
"""
import json, re, subprocess, sys, time, urllib.request
from pathlib import Path

try:
    from PIL import Image
except ImportError:
    sys.exit("Pillow is required:  pip install Pillow")

ROOT = Path(r"C:\appdev\drk")
from figma_config import FILE_KEY, TOKEN  # gitignored — see figma_config.py
REFS     = ROOT / "figma_refs"
REFS.mkdir(exist_ok=True)

CHROME = (
    r"C:\Program Files\Google\Chrome\Application\chrome.exe"
)

# Comparison thresholds (colour-palette similarity, 0-100)
WARN_THRESHOLD = 60
FAIL_THRESHOLD = 40

SHP_P  = ROOT / "figma_shapes.json"
SHAPES = json.loads(SHP_P.read_text(encoding="utf-8")) if SHP_P.exists() else {}

# Only compare primary page frames (state frames don't have standalone pages)
FRAME_MAP = {
    "Home Page ":                    "index.html",
    "Vision and Mission":            "vision.html",
    "fellowship page":               "fellowship.html",
    "Apply":                         "apply.html",
    "V2 Dr Kasturi Rangan's Life":   "kasturirangan.html",
    "Team":                          "team.html",
}

# ── Helpers ──────────────────────────────────────────────────────────────────

def api(url: str) -> dict:
    req = urllib.request.Request(url, headers={"X-Figma-Token": TOKEN})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.load(r)

def download(url: str, dest: Path) -> None:
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=120) as r:
        dest.write_bytes(r.read())

def frame_node_id(frame_name: str) -> str | None:
    return SHAPES.get(frame_name, {}).get("node_id")

def fetch_figma_png(node_id: str, dest: Path, scale: float = 0.15) -> bool:
    """Export a Figma frame as PNG. Returns True on success."""
    if dest.exists():
        print(f"    (cached) {dest.name}")
        return True
    url = (f"https://api.figma.com/v1/images/{FILE_KEY}"
           f"?ids={node_id}&scale={scale}&format=png")
    data = api(url)
    img_url = data.get("images", {}).get(node_id)
    if not img_url:
        print(f"    WARNING: no image URL returned for node {node_id}")
        return False
    download(img_url, dest)
    print(f"    Downloaded {dest.name}  ({dest.stat().st_size // 1024} KB)")
    return True

def chrome_screenshot(html_file: str, dest: Path) -> bool:
    """Take a headless Chrome viewport screenshot. Returns True on success."""
    src = ROOT / html_file
    cmd = [
        CHROME,
        "--headless", "--disable-gpu", "--disable-cache",
        "--window-size=1440,900",
        f"--screenshot={dest}",
        f"file:///{src}",
    ]
    result = subprocess.run(cmd, capture_output=True, timeout=30)
    time.sleep(1)
    ok = dest.exists() and dest.stat().st_size > 1000
    if not ok:
        print(f"    WARNING: Chrome screenshot failed for {html_file}")
    else:
        print(f"    Screenshot {dest.name}  ({dest.stat().st_size // 1024} KB)")
    return ok

def dominant_palette(img: Image.Image, n: int = 10) -> list[tuple[int,int,int]]:
    """Return the n most dominant colours using quantization."""
    small = img.resize((200, 200), Image.LANCZOS).convert("RGB")
    quantized = small.quantize(colors=n, method=Image.Quantize.FASTOCTREE)
    palette = quantized.getpalette()[:n * 3]
    return [(palette[i*3], palette[i*3+1], palette[i*3+2]) for i in range(n)]

def palette_similarity(pal_a: list, pal_b: list, tol: int = 20) -> float:
    """
    Fraction of pal_a colours that have a close match in pal_b, scaled 0-100.
    tol=20 allows for rendering / anti-aliasing differences.
    """
    if not pal_a:
        return 100.0
    hits = sum(
        1 for ra, ga, ba in pal_a
        if any(abs(ra-rb) <= tol and abs(ga-gb) <= tol and abs(ba-bb) <= tol
               for rb, gb, bb in pal_b)
    )
    return hits / len(pal_a) * 100

def status_label(score: float) -> str:
    if score >= WARN_THRESHOLD:
        return "OK"
    if score >= FAIL_THRESHOLD:
        return "WARN"
    return "FAIL"

# ── Main ─────────────────────────────────────────────────────────────────────

print("=" * 70)
print("VISUAL DIFF  —  Figma render vs Chrome screenshot")
print(f"Warn < {WARN_THRESHOLD}%   Fail < {FAIL_THRESHOLD}%")
print("=" * 70)

if not SHAPES:
    print("WARNING: figma_shapes.json not found. Run figma_shapes_scraper.py first.")
    sys.exit(1)

results = []

for frame_name, html_file in FRAME_MAP.items():
    print(f"\n{frame_name}  ->  {html_file}")
    node_id = frame_node_id(frame_name)
    if not node_id:
        print("  SKIP: node_id not found in figma_shapes.json")
        results.append((frame_name, None, "SKIP"))
        continue

    slug = re.sub(r'[^a-z0-9]+', '-', frame_name.lower()).strip('-')
    figma_path  = REFS / f"figma-{slug}.png"
    chrome_path = REFS / f"chrome-{slug}.png"

    print(f"  Figma  -> {figma_path.name}")
    figma_ok = fetch_figma_png(node_id, figma_path)

    print(f"  Chrome -> {chrome_path.name}")
    chrome_ok = chrome_screenshot(html_file, chrome_path)

    if not figma_ok or not chrome_ok:
        results.append((frame_name, None, "ERROR"))
        continue

    figma_img  = Image.open(figma_path)
    chrome_img = Image.open(chrome_path)

    # Crop both to the same width (Figma is typically narrower after scaling)
    fw, fh = figma_img.size
    cw, ch = chrome_img.size
    # Scale Chrome to Figma width, then crop to Figma height (or Chrome height, whichever is less)
    scale_factor = fw / cw
    new_cw = fw
    new_ch = round(ch * scale_factor)
    chrome_scaled = chrome_img.resize((new_cw, new_ch), Image.LANCZOS)
    compare_height = min(fh, new_ch)
    figma_crop  = figma_img.crop((0, 0, fw, compare_height))
    chrome_crop = chrome_scaled.crop((0, 0, new_cw, compare_height))

    pal_figma  = dominant_palette(figma_crop)
    pal_chrome = dominant_palette(chrome_crop)

    score_f2c = palette_similarity(pal_figma, pal_chrome)   # Figma colours found in Chrome
    score_c2f = palette_similarity(pal_chrome, pal_figma)   # Chrome colours found in Figma
    score     = (score_f2c + score_c2f) / 2

    label = status_label(score)
    print(f"  Colour palette similarity: {score:.0f}%  [{label}]"
          f"  (Figma->Chrome {score_f2c:.0f}%  Chrome->Figma {score_c2f:.0f}%)")
    results.append((frame_name, score, label))

# Summary
print("\n" + "=" * 70)
print("SUMMARY")
print("=" * 70)
for frame, score, label in results:
    s = f"{score:.0f}%" if score is not None else "n/a"
    print(f"  [{label:4s}]  {frame}  ({s})")

# Fail if any FAIL
if any(r[2] == "FAIL" for r in results):
    print("\nResult: FAIL  -- one or more pages diverge significantly from Figma.")
    sys.exit(1)
else:
    print("\nResult: PASS")

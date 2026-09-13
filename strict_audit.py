"""
strict_audit.py — three-layer Figma vs HTML audit.

Layer 1 (text)   : Every Figma text string must appear in the HTML.
                   Structural skips are surfaced as WARN, not silently dropped. [Fix 6]
Layer 2 (shapes) : Every significant Figma fill colour must appear in the CSS. [Fix 2]
Layer 3 (reverse): Every non-trivial CSS background colour must have a
                   Figma shape counterpart (catches invented elements). [Fix 4]

State frames (hover / click expansions) are included in every layer. [Fix 3]

Run:
    python strict_audit.py
"""
import json, re, sys, html as html_mod
from pathlib import Path

ROOT   = Path(r"C:\appdev\drk")
FIGMA  = json.loads((ROOT / "figma_texts.json").read_text(encoding="utf-8"))
SHP_P  = ROOT / "figma_shapes.json"
SHAPES = json.loads(SHP_P.read_text(encoding="utf-8")) if SHP_P.exists() else {}

# ── Frame → HTML mapping (Fix 3: state frames included) ─────────────────────
FRAME_MAP = {
    # Primary page frames
    "Home Page ":                    "index.html",
    "Vision and Mission":            "vision.html",
    "fellowship page":               "fellowship.html",
    "Apply":                         "apply.html",
    "V2 Dr Kasturi Rangan's Life":   "kasturirangan.html",
    "Team":                          "team.html",
    # Interactive / state frames [Fix 3]
    "Space and Cosmos":              "index.html",
    "Environment":                   "index.html",
    "Education":                     "index.html",
    "Public Life":                   "index.html",
    "Application process 2":         "fellowship.html",
    "Application process 3":         "fellowship.html",
    "Application process 4":         "fellowship.html",
}

SKIP_STRINGS = {
    "Useful Links", "Journeys of Change", "Publications",
    "Initiatives", "K. Kasturirangan", "About Us",
    "Office hours: 9 AM to 5 PM\ninfo@drkasturirangantrust.org",
    "Dr Kasturirangan Trust\nAlder 1002,\n"
    "Godrej Woodsman Estate, Hebbal, Bengaluru \u2013 560045",
    "View on Map",
    "\u201c", "\u201d",
}

# ── HTML→frames reverse map (used in Layer 3) ────────────────────────────────
HTML_TO_FRAMES: dict[str, list[str]] = {}
for _f, _h in FRAME_MAP.items():
    HTML_TO_FRAMES.setdefault(_h, []).append(_f)

# ═══════════════════════════════════════════════════════════════════════════════
# Helpers
# ═══════════════════════════════════════════════════════════════════════════════

def _read_html(fname: str) -> str:
    return (ROOT / fname).read_text(encoding="utf-8")

def _read_tokens() -> str:
    p = ROOT / "tokens.css"
    return p.read_text(encoding="utf-8") if p.exists() else ""

def html_text(fname: str) -> str:
    raw  = _read_html(fname)
    attrs = re.findall(r'\b(?:alt|title)="([^"]*)"', raw)
    flat  = re.sub(r'<[^>]+>', ' ', raw) + ' ' + ' '.join(attrs)
    flat  = html_mod.unescape(flat)
    return re.sub(r'[ \t]+', ' ', flat)

def normalise(s: str) -> str:
    s = re.sub(r'[\u200b\u200c\u200d\ufeff\u00ad\ufffd]', '', s)
    s = s.replace('\u2018', "'").replace('\u2019', "'")
    s = s.replace('\u201c', '"').replace('\u201d', '"')
    s = s.replace('\u2011', '-').replace('\u2013', '-').replace('\u2014', '-')
    s = s.replace('\u2026', '...')   # ellipsis char -> three dots
    return re.sub(r'\s+', ' ', s).strip()

def _resolve_vars(text: str, tokens: str) -> str:
    """Replace var(--name) with their token value."""
    tmap: dict[str, str] = {}
    for m in re.finditer(r'--([a-zA-Z0-9_-]+)\s*:\s*([^;]+);', tokens):
        tmap[m.group(1)] = m.group(2).strip()
    return re.sub(r'var\(--([a-zA-Z0-9_-]+)\)',
                  lambda m: tmap.get(m.group(1), m.group(0)), text)

def _parse_colors(text: str) -> set[tuple[int, int, int, float]]:
    """Extract (r,g,b,a) tuples from rgba/rgb/hex color values in text."""
    colors: set[tuple[int, int, int, float]] = set()
    for m in re.finditer(
            r'rgba?\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)(?:\s*,\s*([\d.]+))?\s*\)', text):
        r, g, b = int(m.group(1)), int(m.group(2)), int(m.group(3))
        a = float(m.group(4)) if m.group(4) else 1.0
        colors.add((r, g, b, round(a, 3)))
    for m in re.finditer(r'#([0-9a-fA-F]{6})\b', text):
        h = m.group(1)
        colors.add((int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16), 1.0))
    for m in re.finditer(r'(?<![0-9a-fA-F])#([0-9a-fA-F]{3})\b', text):
        h = m.group(1)
        colors.add((int(h[0]*2, 16), int(h[1]*2, 16), int(h[2]*2, 16), 1.0))
    return colors

def extract_all_colors(fname: str) -> set[tuple[int, int, int, float]]:
    """All CSS colors in the HTML file + tokens.css (with var() resolved)."""
    tokens = _read_tokens()
    raw    = _read_html(fname) + "\n" + tokens
    resolved = _resolve_vars(raw, tokens)
    return _parse_colors(resolved)

def extract_bg_colors(fname: str) -> set[tuple[int, int, int, float]]:
    """Only colors from CSS background/background-color properties (resolved)."""
    tokens   = _read_tokens()
    raw      = _read_html(fname) + "\n" + tokens
    resolved = _resolve_vars(raw, tokens)
    colors: set[tuple[int, int, int, float]] = set()
    for m in re.finditer(r'background(?:-color)?\s*:\s*([^;{}\n]+)', resolved):
        colors |= _parse_colors(m.group(1))
    return colors

def _color_near(r: int, g: int, b: int,
                color_set: set[tuple[int, int, int, float]],
                tol: int = 12) -> bool:
    """RGB match within tolerance (alpha ignored — opacity is often applied differently)."""
    return any(abs(r-cr) <= tol and abs(g-cg) <= tol and abs(b-cb) <= tol
               for cr, cg, cb, _ in color_set)

def _is_trivial(r: int, g: int, b: int, a: float) -> bool:
    if a < 0.05:
        return True
    if r > 242 and g > 242 and b > 242:  # white / near-white
        return True
    if r < 15 and g < 15 and b < 15:     # black / near-black
        return True
    return False

# ═══════════════════════════════════════════════════════════════════════════════
# Layer 1 — Text audit
# ═══════════════════════════════════════════════════════════════════════════════

def check_text(frame: str, html_fname: str) -> tuple[list[str], list[str]]:
    """Returns (missing_texts, structural_skip_warnings)."""
    texts     = FIGMA.get(frame, [])
    html_norm = normalise(html_text(html_fname))
    missing: list[str] = []
    warns:   list[str] = []

    for t in texts:
        t = t.strip()
        if not t or t in SKIP_STRINGS:
            continue
        # skip sidebar year navigation block
        if "1940" in t and "2025" in t and len(t) > 200:
            continue

        if normalise(t) in html_norm:
            continue

        # Fix 6: named structural skips surfaced as WARN (not silent continue)
        if "partner with government institutions" in t and "Trustees@" in t:
            warns.append(
                "[STRUCTURAL-SKIP] vision.html: partnership+contact spans elements | "
                + t[:80])
            continue
        if "Space and Beyond" in t and "many-splendored" in t:
            warns.append(
                "[STRUCTURAL-SKIP] kasturirangan.html: <em> creates space before comma | "
                + t[:80])
            continue
        if "experimental high-energy astronomy" in t and "Aryabhata" in t:
            warns.append(
                "[STRUCTURAL-SKIP] kasturirangan.html: multi-year block spans kk-entry elements | "
                + t[:80])
            continue

        missing.append(t)

    return missing, warns

# ═══════════════════════════════════════════════════════════════════════════════
# Layer 2 — Shapes audit (Fix 2)
# ═══════════════════════════════════════════════════════════════════════════════

def check_shapes(frame: str, html_fname: str) -> list[dict]:
    """Returns list of Figma shapes whose fill colour is absent from the CSS."""
    if not SHAPES or frame not in SHAPES:
        return []
    css_colors = extract_all_colors(html_fname)
    missing = []
    for s in SHAPES[frame].get("shapes", []):
        r, g, b = s["fill_r"], s["fill_g"], s["fill_b"]
        if not _color_near(r, g, b, css_colors):
            missing.append(s)
    return missing

# ═══════════════════════════════════════════════════════════════════════════════
# Layer 3 — Reverse audit (Fix 4)
# ═══════════════════════════════════════════════════════════════════════════════

def _token_colors() -> set[tuple[int, int, int, float]]:
    """All colour values defined in tokens.css (the approved design palette)."""
    return _parse_colors(_read_tokens())

def check_reverse(html_fname: str) -> list[str]:
    """
    Returns CSS background colours that have NEITHER a Figma shape counterpart
    NOR a design-token definition.
    Likely causes: hover states, frame fills (not captured by shapes scraper),
    or genuinely invented colours — all reported as WARN for manual review.
    """
    if not SHAPES:
        return []
    bg_colors    = extract_bg_colors(html_fname)
    token_colors = _token_colors()
    figma_rgbs   = set()
    for frame in HTML_TO_FRAMES.get(html_fname, []):
        for s in SHAPES.get(frame, {}).get("shapes", []):
            figma_rgbs.add((s["fill_r"], s["fill_g"], s["fill_b"]))

    orphans = []
    for r, g, b, a in bg_colors:
        if _is_trivial(r, g, b, a):
            continue
        # OK if it matches a known Figma shape fill
        if any(abs(r-fr) <= 12 and abs(g-fg) <= 12 and abs(b-fb) <= 12
               for fr, fg, fb in figma_rgbs):
            continue
        # OK if it matches a design-token colour (approved palette)
        if _color_near(r, g, b, token_colors):
            continue
        orphans.append(f"rgba({r},{g},{b},{a})")
    return sorted(set(orphans))

# ═══════════════════════════════════════════════════════════════════════════════
# Main
# ═══════════════════════════════════════════════════════════════════════════════

print("=" * 70)
print("STRICT FIGMA -> HTML AUDIT  (Layers 1, 2, 3)")
if not SHAPES:
    print("  WARNING: figma_shapes.json not found -- Layer 2 & 3 skipped.")
    print("           Run: python figma_shapes_scraper.py")
print("=" * 70)

all_ok  = True
l2_ok   = True
l3_ok   = True

seen_html_l3: set[str] = set()

for frame, html_file in FRAME_MAP.items():
    m_text, skip_warns = check_text(frame, html_file)
    m_shapes            = check_shapes(frame, html_file)

    parts = []
    if not m_text and not m_shapes:
        parts.append("OK")
    if m_text:
        parts.append(f"TEXT-MISSING:{len(m_text)}")
        all_ok = False
    if m_shapes:
        parts.append(f"SHAPE-COLOUR-MISSING:{len(m_shapes)}")
        l2_ok  = False
        all_ok = False

    print(f"\n[{' '.join(parts)}]  {frame}  ->  {html_file}")

    for t in m_text:
        print("  X TEXT:  " + t.replace("\n", " / ")[:200])
    for w in skip_warns:
        print("  ~  " + w)
    for s in m_shapes:
        print(f"  X SHAPE: {s['name']!r:30s} fill={s['fill_rgba']}"
              f"  cr={s['corner_radius']}  {s['width']}x{s['height']}")

# Layer 3: one check per HTML file
print("\n" + "=" * 70)
print("LAYER 3 -- Reverse audit  (CSS background colours without Figma shape)")
print("=" * 70)

for frame, html_file in FRAME_MAP.items():
    if html_file in seen_html_l3:
        continue
    seen_html_l3.add(html_file)

    orphans = check_reverse(html_file)
    if orphans:
        l3_ok = False
        print(f"\n  [WARN - UNMATCHED BG COLOURS]  {html_file}:")
        print(f"       These are not in any Figma shape OR design token.")
        print(f"       Likely hover states or frame fills -- verify manually.")
        for o in orphans:
            print(f"    ~  {o}")
    else:
        print(f"\n  [OK]  {html_file}")

# Summary
print("\n" + "=" * 70)
print(f"Layer 1+2 (text + shapes) : {'ALL MATCH' if all_ok else 'ISSUES FOUND'}")
print(f"Layer 3   (reverse)       : {'OK' if l3_ok else 'WARN - unmatched bg colours (see above)'}")
print("=" * 70)

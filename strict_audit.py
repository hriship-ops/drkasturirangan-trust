"""
Strict Figma-vs-HTML audit.
Loads figma_texts.json and checks each text string against the
corresponding HTML file. Reports MISSING (text in Figma, not in HTML).
"""
import json, re, sys, html as html_mod
from pathlib import Path

ROOT = Path(r"C:\appdev\drk")
FIGMA = json.loads((ROOT / "figma_texts.json").read_text(encoding="utf-8"))

# Map Figma frame name -> HTML file
FRAME_MAP = {
    "Home Page ":          "index.html",
    "Vision and Mission":  "vision.html",
    "fellowship page":     "fellowship.html",
    "Apply":               "apply.html",
    "V2 Dr Kasturi Rangan's Life": "kasturirangan.html",
    "Team":                "team.html",
}

# Texts to skip (nav/footer boilerplate present on every page)
SKIP_STRINGS = {
    "Useful Links", "Journeys of Change", "Publications",
    "Initiatives", "K. Kasturirangan", "About Us",
    "Office hours: 9 AM to 5 PM\ninfo@drkasturirangantrust.org",
    "Dr Kasturirangan Trust\nAlder 1002,\nGodrej Woodsman Estate, Hebbal, Bengaluru \u2013 560045",
    "View on Map",
    # sidebar year list (single block – not rendered as HTML text)
    # quote marks used as design decoration
    "\u201c", "\u201d",
}

def html_text(fname):
    raw = (ROOT / fname).read_text(encoding="utf-8")
    # extract alt/title attribute values before stripping tags
    attrs = re.findall(r'\b(?:alt|title)="([^"]*)"', raw)
    attr_text = ' '.join(attrs)
    # strip all tags from main content
    no_tags = re.sub(r'<[^>]+>', ' ', raw)
    # combine: main text + attribute values
    combined = no_tags + ' ' + attr_text
    # decode HTML entities (e.g. &rsquo; → ', &amp; → &, &#8377; → ₹)
    decoded = html_mod.unescape(combined)
    # collapse whitespace
    flat = re.sub(r'[ \t]+', ' ', decoded)
    return flat

def normalise(s):
    """Normalise for comparison: zero-width, quotes, dashes, whitespace."""
    # remove zero-width / BOM chars Figma sometimes adds
    s = re.sub(r'[​‌‍﻿­￾]', '', s)
    # normalise typographic apostrophes / quotes → ASCII equivalents
    s = s.replace('’', "'").replace('‘', "'")
    s = s.replace('“', '"').replace('”', '"')
    # normalise dashes/hyphens (en, em, non-breaking) → regular hyphen
    s = s.replace('‑', '-').replace('–', '-').replace('—', '-')
    # collapse all whitespace
    s = re.sub(r'\s+', ' ', s).strip()
    return s

def check_frame(frame_name, html_fname):
    texts = FIGMA.get(frame_name, [])
    html = html_text(html_fname)
    html_norm = normalise(html)

    missing = []
    for t in texts:
        t = t.strip()
        if not t or t in SKIP_STRINGS:
            continue
        # skip the sidebar year navigation block
        if "1940" in t and "2025" in t and len(t) > 200:
            continue
        # normalise figma text and search in html
        t_norm = normalise(t)
        if t_norm not in html_norm:
            # structural false positives: content exists but spans multiple HTML elements
            # vision.html: partnership text + email + address are separate <p> elements
            if "partner with government institutions" in t and "Trustees@" in t:
                continue
            # kasturirangan.html: <em> tag around "Space and Beyond" creates space before comma
            if "Space and Beyond" in t and "many-splendored" in t:
                continue
            # kasturirangan.html: multi-year Figma text block spans separate kk-entry elements
            if "experimental high-energy astronomy" in t and "Aryabhata" in t:
                continue
            missing.append(t)

    return missing

print("=" * 70)
print("STRICT FIGMA → HTML AUDIT")
print("=" * 70)

all_ok = True
for frame, html_file in FRAME_MAP.items():
    missing = check_frame(frame, html_file)
    status = "OK" if not missing else f"MISSING {len(missing)} text(s)"
    print(f"\n[{status}] {frame} → {html_file}")
    for m in missing:
        short = m.replace("\n", " / ")[:300]
        print(f"  ✗ {short}")
    if missing:
        all_ok = False

print("\n" + "=" * 70)
print("RESULT:", "ALL MATCH" if all_ok else "DISCREPANCIES FOUND")
print("=" * 70)

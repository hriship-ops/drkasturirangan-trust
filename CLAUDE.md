# Dr Kasturirangan Trust — Claude Code Conventions

## Figma credentials
- File key and token are stored in `figma_config.py` (gitignored — never commit).
- API base: `https://api.figma.com/v1`

## Fix 1 — Fetch-before-implement (mandatory)

Before writing any CSS or HTML for a new section or component, run a
Figma node fetch for that frame first. Print every RECTANGLE/ELLIPSE
with its fill colour, cornerRadius, and dimensions. Use those exact
numbers in the code. Never design from assumption.

```python
# Quick fetch template
import urllib.request, json
from figma_config import FILE_KEY, TOKEN  # gitignored
NODE_ID = "<id>"   # replace
url = f"https://api.figma.com/v1/files/{FILE_KEY}/nodes?ids={NODE_ID}"
req = urllib.request.Request(url, headers={"X-Figma-Token": TOKEN})
with urllib.request.urlopen(req, timeout=60) as r:
    data = json.load(r)
```

## Audit workflow

Run all three layers after every implementation session:

```
python strict_audit.py        # Layers 1-3: text, shapes, reverse
python visual_diff.py         # Layer 4: color-palette diff vs Figma renders
```

Layer | Checks | Script
------|--------|-------
1 | Figma text strings present in HTML | `strict_audit.py`
2 | Figma shape fill colours present in CSS | `strict_audit.py`
3 | CSS background colours all have a Figma counterpart | `strict_audit.py`
4 | Rendered page colour palette matches Figma export | `visual_diff.py`

## Git commits

- Author: hrishi only — no `Co-Authored-By` line, ever.
- Commit via `commitmsg.txt` → `git commit -F commitmsg.txt` → delete file.

## Headless Chrome screenshots

```
chrome.exe --headless --disable-gpu --disable-cache --window-size=1440,900 --screenshot="out.png" "file:///C:/appdev/drk/page.html"
```
Use `--disable-cache` only — no `--incognito` (blocks `file://`).

## Design tokens (tokens.css)

Key tokens:
- `--c-primary: #2a427e` — navy
- `--c-accent: #ffb338` — amber (solid)
- `--c-amber-bg: rgba(255,179,56,0.8)` — amber with opacity (pill backgrounds)
- `--font-deco: Agdasima` — display/decorative
- `--font-main: Afacad` — body

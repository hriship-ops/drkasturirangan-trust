---
name: figma-to-html
description: This skill should be used when the user asks to implement, audit, compare, or fix HTML/CSS against a Figma design. Applies to tasks like "check Figma fidelity", "replicate the Figma design", "audit this page against Figma", "fix this to match Figma", or any task that involves reading a Figma file and translating it into HTML/CSS. Covers the REST API workflow, what to fetch, what is commonly missed, and the no-invention rule.
version: 1.0.0
---

# Figma → HTML Skill

**Rule zero: yours not to reason why — replicate Figma look and feel faithfully.**

Never substitute judgment for Figma data. Never invent content, sizes, colors, or states that are not explicitly present in the Figma node tree.

---

## 1. REST API — How to Fetch

### Credentials
Store in a gitignored file (never commit):
```python
# figma_config.py  ← in .gitignore
FILE_KEY = "..."   # from the Figma URL: figma.com/file/{FILE_KEY}/...
TOKEN    = "..."   # personal access token from Figma account settings
```

All scripts import from it:
```python
from figma_config import FILE_KEY, TOKEN
```

### Fetch a specific node (frame, component, group)
```python
import json, urllib.request

def fetch_node(node_id):
    url = f"https://api.figma.com/v1/files/{FILE_KEY}/nodes?ids={node_id}"
    req = urllib.request.Request(url, headers={"X-Figma-Token": TOKEN})
    with urllib.request.urlopen(req) as r:
        return json.loads(r.read())
```

Node IDs look like `1029:890`. Get them from the Figma URL when a frame is selected, or by listing all frames first (see below).

### List all frames in the file (to find node IDs)
```python
url = f"https://api.figma.com/v1/files/{FILE_KEY}"
req = urllib.request.Request(url, headers={"X-Figma-Token": TOKEN})
with urllib.request.urlopen(req) as r:
    data = json.loads(r.read())
pages = data["document"]["children"]
for page in pages:
    for frame in page.get("children", []):
        print(frame["id"], frame["name"])
```

### Walk all TEXT nodes in a frame
```python
def walk(node, rows):
    if node.get("type") == "TEXT":
        chars = node.get("characters", "").strip()
        if not chars:
            return
        style  = node.get("style", {})
        fs     = style.get("fontSize")
        fw     = style.get("fontWeight")
        fills  = node.get("fills", [])
        color  = get_color_hex(fills)   # see helper below
        bbox   = node.get("absoluteBoundingBox", {})
        x, y   = bbox.get("x", 0), bbox.get("y", 0)
        rows.append({"text": chars, "fontSize": fs, "fontWeight": fw,
                     "color": color, "x": x, "y": y})
    for child in node.get("children", []):
        walk(child, rows)

def get_color_hex(fills):
    for f in fills:
        if f.get("type") == "SOLID":
            c = f["color"]
            return "#{:02x}{:02x}{:02x}".format(
                round(c["r"]*255), round(c["g"]*255), round(c["b"]*255))
    return ""
```

### Convert absolute coordinates to frame-relative CSS
```
frame_x, frame_y = absoluteBoundingBox of the frame node
left_px  = node_x - frame_x
top_px   = node_y - frame_y
left_%   = left_px / frame_width * 100      # frame_width is typically 1440px
```

---

## 2. What to Fetch — Checklist per Element

For every element being implemented or audited, fetch:

| Property | Where in JSON | CSS mapping |
|---|---|---|
| Position (x, y) | `absoluteBoundingBox.x / .y` | `left`, `top` (absolute px or %) |
| Size (w, h) | `absoluteBoundingBox.width / .height` | `width`, `height` |
| Font size | `style.fontSize` | `font-size` |
| Font weight | `style.fontWeight` | `font-weight` |
| Line height | `style.lineHeightPx` | `line-height` (in px or unit-less ratio) |
| Letter spacing | `style.letterSpacing` | `letter-spacing` |
| Text content | `characters` | innerHTML |
| Fill color | `fills[0].color` → hex | `color` or `background` |
| Border radius | `cornerRadius` or `rectangleCornerRadii` | `border-radius` |
| Stroke | `strokes[0].color`, `strokeWeight` | `border` |
| Opacity | `opacity` | `opacity` |
| Blend mode | `blendMode` | `mix-blend-mode` |
| Gap / spacing | `itemSpacing` | `gap` |
| Padding | `paddingLeft/Right/Top/Bottom` | `padding` |
| Layout mode | `layoutMode` (HORIZONTAL/VERTICAL/NONE) | flex vs absolute |

---

## 3. What Is Easily Missed

### 3.1 Font sizes — the single most common error
- Always read `style.fontSize` from the node. Never estimate from visual appearance.
- Font sizes that do NOT appear in Figma are invalid and should not be used: 14px, 19px, 26px are known wrong values for the drk project.
- After any designer update, run a full text-node audit across all frames before touching any CSS.
- Minimum font size in most designs: 16px (nav links, small labels). Check before using smaller.

### 3.2 Font weight drift
- `400` = Regular, `500` = Medium, `700` = Bold — always match exactly.
- A heading that looks "bold" in a screenshot might be `500` (Medium), not `700`.

### 3.3 Hover states — only implement what Figma shows
- Check the Prototype tab and variant panel before adding any `:hover` CSS.
- If Figma has no hover variant → write no `:hover` rule.
- A hover state you invent can cause visual breakage (e.g., a white background image appearing on hover because the asset was meant for a different state).

### 3.4 Vector connectors and decorative lines
- VECTOR and LINE nodes in Figma = assets that need to be exported, not CSS borders.
- Common case: dashed curved connector between two callout pills (date pills, stat callouts).
- Walk all nodes and flag every `"type": "VECTOR"` or `"type": "LINE"` — each one needs: export at 2×, save to `assets/images/`, position with absolute CSS.
- Never substitute a CSS border or SVG inline guess for a Figma vector without exporting the actual asset.

### 3.5 Z-order / layer stack
- Figma's layer panel: bottom = z-index 0, top = z-index highest.
- Decorative elements (dots, waves, quote marks) often sit behind text in Figma — match that.
- Never set z-index by intuition; read the layer order.

### 3.6 Text that exists in Figma but wasn't visible in HTML
- Some text nodes in Figma are low-opacity overlays or secondary states — they still need to be in the HTML.
- Walk ALL text nodes, including inside groups and components. Don't rely on what is visually prominent.

### 3.7 Empty or placeholder rows
- If Figma shows a year row, a card slot, or a table row — build it in HTML even if it has no content text.
- Do not decide "there's no content so I'll omit this."

### 3.8 Absolute vs. relative coordinates
- Figma reports `absoluteBoundingBox` in canvas coordinates, not frame-relative.
- Always subtract the frame's own x/y to get the element's position within the frame.

### 3.9 Colors and fills
- SOLID fills are the common case. Also check GRADIENT fills — they don't reduce to a single hex.
- `opacity` on the node level multiplies with the fill color's alpha — account for both.
- Never hardcode a hex that doesn't come directly from a Figma fill or design token.

### 3.10 Text alignment and line breaks
- Check `style.textAlignHorizontal` (LEFT, CENTER, RIGHT) and apply `text-align`.
- For text with forced line breaks visible in Figma: use `<br>` at the exact break point, OR set `width` to cause natural breaking at 1440px viewport. Test at 1440px, not a narrower width.

---

## 4. Text Comparison — The No-Invention Rule

Before writing any text content in HTML:

1. Fetch the Figma node for that section.
2. Extract all `characters` values from TEXT nodes.
3. Paste exactly — punctuation, spacing, capitalization, line breaks.
4. Do not paraphrase, correct, expand, or "improve" text from Figma.
5. Do not add alt text, tooltips, or ARIA labels that aren't in Figma.
6. If a text field is empty in Figma, leave it empty in HTML.

**Invented content that has appeared and must be purged:**
- Timeline years or entries not present in Figma
- `alt` attributes invented from guessing what an image shows
- Hover text for images that have no hover state in Figma
- Placeholder copy invented to fill what looked like a gap

---

## 5. Layout Model — Figma Absolute vs. HTML Flow

**The baseline contract of any website: it must compose correctly at any viewport width, on any device, at any zoom level. Responsive layout is not optional.**

Figma's absolute pixel coordinates describe where something appears *at 1440px design width* — they are not CSS instructions. Translating them one-to-one as `position: absolute; left: Xpx` is wrong and produces layouts that break at every other viewport.

### Correct translation table

| Figma element | Wrong CSS | Correct CSS |
|---|---|---|
| Two elements side by side | `position: absolute; left: Xpx` | `display: flex; gap: Xpx` |
| Text beside image | Absolute coords | `grid-template-columns: 53% 1fr` |
| Fixed-width column (360px) | `width: 360px` | `flex: 1 1 300px; max-width: 360px` |
| Font size (36px from Figma) | `font-size: 36px` | `font-size: clamp(22px, 2.5vw, 36px)` |
| Padding/gap (58px from Figma) | `padding: 58px` | `padding: clamp(16px, 4vw, 58px)` |
| Decorative overlay element | `left: 154px` | `left: clamp(16px, 10.7vw, 200px)` |
| Fixed grid columns | `repeat(3, 360px)` | `repeat(3, 1fr)` |

### When to use `position: absolute`

Only for truly decorative elements that float over a background — quote marks, decorative dots, walking figures. Even then:
- `left` / `top` must use `vw` or `%`, never fixed `px`
- `width` / `height` must use `clamp()` or `vw`

### When to use flex / grid (structural layout)

Always — for any side-by-side or stacked layout that should reflow. Read from Figma:
- `layoutMode: "HORIZONTAL"` → `display: flex; flex-direction: row`
- `layoutMode: "VERTICAL"` → `display: flex; flex-direction: column`
- `itemSpacing` → `gap`
- `paddingLeft/Right/Top/Bottom` → `padding`

### Never use `display: none` as a responsive fix

Hiding an element at a breakpoint because it overlaps is a symptom that its positioning is wrong. Fix the positioning with fluid units instead. Only use `display: none` at genuine phone widths (≤480px) for elements that genuinely cannot fit.

---

## 6. Audit Workflow — Page-by-Page Fidelity Check

For each page:

```
1. Fetch the frame's full node tree (walk all TEXT nodes → collect text, fontSize, fontWeight, color)
2. Sort by y-coordinate (top-to-bottom reading order)
3. Compare against HTML line by line:
   a. Text content matches exactly
   b. font-size matches Figma fontSize
   c. font-weight matches Figma fontWeight
   d. color matches Figma fill hex
4. Flag every VECTOR/LINE node → verify it is exported and wired up in CSS
5. Check Prototype tab for hover states → verify no uninvented :hover rules exist
6. Confirm no text node in Figma is absent from HTML
```

Write a small Python script per audit (pattern: `figma_<page>_audit.py`). Never audit by eye alone.

---

## 7. Verification — Before Reporting "Done"

Every fix requires all three:

1. **Screenshot** the HTML at 1440px viewport (Chrome headless: `--disable-cache`, no `--incognito`, temp file in project folder — not `/tmp`).
2. **Crop** to the affected section.
3. **Explicit diff statement**: "Figma shows X at position Y with size Z — HTML now matches."

Do not report "looks good" without completing the diff. "Looks similar" is not a diff.

---

## 8. Responsive — After Implementing at 1440px

Test at: 1440px → 1280px → 1024px → 768px → 375px.

Fluid sizing pattern:
```css
/* Replace fixed px with clamp(min, vw-based, max) */
font-size: clamp(18px, 2.5vw, 36px);
padding: clamp(16px, 4vw, 58px);

/* Replace fixed-width grids with 1fr */
grid-template-columns: repeat(3, 1fr);  /* NOT repeat(3, 360px) */
```

Decorative elements (vectors, connectors, walking figures) that clip or overflow at narrow widths: `display: none` at the breakpoint where they break, not at a fixed px. Never hide primary content.

When a fix applies to a layout pattern (e.g., a 3-column grid), audit all pages for the same pattern and apply the fix everywhere.

---

## 9. Common Mistakes Reference

| Mistake | Rule |
|---|---|
| Setting font-size without fetching Figma's `style.fontSize` | Fetch first, always |
| Adding `:hover` CSS that doesn't exist in Figma | No hover without Figma Prototype tab confirmation |
| Missing a vector connector between callout elements | Walk all nodes; flag every VECTOR type |
| Adding timeline rows/years not in Figma | If Figma doesn't show it, HTML doesn't have it |
| Inventing alt text for images | Use `alt=""` unless Figma specifies text |
| Using `margin-left` to position something Figma places absolutely | Use `position: absolute; left: Xpx` |
| Reporting "done" without a screenshot + diff | Never — always screenshot and diff |
| Fixing one page's pattern, not all pages | Audit all pages for the same pattern |
| Not pushing after commit | Always `git push` immediately after `git commit`; verify with `git log` |
| Hardcoding colors not from Figma | All colors from tokens.css or fetched from Figma fills |

---

## 10. drk Project Specifics

| Detail | Value |
|---|---|
| Figma FILE_KEY | `uCEgsWIgbUqMZlWGEta6Vf` (in gitignored `figma_config.py`) |
| Frame width | 1440px for all pages |
| Fonts | Afacad (body, headings) + Agdasima (decorative large numerals) |
| Frame IDs | `1:2` Home, `1029:890` Vision, `1029:1114` Team, `1029:1574` KK Life, `1029:689` Fellowship, `1029:1018` Apply, `1029:1181` Memories, `194:127` About Us |
| Token file | `tokens.css` — single source of truth for colors, font sizes, spacing |
| Never commit | `figma_config.py`, screenshot PNGs, audit dump TXTs, `*.py` Figma scripts |
| Git authorship | hrishi only — no Co-Authored-By lines |

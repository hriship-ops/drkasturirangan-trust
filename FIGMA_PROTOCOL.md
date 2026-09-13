# Figma Faithfulness Protocol — drk project

**Rule zero: yours not to reason why — replicate Figma look and feel faithfully.**

---

## Before writing any CSS or HTML

1. **Fetch first.** For any element you are adding or fixing, call the Figma REST API and read the node's `absoluteBoundingBox` before touching code.  
   - Script pattern: `from figma_config import FILE_KEY, TOKEN` → `GET /v1/files/{FILE_KEY}/nodes?ids={nodeId}`  
   - Convert absolute coords to frame-relative: `rx = x - frame_x`, `ry = y - frame_y`.  
   - Frame width is 1440px for all drk pages.

2. **Run `strict_audit.py`** after every change to catch color and shape regressions before committing.

---

## Layout model

Figma uses a **flat/absolute model** — every child has an explicit x/y from the frame origin. HTML defaults to flow/flex. The rule:

- If Figma shows elements at fixed y-positions that would overlap or reorder in flex, use `position: absolute` on all children of that container.  
- Never assume flex column order matches Figma's visual order.  
- Convert Figma `x` → CSS `left` (px or %), `y` → CSS `top` (px or %).  
- For widths that should scale: `width = figma_w / 1440 * 100%`.

**Lesson (testimonials cards):** Photo at y=254px, quote text ending at y~240px. Flex column placed photo at ~118px, inside the text zone. Fix: full absolute positioning on `.tc-card`, hard floor on `.tc-quote-text { bottom: 36px }`.

---

## Hover / interactive states

**Only implement a hover state if Figma has one.** Check the Prototype tab or variant group.  
If no hover variant exists → no CSS `:hover` rule for that element.

**Lesson (quote strip):** `.quote-strip:hover .quote-amber-bg { background-image: url(quote-box-flip.png) }` caused a white screen because `quote-box-flip.png` contains a large white rectangle. No hover state existed in Figma. Rule removed entirely.

---

## Vectors / decorative connectors

Every VECTOR or LINE node in Figma must be handled as one of:

| Case | Action |
|------|--------|
| Decorative connector between two elements | Export from Figma at 2×, save to `assets/images/`, position with absolute CSS matching Figma coords |
| Decorative wave/organic shape | Export as SVG, use as `<img>` or inline |
| Team card wave (repeating) | One SVG shared across all cards |

After adding a new vector asset:  
1. Re-run `python figma_scraper.py` to regenerate `figma_shapes.json` with the new `vectors` list.  
2. Run `strict_audit.py` — Layer 2b will confirm WARN is gone.  
3. At narrow breakpoints, hide decorative connectors: `@media (max-width: 1100px) { .connector { display: none; } }`.

---

## Text positioning

Convert Figma text node coords to CSS:

```
left  = figma_text_x / 1440          → use as left% or absolute px
top   = figma_text_y - frame_y_abs   → relative to strip/section top
width = figma_text_w / 1440
```

Do **not** use `margin-left` or `margin-top` to position text that Figma places absolutely — use `position: absolute; left; top; width`.

---

## Z-order

Figma's layer panel order (bottom to top) maps to CSS `z-index` (low to high).  
Read the layer stack before setting z-index values. Typical card stack:  
`background (z=0) → quote mark (z=1) → wave (z=2) → cream band (z=3) → photo (z=4)`.

---

## Colors

All colors come from `tokens.css`. Never hardcode a hex that isn't already a token unless it comes directly from a Figma fill:

- `--c-accent: #ffb338`
- `--c-amber-bg: rgba(255,179,56,0.8)`
- `--c-primary: #2a427e`
- `--c-amber-border: #e9a22d`

Run **Layer 3** of `strict_audit.py` to catch any color that doesn't match a Figma fill.

---

## Workflow when a designer updates Figma

1. Identify which frames changed (ask designer or compare node IDs in `figma_shapes.json`).
2. For each changed frame:  
   a. Fetch updated node tree with a temp script (pattern: `figma_<page>_fetch.py`).  
   b. Note any new/moved/resized elements.  
   c. Apply CSS/HTML changes using exact Figma coords.  
   d. If new vectors appear: export at 2×, add to `assets/images/`, wire up CSS, re-scrape.
3. Run `strict_audit.py` (Layers 1-3 + 2b).
4. Screenshot with Chrome headless (`--disable-cache`, no `--incognito`, temp file in project folder).
5. Compare crop against Figma screenshot side-by-side.
6. Commit with `git commit` — hrishi as author, no Co-Authored-By line.

---

## Files

| File | Purpose |
|------|---------|
| `figma_config.py` | FILE_KEY + TOKEN — **gitignored, never commit** |
| `figma_shapes.json` | Scraped shapes/vectors per frame — committed |
| `figma_scraper.py` | Regenerates `figma_shapes.json` |
| `strict_audit.py` | 3-layer + Layer 2b audit |
| `visual_diff.py` | Layer 4 color palette diff |
| `figma_font_audit.py` | Fetches all frames, prints canonical font-size table; run after any designer update |
| `tokens.css` | Design tokens — single source of truth |

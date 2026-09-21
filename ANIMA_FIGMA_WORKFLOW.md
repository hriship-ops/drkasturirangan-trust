# Anima + Figma MCP/API — Efficient Page-Build Methodology

Reference document for the Dr Kasturirangan Trust website project.  
Covers the full two-source workflow, coordinate rules, and every class of bug discovered during implementation.

---

## 1. The Two-Source Principle

Every page is built from **two complementary sources**:

| Source | What it gives you | What it does NOT give you |
|---|---|---|
| **Anima React/TS export** | Exact pixel positions, widths, heights, font sizes, colours, line-heights, z-order, text content | Responsive behaviour, semantic structure, correct clipping contexts |
| **Figma REST API / MCP** | Exported assets (SVG/PNG), exact colour hex values, font names, frame dimensions | Sub-pixel text layout, mixed line-heights inside a text block |

Never rely on just one. Anima is your **coordinate ground truth**; Figma API is your **asset and colour source**.

---

## 2. Project Setup

### 2.1 Figma API token (never commit)

Store the token in a gitignored file only:

```
# C:\appdev\drk\figma_config.py  (in .gitignore)
TOKEN = "figd_..."
FILE_KEY = "yv1BNsSxoz6yRcWDqqDxyi"
```

Every script imports from there:

```python
import sys
sys.path.insert(0, r"C:\appdev\drk")
from figma_config import TOKEN, FILE_KEY
```

### 2.2 Fetching assets via API

```python
import json, urllib.request

def figma_get(path):
    url = f"https://api.figma.com/v1/{path}"
    req = urllib.request.Request(url, headers={"X-Figma-Token": TOKEN})
    with urllib.request.urlopen(req) as r:
        return json.loads(r.read())

# Get image export URLs for a list of node IDs
ids = "1029:1234,1029:1235"
data = figma_get(f"images/{FILE_KEY}?ids={ids}&format=png&scale=2")
urls = data["images"]   # dict: node_id → CDN URL
```

### 2.3 Anima export

1. In Figma, select the page frame → Plugins → Anima → Export React.
2. Extract the zip; the component lives at  
   `src/screens/<PageName>/<PageName>.tsx`.
3. **Read the entire TSX before writing any HTML.** Positions that look simple often have section-relative children or conditional renders you will miss from a partial read.

---

## 3. Coordinate System

### 3.1 The nav-height offset

Anima exports the **full page frame** including the nav bar at the top.  
Our pages use a shared `<nav class="site-nav">` outside the wrap div, so the wrap starts below the nav.

```
wrap-relative y  =  Anima absolute y  −  101
```

Nav height is 101 px (confirmed by measuring `site-nav` in `shared.css`).  
X coordinates are **unchanged** — the nav does not affect horizontal position.

**Example:**

```
Anima: top-[649px]  →  wrap y = 649 − 101 = 548 px
Anima: top-[730px]  →  wrap y = 729
Anima: top-[1957px] →  wrap y = 1856
```

Apply this formula to every element: dots, headings, body text, cards, images, divider lines.

### 3.2 Section-relative children — the most common mistake

When Anima wraps children inside a `<section>` or `<div>` with an absolute position, those children are **positioned relative to their parent**, not to the main frame.

**Anima TSX pattern:**
```jsx
<section className="absolute left-0 top-28 h-[461px] w-[1439px] bg-[#fffcf6]">
  <div className="absolute left-[301px] top-0 ...">   {/* relative to section */}
  <p  className="absolute left-[calc(50%_-_330px)] top-28 ..."> {/* relative to section */}
  <div className="absolute left-[1070px] top-[284px] ..."> {/* relative to section */}
  <img className="absolute left-[154px] top-[257px] ..."> {/* relative to section */}
</section>
```

**What this means for your CSS:**  
`top-28` on the section = 7 rem = 112 px from the Anima frame top.  
Children at `top-0`, `top-28`, `top-[284px]`, `top-[257px]` are **section-relative**.

**Conversion to wrap-relative:**
```
wrap y  =  (section top − 101)  +  child top
         =  (112 − 101)          +  child top
         =  11                   +  child top

Opening quote (child top=0):   wrap y = 11 +   0 = 11
Mission text   (child top=112): wrap y = 11 + 112 = 123
Closing quote  (child top=284): wrap y = 11 + 284 = 295
Layer image    (child top=257): wrap y = 11 + 257 = 268
```

**The correct HTML structure:**  
Replicate the section as an actual container with `position: relative` (or `absolute`) so its children can use the same relative coordinates:

```html
<section class="vm-mission-section" aria-label="Mission statement">
  <div class="vm-quote" style="left:301px;top:0">&ldquo;</div>
  <p class="vm-mission-text">…</p>
  <div class="vm-quote" style="left:1070px;top:284px;transform:rotate(180deg)">&ldquo;</div>
  <img class="vm-layer" src="…" alt="">
</section>
```

```css
.vm-mission-section {
  position: absolute;
  top: 11px; left: 0;
  width: 1440px; height: 461px;
  background: #fffcf6;
  /* no overflow:hidden here — see §5.2 */
}
```

---

## 4. Horizontal Overflow (Viewport) Fix

### The problem

Pages are designed on a 1440 px canvas. At browser zoom 100 % on a 1280–1366 px screen, or whenever the viewport is narrower than 1440 px, a horizontal scrollbar appears. Elements placed beyond the canvas edge (e.g. a decorative circle at x=1155 + w=403 = x=1558) extend the scrollable width.

### The fix — two layers

**Layer 1 — global, in `tokens.css`:**
```css
html { overflow-x: hidden; }   /* already present */

body {
  overflow-x: clip;   /* ← added; does NOT create a scroll container */
  /* ... other rules ... */
}
```

**Why `clip` not `hidden`:** `overflow-x: hidden` creates a new scroll container, which breaks `position: sticky` on the nav bar. `overflow-x: clip` clips visually without creating a scroll container, so sticky nav continues to work.

**Layer 2 — per-page wrapper, in each page's CSS:**
```css
.hl-wrap,
.vm-wrap,
.fellowship-wrap {
  overflow-x: clip;
}
```

This ensures decorative elements that extend past 1440 px are clipped at the wrapper boundary, matching Figma's frame clipping.

---

## 5. Figma Frame Clipping vs CSS

Figma always clips children at the frame boundary. CSS does not clip by default. These two rules map Figma's behaviour to CSS:

### 5.1 Decorative overflow — use `overflow-x: clip`

For elements that intentionally extend past the design canvas edge (e.g. a large amber circle), add `overflow-x: clip` to the wrapper. This clips horizontally without affecting vertical scroll or sticky positioning.

### 5.2 Overflow within a section — avoid `overflow: hidden`

You might be tempted to add `overflow: hidden` to a section container to clip children (as Figma does for section frames). **Do not** unless you have verified the result, because:

- `overflow: hidden` creates a new stacking context AND a scroll container.
- Children that need to render partially outside the section (e.g. decorative elements that bleed across section boundaries) will be clipped unexpectedly.
- The rotating-glyph issue (§6) is made worse because the rotated glyph's visual position differs from its layout box position.

If you need clipping to prevent an overflow bug, use `overflow: clip` (not `hidden`) on the section, and verify in a browser screenshot that nothing is unintentionally hidden.

---

## 6. The Rotating-Glyph Problem (Closing Quote)

### What went wrong

The closing `"` in the mission section was produced by placing the same `"` character as the opening quote and applying `transform: rotate(180deg)`.

At `font-size: 300px; line-height: 1`, the element's CSS layout box is 300 px tall. The `"` glyph in Agdasima renders near the **top** of that 300 px box (it is a superscript-like character, sitting high in the em square). After `rotate(180deg)` around the element's centre:

```
element box   : y = T  to  T + 300
centre        : y = T + 150
glyph (before): y ≈ T  to  T + 100   (top portion)
glyph (after) : y ≈ T + 200  to  T + 300  (bottom portion, mirrored)
```

So if `top: 295px` (section-relative), the rotated glyph's **visual centre** is around `y ≈ 445–545 px`, which is **below** the 461 px section height — entirely invisible if the section has `overflow: hidden`, or floating below the cream background if not.

### The fix

Move the element's `top` up so the rotated glyph lands in the lower half of the section:

```css
/* section-relative top = 100 → rotated glyph lands at section y ≈ 300–400 */
```

```html
<div class="vm-quote"
     style="left:1070px; top:100px; transform:rotate(180deg)">&ldquo;</div>
```

**General rule:** When rotating a large display glyph 180°, test where the glyph visually appears (screenshot at correct pixel density) and adjust `top` empirically. The formula `top_adjusted ≈ top_anima − glyph_height` is a starting point.

---

## 7. Text Box Height — Anima Exports Everything, Figma Shows Less

### The problem

In Figma, text frames have a **fixed height**. When the text overflows that height, Figma clips it silently. Anima exports the **full text content** as an inline string, with no height constraint in the TSX.

Result: in the browser, a body paragraph that Figma clips at 403 px will render for 550+ px and overlap the next element below it.

### Identifying it

Compare:
- `top` of the body text element
- `top` of the next element below (e.g. a timeline link or a decorative rule)
- Gap = available height for the text box

If `paragraph_height_estimate > gap`, you have this problem.

### The fix

Add `overflow: hidden` and `max-height` to the body paragraph using the gap as the constraint:

```html
<p class="vm-body"
   style="top:629px; left:72px; width:759px; line-height:35px;
          max-height:390px; overflow:hidden">
  …full Anima text…
</p>
```

`max-height = next_element_top − this_element_top − small_margin`  
`= 1032 − 629 − 13 = 390 px`

The text will be clipped at the last complete line that fits, matching Figma's rendered output.

**Where this always applies:**
- Any body/paragraph element where the next absolutely-positioned element is less than `estimated_text_height` below it.
- Governance section body text (clipped by the partnership box starting at a nearby y).
- Any section where text runs alongside a photo or card.

---

## 8. Mixed Line-Heights in a Single Paragraph

Anima sometimes exports a single `<p>` with multiple `<span>` children each carrying a different Tailwind `leading-*` class:

```jsx
<p>
  <span className="leading-[35px]">First paragraph…<br/></span>
  <span className="leading-[60px]">He also leaves… </span>
  <span className="leading-[35px]">integrity, committed…</span>
</p>
```

This signals that the designer wants extra visual breathing room on the line that starts the second paragraph, without a full paragraph break.

**In HTML/CSS** you can replicate this with `<span style="line-height:60px">` inline, but it only affects the line-height of the lines that span touches. Verify visually — the extra spacing creates a rhythm the reader expects.

If implementing with a single `line-height` for simplicity, use the dominant value (usually 35 px) and accept the minor visual difference. The `max-height` clip (§7) is still mandatory.

---

## 9. Z-Order Rules

CSS paints elements in DOM order: later elements render **on top of** earlier ones (within the same stacking context, without explicit `z-index`).

Anima's TSX shows the intended z-order through DOM order. Match it:

| Pattern | Rule |
|---|---|
| Amber decorative circle + photo | Circle **before** photo in DOM — photo covers the overlapping edge |
| Body text + photo | Body text **before** photo — photo covers body text in overlap region |
| Timeline link + body text | Timeline link **after** body text — link is always readable on top |
| Ethos ellipses + question images | Ellipses before questions — questions render on top of the ellipse fill |

When in doubt: check which element Anima renders last in its JSX for the section.

---

## 10. Asset Workflow

### 10.1 Extracting from Anima zip

```
<PageName>.zip
└── src/
    └── screens/<PageName>/
        └── <PageName>.tsx    ← read this fully
public/
└── img/
    ├── layer-1.png
    ├── ellipse-18.svg
    ├── science-with-conscience.svg
    └── …
```

Copy the `public/img/` assets to `2ndpass/assets/<pagename>/`.

Check each SVG before using it. SVGs from Anima come in two types:

| Type | What it is | How to use |
|---|---|---|
| **Path-based text** | Glyphs rendered as `<path>` — font not present on client | `<img src="…">` — never inline, text is not selectable |
| **Geometric / icon** | Pure shape SVG | Can inline or use as `<img>` |

Identify the type: open the file and check for `<text>` or `<path d="M …">` with many points. If paths only: use as `<img>`.

### 10.2 Exporting from Figma API

Use node IDs from the Anima `data-model-id` attributes or from `figma_list_frames.py`:

```python
node_ids = "1029:890,1029:1234"
data = figma_get(f"images/{FILE_KEY}?ids={node_ids}&format=png&scale=2")
# Then download each URL with urllib.request.urlretrieve(url, local_path)
```

Scale=2 gives retina-quality assets. Scale=1 for icons, scale=2+ for photos and illustrations.

---

## 11. Shared CSS Architecture

```
tokens.css    ← CSS variables: colours, fonts, spacing, page max-width
shared.css    ← nav (.site-nav) + footer (.site-footer, .footer-*)
<page>.css    ← page-specific: .vm-*, .hl-*, .fp-* etc.
```

**Always use `var(--font-deco)` and `var(--font-main)`**, never hard-code font names. The tokens file is the single source of truth for Agdasima and Afacad.

Key tokens:
```css
--font-deco: 'Agdasima', sans-serif;
--font-main: 'Afacad', sans-serif;
--c-navy:    #2a417d;
--c-navy-dk: #2e3d63;
--c-amber:   #ffb337;
--c-amber-dk:#d9982e;
--c-amber-lk:#ffb338;
--c-cream:   #fffcf6;
--c-cream-dk:#fff6e6;
--max-w-page: 1440px;
```

---

## 12. Page Wrapper Pattern

Every page follows this skeleton:

```html
<nav class="site-nav">…</nav>

<div class="<page>-wrap">
  <!-- All page content, absolutely positioned -->
</div>

<div class="footer-rule-wrap">…</div>
<footer class="site-footer">…</footer>
```

```css
.<page>-wrap {
  position: relative;
  width: 1440px;
  min-height: <anima_frame_height − 101 − footer_height>px;
  background: #fff;
  overflow-x: clip;   /* always */
}
```

The `min-height` should equal the Anima frame height minus nav (101 px) minus the shared footer height. If unsure, set it to the last element's bottom edge + 80 px padding.

---

## 13. Checklist — Starting a New Page

1. **Read the full Anima TSX** before writing a single line of HTML.
2. **Identify nested sections** — any `<section>` or `<div>` with an absolute position whose children are also absolutely positioned. Convert to offset coordinates (§3.2).
3. **Record the nav offset** — subtract 101 from every Anima `top-[Npx]` value on direct children of `<main>`.
4. **List all assets** needed from `public/img/`. Copy to `assets/<pagename>/`. Classify each SVG (§10.1).
5. **Identify text elements** with a next-sibling element close below. Calculate the gap and apply `max-height + overflow:hidden` (§7).
6. **Check for rotated large display elements** (quote marks, decorative type). Verify visually that the glyph lands where you expect after rotation (§6).
7. **Set overflow-x: clip** on the page wrapper.
8. **Screenshot** at 1440 px width and compare section by section against Anima. Do not mark a section done until both match.

---

## 14. Full Bug Log — Issues Found During Implementation

### B-01 Horizontal overflow (global)
**Symptom:** Page scrolls sideways at browser zoom 100 % on screens narrower than 1440 px.  
**Root cause:** `width: 1440px` on the page wrapper plus decorative elements extending past x=1440. CSS default `overflow: visible` made the page width the widest element.  
**Fix:** `overflow-x: clip` on `body` (in tokens.css) and on each page wrapper. Use `clip` not `hidden` to preserve sticky nav.  
**Applies to:** All pages. Added to tokens.css globally.

---

### B-02 Section-relative children flattened to wrap-absolute (mission section)
**Symptom:** Mission section children (quote marks, layer image, mission text) appeared in wrong positions — some overlapping The Legacy heading below.  
**Root cause:** Anima positions these children relative to the `<section>` element, not the main frame. Implementing them as flat children of `vm-wrap` requires converting coordinates, but the conversion formula was not initially applied correctly.  
**Fix:** Implement the section as an actual `<section class="vm-mission-section">` CSS container. Place children inside it using section-relative coordinates directly from Anima (no offset needed). The section itself uses wrap-relative top=11px.

---

### B-03 Closing quote glyph below the cream section (rotating-glyph)
**Symptom:** The closing `"` appeared to the right of "The Legacy" heading, on the white background below the cream panel — not inside the cream panel.  
**Root cause:** `transform: rotate(180deg)` on a 300px font glyph moves the visual glyph ~200 px downward from the element's `top` value. At `top: 295px` the rotated glyph landed around y=495 px, past the section's 461 px height.  
**Fix:** Move `top` from 295px to 100px (section-relative). Rotated glyph now lands at section y ≈ 300–400 px, visible within the cream section.  
**General rule:** Always screenshot-verify the visual position of any rotated display-size glyph.

---

### B-04 Body text overflows into next element (Figma text-box clipping not replicated)
**Symptom:** Legacy section body text lines and the timeline link text appeared interleaved at the same y-position — both visible, overlapping, unreadable.  
**Root cause:** In Figma, text frames have a fixed height and clip overflow. Anima exports the full text content as a string with no height constraint. The paragraph rendered 550 px tall but the next element (timeline link) was only 403 px below.  
**Fix:** `max-height: 390px; overflow: hidden` on the body paragraph. The browser clips at the last complete line that fits, matching Figma's frame-clipped appearance.  
**Applies to:** Any long body text paragraph where the gap to the next element is smaller than the paragraph's natural rendered height.

---

### B-05 Objective card labels clipped / wrapping
**Symptom:** "Creating Future Leaders" tag text wrapped to two lines, overflowing the 45px-tall tag.  
**Root cause:** `.vm-obj-label` was set to `width: 193px; white-space: nowrap`, which is narrower than the 223px tag. Text overflowed and was clipped, or wrapped when `white-space` was removed.  
**Fix:** Set `width: 223px` (match tag width exactly) and `line-height: 45px` (vertically centres a single-line label within the 45px tag). Also align label `left` and `top` exactly with the tag — no +15px offset.

---

### B-06 `overflow: hidden` breaking sticky nav
**Symptom:** After adding `overflow: hidden` to `body` to fix horizontal overflow, the nav bar stopped being sticky and scrolled with the page.  
**Root cause:** `overflow: hidden` creates a new scroll container. A sticky-positioned element inside a scroll container sticks to that container's scroll port, not the viewport — effectively disabling the sticky behaviour.  
**Fix:** Replace `overflow: hidden` with `overflow-x: clip`. The `clip` value clips visually but does not create a scroll container.

---

### B-07 Path-based SVG text not rendering correctly when inlined
**Symptom:** Ethos title SVGs (science-with-conscience.svg, etc.) showed no text when referenced with certain methods.  
**Root cause:** These SVGs render text as filled path data (no `<text>` elements). They require the font to be baked into paths already. They work correctly as `<img>` tags but may render incorrectly or blank when inlined and CSS font rules interfere.  
**Fix:** Always use `<img src="…">` for path-based SVGs from the Anima export. Never inline them.

---

### B-08 Z-order: amber circle covers photo
**Symptom:** The amber decorative circle appeared on top of the photo of Dr Kasturirangan instead of behind it.  
**Root cause:** The circle was placed in the DOM after the photo, so it rendered on top.  
**Fix:** Place the amber circle **before** the photo in DOM order. CSS paints later elements on top.

---

### B-09 Asset paths: `../assets/images/` vs `assets/images/`
**Symptom:** Logo and other images 404 in `drkfinal/` — the logo path was `../assets/images/logo-final.png` which points to the parent of the project folder.  
**Root cause:** Files in `2ndpass/` reference assets in the parent `drk/assets/` directory using `../`. When files are copied flat into `drkfinal/`, the `../` prefix is wrong.  
**Fix:** After copying to `drkfinal/`, run a string replacement: `../assets/images/` → `assets/images/` (and similarly for other `../` paths). Keep `2ndpass/` files unchanged.

---

### B-10 Fellowship hero: cascading coordinate mismatches between flex layout and Figma absolute layout
**Symptom:** `fellowship.html` — visible ~100px grey gap between the last hero bullet ("Financial support worth Rs 4 lakh for selected fellows") and the full-width navy banner. Figma shows only ~44px of intentional background colour between them.  
**Root cause:** Figma uses fully absolute-positioned elements; the HTML uses flex layout. Six independent mismatches compounded to create a 102px gap vs Figma's intended 44px:
1. `fp-hero` `padding-top` was 44px; Figma's grid starts at wrap y=58 (14px short)
2. `fp-hero-left` `padding-top` was 40px; Figma title starts at wrap y=112 (14px short)
3. `fp-hero-label` `margin-bottom` was 24px; Figma gap is 50px (26px short)
4. Bullet text column was 691px wide (flex fill of available space); Figma text is `w-[613px]` — the wider column caused less text wrapping, so bullets ended 98px higher on the page
5. Illustration PNG (1438×1093) rendered at 458px tall at 603px display width; Figma specifies `h-[476px]` (18px short)
6. `fp-hero-banner` `margin-top` was clamp(20–44px); Figma has 8px clearance below the illustration  

**Fix:** Correct all six values to match Figma coordinates:
- `fp-hero` padding-top: `clamp(32px, 4.0vw, 58px)`
- `fp-hero-left` padding-top: `clamp(12px, 3.75vw, 54px)`
- `fp-hero-label` margin-bottom: `clamp(14px, 3.5vw, 50px)`
- `fp-hero-bullets` `max-width: 613px` (Figma's `w-[613px]`)
- `fp-hero-illus` explicit `height: clamp(300px, 33.06vw, 476px)` + `object-fit: contain; object-position: bottom` on img
- `fp-hero-banner` `margin-top: 8px`  

**Rule:** When a section uses flex layout to approximate an absolute-positioned Figma design, check EVERY coordinate: padding-top, padding-bottom, element gaps, text column widths, and image heights. Any one mismatch is hidden; six together produce a large visible discrepancy. Always cross-check by reading Anima's `top-[Npx]` values for each element and verifying the rendered position matches `wrap y = Anima absolute y − 101`.

---

## 15. Quick-Reference: Anima Tailwind → CSS

| Tailwind class | CSS value |
|---|---|
| `top-28` | `top: 112px` (7 rem) |
| `top-[Npx]` | `top: Npx` |
| `leading-[35px]` | `line-height: 35px` |
| `leading-[normal]` | `line-height: normal` |
| `rounded-2xl` | `border-radius: 16px` |
| `rounded-[26px]` | `border-radius: 26px` |
| `text-4xl` | `font-size: 36px` |
| `text-2xl` | `font-size: 24px` |
| `text-xl` | `font-size: 20px` |
| `font-semibold` | `font-weight: 600` |
| `font-bold` | `font-weight: 700` |
| `font-medium` | `font-weight: 500` |
| `object-cover` | `object-fit: cover` |
| `whitespace-nowrap` | `white-space: nowrap` |
| `rotate-180` | `transform: rotate(180deg)` |
| `overflow-hidden` | `overflow: hidden` |
| `inset-x-0` | `left: 0; right: 0` |
| `min-h-[Npx]` | `min-height: Npx` |
| `min-w-[Npx]` | `min-width: Npx` |
| `h-8 w-8` | `height: 32px; width: 32px` |
| `rounded-2xl` on a dot | `border-radius: 16px` (circle) |
| `left-14` | `left: 56px` (3.5 rem) |
| `left-[72px]` | `left: 72px` |
| `calc(50%_-_330px)` | `calc(50% - 330px)` |

---

*Last updated: September 2026. See also: `FIGMA_PROTOCOL.md`, `FIGMA_ERRORS_LEARNED.md`.*

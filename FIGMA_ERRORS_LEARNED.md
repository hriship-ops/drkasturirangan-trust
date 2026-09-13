# Comprehensive Error Log & Learning — drk Project
*Every mistake made across all sessions, categorised by type. Reference this before any Figma-to-HTML work.*

---

## CATEGORY 1 — Substituting Judgment for Figma Data
*The single largest failure class. "Yours not to reason why — replicate Figma faithfully."*

### 1.1 Truncating the timeline
**What happened:** Kasturirangan timeline in Figma goes to 2025. Claude stopped adding entries well before 2025 because there was no content text yet in Figma.  
**User:** "yours not to reason why — you should replicate figma look and feel — if they take it to 2999 you replicate it whether there's content or not."  
**Rule:** If Figma shows a year row, build the row — even empty. Never decide "there's no content so I'll stop."

### 1.2 Deciding circle color variant without Figma confirmation
**What happened:** When renaming circle assets (navy vs amber), Claude decided navy = default state and renamed files accordingly, baking an assumption in before confirming with Figma.  
**User:** "it went ahead and stated it will use the navy circle variant without you confirming that matches Figma's actual current design intent"  
**Rule:** When Figma has multiple variants of an asset, confirm which variant maps to which state before renaming or wiring.

### 1.3 Adding hover state that doesn't exist in Figma
**What happened:** CSS rule `.quote-strip:hover .quote-amber-bg { background-image: url(quote-box-flip.png) }` switched the background on hover. No hover state existed in Figma for the quote strip. Result: white screen on hover.  
**Rule:** Never implement a `:hover`, `:focus`, or interactive state unless Figma's Prototype tab or variant panel explicitly shows it. Check before coding.

### 1.4 Suggesting "appropriate" photos instead of matching Figma
**What happened:** Claude suggested a parliament photo as "more appropriate" instead of using whatever image Figma specified.  
**User:** "don't worry about appropriate photos!!!! just edit your html to match figma text"  
**Rule:** Editorial and content judgment is not Claude's role on this project. Replicate exactly what is in Figma, including placeholder images, text, and assets.

### 1.5 Deciding a spacing/gap value was "close enough"
**What happened:** Figma gap was ~77px; Claude used 40px and called it "not Figma-defined, acceptable."  
**User:** "Why isn't it Figma-defined — if it exists as a node, pull its actual position rather than deciding 40px is close enough."  
**Rule:** If a gap or offset exists in Figma (even as an implicit gap between two nodes), measure it from absoluteBoundingBox, don't estimate.

### 1.6 Stopping at visual "good enough" without a diff
**What happened:** Multiple times Claude reported a fix as done after one screenshot without explicitly diffing against the Figma frame.  
**User:** "can you reconfirm all fixes pushed to github pages… specifically screenshot the fixes, compare with figma and reconfirm"  
**Rule:** Every fix requires: (a) screenshot of HTML, (b) Figma screenshot of same area, (c) explicit diff statement. Not: "looks good."

---

## CATEGORY 2 — Layout Model Mismatch (Figma Absolute vs HTML Flow)

### 2.1 Testimonials card: photo overwrote quote text
**What happened:** Used `display: flex; flex-direction: column` on `.tc-card`. Flex placed the photo at ~118px from the top — inside the quote text zone. Figma uses flat absolute positioning: photo at y=254px, text ending at ~240px.  
**Fix:** Full absolute positioning on all children of `.tc-card`. Hard floor `bottom: 36px` on `.tc-quote-text` to maintain 14px gap above photo at 254px.

### 2.2 Text centering: margin-left instead of Figma absolute x
**What happened:** Quote text had `position: relative; margin-left: 110px; max-width: 700px`. Figma placed text at x=367/1440=25.5%, y=1703.  
**Fix:** `position: absolute; left: 25.5%; top: 244px; width: 34.9%`.  
**Rule:** Never use margin to position an element that Figma places at an explicit x/y. Always convert Figma coords to absolute CSS.

### 2.3 Circles section: text behind/over circles
**What happened:** Multiple iterations where text labels (SPACE & TECHNOLOGY, ENVIRONMENT, EDUCATION, PUBLIC LIFE) overlapped the circle icons. Tried multiple z-index and margin fixes, each one displaced something else.  
**Rule:** Read Figma absoluteBoundingBox for each text node and each circle. Set `position: absolute; top: <y>; left: <x>` directly — don't rely on flex/grid ordering to match Figma's visual stack.

### 2.4 Amber dot covering first letters of headings
**What happened:** Amber dot CSS placed it overlapping the first characters of "Cultivating Excellence", "Futures Thinking", "Advancing Humanity".  
**Fix:** `margin-right: -18px; z-index` layering so dot sits behind first letter.  
**Rule:** Check Figma layer order (bottom→top = lowest→highest z-index). Decorative elements often sit behind text in Figma; match that z-order.

---

## CATEGORY 3 — Screenshot-Based Guessing Instead of JSON Fetch

### 3.1 Early sessions: used screenshots to understand layout
**What happened:** In early sessions (before the strict-fetch protocol), Claude took screenshots of the rendered HTML and used those to make layout decisions rather than reading Figma JSON.  
**User:** "Stop taking screenshots. Screenshots make you guess the layout, which causes the overlaps and broken rendering. Instead, use your Figma MCP tools to fetch the raw JSON node tree data."  
**Rule:** Screenshots verify; they do not inform layout decisions. Figma JSON (absoluteBoundingBox, paddingLeft/Right/Top/Bottom, itemSpacing, layoutMode) is the only valid source for dimensions.

### 3.2 Reading screenshot crops instead of full page
**What happened:** Took a full-page screenshot but read only the top portion, missing the section under review (e.g., the quote strip was in the lower half of index.html).  
**Rule:** When verifying a specific section, take a targeted crop or scroll to the right viewport offset. Confirm you are looking at the right area of the page before reporting.

---

## CATEGORY 4 — Iterative Failures Without Root-Cause Analysis

### 4.1 Kasturirangan sidebar scroll (12+ failed iterations)
**What happened:** User wanted a compact, fully static left sidebar where relevant years highlight as content scrolls on the right. Claude made 12+ attempts:
- Made sidebar non-static (scrolled with content)
- Made row heights dynamic (heights varied per entry instead of uniform)
- Changed visible year count to 5 (years disappeared on scroll)
- Changed image formatting in 1971 without being asked
- Didn't read earlier implementations before "fixing"

**User:** "horrible… i repeat… nothing changed… pls clear your head… look at the latest two screenshots in troubleshoot folder… otherwise you are just not getting it"  
**Rule:** Before attempt N+1 on a repeated failure, read the git history (`git log -p`) to see what was tried. Screenshot the current state before touching anything. Identify specifically what property is wrong and change only that.

### 4.2 Closing quote mark (8 screenshot iterations)
**What happened:** Closing quote mark on vision.html: appeared outside box → looked like an opening quote → vanished entirely → needed to be in front (z-index). 8 successive screenshots (v1–v8) with small adjustments each time without fixing the root cause.  
**Rule:** Before iterating a visual fix, read the Figma node for the quote element to see its exact type, position, and character. Don't iterate blind — fetch first.

---

## CATEGORY 5 — Missing Figma Vectors / Assets

### 5.1 Dashed connector between date pills not detected
**What happened:** Figma has a VECTOR node (id=1186:418, 308×143px) — a dashed curved string connecting "Nominations accepted" and "Last date for submission" pills on fellowship.html. Never detected in any audit pass until user explicitly pointed it out.  
**User:** "in figma there is a string image connecting these two. add this failure to audit fixes."  
**Fix:** Added Layer 2b to `strict_audit.py` to report all VECTOR/LINE nodes as WARN for manual verification. Exported connector as PNG, wired up CSS.  
**Rule:** After every scrape, check `figma_shapes.json` for `"vectors"` entries per frame. Every vector is an asset that needs exporting — connectors, decorative lines, ornamental curves.

### 5.2 Apply page connector also missed initially
**What happened:** Same class of error on apply.html — the dashed connector between date pills was absent until explicitly implemented.  
**Rule:** Any frame with date pills or callout cards should be checked specifically for connector vectors between them.

---

## CATEGORY 6 — Text and Content Errors

### 6.1 Timeline text cut off mid-sentence at section boundaries
**What happened:** Timeline entry for 1963 ("Joins Physical Research Laboratory…") was visually crossing the divider line into the next entry.  
**Fix:** `overflow: hidden` on entry containers, explicit `min-height` matching Figma row height.

### 6.2 "KK. Kasturirangan" typo (double K)
**What happened:** Timeline intro text read "KK. Kasturirangan" — extra K introduced during edit.  
**User:** pointed this out in a screenshot read.  
**Rule:** When editing text nodes, read the final output back. Don't assume string substitution worked correctly.

### 6.3 Closing quote looked like opening quote
**What happened:** Used `&rdquo;` but CSS `transform: rotate(180deg)` or wrong glyph made it render as an opening quote.  
**Rule:** Use actual Unicode closing quote characters (`"` = `&rdquo;` = U+201D) and verify in the screenshot that the glyph is oriented correctly.

### 6.4 "Every phase of work must contribute…" line breaks wrong across multiple iterations
**What happened:** Four separate fix attempts each put "must" or "larger" on the wrong line. User had to correct each iteration.  
**Rule:** Text with forced line breaks — either use `<br>` at the exact positions Figma shows, or set a `width` that causes natural breaking at those points. Test at exactly 1440px viewport, not a different width.

---

## CATEGORY 7 — Verification Failures

### 7.1 Claiming push/commit was done when it wasn't
**What happened:** Multiple times Claude reported "pushed to GitHub Pages" but the live site showed no change.  
**User:** "did you push it. no change" / "pushed to github pages?" (asked repeatedly across sessions)  
**Rule:** After `git push`, verify with `git log --oneline -3` to confirm the commit hash. The push output itself shows the hash — report it to the user.

### 7.2 XLS: wrote to wrong column
**What happened:** `mark_done` function wrote "Done" to column E (Plan to Fix) instead of column D (Current Status). User couldn't see any changes in the file.  
**Rule:** Before writing to Excel: print the column header row and confirm which column index corresponds to which header.

### 7.3 XLS: wrote comments user couldn't see
**What happened:** Claimed to have written comments in XLS but user opened the file and saw nothing had changed.  
**Rule:** After every XLS write, confirm by reading back the cells that were written and printing their values.

### 7.4 Verifying wrong section of screenshot
**What happened:** After a fix, took a full-page screenshot but the report was based on reading the top of the page — the affected section was lower and not actually reviewed.  
**Rule:** When reporting a visual fix, explicitly state which pixel range of the screenshot you read and what you see there.

---

## CATEGORY 8 — Tool / Shell Mistakes

### 8.1 PowerShell inline `$()` subexpressions
**What happened:** Used `$()` inline subexpressions in PowerShell — caused safety popups every time.  
**User:** "Do not use inline subexpressions $() in your PowerShell scripts anymore… declare variables on separate, clean lines first"  
**Rule:** Always declare the value in a variable first, then pass the variable. No `$()` inside another expression.

### 8.2 Python nontrivial logic as inline `-c` strings
**What happened:** Wrote nontrivial Python as `python -c "..."` heredocs — caused parse errors and was hard to debug.  
**User:** "Stop using inline python -c multi-line strings and heredocs for anything nontrivial. Write scripts to an actual .py file."  
**Rule:** Any Python with more than one logical step goes to a `.py` file. Run it with `python filename.py`.

### 8.3 Chrome headless: `--incognito` blocking file://
**What happened:** Used `--incognito` flag in Chrome headless screenshots — this blocks `file://` access for freshly-written files.  
**Rule:** Use `--disable-cache` only. Write temp HTML files into the project folder, not `/tmp`. No `--incognito`.

### 8.4 Giant shell heredoc command too long to parse
**What happened:** Tried to write XLS update as a single giant PowerShell command — too long, malformed, failed.  
**User:** "That command is malformed/too long to parse. Don't force it through — break this into a proper file write instead."  
**Rule:** If a shell command needs more than ~200 chars of logic, it belongs in a script file.

---

## CATEGORY 9 — Git / Authorship

### 9.1 Added Co-Authored-By line with wrong author
**What happened:** Initial commits included `Co-Authored-By: claude` or similar.  
**User:** "make the co-author hrishi not claude" → "no — hrishikesh parthasarathy"  
**Rule:** drk project commits are authored by hrishi (hrishikesh parthasarathy) only. Never add Co-Authored-By line for Claude.

### 9.2 Using wrong git email/name
**What happened:** Commit author name was set to "hrishiow" instead of "hrishi".  
**User:** "its hriship how did you get hrishiow"  
**Rule:** Always confirm `git config user.name` and `git config user.email` match the project owner before committing.

---

## CATEGORY 10 — Scope Creep / Unrequested Changes

### 10.1 Changed 1971 image formatting when not asked
**What happened:** While fixing sidebar scroll, also changed image formatting for 1971 entry without being asked.  
**User:** "i dont know what you did for 11 mins"  
**Rule:** Change only the specific thing asked. If anything adjacent seems broken, flag it — don't fix it silently.

### 10.2 Suggested "appropriate" photos / content judgments
**What happened:** Claude suggested swapping a placeholder image for "a more appropriate photo of the Indian Parliament."  
**Rule:** Never make editorial content decisions. If Figma has placeholder text or images, replicate them. Flag missing assets; don't substitute your own choices.

### 10.3 Rewrote testimonials page when not asked
**What happened:** User asked to check other pages, and Claude redid testimonials independently.  
**User:** "why did you just redo testimonials — didn't we earlier pull all"  
**Rule:** Before starting work on any page not explicitly mentioned in the current instruction, confirm with the user.

---

## CATEGORY 11 — Mobile Responsiveness Gaps

### 11.1 Hard-coded px values not responsive
**What happened:** Circles section at 100% zoom: all 4 circles didn't fit on screen. Other elements (logo, Apply button) clipped at narrower widths.  
**User:** "you need to make it fit on any screen as it renders"  
**Rule:** After every major layout addition, test at 1440px, 1280px, 1024px, and 768px. Hard-coded pixel widths must be converted to `max-width` + `%` or `clamp()`.

### 11.2 Fixes applied to one page, not propagated site-wide
**What happened:** A responsiveness fix (e.g., fluid grid) was applied to the circles section of index.html but not to equivalent sections on other pages.  
**User:** "this kind of rendering fix should apply to all pages, not just these circles"  
**Rule:** When a structural fix applies by pattern (e.g., any 4-column grid), audit all pages for the same pattern and apply the fix everywhere before committing.

---

## CATEGORY 12 — Font Size Drift (Hardcoded Sizes That Don't Match Figma)

*Font sizes were set by estimation or copy-paste rather than being fetched from Figma `style.fontSize`.*

### 12.1 Canonical font size table (from full Figma audit, September 2026)

All text nodes across all frames. Use these — never estimate.

| Figma fs | fw | Afacad / Agdasima | Usage |
|---|---|---|---|
| 16px | 400 | Afacad | Nav links, footer nav, small labels |
| 18px | 400 | Afacad | Hero description, responsive fallback body |
| 20px | 400/500 | Afacad | Story captions, kicker labels, explore links |
| 22px | 400 | Afacad | Circle panel description text, standard body |
| 23px | 400 | Afacad | CTA tagline |
| 24px | 400/500/700 | Afacad | Circle panel quote, footer text, subheadings |
| 28px | 700 | Afacad | Fellowship "Nominations accepted from" header |
| 30px | 400 | Afacad | KK Life body paragraphs |
| 32px | 400/500/700 | Afacad | Apply page headings and notes |
| 35px | 400 | Afacad | Home hero headline |
| 36px | 400/500/700 | Afacad | Section h2 headings, banner text, button text |
| 50px | 500 | Afacad | Pull quote (area panel default, KK Life) |
| 96px | 400 | Agdasima | KK Life decade labels |
| 200/250/300/500px | 400 | Agdasima | Decorative quotation mark glyphs only |

**Sizes NOT in Figma** (found in HTML — wrong): `14px`, `19px`, `26px`

### 12.2 Known mismatches found (September 2026 audit)

| File | CSS value | Figma value | Element |
|---|---|---|---|
| `index.html` area panel default | 26px | **50px** fw=500 | "Every phase of work…" quote |
| `index.html` story hover | 14px | **20px** fw=400 | Hover overlay text |
| `index.html` circle quote | 22px | **24px** fw=500 | Per-circle italic quote |
| `index.html` circle desc | 18px | **22px** fw=400 | Per-circle description card |
| `vision.html:467` `.vm-quote-text` | 26px | needs verify | Pull quote on Vision page |
| `fellowship.html:329` | 14px | needs verify | Sub-label text |
| `fellowship.html:624` | 19px | needs verify | Card sub-text |
| `fellowship.html:775` | 26px | needs verify | Section text |

### 12.3 Rule
**Always fetch `style.fontSize` and `style.fontWeight` from the Figma node before setting any font-size in CSS.** Run `figma_font_audit.py` after any designer update — it fetches all frames and prints the canonical size table. Never set 26px (not in Figma), 19px (not in Figma), or 14px (not in Figma — minimum is 16px).

---

## SUMMARY: THE 5 ROOT CAUSES

All errors trace back to five habits to eliminate:

| # | Root Cause | Antidote |
|---|---|---|
| 1 | **Substituting judgment for Figma data** | Fetch the node JSON first. Never decide from visual intuition. |
| 2 | **Assuming HTML flow model matches Figma** | When Figma has explicit y-coords, use `position: absolute`. Do not assume flex/grid order will match. |
| 3 | **Claiming "done" without an explicit diff** | Every fix = screenshot + Figma frame comparison + explicit diff statement before reporting. |
| 4 | **Iterating fixes without reading prior state** | Before attempt N+1: read git history, read current file, screenshot current state, identify the single property that is wrong. |
| 5 | **Applying fixes narrowly, not site-wide** | When a bug pattern is found on one page, audit all pages for the same pattern before closing. |

---

## WORKFLOW (enforced every session)

```
1. git pull → confirm clean working tree
2. Fetch Figma node JSON (absoluteBoundingBox) for the section being touched
3. Read current HTML/CSS for that section
4. Write an explicit diff: "Figma says X, code has Y, changing to Z"
5. Edit code
6. Screenshot (Chrome headless, --disable-cache, temp file in project folder)
7. Crop to affected section; compare side-by-side with Figma
8. If not matching: read git history for prior attempts, identify single wrong property, fix only that
9. git add <specific files>; git commit (hrishi author, no Co-Authored-By); git push
10. Confirm push with git log --oneline -1; report hash to user
```

# Peptides — Elementor Homepage Template

An importable, fully editable Elementor page template built from the homepage
design. Header and footer are intentionally **not** included — the template
covers the page content only, so it drops into any theme's header/footer.

```
templates/peptides-homepage.json    <- import this into Elementor
assets/images/*.svg                 <- the artwork, as standalone files
build/                              <- generator scripts (optional, see below)
```

---

## Import

**As a reusable template**

1. WordPress admin → **Templates → Saved Templates**
2. **Import Templates** → upload `templates/peptides-homepage.json`
3. Edit any page with Elementor → folder icon in the canvas → **My Templates** →
   **Insert**

**Straight onto a page**

1. Create/edit a page with Elementor
2. Folder icon → **My Templates** → insert the imported template
3. Set the page's Elementor layout to **Full Width** (or **Elementor Canvas** if
   you don't want the theme header/footer)

The template imports as `type: page`, so Elementor will offer to apply the page
settings too. It sets only *Hide Title* and a white page background — accept or
decline, neither breaks the layout.

---

## What's inside

| # | Section | Notes |
|---|---------|-------|
| 1 | Hero | Gradient band, two badges, split-colour H1, two CTAs, slider dots |
| 2 | Trust bar | White card overlapping the hero, 4 icon boxes with dividers |
| 3 | Most-Ordered By Research | 4 product cards + carousel arrows |
| 4 | Browse By Category | 3 gradient/flat category cards |
| 5 | Built For Researchers | Dark band, `100%` stat, Certificate of Analysis |
| 6 | Explore Our Catalog | 4 product cards with stock badges |
| 7 | Feature strip | 99.8% Purity / Lab Verified / Secure Payment / Fast Shipping |
| 8 | Promo duo | "New Arrivals" + "Every Peptide. Every Batch." |
| 9 | FAQ | Two accordion columns, 8 questions |
| 10 | Newsletter | Teal gradient band with email capture |

### Built for editability

* **Free Elementor only.** Widgets used: `heading`, `text-editor`, `button`,
  `image`, `icon`, `icon-box`, `accordion`, `html`. No Elementor Pro required.
* **Classic Sections / Columns**, not Flexbox Containers — imports and stays
  editable on every Elementor version, old or current.
* **No custom CSS and no custom classes.** Every colour, size and spacing value
  is a normal control in the Style/Advanced panels, so anything can be changed
  by clicking it.
* Responsive sizes are set for tablet and mobile (typography, column widths,
  section padding).

---

## Design tokens

**Colours**

| Token | Hex | Used for |
|-------|-----|----------|
| Navy | `#0B1B3A` | Headings, primary buttons, dark bands |
| Navy raised | `#132A50` | Buttons on dark backgrounds |
| Teal | `#16A6A0` | Highlighted words, `100%`, links, hover |
| Teal light | `#2FB8AF` | Newsletter gradient end |
| Body text | `#5B6B7C` | Paragraphs |
| Muted | `#8A99A8` | Captions, icon-box descriptions |
| Border | `#E6ECF2` | Card borders, accordion hairlines |
| Hero gradient | `#E7F2F9` → `#EDF5FA` | Hero band |
| Panel | `#F7FAFC` | Product image panel |
| Category blue | `#5FAEE9` → `#3E8FD6` | Category 1, New Arrivals |
| Category mint | `#DEF0E2` | Category 2 |
| Category peach | `#FBE3C6` | Category 3 |
| Badge green | `#E9F4DA` / `#4E7A1E` | Bestseller, In Stock |
| Badge blue | `#DCEDFB` / `#1A5C9E` | Best Seller |
| Badge orange | `#FCE6C9` / `#94590F` | Low Stock |

To apply these globally: **Site Settings → Global Colors**, then repoint the
widgets at the global swatches if you'd rather manage colour in one place.

**Typography** — a single family, **Inter** (Google Fonts, loaded by Elementor
automatically). Weights carry the hierarchy:

| Role | Size | Weight |
|------|------|--------|
| H1 hero | 46 / 36 tablet / 29 mobile | 700 |
| Section H2 | 27 / 24 / 21 | 700 |
| Stat (`100%`) | 58 / 48 / 42 | 800 |
| Card title | 14.5 | 600 |
| Price | 17 | 700 |
| Body | 15 | 400 |
| Badge | 10, uppercase, +0.7 letter-spacing | 700 |

Content width is **1200px**.

---

## Images

All 14 images ship **embedded in the JSON as SVG data URIs**, so the template
looks right the moment it's imported and never depends on an external host.

To use your own product photography, click any image widget and pick from the
Media Library as usual — nothing else needs to change.

The same artwork is also in `assets/images/` as standalone SVGs if you'd rather
upload them to the Media Library first and point the widgets at real
attachments (better for CDN/caching on a production site).

---

## Things you'll want to wire up

These are placeholders by design — the template has no way to know your setup:

* **Buttons/links** all point at `#`. Set real URLs on Browse Catalog, Research
  Standards, Shop now, Add to Cart, See our testing, View Catalog, View All FAQ.
* **Add to Cart** buttons are styled `button` widgets, not WooCommerce widgets.
  If you're on WooCommerce, either link them to the product pages or swap the
  product rows for a WooCommerce Products widget once your catalogue exists.
* **Newsletter form** is an HTML widget with a styled input and button, so the
  section renders correctly out of the box. Replace it with your form plugin's
  widget/shortcode (Elementor Pro Forms, WPForms, Fluent Forms, Mailchimp) —
  the surrounding teal band and copy stay as they are.
* **Carousel arrows** in the two product rows are `icon` widgets — decorative,
  since a real carousel needs a Pro/third-party widget. Delete them or point
  them at a carousel if you add one.

One content change worth flagging: the last FAQ in the right-hand column of the
mockup was a joke placeholder. It's been replaced with *"Do you offer bulk or
wholesale pricing?"*. All FAQ answers are written as sensible starting copy —
review them before going live.

---

## Regenerating the template

The JSON is generated, not hand-written, so it stays maintainable. You only need
this if you want to change tokens globally or edit the artwork.

```bash
cd build
python3 build_template.py     # writes templates/*.json and assets/images/*.svg
python3 validate.py           # structure + free-widget-only checks
python3 render_preview.py     # build/preview.html, a static approximation
```

Requires Python 3 only — no dependencies. Design tokens live at the top of
`build/build_template.py`; the artwork lives in `build/svg_assets.py`.

Editing the template in Elementor and re-exporting is completely fine too — the
build scripts are a convenience, not a requirement.

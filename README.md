# Peptides — Elementor Homepage Template

An importable, fully editable Elementor page template built from the homepage
design. Header and footer are intentionally **not** included — the template
covers the page content only, so it drops into any theme's header/footer.

```
templates/peptides-homepage.json    <- import this into Elementor
compound-index.zip                  <- WooCommerce archive plugin, ready to upload
plugin/compound-index/              <- ...and its source
docs/slider-revolution-hero.md      <- how to build the hero slider
docs/archive-product-page.md        <- how to change the shop/category archive
assets/images/*.svg                 <- artwork (hero, COA, category, product vials)
build/                              <- generator scripts (optional, see below)
```

Two separate deliverables live here:

| | What it does |
|---|---|
| **Homepage** — `templates/peptides-homepage.json` | An Elementor template you import. Covered below. |
| **Product archive** — `compound-index.zip` | A WordPress plugin that restyles the shop and product-category pages. See **[docs/archive-product-page.md](docs/archive-product-page.md)**. |

Built with **Flexbox Containers** — no legacy Sections or Columns anywhere.

---

## Requirements

| | Needed for |
|---|---|
| Elementor **3.16+** | Flexbox Containers, nested Accordion |
| **WooCommerce** | the products in the two product rows |
| **Elementor Pro** | the WooCommerce Products widget (see the fallback below if you're on free Elementor) |
| **Slider Revolution** | the hero section |

Everything else uses free core Elementor widgets.

---

## Import

1. WordPress admin → **Templates → Saved Templates**
2. **Import Templates** → upload `templates/peptides-homepage.json`
3. Edit a page with Elementor → folder icon in the canvas → **My Templates** →
   **Insert**
4. Set the page's Elementor layout to **Full Width** (or **Elementor Canvas** to
   drop the theme header/footer)

Then do the three wiring steps below.

---

### 1. Products — pick a category, that's it

The two product rows are **WooCommerce Products** widgets. Nothing about the
products is hard-coded — no fixed names, prices, images or Add to Cart buttons.

Click the widget → **Query** → choose your **Product Category**. Those products
render, straight from WooCommerce, with live pricing and working cart buttons.
Under **Content** you can change how many show (`Columns` 4, `Rows` 1 by
default) and under **Style** you can restyle the cards.

> **On free Elementor?** Delete the Products widget, drop a **Shortcode** widget
> in its place, and paste:
> `[products category="your-category-slug" columns="4" limit="4"]`
> Same result, styled by your theme instead of by Elementor.

The circular arrows next to each product heading are `icon` widgets kept from
the design. They're decorative — a real carousel needs a carousel plugin. Delete
them if you don't want them.

### 2. Hero — Slider Revolution

The hero is a Shortcode widget containing `[rev_slider alias="peptides-hero"]`.
Build a slider with that alias and it appears.

**`docs/slider-revolution-hero.md` has the full build sheet** — slider settings,
every layer with its X/Y position, fonts, colours, animation timings, and the
responsive overrides. The product artwork for the slide is
`assets/images/hero-vial.svg`.

The container behind the slider already carries the hero gradient and the bottom
padding that lets the trust bar overlap it, so set the slider background to
transparent.

Prefer Slider Revolution's own Elementor widget? Delete the Shortcode widget and
drop the **Slider Revolution** widget into the same container.

### 3. Everything else

* **Links** all point at `#` — set real URLs on Shop now, See our testing, View
  Catalog, View All FAQ, and the hero buttons.
* **Newsletter** is an HTML widget with a styled input and button so the section
  renders correctly out of the box. Replace it with your form plugin's widget
  (Elementor Pro Forms, WPForms, Fluent Forms, Mailchimp) — the teal band and
  copy stay as they are.

---

## What's inside

| # | Section | Rendered by |
|---|---------|-------------|
| 1 | Hero | Slider Revolution |
| 2 | Trust bar | Elementor — white card overlapping the hero, 4 icon boxes |
| 3 | Most-Ordered By Research | WooCommerce Products |
| 4 | Browse By Category | Elementor — 3 gradient/flat cards |
| 5 | Built For Researchers | Elementor — dark band, `100%` stat, Certificate of Analysis |
| 6 | Explore Our Catalog | WooCommerce Products |
| 7 | Feature strip | Elementor — purity / lab / payment / shipping |
| 8 | Promo duo | Elementor — "New Arrivals" + "Every Peptide. Every Batch." |
| 9 | FAQ | Elementor — two nested Accordions, 8 questions |
| 10 | Newsletter | Elementor — teal gradient band |

### Built for editability

* **Containers only**, `flex-direction` + percentage widths. Rows use
  `nowrap` so children shrink to absorb the gap, and stack by switching
  `flex-direction` to `column` at the tablet or mobile breakpoint — the same
  pattern Elementor's own container presets use.
* **No custom CSS and no custom classes.** Every colour, size and spacing value
  is a normal control in the Layout/Style/Advanced panels.
* Responsive sizes are set for tablet and mobile (typography, widths, padding,
  stacking direction).

---

## Icons

Every icon is **Font Awesome Regular** (`far`) — the outline set. There is no
solid (`fas`) icon anywhere in the template; `build/validate.py` fails the build
if one appears.

`arrow-alt-circle-left`, `arrow-alt-circle-right`, `check-circle`, `clipboard`,
`clock`, `clone`, `credit-card`, `dot-circle`, `envelope`, `file-alt`, `gem`,
`minus-square`, `paper-plane`, `plus-square`, `snowflake`

Button arrows are the thin `→` glyph in the button label rather than an icon, so
they stay hairline-weight next to the outline set.

One consequence worth knowing: Font Awesome **Free** ships only ~150 Regular
icons, and lab-specific glyphs (flask, vial, DNA, shield, truck, padlock) exist
only in Solid. The icons above are the closest outline equivalents. If you want
the exact lab iconography, either add Font Awesome Pro, or enable SVG uploads
and switch the icon controls to **Upload SVG** with your own line icons — the
widgets don't change, only the icon source.

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
| Category blue | `#5FAEE9` → `#3E8FD6` | Category 1, New Arrivals |
| Category mint | `#DEF0E2` | Category 2 |
| Category peach | `#FBE3C6` | Category 3 |

To manage colour in one place, add these under **Site Settings → Global Colors**
and repoint the widgets at the global swatches.

**Typography** — a single family, **Inter** (Google Fonts, loaded by Elementor
automatically). Weights carry the hierarchy:

| Role | Size | Weight |
|------|------|--------|
| H1 hero (in Slider Revolution) | 46 / 36 tablet / 29 mobile | 700 |
| Section H2 | 27 / 24 / 21 | 700 |
| Stat (`100%`) | 58 / 48 / 42 | 800 |
| Body | 15 | 400 |

Content width is **1200px**.

---

## Images

The five images the template still owns (Certificate of Analysis, three category
cards, New Arrivals vial) ship **embedded as SVG data URIs**, so the template
looks right the moment it's imported and never depends on an external host.
Click any image widget to swap in your own.

`assets/images/` also holds the standalone files:

| File | Use |
|------|-----|
| `hero-vial.svg` | the hero product shot — upload for the Slider Revolution slide |
| `coa-certificate.svg` | Certificate of Analysis card |
| `category-*.svg` | the three category cards |
| `vial-bpc-157.svg`, `vial-cjc-1295.svg`, `vial-ipamorelin.svg`, `vial-tb-500.svg` | placeholder product shots — useful as WooCommerce product images until you have photography |

---

## Content note

The last FAQ in the right-hand column of the mockup was a joke placeholder. It's
been replaced with *"Do you offer bulk or wholesale pricing?"*. All FAQ answers
are sensible starting copy — review them before going live.

---

## The archive plugin

`compound-index.zip` restyles the WooCommerce shop and product-category archives
into the Compound Index layout — stats header, category chips with live counts,
and specification-led product cards. Upload it under **Plugins → Add New →
Upload Plugin**, then configure it at **Products → Compound Index**.

The product grid stays WooCommerce's own main query, so category archives,
search, sorting and pagination all work natively and new products appear on
their own. Full write-up, including why your theme has no `archive-product.php`
to edit, is in **[docs/archive-product-page.md](docs/archive-product-page.md)**.

Rebuild the zip after editing the source:

```bash
./build/make-plugin-zip.sh
```

---

## Regenerating the template

The JSON is generated, not hand-written, so it stays maintainable. You only need
this if you want to change tokens globally or edit the artwork.

```bash
cd build
python3 build_template.py     # writes templates/*.json and assets/images/*.svg
python3 validate.py           # structure, container, and outline-icon checks
python3 render_preview.py     # build/preview.html, a static approximation
```

Requires Python 3 only — no dependencies. Design tokens live at the top of
`build/build_template.py`; the artwork lives in `build/svg_assets.py`.

The preview renderer draws stand-ins for the two plugin-rendered blocks (the
Slider Revolution hero and the WooCommerce product rows) so you can see the
finished page shape; both are labelled in the output.

Editing the template in Elementor and re-exporting is completely fine too — the
build scripts are a convenience, not a requirement.

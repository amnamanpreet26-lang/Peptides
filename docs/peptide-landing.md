# Peptide Landing Page — Elementor template

`templates/peptide-landing.json` — a full page template built from the reference
design. Import it under **Templates → Saved Templates → Import**, then insert it
on a page.

Built with **Flexbox Containers**. Everything is a free core Elementor widget
except the two product areas, which use the Elementor Pro **WooCommerce
Products** widget.

---

## Requirements

| | Needed for |
|---|---|
| Elementor **3.16+** | Containers, nested Tabs, nested Accordion |
| **WooCommerce** | the products in the showcase and best-sellers |
| **Elementor Pro** | the WooCommerce Products widget |

The **Satoshi** font is already registered by your theme's `functions.php` at
weights **300 / 400 / 500**. The template only uses 400 and 500, so nothing gets
a browser-faked bold. If you add a heavier Satoshi `@font-face` later you can
raise the weights; until then, keep to those three.

---

## Sections

| # | Section | Contents |
|---|---------|----------|
| 1 | Hero | Eyebrow, three-line heading, description, two buttons, three trust points, product shot |
| 2 | Product showcase | Eyebrow, heading, *Shop All*, **category tabs** with WooCommerce products in each |
| 3 | About / lab testing | Dark band — eyebrow, heading, copy, three counters, two buttons, product visual |
| 4 | Best sellers | Centred eyebrow + heading, WooCommerce products (4 across) |
| 5 | Why researchers choose | Centred eyebrow + heading, four icon columns |
| 6 | FAQ | Eyebrow, heading, contact copy + button, five-item accordion |
| 7 | Footer | Brand, socials, two link columns, newsletter, legal bar |

**The footer is included** because it is in the design. If your theme already
outputs a footer, delete that last container — otherwise you will have two.

---

## The category tabs

This is the part with the moving pieces, so it is worth a minute.

The showcase is Elementor's **Tabs** widget with **six tabs**, and each tab
holds its own **WooCommerce Products** widget. That means the tab labels are
real tabs and the products inside each one come from WooCommerce, not from
anything hard-coded.

Set it up like this:

1. Click the Tabs widget → **Content → Tabs**. Rename, reorder, add or remove
   tabs. The shipped labels are *All, Repair & Recovery, Anti-Aging, Hydration,
   Brightening, Barrier Support* — change them to your own categories.
2. Click into a tab, select the **Products** widget inside it, and open
   **Query → Product Categories**. Pick the category that tab should show.
3. Leave the **All** tab's query empty so it lists everything.

Under **Content** on each Products widget you can change `Columns` (5 by
default, matching the design) and `Rows`. Under **Style** you can restyle the
cards.

If you add or remove a tab, remember each tab needs its own Products widget —
copy an existing one rather than starting from an empty tab.

> **On free Elementor?** Replace each Products widget with a **Shortcode**
> widget containing
> `[products category="your-category-slug" columns="5" limit="5"]`.
> Same result, styled by your theme.

The **Best sellers** section is a single Products widget — point its query at a
"Best sellers" category, or set **Order by → Popularity** to have WooCommerce
work it out from sales.

---

## Colours

Both requested colours are in, and the dark one is deliberately *not* used
everywhere — large areas use a lighter version of it, and the accent appears as
a pale wash in places rather than at full strength.

| Token | Hex | Where |
|-------|-----|-------|
| Accent | `#019DA6` | Eyebrows, "You-Focused.", counters, primary button on the dark band, newsletter button, icon tiles |
| Accent deep | `#017A81` | Hover |
| Accent pale | `#E6F5F6` | Soft washes |
| Near-black | `#00030E` | Hero buttons, headings, footer — used sparingly |
| Near-black soft | `#141821` | The large dark band, so it reads softer than pure black |
| Body | `#4A5160` | Paragraphs |
| Muted | `#8A8F9C` | Captions |
| Hero band | `#EFEEEA` | Warm neutral |
| Product band | `#EFF2F3` | Cool neutral |
| FAQ band | `#F6F5F2` | Warm neutral |

To manage them in one place, add the first four under **Site Settings → Global
Colors** and repoint the widgets at the swatches.

## Type scale

| Role | Size (desktop / tablet / mobile) | Weight |
|------|------|--------|
| Hero H1 | 54 / 42 / 34 | 500 |
| Section heading | 34–38 / 28–30 / 24–26 | 400 |
| Counter value | 28 / – / 24 | 500 |
| Body | 15 | 400 |
| Eyebrow | 11, uppercase, +1.8 tracking | 500 |
| Buttons | 12.5, uppercase, +0.8 tracking | 500 |

Content width is **1240px**.

---

## Images

Two images ship **embedded as SVG data URIs**, so the page looks right the
moment it imports and depends on no external host:

| File | Where |
|------|-------|
| `assets/images/landing-hero.svg` | hero product shot, plinth and the "free mini body oil" badge |
| `assets/images/landing-lab.svg` | the bottle-and-liquid visual on the dark band |

Click either image widget to swap in your own photography. The standalone files
are in `assets/images/` if you would rather upload them to the Media Library
first.

---

## Placeholders to wire up

* **Links** all point at `#` — Shop Best Sellers, Learn the Science, Shop All,
  View Lab Results, Download Sample Report, Contact Support, the footer link
  lists and the social icons.
* **Newsletter** is an HTML widget with a styled input and button so the footer
  renders correctly out of the box. Replace it with your form plugin's widget.
* **Brand name** in the footer reads *Your Brand* — replace it with your
  wordmark or swap the heading for an Image widget.
* **Counters** (99.5%+, 100%, 24h) are typed values, not calculated. Edit them
  in place.

---

## Rebuilding

```bash
cd build
python3 build_landing.py     # writes templates/peptide-landing.json + the SVGs
python3 render_landing.py    # build/landing-preview.html, a static approximation
```

Design tokens are at the top of `build/build_landing.py`; the artwork lives in
`build/svg_landing.py`. Editing the template in Elementor and re-exporting is
equally fine — the scripts are a convenience, not a requirement.

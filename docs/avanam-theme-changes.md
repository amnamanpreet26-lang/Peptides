# Avanam — Compound Index archive

The shop and product-category archives now render in the Compound Index design,
straight from the theme. Products are untouched: the grid is still WooCommerce's
own main query, and nothing new is stored against a product.

Install `avanam-compound-index.zip` under **Appearance → Themes → Add New →
Upload Theme** (tick *Replace current with uploaded* if WordPress asks).

---

## What changed in the theme

| File | |
|---|---|
| `functions.php` | **modified** — one `require` line added after the theme initialises |
| `woocommerce/archive-product.php` | **new** — the archive layout |
| `inc/compound-index/compound-index.php` | **new** — loader + template-part helper |
| `inc/compound-index/category-fields.php` | **new** — the header fields on product categories |
| `inc/compound-index/settings.php` | **new** — shop-page defaults screen |
| `inc/compound-index/archive.php` | **new** — header, chips and card data |
| `inc/compound-index/parts/*.php` | **new** — header, toolbar, card, pagination, cta, empty |
| `assets/css/compound-index.css` | **new** — loaded only on those archives |

Nothing else in Avanam was edited. To switch the layout off entirely, remove the
`require` line from `functions.php`; the theme goes back to its own archive.

Avanam has no `archive-product.php` of its own — it reshapes WooCommerce through
hooks — which is why there was no file to find. Adding
`avanam/woocommerce/archive-product.php` is the standard WooCommerce theme
override and takes precedence over the plugin's copy.

Three of the theme's own behaviours are stood down on these archives only:

* its archive title / hero, via the theme's `base_post_layout` filter
* its results-count and ordering bar (that one callback only, so store notices
  and anything a plugin adds to the same hook still run)
* WooCommerce's default pagination, replaced by the design's pill pagination

---

## The category fields

**Products → Categories →** add or edit a category. Each one carries its own
header:

| Field | What it does |
|---|---|
| Header eyebrow | Small line above the title. Blank hides it. |
| Header title | Overrides the category name. Blank uses the category name. |
| Header intro | The paragraph under the title. Blank uses the category description. |
| Counter 1–4 — value | The big number. |
| Counter 1–4 — label | The small caption under it. |
| Card badge | Plain badge in the top-right of every card in this category — this is how *Blend* appears in the design. Blank for none. |

Any field left blank falls back to **Products → Compound Index**, so you only
fill in what differs per category.

### Counter tokens

Type a plain value (`36 mo`, `99.2%`) or a token that's worked out for you:

| Token | Gives |
|---|---|
| `{count}` | products in view — on a category archive, that category's count |
| `{total}` | products in the whole catalogue |
| `{categories}` | number of product categories holding products |

So `{count}` + label `Compounds listed` keeps itself up to date as you add
products. That's the default for counter 1.

---

## Shop-page defaults — Products → Compound Index

Same header fields for the main shop page, plus the settings that apply
everywhere:

* **Toolbar** — search box, category chips, chip counts, "12 of 55 shown", sort
  dropdown, each on/off
* **Columns** — 2 to 4; the design uses 3
* **Status badge** — the highlighted badge in the top-left of every card
  (*Documented* by default). Blank for none.
* **Card link text** — *Specification* by default
* **Closing panel** — heading, text, button label and URL

### Category chips

Each chip shows that category's WooCommerce product count and links to its real
archive, so clicking *Peptides* loads `/product-category/peptides/` and the grid
below is that category's products from WooCommerce. Counts can be turned off.

---

## Card details come from product attributes

Nothing is added to your products. The card reads **existing WooCommerce
attributes**, so set them up once under **Products → Attributes** (e.g. CAS,
Molecular weight, Purity, Latest lot) and assign them on products as normal.

Then in **Products → Compound Index → Card details**:

* **Spec line** — attributes joined by a dot on the small grey line under the
  product name
* **Data rows** — attributes shown as label / value rows, like *Purity* and
  *Latest lot* in the design

Until you pick any, cards fall back to showing the price, so the grid never
looks broken. Attributes with no value on a given product are simply left out.

---

## Customising

**Colours and spacing** are CSS custom properties at the top of
`assets/css/compound-index.css`:

```css
.compound-index {
	--ci-navy: #14304f;
	--ci-badge-bg: #d3ebef;
	--ci-radius: 10px;
}
```

The title uses **Satoshi**, the font already registered in `functions.php`, with
a system fallback stack.

**Markup** — a child theme can override any part by placing a file of the same
name in its `compound-index/` directory, e.g.
`avanam-child/compound-index/card.php`.

**Hooks** — `avanam_ci_is_active`, `avanam_ci_chips`, `avanam_ci_card_badges`,
`avanam_ci_card_rows`, `avanam_ci_breadcrumb`, and
`avanam_ci_after_card_body` for putting an Add to Cart button back:

```php
add_action( 'avanam_ci_after_card_body', 'woocommerce_template_loop_add_to_cart' );
```

---

## Notes

**Don't run the standalone plugin as well.** `compound-index.zip` from the
earlier round does the same job from outside the theme. Use one or the other —
if the plugin is active, deactivate it.

**Add to Cart** is not on the cards by design; the action is *Specification →*,
linking to the product page. See the hook above to add it back.

**The site header** — logo, menu, dark-mode toggle, the *Updates* button — is
Avanam's own header, set in the Customizer and Appearance → Menus. It was left
alone so it stays consistent across the site.

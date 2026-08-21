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
| `inc/compound-index/archive.php` | **new** — header, chips and column count |
| `inc/compound-index/parts/*.php` | **new** — header, toolbar, pagination, cta, empty |
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
* **Columns** — 2 to 6, feeding WooCommerce's own `loop_shop_columns`, so the
  theme lays the grid out as it normally would. Default 4.
* **Closing panel** — heading, text, button label and URL

### Category chips

Each chip shows that category's WooCommerce product count and links to its real
archive, so clicking *Peptides* loads `/product-category/peptides/` and the grid
below is that category's products from WooCommerce.

**Which categories** — three choices:

* **Top-level product categories** (default) — picks itself up as you add
  categories
* **Every product category, sub-categories included**
* **Only the ones I pick** — a multi-select of every category

**Empty categories** are shown by default, so a category you have just created
appears on the shop page straight away even before anything is assigned to it.
Tick *Hide categories that have no products yet* if you would rather they waited.

The first chip is *All*, which links to the shop page and lists every product.

---

## Product cards

The grid is **WooCommerce's own loop, rendered by Avanam** — the same
`.product-thumbnail`, `.product-details`, `.product-actions` and
`.add_to_cart_button` markup the theme produces everywhere else. Nothing about
the card is rebuilt, so product title, rating, price and Add to Cart all behave
exactly as WooCommerce intends, and any plugin that hooks the loop still works.

The look — product shot floated above the card and tilted, white card with a
hairline border, full-width navy button — comes from the CSS in
`assets/css/compound-index.css`, which loads only on these archives.

> **If you pasted that CSS into Appearance → Customize → Additional CSS,
> remove it from there.** It now ships with the theme, and keeping both means
> two copies fighting each other.

Three corrections were made to it on the way in:

| Was | Now |
|---|---|
| The card shadow was scoped to `.product_cat-uncategorized` | Applies to every product card — otherwise the shadow vanished the moment a product was given a real category |
| `:hover img` set `transform` twice, so `scale(1.08)` never applied | The two values are combined: `rotate(20deg) scale(1.08)`. Drop the scale if you only want the rotation |
| The floating `.product-thumbnail` had no width | `width: 100%`, so the `margin: auto` on the image actually centres it whatever size the photo is |

Two duplicate selectors were also merged into one rule each, keeping the values
that were winning, so there is nothing to trip over when you edit it.

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
`avanam-child/compound-index/header.php`.

**Hooks** — `avanam_ci_is_active`, `avanam_ci_chips`, `avanam_ci_breadcrumb`.
The product card itself is WooCommerce's, so the usual loop hooks
(`woocommerce_before_shop_loop_item_title`, `woocommerce_after_shop_loop_item`
and friends) apply to it as normal.

---

## Notes

**Don't run the standalone plugin as well.** `compound-index.zip` from the
earlier round does the same job from outside the theme. Use one or the other —
if the plugin is active, deactivate it.

**The site header** — logo, menu, dark-mode toggle, the *Updates* button — is
Avanam's own header, set in the Customizer and Appearance → Menus. It was left
alone so it stays consistent across the site.

# Changing the WooCommerce archive (shop / category) page

Two parts: **why you can't find the file**, and **the plugin that changes the
layout without needing it**.

---

## 1. Why there is no `archive-product.php` in your theme

WooCommerce resolves the shop and category archive in this order:

```
1. yourtheme-child/woocommerce/archive-product.php     <- child theme override
2. yourtheme/woocommerce/archive-product.php           <- parent theme override
3. wp-content/plugins/woocommerce/templates/archive-product.php   <- the real one
```

Most commercial themes — Codezeel's included — **do not ship
`archive-product.php` at all**. They leave WooCommerce's own template in place
and change the output by hooking into it instead, from files like:

```
wp-content/themes/<theme>/inc/woocommerce.php
wp-content/themes/<theme>/framework/woocommerce/…
wp-content/themes/<theme>/functions.php
```

using hooks such as `woocommerce_before_shop_loop`,
`woocommerce_after_shop_loop_item`, `woocommerce_before_main_content`. So
searching the theme folder for the template finds nothing, because there is
nothing to find. That's normal, not a broken install.

### Check what your theme actually overrides

**WooCommerce → Status → Templates.** It lists every WooCommerce template your
theme overrides and flags any that are out of date. If `archive-product.php`
isn't listed there, your theme isn't overriding it.

The card markup, by the way, is a different file — `content-product.php` — and
newer WooCommerce splits it further into `woocommerce/loop/title.php`,
`loop/price.php`, `loop/add-to-cart.php` and so on.

### Three ways to change the archive

| Approach | Survives theme updates | Notes |
|---|---|---|
| Edit the parent theme | ❌ No | Wiped on the next update. Don't. |
| Child theme override — copy WooCommerce's `archive-product.php` to `yourtheme-child/woocommerce/` | ✅ Yes | Standard approach, but you inherit the theme's hooks and have to fight them |
| A plugin that swaps the template | ✅ Yes | Theme-independent, and turns off cleanly |

This repo takes the third route, because you couldn't find the file and because
it keeps the layout intact if you ever change themes.

---

## 2. The Compound Index plugin

`plugin/compound-index/` replaces the archive with the layout from your design:
breadcrumb, big title, intro, four counters, a search field, category chips with
counts, the three-column card grid, pagination and the closing panel.

**Products always come from WooCommerce.** The grid is WooCommerce's ordinary
main query — the plugin never queries or hard-codes products. So a category
archive shows that category's products, search works, sorting works, pagination
works, and new products appear on their own.

### Install

1. Zip the `plugin/compound-index` folder (or use the ready-made
   `compound-index.zip`)
2. **Plugins → Add New → Upload Plugin** → choose the zip → Install → Activate
3. Visit your shop page — the layout is already applied

To hand the archive back to your theme at any time, deactivate the plugin, or
turn off all three checkboxes under *Where the layout applies*.

### Set it up: Products → Compound Index

| Section | What it controls |
|---|---|
| **Where the layout applies** | Shop page, category archives, tag archives — each independently. Also whether to suppress the theme's own page title and breadcrumb. Column count (2–4, design uses 3). |
| **Page header** | Breadcrumb on/off, the title (archive title or a fixed one), and the intro paragraph. On a category archive the category description wins if it has one. |
| **Counters** | The four figures. See below. |
| **Category chips** | On/off, whether to show counts, and which categories appear. |
| **Toolbar** | Search box, "12 of 55 shown", sort dropdown — each on/off, plus the search placeholder. |
| **Card badges** | The "Documented" badge rule, and which categories get a second badge (this is how "Blend" appears). |
| **Closing panel** | Heading, text, button label and URL. |

### The counters — where you add them

**Products → Compound Index → Counters.** Four rows, each one either a number
you type or a figure worked out from your catalogue:

| Source | What you get |
|---|---|
| Fixed value I type below | Whatever you type, e.g. `36` with suffix ` mo` |
| Number of products in this archive | Live count. On a category archive it counts that category |
| Number of products in the whole catalogue | Live count across the shop |
| **Number of product categories** | Live count of categories holding products |
| Average of a product field | e.g. mean purity |
| Median of a product field | e.g. `99.2%` median purity |
| Percent of products with a field filled in | e.g. `100%` of lots having a COA |

Each row also takes a **suffix** (`%`, ` mo`), **decimals** (0–3) and the
**label** underneath.

The design's four map to: *Number of products in this archive* → `Compounds
listed`; *Median of `Purity`* with suffix `%`, 1 decimal → `Median purity`;
*Percent of products with `Certificate of analysis URL` filled* → `Lots with a
COA`; *Fixed value* `36` + suffix ` mo` → `Records retained`. Those are the
defaults, so out of the box it matches.

Computed figures are cached for 12 hours and recalculated whenever you save a
product or change these settings.

### The chip counts

Each chip shows that category's WooCommerce product count and links to the real
category archive — so clicking *Peptides* loads
`/product-category/peptides/`, and the grid below is that category's products
straight from WooCommerce. Turn the numbers off with *Show the product count on
each chip*.

Choose **all top-level categories** (updates itself as you add categories) or
**only the ones I pick**.

### Filling in the card data

Each product gets a **Compound Index** tab in the product data panel
(Products → edit a product → the tabs beside General / Inventory):

| Field | Appears as |
|---|---|
| CAS number | `CAS 137525-51-0 · …` under the product name |
| Molecular weight | `… · 1419.5 g/mol` |
| Spec line override | Replaces both of the above — use it for blends: `5 mg + 5 mg · blended 1:1` |
| Purity | The `Purity` row, and feeds the median purity counter |
| Latest lot | The `Latest lot` row |
| Certificate of analysis URL | Earns the *Documented* badge and feeds the COA counter |

Empty fields are simply left out — a product with no CAS number just doesn't
show that line.

---

## 3. Customising further

**Colours and spacing** — every value is a CSS custom property at the top of
`assets/compound-index.css`. Override them in your child theme:

```css
.compound-index {
	--ci-navy: #0b1b3a;
	--ci-badge-bg: #d9f2ee;
	--ci-radius: 6px;
}
```

**Markup** — copy any template into your theme and it wins automatically:

```
yourtheme/compound-index/archive-product.php
yourtheme/compound-index/content-product.php
yourtheme/compound-index/parts/page-header.php
yourtheme/compound-index/parts/toolbar.php
yourtheme/compound-index/parts/cta.php
yourtheme/compound-index/parts/pagination.php
yourtheme/compound-index/parts/empty.php
```

**Hooks** — `compound_index_is_active`, `compound_index_chips`,
`compound_index_badges`, `compound_index_card_rows`,
`compound_index_template_part`.

---

## 4. If something looks off

**The theme's own title or breadcrumb still shows.** Some themes print theirs
from `header.php` rather than through WooCommerce, so the plugin can't remove
it. Look for a page-header/title-bar option in the theme's own settings and
turn it off for the shop.

**The archive is narrower or wider than expected.** The plugin renders inside
the theme's WooCommerce wrapper, so the theme's container controls the outer
width. `.compound-index` caps at `1180px`; change `max-width` if your theme's
container is different.

**Sidebar still showing.** That's the theme's, from `woocommerce_sidebar`. Turn
the shop sidebar off in the theme or Appearance → Widgets.

**Add to Cart is gone.** Deliberate — the design is an information index whose
card action is *Specification →*, linking to the product page. The card ships
with a `compound_index_after_card_body` hook for putting things back, so this in
your child theme's `functions.php` is enough:

```php
add_action( 'compound_index_after_card_body', 'woocommerce_template_loop_add_to_cart' );
```

Loop plugins (wishlist, quick view) hook `woocommerce_after_shop_loop_item`,
which a bespoke card doesn't fire. Same hook brings them back:

```php
add_action( 'compound_index_after_card_body', function () {
	do_action( 'woocommerce_after_shop_loop_item' );
} );
```

**Note on the site header.** The navigation bar at the top of your design — logo,
menu, dark-mode toggle, the *Updates* button — is site-wide theme furniture, not
part of the product archive. It's set in your theme's header options and
Appearance → Menus. This plugin deliberately doesn't touch it, so it stays
consistent with the rest of the site. Say the word if you want that rebuilt too.

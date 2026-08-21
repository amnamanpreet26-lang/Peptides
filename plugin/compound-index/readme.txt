=== Compound Index - WooCommerce Archive Layout ===
Requires at least: 6.0
Tested up to: 6.8
Requires PHP: 7.4
WC requires at least: 7.0
Stable tag: 1.0.0
License: GPLv2 or later

Replaces the WooCommerce shop and product-category archives with a data-led
index layout: a stats header, category filter chips with live counts, and cards
built around specification data rather than price.

== Description ==

The product grid is WooCommerce's ordinary main query. The plugin never queries
or hard-codes products, so category archives, search, sorting and pagination all
behave exactly as WooCommerce intends, and new products appear on their own.

What it adds:

* A page header with breadcrumb, title, intro and four configurable counters.
* Counters that can be fixed numbers or figures worked out from the catalogue -
  product counts, category counts, average or median of a product field, or the
  percentage of products with a field filled in.
* Category chips showing each category's product count, linking to that
  category's archive.
* Search, result count and a sort dropdown (with alphabetical sorting, which
  WooCommerce leaves out of the default list).
* Cards showing CAS number, molecular weight, purity and latest lot, with
  badges driven by product data and category.
* A "Compound Index" tab on the product data panel for those fields.

Settings live under Products > Compound Index.

== Overriding templates ==

Copy any file from the plugin's templates directory to
yourtheme/compound-index/ and it takes precedence. Colours and spacing are CSS
custom properties on .compound-index.

== Changelog ==

= 1.0.0 =
* First release.

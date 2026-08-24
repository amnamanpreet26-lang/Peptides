#!/usr/bin/env python3
"""Generate the peptide landing page Elementor template.

Output: templates/peptide-landing.json

Flexbox Containers throughout, free core widgets plus the Elementor Pro
WooCommerce Products widget for the two product areas. The product showcase uses
Elementor's nested Tabs widget with one Products widget per tab, so the category
tabs are real and the products inside them come from WooCommerce.
"""

import hashlib
import itertools
import json
import os

import svg_landing as A

# ---------------------------------------------------------------------------
# Design tokens
# ---------------------------------------------------------------------------
INK = "#00030E"           # the requested near-black, used sparingly
INK_SOFT = "#141821"      # lighter version of it, for large dark areas
BODY = "#4A5160"          # lighter still, for paragraphs
MUTED = "#8A8F9C"         # captions and meta
TEAL = "#019DA6"          # the requested accent
TEAL_DEEP = "#017A81"     # hover
TEAL_TINT = "#E6F5F6"     # pale wash of the accent
TEAL_SOFT = "#B9E3E5"     # mid tint, for rules on dark
LINE = "#E6E8EC"
SURFACE = "#EFF2F3"       # product band
SURFACE_WARM = "#F6F5F2"  # faq band
HERO_BG = "#EFEEEA"
WHITE = "#FFFFFF"

# Satoshi is registered by the theme at 300 / 400 / 500 only. Staying inside
# those weights avoids the browser synthesising a fake bold.
FONT = "Satoshi"
W_LIGHT, W_BOOK, W_MED = "300", "400", "500"

WIDTH = 1240

_used = set()
_counter = itertools.count(1)


def nid():
    while True:
        v = hashlib.md5(str(next(_counter)).encode()).hexdigest()[:7]
        if v not in _used:
            _used.add(v)
            return v


# ---------------------------------------------------------------------------
# Value helpers
# ---------------------------------------------------------------------------
def dim(top, right, bottom, left, unit="px", linked=False):
    return {"unit": unit, "top": str(top), "right": str(right),
            "bottom": str(bottom), "left": str(left), "isLinked": linked}


def all_(v, unit="px"):
    return dim(v, v, v, v, unit=unit, linked=True)


def sz(size, unit="px"):
    return {"unit": unit, "size": size, "sizes": []}


def gaps(column, row=None):
    row = column if row is None else row
    return {"unit": "px", "size": column, "column": str(column),
            "row": str(row), "isLinked": column == row}


def shadow(v=6, blur=24, color="rgba(0,3,14,0.06)", h=0, spread=0):
    return {"horizontal": h, "vertical": v, "blur": blur,
            "spread": spread, "color": color}


def typo(p="typography_", size=None, weight=None, lh=None, ls=None,
         transform=None, tablet=None, mobile=None, family=FONT):
    t = {p + "typography": "custom", p + "font_family": family}
    if size is not None:
        t[p + "font_size"] = sz(size)
    if tablet is not None:
        t[p + "font_size_tablet"] = sz(tablet)
    if mobile is not None:
        t[p + "font_size_mobile"] = sz(mobile)
    if weight is not None:
        t[p + "font_weight"] = str(weight)
    if lh is not None:
        t[p + "line_height"] = sz(lh, "em")
    if ls is not None:
        t[p + "letter_spacing"] = sz(ls)
    if transform is not None:
        t[p + "text_transform"] = transform
    return t


def merge(*dicts):
    out = {}
    for d in dicts:
        out.update(d)
    return out


def ico(name, lib="fa-regular", prefix="far"):
    return {"value": f"{prefix} fa-{name}", "library": lib}


# ---------------------------------------------------------------------------
# Element factories
# ---------------------------------------------------------------------------
def W(widget_type, **settings):
    return {"id": nid(), "elType": "widget", "widgetType": widget_type,
            "settings": settings, "elements": [], "isInner": False}


def CONT(children, **settings):
    return {"id": nid(), "elType": "container", "settings": settings,
            "elements": children, "isInner": False}


def band(children, pad_top=96, pad_bottom=96, gap=0, **extra):
    s = {
        "content_width": "boxed",
        "boxed_width": sz(WIDTH),
        "flex_direction": "column",
        "flex_gap": gaps(gap),
        "padding": dim(pad_top, 24, pad_bottom, 24),
        "padding_tablet": dim(int(pad_top * 0.7), 24, int(pad_bottom * 0.7), 24),
        "padding_mobile": dim(int(pad_top * 0.55), 18, int(pad_bottom * 0.55), 18),
    }
    s.update(extra)
    return CONT(children, **s)


def row(children, gap=24, align="center", justify=None, stack="mobile",
        width=None, tablet=None, mobile=100, **extra):
    """Rows stay nowrap so children shrink to absorb the gap, and stack by
    switching flex-direction at the breakpoint."""
    s = {
        "content_width": "full",
        "flex_direction": "row",
        "flex_gap": gaps(gap),
        "flex_wrap": "nowrap",
        "padding": all_(0),
    }
    if align:
        s["flex_align_items"] = align
    if justify:
        s["flex_justify_content"] = justify
    if stack in ("tablet", "mobile"):
        s["flex_direction_mobile"] = "column"
    if stack == "tablet":
        s["flex_direction_tablet"] = "column"
    if width is not None:
        s["width"] = sz(width, "%")
        s["width_mobile"] = sz(mobile, "%")
    if tablet is not None:
        s["width_tablet"] = sz(tablet, "%")
    s.update(extra)
    return CONT(children, **s)


def cell(children, width=None, tablet=None, mobile=100, gap=0, **extra):
    s = {
        "content_width": "full",
        "flex_direction": "column",
        "flex_gap": gaps(gap),
        "padding": all_(0),
    }
    if width is not None:
        s["width"] = sz(width, "%")
        s["width_mobile"] = sz(mobile, "%")
    if tablet is not None:
        s["width_tablet"] = sz(tablet, "%")
    s.update(extra)
    return CONT(children, **s)


# ---------------------------------------------------------------------------
# Widget shortcuts
# ---------------------------------------------------------------------------
def heading(title, size=34, color=INK, weight=W_BOOK, tag="h2", align="left",
            lh=1.2, ls=None, transform=None, tablet=None, mobile=None,
            margin=None, **extra):
    s = {"title": title, "header_size": tag, "align": align, "title_color": color}
    s.update(typo(size=size, weight=weight, lh=lh, ls=ls, transform=transform,
                  tablet=tablet, mobile=mobile))
    if margin is not None:
        s["_margin"] = margin
    s.update(extra)
    return W("heading", **s)


def eyebrow(text_, color=TEAL, align="left", margin=None, rule=True):
    """Small tracked label above a heading, with the little rule from the design."""
    label = f'<span style="display:inline-block;width:22px;height:1px;background:{color};' \
            f'vertical-align:middle;margin-right:10px"></span>{text_}' if rule else text_
    return heading(label, size=11, color=color, weight=W_MED, tag="div", align=align,
                   lh=1.4, ls=1.8, transform="uppercase",
                   margin=margin if margin is not None else dim(0, 0, 14, 0))


def text(html, size=15, color=BODY, lh=1.75, align="left", weight=W_BOOK,
         margin=None, mobile=None):
    s = {"editor": html, "align": align, "text_color": color}
    s.update(typo(size=size, weight=weight, lh=lh, mobile=mobile))
    if margin is not None:
        s["_margin"] = margin
    return W("text-editor", **s)


def button(label, bg=INK, fg=WHITE, size=12.5, weight=W_MED, align="left",
           arrow=True, radius=999, pad=(16, 30, 16, 30), border=None,
           hover_bg=None, hover_fg=None, url="#", margin=None, full=False,
           ls=0.8, **extra):
    s = {
        "text": f"{label}  →" if arrow else label,
        "link": {"url": url, "is_external": "", "nofollow": "",
                 "custom_attributes": "", "custom_html": ""},
        "align": "justify" if full else align,
        "background_color": bg,
        "button_text_color": fg,
        "border_radius": all_(radius),
        "text_padding": dim(*pad),
        "button_background_hover_color": hover_bg or TEAL,
        "hover_color": hover_fg or WHITE,
        "button_hover_border_color": hover_bg or TEAL,
        "selected_icon": {"value": "", "library": ""},
    }
    s.update(typo(size=size, weight=weight, lh=1.2, ls=ls, transform="uppercase"))
    if border:
        s["border_border"] = "solid"
        s["border_width"] = all_(1)
        s["border_color"] = border
    if margin is not None:
        s["_margin"] = margin
    s.update(extra)
    return W("button", **s)


def image(uri, alt, width=100, align="center", margin=None, **extra):
    s = {
        "image": {"url": uri, "id": "", "alt": alt, "source": "library", "size": ""},
        "image_size": "full",
        "align": align,
        "width": sz(width, "%"),
        "link_to": "none",
        "caption_source": "none",
    }
    if margin is not None:
        s["_margin"] = margin
    s.update(extra)
    return W("image", **s)


def icon_box(icon, title, desc, icon_color=TEAL, icon_size=18, position="left",
             title_size=14, desc_size=12.5, view="default", bg=None,
             title_color=INK, desc_color=MUTED, align="left", radius=None,
             **extra):
    s = {
        "selected_icon": icon,
        "view": view,
        "shape": "square" if radius is not None else "circle",
        "title_text": title,
        "description_text": desc,
        "position": position,
        "title_size": "h6",
        "text_align": align,
        "content_vertical_alignment": "middle",
        "icon_size": sz(icon_size),
        "icon_space": sz(14),
        "title_bottom_space": sz(8),
        "title_color": title_color,
        "description_color": desc_color,
        "link": {"url": "", "is_external": "", "nofollow": ""},
    }
    if view == "stacked":
        s["primary_color"] = bg or TEAL
        s["secondary_color"] = icon_color
        s["icon_padding"] = sz(14)
        if radius is not None:
            s["border_radius"] = all_(radius)
    else:
        s["primary_color"] = icon_color
    s.update(typo("title_typography_", size=title_size, weight=W_MED, lh=1.45))
    s.update(typo("description_typography_", size=desc_size, weight=W_BOOK, lh=1.7))
    s.update(extra)
    return W("icon-box", **s)


def stat(value, label, value_color=TEAL, label_color="#9AA0AC"):
    return cell([
        heading(value, size=28, color=value_color, weight=W_MED, tag="div", lh=1,
                mobile=24, margin=dim(0, 0, 6, 0)),
        heading(label, size=10, color=label_color, weight=W_BOOK, tag="div", lh=1.4,
                ls=1.4, transform="uppercase"),
    ], gap=0)


def woo_products(columns=5, rows_=1, css_class="pl-products"):
    """WooCommerce renders these. The query is left at its defaults so the
    category is picked in the widget, exactly like the shop page."""
    return W(
        "woocommerce-products",
        columns=str(columns),
        rows=str(rows_),
        paginate="",
        allow_order="",
        show_result_count="",
        _css_classes=css_class,
    )


def nested_tabs(titles, panels):
    """Elementor's Tabs widget. One child container per tab, in order."""
    settings = {
        "tabs": [{"tab_title": t, "element_id": "",
                  "tab_icon": {"value": "", "library": ""},
                  "tab_icon_active": {"value": "", "library": ""},
                  "_id": nid()} for t in titles],
        "tabs_justify_horizontal": "start",
        "title_alignment": "center",
        "horizontal_scroll": "enable",
        "title_text_color": BODY,
        "title_text_color_active": WHITE,
        "tabs_title_background_color_background": "classic",
        "tabs_title_background_color_color": WHITE,
        "tabs_title_background_color_active_background": "classic",
        "tabs_title_background_color_active_color": INK,
        "tabs_title_border_border": "solid",
        "tabs_title_border_width": all_(1),
        "tabs_title_border_color": LINE,
        "tabs_title_border_active_border": "solid",
        "tabs_title_border_active_width": all_(1),
        "tabs_title_border_active_color": INK,
        "tabs_title_border_radius": all_(999),
        "tabs_title_space_between": sz(8),
        "tabs_title_padding": dim(11, 20, 11, 20),
        "box_border_border": "none",
        "box_background_color_background": "classic",
        "box_background_color_color": "rgba(0,0,0,0)",
        "box_padding": dim(34, 0, 0, 0),
    }
    settings.update(typo("title_typography_", size=12, weight=W_MED, lh=1.2,
                         ls=0.6, transform="uppercase"))
    return {"id": nid(), "elType": "widget", "widgetType": "nested-tabs",
            "settings": settings, "elements": panels, "isInner": False}


def nested_accordion(items):
    rows = [{"item_title": q, "element_css_id": "", "_id": nid()} for q, _ in items]
    children = [
        CONT([text(a, size=13.5, lh=1.8, color=BODY)],
             content_width="full", flex_direction="column",
             padding=dim(2, 0, 18, 0))
        for _, a in items
    ]
    settings = {
        "items": rows,
        "title_tag": "div",
        "default_state": "expanded",
        "max_items_expended": "one",
        "accordion_item_title_icon": ico("plus-square"),
        "accordion_item_title_icon_active": ico("minus-square"),
        "accordion_item_title_position_horizontal": "start",
        "accordion_item_title_icon_position": "end",
        "accordion_item_title_space_between": sz(0),
        "normal_title_color": INK,
        "hover_title_color": TEAL,
        "active_title_color": TEAL,
        "normal_icon_color": MUTED,
        "hover_icon_color": TEAL,
        "active_icon_color": TEAL,
        "icon_size": sz(13),
        "icon_spacing": sz(12),
        "accordion_border_normal_border": "solid",
        "accordion_border_normal_width": dim(0, 0, 1, 0),
        "accordion_border_normal_color": "#DFDCD6",
        "accordion_padding": dim(20, 0, 20, 0),
        "content_padding": dim(0, 0, 0, 0),
        "content_color": BODY,
    }
    settings.update(typo("title_typography_", size=14.5, weight=W_MED, lh=1.5))
    settings.update(typo("content_typography_", size=13.5, weight=W_BOOK, lh=1.8))
    return {"id": nid(), "elType": "widget", "widgetType": "nested-accordion",
            "settings": settings, "elements": children, "isInner": False}


def link_list(title, links):
    items = [{"text": label, "link": {"url": url, "is_external": "", "nofollow": ""},
              "selected_icon": {"value": "", "library": ""}, "_id": nid()}
             for label, url in links]
    lst = W(
        "icon-list",
        icon_list=items,
        view="traditional",
        space_between=sz(11),
        icon_color="rgba(0,0,0,0)",
        icon_size=sz(0),
        text_color="#A7ACB6",
        text_indent=sz(0),
        **merge(typo("icon_typography_", size=13, weight=W_BOOK, lh=1.6),
                typo("text_typography_", size=13, weight=W_BOOK, lh=1.6)),
    )
    return cell([
        heading(title, size=11, color=TEAL, weight=W_MED, tag="div", lh=1.4,
                ls=1.6, transform="uppercase", margin=dim(0, 0, 20, 0)),
        lst,
    ], gap=0)


PRODUCTS_CSS = """/* -------------------------------------------------------------------------
 * Product grids on the peptide landing page.
 *
 * Scoped to .pl-products - the custom class on the two product sections - so it
 * cannot reach the shop archive or anything else WooCommerce renders. It styles
 * the theme's own loop markup (.product-thumbnail / .product-details /
 * .product-action-wrap), so the products themselves stay WooCommerce's.
 *
 * .pl-products--accent is the best-sellers variant: no card border, teal button.
 * ---------------------------------------------------------------------- */

.pl-products ul.products {
	margin: 0;
	padding: 0;
	list-style: none;
	column-gap: 18px;
	row-gap: 28px;
}

/* Only lay the grid out ourselves if the theme has not already done it. */
.pl-products ul.products:where(:not(.grid-cols)) {
	display: grid;
	grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
}

.pl-products ul.products.grid-cols li.product::before,
.pl-products ul.products.grid-cols::after {
	border: 0;
	content: none;
}

/* --- the card ---------------------------------------------------------- */

.pl-products ul.products li.product {
	display: flex;
	flex-direction: column;
	width: auto;
	margin: 0;
	padding: 0;
	float: none;
	background: #FFFFFF;
	border: 1px solid #E6E8EC;
	border-radius: 14px;
	overflow: hidden;
	transition: transform .3s ease, box-shadow .3s ease, border-color .3s ease;
}

.pl-products ul.products li.product:hover {
	transform: translateY(-4px);
	border-color: #00030E;
	box-shadow: 0 14px 34px rgba(0, 3, 14, .10);
}

/* --- image ------------------------------------------------------------- */

.pl-products .product-thumbnail {
	position: static;
	display: flex;
	align-items: center;
	justify-content: center;
	aspect-ratio: 1 / 1;
	padding: 20px;
	background: #EDEFF1;
	overflow: hidden;
	transform: none;
}

.pl-products .product-thumbnail img {
	width: auto;
	max-width: 80%;
	max-height: 100%;
	margin: 0;
	object-fit: contain;
	transition: transform .5s ease;
}

.pl-products ul.products li.product:hover .product-thumbnail img {
	transform: scale(1.05);
}

/* The theme's over-image action icons are not part of this design. */
.pl-products .product-actions {
	display: none;
}

/* --- text: title on its own line, then price left / button right -------- */

.pl-products .product-details {
	display: flex;
	flex-wrap: wrap;
	align-items: center;
	gap: 10px;
	margin: 0;
	padding: 15px 16px 16px;
}

.pl-products .product-details h2,
.pl-products .product-details h3,
.pl-products .woocommerce-loop-product__title {
	flex: 0 0 100%;
	margin: 0;
	padding: 0;
	font-family: "Satoshi", -apple-system, BlinkMacSystemFont, Arial, sans-serif;
	font-size: 13px;
	font-weight: 400;
	line-height: 1.45;
	letter-spacing: 0;
	text-transform: none;
	color: #00030E;
}

.pl-products .product-details h2 a,
.pl-products .woocommerce-loop-product__title a {
	color: inherit;
	text-decoration: none;
}

.pl-products .price {
	flex: 1 1 auto;
	margin: 0;
	font-family: "Satoshi", -apple-system, BlinkMacSystemFont, Arial, sans-serif;
	font-size: 15px;
	font-weight: 500;
	line-height: 1.2;
	color: #00030E;
}

.pl-products .price del { margin-right: 6px; font-weight: 400; opacity: .45; }
.pl-products .price ins { text-decoration: none; }

/* The design has no star rating in the card. */
.pl-products .star-rating { display: none; }

/* --- add to cart becomes the round icon button ------------------------- */

.pl-products .product-action-wrap {
	flex: 0 0 auto;
	margin: 0 0 0 auto;
	padding: 0;
}

.pl-products .product-action-wrap .button,
.pl-products .add_to_cart_button {
	display: inline-flex;
	align-items: center;
	justify-content: center;
	width: 34px;
	height: 34px;
	min-width: 0;
	margin: 0;
	padding: 0;
	border: 0;
	border-radius: 50%;
	background: #00030E;
	color: #FFFFFF;
	/* Hides the label visually; screen readers still read it. */
	font-size: 0;
	line-height: 0;
	transition: background-color .25s ease, transform .25s ease;
}

.pl-products .product-action-wrap .button::before,
.pl-products .add_to_cart_button::before {
	content: "";
	width: 15px;
	height: 15px;
	background: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='%23ffffff' stroke-width='1.7' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpath d='M3 4h2l2.4 11.2a2 2 0 0 0 2 1.6h7.9a2 2 0 0 0 2-1.5L21 8H6'/%3E%3Ccircle cx='10' cy='20' r='1.3'/%3E%3Ccircle cx='18' cy='20' r='1.3'/%3E%3C/svg%3E") center / contain no-repeat;
}

.pl-products .product-action-wrap .button:hover,
.pl-products .add_to_cart_button:hover {
	background: #019DA6;
	transform: scale(1.06);
}

/* WooCommerce's "View cart" link would break the row - keep it out. */
.pl-products .added_to_cart { display: none; }

/* --- best-sellers variant ---------------------------------------------- */

.pl-products--accent ul.products li.product {
	border-color: transparent;
	background: transparent;
}

.pl-products--accent ul.products li.product:hover {
	border-color: transparent;
	box-shadow: none;
	transform: translateY(-4px);
}

.pl-products--accent .product-thumbnail { border-radius: 14px; }
.pl-products--accent .product-details { padding: 16px 2px 0; }

.pl-products--accent .product-action-wrap .button,
.pl-products--accent .add_to_cart_button { background: #019DA6; }

.pl-products--accent .product-action-wrap .button:hover,
.pl-products--accent .add_to_cart_button:hover { background: #00030E; }

@media (max-width: 640px) {
	.pl-products .product-details { padding: 13px 13px 15px; }
	.pl-products--accent .product-details { padding: 14px 2px 0; }
}
"""


IMG = {name: A.data_uri(svg) for name, svg in A.all_assets().items()}


# ---------------------------------------------------------------------------
# 1. Hero
# ---------------------------------------------------------------------------
TRUST = [
    (ico("check-circle"), "Research-Use Only", "Highest purity"),
    (ico("clipboard"), "Clinically", "Informed"),
    (ico("gem"), "Clean &amp;", "Conscious"),
]


def s_hero():
    ctas = row([
        button("Shop Best Sellers", bg=INK, fg=WHITE, hover_bg=TEAL,
               _element_width="auto"),
        button("Learn the Science", bg="rgba(0,0,0,0)", fg=INK, arrow=True,
               radius=0, pad=(16, 0, 16, 0), hover_bg="rgba(0,0,0,0)",
               hover_fg=TEAL, _element_width="auto"),
    ], gap=22, align="center", stack=None, margin=dim(34, 0, 40, 0))

    trust = row([
        cell([icon_box(ic, t, d, icon_size=17, title_size=12, desc_size=11,
                       icon_color=INK, title_color=INK, desc_color=MUTED)],
             width=33.33)
        for ic, t, d in TRUST
    ], gap=18, align="center", stack="mobile")

    left = cell([
        eyebrow("Peptide science, made simple"),
        heading('Science-Led.<br>Skin-First.<br>'
                f'<span style="color:{TEAL}">You-Focused.</span>',
                size=54, tag="h1", weight=W_MED, lh=1.1, ls=-1.2,
                tablet=42, mobile=34, margin=dim(0, 0, 20, 0)),
        text("Advanced peptide formulas that support visible skin renewal, "
             "strength, and radiance.", size=15, lh=1.8,
             margin=dim(0, 40, 0, 0)),
        ctas,
        trust,
    ], width=47, tablet=100, padding=dim(0, 20, 0, 0))

    right = cell([image(IMG["landing-hero.svg"], "Peptide vial and body oil",
                        width=100)],
                 width=53, tablet=100)

    return band([row([left, right], gap=30, align="center", stack="tablet")],
                pad_top=72, pad_bottom=72,
                background_background="classic",
                background_color=HERO_BG)


# ---------------------------------------------------------------------------
# 2. Product showcase - category tabs, products from WooCommerce
# ---------------------------------------------------------------------------
TABS = ["All", "Repair & Recovery", "Anti-Aging", "Hydration", "Brightening",
        "Barrier Support"]


def style_block():
    """The product CSS, carried inside the template so an import is self-contained.

    Prefer it in a stylesheet? Paste PRODUCTS_CSS into Appearance > Customize >
    Additional CSS (or enqueue assets/css/peptide-landing-products.css) and
    delete this HTML widget.
    """
    return W("html", html="<style>\n" + PRODUCTS_CSS + "</style>")


def s_showcase():
    head = row([
        cell([
            eyebrow("Targeted care, real results"),
            heading("Peptide Solutions<br>For Every Goal.", size=36, weight=W_BOOK,
                    lh=1.22, tablet=30, mobile=26),
        ], width=70, tablet=70, mobile=100),
        cell([button("Shop All", bg=INK, fg=WHITE, align="right", arrow=False,
                     hover_bg=TEAL, _element_width="auto")],
             width=30, tablet=30, mobile=100, flex_align_items="flex-end"),
    ], gap=20, align="flex-end", justify="space-between", stack=None,
        margin=dim(0, 0, 34, 0))

    panels = [
        CONT([woo_products(columns=5)], content_width="full",
             flex_direction="column", padding=all_(0))
        for _ in TABS
    ]

    return band([style_block(), head, nested_tabs(TABS, panels)],
                pad_top=88, pad_bottom=88,
                background_background="classic",
                background_color=SURFACE,
                _css_classes="pl-products",
                css_classes="pl-products")


# ---------------------------------------------------------------------------
# 3. About - lab tested (dark band)
# ---------------------------------------------------------------------------
def s_about():
    stats = row([
        stat("99.5%+", "Min. purity"),
        stat("100%", "Batches tested"),
        stat("24h", "COA lookup"),
    ], gap=20, align="flex-start", stack="mobile", margin=dim(30, 0, 34, 0))

    ctas = row([
        button("View Lab Results", bg=TEAL, fg=WHITE, hover_bg=WHITE,
               hover_fg=INK, _element_width="auto"),
        button("Download Sample Report", bg="rgba(0,0,0,0)", fg=WHITE,
               border="rgba(255,255,255,0.32)", arrow=False, hover_bg=WHITE,
               hover_fg=INK, _element_width="auto"),
    ], gap=14, align="center", stack="mobile")

    left = cell([
        eyebrow("Multi-stage testing", color=TEAL),
        heading("Lab-Tested Before<br>They Hit Your Lab.", size=38, color=WHITE,
                weight=W_BOOK, lh=1.18, ls=-0.4, transform="uppercase",
                tablet=30, mobile=25, margin=dim(0, 0, 18, 0)),
        text("Every batch passes four independent checks &mdash; mass spectrometry "
             "for identity, HPLC for purity, peptide content analysis for accurate "
             "concentration, and stability testing for shelf life.",
             size=14, color="#A7ADBA", lh=1.85, margin=dim(0, 30, 0, 0)),
        stats,
        ctas,
    ], width=54, tablet=100, padding=dim(0, 20, 0, 0))

    right = cell([image(IMG["landing-lab.svg"], "Independently tested peptide vial",
                        width=100)],
                 width=46, tablet=100)

    return band([row([left, right], gap=30, align="center", stack="tablet")],
                pad_top=88, pad_bottom=88,
                background_background="gradient",
                background_color=INK_SOFT,
                background_color_stop=sz(0, "%"),
                background_color_b=INK,
                background_color_b_stop=sz(100, "%"),
                background_gradient_type="linear",
                background_gradient_angle=sz(145, "deg"))


# ---------------------------------------------------------------------------
# 4. Best sellers
# ---------------------------------------------------------------------------
def s_bestsellers():
    return band([
        cell([
            eyebrow("Best sellers", align="center", margin=dim(0, 0, 12, 0)),
            heading("Best-Selling Compounds", size=34, weight=W_BOOK, lh=1.2,
                    align="center", transform="uppercase", ls=0.4,
                    tablet=28, mobile=24, margin=dim(0, 0, 40, 0)),
        ], gap=0),
        woo_products(columns=4, css_class="pl-products pl-products--accent"),
    ], pad_top=88, pad_bottom=88,
        background_background="classic", background_color=WHITE,
        _css_classes="pl-products pl-products--accent",
        css_classes="pl-products pl-products--accent")


# ---------------------------------------------------------------------------
# 5. Why researchers choose
# ---------------------------------------------------------------------------
FEATURES = [
    (ico("gem"), "Pharma-Grade Sourcing",
     "Raw materials from GMP-aligned manufacturers with full chain-of-custody records."),
    (ico("check-circle"), "Verified Purity",
     "No in-house grading. Every batch is tested by accredited third-party labs."),
    (ico("paper-plane"), "Fast, Discreet Dispatch",
     "Same-day dispatch before 2PM in temperature-stable, tamper-evident packaging."),
    (ico("comments"), "Real Human Support",
     "A dedicated team that knows the catalogue &mdash; reachable by chat, email or phone."),
]


def s_features():
    cards = [
        cell([icon_box(ic, t, d, position="top", align="left", view="stacked",
                       bg=TEAL, icon_color=WHITE, icon_size=17, radius=10,
                       title_size=15, desc_size=12.5, desc_color=BODY)],
             width=25, tablet=50, padding=dim(0, 14, 0, 0))
        for ic, t, d in FEATURES
    ]

    return band([
        cell([
            eyebrow("How we work", align="center", margin=dim(0, 0, 12, 0)),
            heading("Why Researchers Choose", size=34, weight=W_BOOK, lh=1.2,
                    align="center", transform="uppercase", ls=0.4,
                    tablet=28, mobile=24, margin=dim(0, 0, 44, 0)),
        ], gap=0),
        row(cards, gap=26, align="flex-start", stack="mobile",
            flex_wrap_tablet="wrap"),
    ], pad_top=20, pad_bottom=96,
        background_background="classic", background_color=WHITE)


# ---------------------------------------------------------------------------
# 6. FAQ
# ---------------------------------------------------------------------------
FAQ = [
    ("Is every batch tested before it ships?",
     "Yes. Every production batch is sent to an accredited third-party lab for "
     "HPLC and LC-MS testing, and the resulting COA is linked to that batch's lot "
     "number before it is listed."),
    ("Where do you ship?",
     "Domestic orders ship the same business day when placed before 2:00&nbsp;PM. "
     "International shipping is available to most countries with tracking."),
    ("Do you accept returns?",
     "Unopened vials in original packaging can be returned within 30 days. Opened "
     "vials cannot be accepted, for the same reason we do not resell them."),
    ("Who can purchase your products?",
     "Sales are restricted to qualified researchers and institutions. Everything "
     "listed is for laboratory research use only."),
    ("What payment methods do you accept?",
     "All major cards, bank transfer, and institutional purchase orders for "
     "approved accounts."),
]


def s_faq():
    left = cell([
        eyebrow("Common questions"),
        heading("Frequently Asked<br>Questions", size=32, weight=W_BOOK, lh=1.22,
                transform="uppercase", ls=0.2, tablet=28, mobile=24,
                margin=dim(0, 0, 18, 0)),
        text("Can&rsquo;t find what you&rsquo;re looking for? Reach out to our "
             "team directly.", size=14, lh=1.8, margin=dim(0, 30, 26, 0)),
        button("Contact Support", bg="rgba(0,0,0,0)", fg=INK, border="#CFCCC5",
               arrow=False, hover_bg=INK, hover_fg=WHITE, _element_width="auto"),
    ], width=38, tablet=100, padding=dim(0, 30, 0, 0))

    right = cell([nested_accordion(FAQ)], width=62, tablet=100)

    return band([row([left, right], gap=40, align="flex-start", stack="tablet")],
                pad_top=88, pad_bottom=88,
                background_background="classic",
                background_color=SURFACE_WARM)


# ---------------------------------------------------------------------------
# 7. Footer
# ---------------------------------------------------------------------------
NEWSLETTER = (
    "<!-- Swap this HTML widget for your form widget (Elementor Pro Forms, "
    "WPForms, Mailchimp, Fluent Forms...) and keep the styling. -->\n"
    '<form class="pl-subscribe" method="post" action="#" '
    'style="display:flex;gap:8px;flex-wrap:wrap;align-items:center;margin-top:18px">'
    '<label for="pl-email" style="position:absolute;left:-9999px">Email address</label>'
    '<input id="pl-email" type="email" name="email" required placeholder="your@email.com" '
    'style="flex:1 1 170px;min-width:0;height:44px;padding:0 16px;border:1px solid '
    "rgba(255,255,255,.18);border-radius:999px;background:rgba(255,255,255,.06);"
    'color:#fff;font:400 13px/1 Satoshi,Arial,sans-serif;outline:none">'
    '<button type="submit" style="height:44px;padding:0 22px;border:0;border-radius:999px;'
    "background:#019DA6;color:#fff;font:500 12px/1 Satoshi,Arial,sans-serif;"
    'letter-spacing:.06em;text-transform:uppercase;cursor:pointer">Subscribe</button>'
    "</form>"
)

SOCIALS = ["linkedin-in", "x-twitter", "instagram", "youtube"]


def s_footer():
    socials = W(
        "social-icons",
        social_icon_list=[
            {"social_icon": {"value": f"fab fa-{name}", "library": "fa-brands"},
             "link": {"url": "#", "is_external": "on", "nofollow": ""},
             "_id": nid()}
            for name in SOCIALS
        ],
        shape="circle",
        columns="0",
        icon_size=sz(13),
        icon_padding=sz(10),
        icon_spacing=sz(8),
        icon_color="custom",
        icon_primary_color="rgba(255,255,255,0.08)",
        icon_secondary_color="#FFFFFF",
        hover_primary_color=TEAL,
        hover_secondary_color="#FFFFFF",
        align="left",
        _margin=dim(22, 0, 0, 0),
    )

    brand = cell([
        heading("Your Brand", size=17, color=WHITE, weight=W_MED, tag="div",
                lh=1.2, ls=1.4, transform="uppercase", margin=dim(0, 0, 16, 0)),
        text("An information resource for high-purity research peptides "
             "&mdash; independently verified, lab-grade, delivered with precision.",
             size=12.5, color="#8F95A0", lh=1.8, margin=dim(0, 30, 0, 0)),
        socials,
    ], width=34, tablet=100, gap=0)

    shop = link_list("Shop", [("All Products", "#"), ("Fat Loss", "#"),
                              ("Performance", "#"), ("Cognitive", "#")])
    support = link_list("Support", [("Contact", "#"), ("Lab Certificates", "#"),
                                    ("Shipping", "#"), ("Refunds", "#")])

    news = cell([
        heading("Newsletter", size=11, color=TEAL, weight=W_MED, tag="div",
                lh=1.4, ls=1.6, transform="uppercase", margin=dim(0, 0, 20, 0)),
        text("Get monthly research updates, new compound launches and exclusive "
             "batch releases.", size=12.5, color="#8F95A0", lh=1.8),
        W("html", html=NEWSLETTER),
    ], width=30, tablet=100, gap=0)

    columns = row([brand, shop, support, news], gap=30, align="flex-start",
                  stack="tablet")

    legal = row([
        cell([text("Copyright &copy; 2026. Designed &amp; developed for research use.",
                   size=11.5, color="#6E7480", lh=1.6)], width=60, mobile=100),
        cell([text('<a href="#" style="color:#6E7480;text-decoration:none">Terms of Use</a>'
                   '&nbsp;&nbsp;&nbsp;'
                   '<a href="#" style="color:#6E7480;text-decoration:none">Privacy Policy</a>',
                   size=11.5, color="#6E7480", lh=1.6, align="right")],
             width=40, mobile=100),
    ], gap=16, align="center", justify="space-between", stack="mobile",
        margin=dim(34, 0, 0, 0),
        border_border="solid", border_width=dim(1, 0, 0, 0),
        border_color="rgba(255,255,255,0.08)",
        padding=dim(24, 0, 0, 0))

    return band([columns, legal], pad_top=72, pad_bottom=44,
                background_background="classic", background_color=INK)


# ---------------------------------------------------------------------------
# Assemble
# ---------------------------------------------------------------------------
def build():
    return {
        "content": [
            s_hero(),
            s_showcase(),
            s_about(),
            s_bestsellers(),
            s_features(),
            s_faq(),
            s_footer(),
        ],
        "page_settings": {
            "hide_title": "yes",
            "background_background": "classic",
            "background_color": WHITE,
        },
        "version": "0.4",
        "title": "Peptide Landing Page",
        "type": "page",
    }


def main():
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    tpl_dir = os.path.join(root, "templates")
    img_dir = os.path.join(root, "assets", "images")
    os.makedirs(tpl_dir, exist_ok=True)
    os.makedirs(img_dir, exist_ok=True)

    out = os.path.join(tpl_dir, "peptide-landing.json")
    with open(out, "w", encoding="utf-8") as f:
        json.dump(build(), f, ensure_ascii=False, indent=2)
        f.write("\n")

    for name, svg in A.all_assets().items():
        with open(os.path.join(img_dir, name), "w", encoding="utf-8") as f:
            f.write(A.minify(svg) + "\n")

    css_dir = os.path.join(root, "assets", "css")
    os.makedirs(css_dir, exist_ok=True)
    css_out = os.path.join(css_dir, "peptide-landing-products.css")
    with open(css_out, "w", encoding="utf-8") as f:
        f.write(PRODUCTS_CSS)
    print(f"wrote {css_out}")

    print(f"wrote {out} ({os.path.getsize(out) / 1024:.1f} KB)")


if __name__ == "__main__":
    main()

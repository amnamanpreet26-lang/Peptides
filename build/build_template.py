#!/usr/bin/env python3
"""Generate the Elementor homepage template JSON.

Output: templates/peptides-homepage.json  (import via Elementor > Templates)

Built with Flexbox Containers (Elementor 3.16+), free core widgets plus the
Elementor Pro WooCommerce Products widget for the two product rows, and a
Slider Revolution shortcode for the hero. All icons are Font Awesome *Regular*
(outline), never Solid.
"""

import hashlib
import itertools
import json
import os

import svg_assets as A

# ---------------------------------------------------------------------------
# Design tokens - change these in one place to re-skin the whole template
# ---------------------------------------------------------------------------
NAVY = "#0B1B3A"          # primary dark - headings, buttons, dark bands
NAVY_2 = "#132A50"        # raised surface on dark bands
TEAL = "#16A6A0"          # accent - highlighted words, stats, links
TEAL_2 = "#2FB8AF"        # lighter accent
BODY = "#5B6B7C"          # body copy
MUTED = "#8A99A8"         # captions, meta
BORDER = "#E6ECF2"        # hairlines and card borders
WHITE = "#FFFFFF"
HERO_A = "#E7F2F9"        # hero band gradient start
HERO_B = "#EDF5FA"        # hero band gradient end

CAT_BLUE_A, CAT_BLUE_B = "#5FAEE9", "#3E8FD6"
CAT_MINT = "#DEF0E2"
CAT_PEACH = "#FBE3C6"

FONT = "Inter"            # single family, weights carry the hierarchy
WIDTH = 1200              # boxed content width

# The Slider Revolution slider that renders the hero. Create a slider with this
# alias in Slider Revolution (see docs/slider-revolution-hero.md).
REV_SLIDER_ALIAS = "peptides-hero"

_used = set()
_counter = itertools.count(1)


def nid():
    """Deterministic, unique, Elementor-shaped element id."""
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
    """Elementor GAPS control (container flex gap)."""
    row = column if row is None else row
    return {"unit": "px", "size": column, "column": str(column),
            "row": str(row), "isLinked": column == row}


def shadow(v=6, blur=24, color="rgba(11,27,58,0.06)", h=0, spread=0):
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


# ---------------------------------------------------------------------------
# Icons - Font Awesome 5 Free *Regular* only (outline style, no solid)
# ---------------------------------------------------------------------------
def ico(name):
    return {"value": f"far fa-{name}", "library": "fa-regular"}


# ---------------------------------------------------------------------------
# Element factories
# ---------------------------------------------------------------------------
def W(widget_type, **settings):
    return {"id": nid(), "elType": "widget", "widgetType": widget_type,
            "settings": settings, "elements": [], "isInner": False}


def CONT(children, **settings):
    return {"id": nid(), "elType": "container", "settings": settings,
            "elements": children, "isInner": False}


def band(children, pad_top=64, pad_bottom=64, gap=0, **extra):
    """A top-level boxed container - one section of the page."""
    s = {
        "content_width": "boxed",
        "boxed_width": sz(WIDTH),
        "flex_direction": "column",
        "flex_gap": gaps(gap),
        "padding": dim(pad_top, 20, pad_bottom, 20),
        "padding_mobile": dim(max(pad_top - 20, 28), 16,
                              max(pad_bottom - 20, 28), 16),
    }
    s.update(extra)
    return CONT(children, **s)


def row(children, gap=20, align="center", justify=None, wrap="nowrap",
        stack="mobile", width=None, tablet=None, mobile=100, **extra):
    """A flex row.

    `wrap` stays "nowrap" so children shrink to absorb the gap instead of
    breaking onto a new line - percentage widths that add up to 100% would wrap
    the moment a gap is added. Stacking is done by switching flex-direction at
    the breakpoint, which is how Elementor's own container presets behave.
    """
    s = {
        "content_width": "full",
        "flex_direction": "row",
        "flex_gap": gaps(gap),
        "flex_wrap": wrap,
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
    if tablet is not None:
        s["width_tablet"] = sz(tablet, "%")
    if mobile is not None and width is not None:
        s["width_mobile"] = sz(mobile, "%")
    s.update(extra)
    return CONT(children, **s)


def cell(children, width=None, tablet=None, mobile=100, gap=0, **extra):
    """A column-ish child container."""
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


CARD = {
    "background_background": "classic",
    "background_color": WHITE,
    "border_border": "solid",
    "border_width": all_(1),
    "border_color": BORDER,
    "border_radius": all_(12),
    "box_shadow_box_shadow_type": "yes",
    "box_shadow_box_shadow": shadow(4, 16, "rgba(11,27,58,0.05)"),
}


# ---------------------------------------------------------------------------
# Widget shortcuts
# ---------------------------------------------------------------------------
def heading(title, size=30, color=NAVY, weight=700, tag="h2", align="left",
            lh=1.25, ls=None, tablet=None, mobile=None, margin=None, **extra):
    s = {"title": title, "header_size": tag, "align": align, "title_color": color}
    s.update(typo(size=size, weight=weight, lh=lh, ls=ls,
                  tablet=tablet, mobile=mobile))
    if margin is not None:
        s["_margin"] = margin
    s.update(extra)
    return W("heading", **s)


def text(html, size=15, color=BODY, lh=1.75, align="left", weight=None,
         margin=None, mobile=None):
    s = {"editor": html, "align": align, "text_color": color}
    s.update(typo(size=size, weight=weight, lh=lh, mobile=mobile))
    if margin is not None:
        s["_margin"] = margin
    return W("text-editor", **s)


def button(label, bg=NAVY, fg=WHITE, size=14, weight=600, align="left",
           arrow=True, radius=8, pad=(14, 26, 14, 26), border=None,
           hover_bg=None, hover_fg=None, url="#", margin=None, full=False,
           **extra):
    """Arrows are the thin -> glyph in the label rather than a solid FA icon."""
    s = {
        "text": f"{label}  →" if arrow else label,
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
    s.update(typo(size=size, weight=weight, lh=1.2))
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


def icon_box(icon, title, desc, icon_color=NAVY, icon_size=22, position="left",
             title_size=14, desc_size=12, view="default", bg=None,
             title_color=NAVY, desc_color=MUTED, **extra):
    s = {
        "selected_icon": ico(icon),
        "view": view,
        "shape": "circle",
        "title_text": title,
        "description_text": desc,
        "position": position,
        "title_size": "h6",
        "text_align": "left" if position == "left" else "center",
        "content_vertical_alignment": "middle",
        "icon_size": sz(icon_size),
        "icon_space": sz(14),
        "title_bottom_space": sz(3),
        "title_color": title_color,
        "description_color": desc_color,
        "link": {"url": "", "is_external": "", "nofollow": ""},
    }
    if view == "stacked":
        s["primary_color"] = bg or "rgba(255,255,255,0.18)"
        s["secondary_color"] = icon_color
        s["icon_padding"] = sz(16)
    else:
        s["primary_color"] = icon_color
    s.update(typo("title_typography_", size=title_size, weight=600, lh=1.4))
    s.update(typo("description_typography_", size=desc_size, weight=400, lh=1.5))
    s.update(extra)
    return W("icon-box", **s)


def icon(name, color=NAVY, size=20, align="left", margin=None, **extra):
    s = {
        "selected_icon": ico(name),
        "view": "default",
        "align": align,
        "size": sz(size),
        "primary_color": color,
        "link": {"url": "", "is_external": "", "nofollow": ""},
    }
    if margin is not None:
        s["_margin"] = margin
    s.update(extra)
    return W("icon", **s)


def nested_accordion(items):
    """Elementor's modern Accordion (nested elements). Content for each item
    lives in a child container, one per repeater row."""
    rows = [{"item_title": q, "element_css_id": "", "_id": nid()}
            for q, _ in items]
    children = [
        CONT([text(a, size=13.5, lh=1.75)],
             content_width="full", flex_direction="column",
             padding=dim(2, 4, 14, 4))
        for _, a in items
    ]
    settings = {
        "items": rows,
        "title_tag": "div",
        "default_state": "all_collapsed",
        "max_items_expended": "one",
        "accordion_item_title_icon": ico("plus-square"),
        "accordion_item_title_icon_active": ico("minus-square"),
        "accordion_item_title_position_horizontal": "start",
        "accordion_item_title_icon_position": "end",
        "accordion_item_title_space_between": sz(0),
        "normal_title_color": NAVY,
        "hover_title_color": TEAL,
        "active_title_color": TEAL,
        "normal_icon_color": MUTED,
        "hover_icon_color": TEAL,
        "active_icon_color": TEAL,
        "icon_size": sz(13),
        "icon_spacing": sz(10),
        "accordion_border_normal_border": "solid",
        "accordion_border_normal_width": all_(1),
        "accordion_border_normal_color": BORDER,
        "accordion_padding": dim(15, 16, 15, 16),
        "content_padding": dim(0, 16, 0, 16),
        "content_color": BODY,
    }
    settings.update(typo("title_typography_", size=14, weight=500, lh=1.5))
    settings.update(typo("content_typography_", size=13.5, weight=400, lh=1.75))
    return {"id": nid(), "elType": "widget", "widgetType": "nested-accordion",
            "settings": settings, "elements": children, "isInner": False}


def woo_products(columns=4, rows_=1):
    """WooCommerce products, rendered by WooCommerce itself.

    Query is intentionally left at its defaults - pick the product category in
    the widget's Query panel and those products appear. Nothing is hard-coded.
    """
    return W(
        "woocommerce-products",
        columns=str(columns),
        rows=str(rows_),
        paginate="",
        allow_order="",
        show_result_count="",
        **merge(
            typo("title_typography_", size=14.5, weight=600, lh=1.4),
            typo("price_typography_", size=17, weight=700, lh=1.3),
            typo("button_typography_", size=13, weight=600, lh=1.2),
        ),
    )


# ---------------------------------------------------------------------------
# Artwork (embedded as data URIs - no external dependencies)
# ---------------------------------------------------------------------------
IMG = {name: A.data_uri(svg) for name, svg in A.all_assets().items()}


# ---------------------------------------------------------------------------
# 1. Hero - rendered by Slider Revolution
# ---------------------------------------------------------------------------
def s_hero():
    return CONT(
        [W("shortcode", shortcode=f'[rev_slider alias="{REV_SLIDER_ALIAS}"]')],
        content_width="full",
        flex_direction="column",
        flex_gap=gaps(0),
        padding=dim(0, 0, 60, 0),
        padding_mobile=dim(0, 0, 48, 0),
        background_background="gradient",
        background_color=HERO_A,
        background_color_stop=sz(0, "%"),
        background_color_b=HERO_B,
        background_color_b_stop=sz(100, "%"),
        background_gradient_type="linear",
        background_gradient_angle=sz(160, "deg"),
    )


# ---------------------------------------------------------------------------
# 2. Trust bar (overlaps the hero)
# ---------------------------------------------------------------------------
TRUST = [
    ("file-alt", "FDA Registered", "cGMP Compliant"),
    ("check-circle", "Third-Party Tested", "Independent Verification"),
    ("credit-card", "Secure Checkout", "Encrypted &amp; Safe"),
    ("paper-plane", "Fast &amp; Reliable", "Worldwide Shipping"),
]


def s_trust():
    cells = []
    for i, (ic, title, desc) in enumerate(TRUST):
        extra = {}
        if i < len(TRUST) - 1:
            extra = {"border_border": "solid",
                     "border_width": dim(0, 1, 0, 0),
                     "border_color": "#EDF1F5",
                     "border_width_tablet": all_(0),
                     "border_width_mobile": all_(0)}
        cells.append(cell([icon_box(ic, title, desc)],
                          width=25, tablet=50, padding=dim(6, 18, 6, 18),
                          **extra))

    card = row(cells, gap=0, align="center", flex_wrap_tablet="wrap",
               padding=dim(20, 14, 20, 14),
               background_background="classic",
               background_color=WHITE,
               border_radius=all_(12),
               box_shadow_box_shadow_type="yes",
               box_shadow_box_shadow=shadow(10, 34, "rgba(11,27,58,0.08)"))

    return band([card], pad_top=0, pad_bottom=0, z_index=3,
                margin=dim(-52, 0, 0, 0),
                margin_tablet=dim(-46, 0, 0, 0),
                margin_mobile=dim(-42, 0, 0, 0))


# ---------------------------------------------------------------------------
# Shared: section heading with optional arrows / link on the right
# ---------------------------------------------------------------------------
def heading_row(title_html, right=None, left_w=70, right_w=30, right_m=40):
    if not right:
        left_w, right_m = 100, 0
    kids = [cell([heading(title_html, size=27, tag="h2", weight=700, lh=1.3,
                          tablet=24, mobile=21)],
                 width=left_w, mobile=100 - right_m)]
    if right:
        kids.append(row(right, width=right_w, mobile=right_m, gap=10,
                        justify="flex-end", stack=None))
    return row(kids, gap=16, align="center", justify="space-between",
               stack=None, margin=dim(0, 0, 22, 0))


def arrows():
    """Inline (auto) width so the pair sits together at the right edge."""
    return [icon("arrow-alt-circle-left", color="#C3D2DE", size=26,
                 align="center", _element_width="auto"),
            icon("arrow-alt-circle-right", color="#1D66C9", size=26,
                 align="center", _element_width="auto")]


# ---------------------------------------------------------------------------
# 3 + 6. Product rows - WooCommerce does the rendering
# ---------------------------------------------------------------------------
def s_most_ordered():
    return band([
        heading_row(f'Most-Ordered <span style="color:{TEAL}">By Research</span>',
                    arrows()),
        woo_products(),
    ], pad_top=54, pad_bottom=44)


def s_catalog():
    return band([
        heading_row(f'Explore Our <span style="color:{TEAL}">Catalog</span>',
                    arrows()),
        woo_products(),
    ], pad_top=54, pad_bottom=44)


# ---------------------------------------------------------------------------
# 4. Browse by category
# ---------------------------------------------------------------------------
CATEGORIES = [
    dict(icon="dot-circle", title="Peptides<br>Category 1",
         img="category-peptides.svg", fg=WHITE,
         gradient=(CAT_BLUE_A, CAT_BLUE_B), alt="Research peptide vials"),
    dict(icon="clone", title="Peptide Blends<br>Category 2",
         img="category-blends.svg", fg=NAVY, flat=CAT_MINT,
         alt="Peptide blend vials"),
    dict(icon="snowflake", title="Bioregulators<br>Category 3",
         img="category-bioregulators.svg", fg=NAVY, flat=CAT_PEACH,
         alt="Bioregulator vials"),
]


def category_card(c):
    if "gradient" in c:
        style = {
            "background_background": "gradient",
            "background_color": c["gradient"][0],
            "background_color_stop": sz(0, "%"),
            "background_color_b": c["gradient"][1],
            "background_color_b_stop": sz(100, "%"),
            "background_gradient_type": "linear",
            "background_gradient_angle": sz(150, "deg"),
        }
    else:
        style = {"background_background": "classic",
                 "background_color": c["flat"]}

    left = cell([
        icon(c["icon"], color=c["fg"], size=20, margin=dim(0, 0, 10, 0)),
        heading(c["title"], size=17, color=c["fg"], weight=700, tag="h3",
                lh=1.32, margin=dim(0, 0, 14, 0)),
        button("Shop now", bg=WHITE, fg=NAVY, size=12, weight=600, radius=6,
               pad=(9, 15, 9, 15), hover_bg=NAVY, hover_fg=WHITE),
    ], width=58, mobile=100)

    right = cell([image(IMG[c["img"]], c["alt"], width=100)],
                 width=42, mobile=100, flex_justify_content="flex-end")

    return row([left, right], gap=8, align="center", stack=None,
               width=33.33, tablet=100, mobile=100,
               min_height=sz(168),
               border_radius=all_(14),
               padding=dim(20, 14, 20, 20),
               **style)


def s_categories():
    return band([
        heading_row(f'Browse <span style="color:{TEAL}">By Category</span>'),
        row([category_card(c) for c in CATEGORIES], gap=20, align="stretch",
            stack="tablet"),
    ], pad_top=20, pad_bottom=44)


# ---------------------------------------------------------------------------
# 5. Built for researchers (dark band)
# ---------------------------------------------------------------------------
def s_quality():
    left = cell([
        heading(
            f'Built <span style="color:{TEAL}">For Researchers</span> Who<br>'
            "Don&#39;t Compromise On Quality",
            size=27, color=WHITE, weight=700, tag="h2", lh=1.36,
            tablet=24, mobile=21, margin=dim(0, 0, 18, 0)),
        heading("100%", size=58, color=TEAL, weight=800, tag="div", lh=1,
                ls=-1.5, tablet=48, mobile=42, margin=dim(0, 0, 14, 0)),
        text("We don&#39;t ask you to take our word for it. Every batch we produce "
             "is third-party tested, verified, and exceeds industry standards for "
             "unmatched research reliability.",
             size=13.5, color="#A9B8CC", lh=1.8, margin=dim(0, 0, 24, 0)),
        button("See our testing", bg=NAVY_2, fg=WHITE, size=13, border="#2C4472",
               radius=7, pad=(12, 22, 12, 22), hover_bg=TEAL),
    ], width=50, tablet=100, padding=dim(0, 24, 0, 0))

    right = cell([image(IMG["coa-certificate.svg"],
                        "Certificate of Analysis for BPC-157", width=100)],
                 width=50, tablet=100)

    return band([
        row([left, right], gap=24, align="center", stack="tablet",
            background_background="gradient",
            background_color=NAVY,
            background_color_stop=sz(0, "%"),
            background_color_b="#0F2547",
            background_color_b_stop=sz(100, "%"),
            background_gradient_type="linear",
            background_gradient_angle=sz(135, "deg"),
            border_radius=all_(16),
            padding=dim(44, 40, 44, 40),
            padding_mobile=dim(30, 22, 30, 22)),
    ], pad_top=20, pad_bottom=24)


# ---------------------------------------------------------------------------
# 7. Feature strip
# ---------------------------------------------------------------------------
FEATURES = [
    ("gem", "99.8% Purity", "Guaranteed high purity in every batch"),
    ("clipboard", "Lab Verified", "Each batch tested for safety and purity"),
    ("credit-card", "Secure Payment", "Safe &amp; encrypted checkout"),
    ("clock", "Fast Shipping", "Worldwide shipping you can trust"),
]


def s_features():
    return band([
        row([cell([icon_box(i, t, d, icon_size=21)],
                  width=25, tablet=50, padding=dim(8, 14, 8, 0))
             for i, t, d in FEATURES],
            gap=0, align="center", flex_wrap_tablet="wrap"),
    ], pad_top=8, pad_bottom=44)


# ---------------------------------------------------------------------------
# 8. Promo duo
# ---------------------------------------------------------------------------
def s_promos():
    new_arrivals = row([
        cell([
            heading("New<br>Arrivals", size=30, color=WHITE, weight=700, tag="h3",
                   lh=1.2, tablet=26, mobile=24, margin=dim(0, 0, 18, 0)),
            button("View Catalog", bg=WHITE, fg=NAVY, size=12.5, weight=600,
                   radius=7, pad=(11, 18, 11, 18), hover_bg=NAVY, hover_fg=WHITE),
        ], width=56, mobile=100),
        cell([image(IMG["new-arrivals-vial.svg"], "New arrival peptide vial",
                    width=46)],
             width=44, mobile=100, flex_justify_content="flex-end"),
    ], gap=8, align="center", stack=None,
        width=50, tablet=100, mobile=100,
        min_height=sz(178),
        border_radius=all_(14),
        padding=dim(26, 20, 26, 24),
        background_background="gradient",
        background_color=CAT_BLUE_A,
        background_color_stop=sz(0, "%"),
        background_color_b=CAT_BLUE_B,
        background_color_b_stop=sz(100, "%"),
        background_gradient_type="linear",
        background_gradient_angle=sz(150, "deg"))

    documented = cell([
        heading("Every Peptide.<br>Every Batch.<br>Fully Documented.",
                size=21, color=WHITE, weight=700, tag="h3", lh=1.42,
                mobile=19, margin=dim(0, 0, 14, 0)),
        text("We supply research-grade peptides backed by real data, real batch "
             "records, and real science you can trust.",
             size=13, color="#A9B8CC", lh=1.8),
    ], width=50, tablet=100,
        flex_justify_content="center",
        min_height=sz(178),
        border_radius=all_(14),
        padding=dim(30, 28, 30, 28),
        background_background="classic",
        background_color=NAVY)

    return band([row([new_arrivals, documented], gap=20, align="stretch",
                     stack="tablet")],
                pad_top=8, pad_bottom=52)


# ---------------------------------------------------------------------------
# 9. FAQ
# ---------------------------------------------------------------------------
FAQ_LEFT = [
    ("How do I know your lab reports are real?",
     "Every batch ships with a Certificate of Analysis from an independent, "
     "ISO&nbsp;17025 accredited laboratory. The batch number on your vial matches "
     "the report, and you can look it up any time from the Certificates page."),
    ("What happens if a product tests under the label dose?",
     "It never reaches the shelf. Any batch that falls outside specification is "
     "quarantined and destroyed, and we publish the failed report alongside the "
     "passing ones so the record stays complete."),
    ("Why do you over-dose your products?",
     "We don&#39;t. We fill to label claim with a small manufacturing overage so the "
     "vial still meets the stated dose after reconstitution and normal handling loss."),
    ("Where is your raw material from?",
     "All peptides are synthesised in cGMP-compliant facilities we audit directly. "
     "Source, synthesis route, and purity method are listed on every Certificate "
     "of Analysis."),
]

FAQ_RIGHT = [
    ("How long does delivery take?",
     "Orders placed before 2:00&nbsp;PM EST ship the same business day. Domestic "
     "delivery is typically 2-3 business days; international is 5-10 business days "
     "with tracking."),
    ("How is my order packaged?",
     "Vials ship in insulated, discreet outer packaging with cold packs where the "
     "product requires it. Nothing on the outside identifies the contents."),
    ("Can I suggest a product you don&#39;t carry yet?",
     "Yes. Send us the peptide and the purity specification you need. We review "
     "requests every month and prioritise the ones our research customers ask for "
     "most often."),
    ("Do you offer bulk or wholesale pricing?",
     "We do. Institutional and volume pricing is available for laboratories and "
     "research organisations - contact us with your requirements for a quote."),
]


def s_faq():
    view_all = button("View All FAQ", bg="rgba(0,0,0,0)", fg=TEAL, size=13,
                      weight=600, align="right", radius=0, pad=(0, 0, 0, 0),
                      hover_bg="rgba(0,0,0,0)", hover_fg=NAVY)
    return band([
        heading_row("Frequently Asked Questions", [view_all],
                    left_w=78, right_w=22, right_m=45),
        row([cell([nested_accordion(FAQ_LEFT)], width=50, tablet=100),
             cell([nested_accordion(FAQ_RIGHT)], width=50, tablet=100)],
            gap=20, align="flex-start", stack="tablet"),
    ], pad_top=8, pad_bottom=52)


# ---------------------------------------------------------------------------
# 10. Newsletter
# ---------------------------------------------------------------------------
NEWSLETTER_FORM = (
    "<!-- Swap this HTML widget for your form widget (Elementor Pro Forms, "
    "WPForms, Mailchimp, Fluent Forms...) and keep the same styling. -->\n"
    '<form class="pep-subscribe" method="post" action="#" '
    'style="display:flex;gap:10px;flex-wrap:wrap;align-items:center;">'
    '<label for="pep-email" '
    'style="position:absolute;left:-9999px;">Email address</label>'
    '<input id="pep-email" type="email" name="email" required '
    'placeholder="Enter your email address" '
    'style="flex:1 1 230px;min-width:0;height:50px;padding:0 18px;border:0;'
    "border-radius:8px;background:#fff;color:#0B1B3A;font:400 14px/1 Inter,"
    'Arial,sans-serif;outline:none;">'
    '<button type="submit" '
    'style="height:50px;padding:0 26px;border:0;border-radius:8px;'
    "background:#0B1B3A;color:#fff;font:600 14px/1 Inter,Arial,sans-serif;"
    'cursor:pointer;white-space:nowrap;">Subscribe &nbsp;&rarr;</button>'
    "</form>"
)


def s_newsletter():
    return band([
        row([
            cell([icon_box("envelope", "Stay in the loop.",
                           "Be the first to know about new products, lab reports, "
                           "and exclusive updates.",
                           icon_color=WHITE, icon_size=20, view="stacked",
                           bg="rgba(255,255,255,0.18)", title_size=19,
                           desc_size=13, title_color=WHITE, desc_color="#DCF0EE")],
                 width=55, tablet=100),
            cell([W("html", html=NEWSLETTER_FORM)], width=45, tablet=100),
        ], gap=24, align="center", stack="tablet",
            border_radius=all_(14),
            padding=dim(26, 30, 26, 30),
            padding_mobile=dim(24, 20, 24, 20),
            background_background="gradient",
            background_color="#2E8B96",
            background_color_stop=sz(0, "%"),
            background_color_b=TEAL_2,
            background_color_b_stop=sz(100, "%"),
            background_gradient_type="linear",
            background_gradient_angle=sz(100, "deg")),
    ], pad_top=8, pad_bottom=64)


# ---------------------------------------------------------------------------
# Assemble + write
# ---------------------------------------------------------------------------
def build():
    return {
        "content": [
            s_hero(),
            s_trust(),
            s_most_ordered(),
            s_categories(),
            s_quality(),
            s_catalog(),
            s_features(),
            s_promos(),
            s_faq(),
            s_newsletter(),
        ],
        "page_settings": {
            "hide_title": "yes",
            "background_background": "classic",
            "background_color": WHITE,
        },
        "version": "0.4",
        "title": "Peptides Homepage",
        "type": "page",
    }


def main():
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    tpl_dir = os.path.join(root, "templates")
    img_dir = os.path.join(root, "assets", "images")
    os.makedirs(tpl_dir, exist_ok=True)
    os.makedirs(img_dir, exist_ok=True)

    out = os.path.join(tpl_dir, "peptides-homepage.json")
    with open(out, "w", encoding="utf-8") as f:
        json.dump(build(), f, ensure_ascii=False, indent=2)
        f.write("\n")

    for name, svg in A.all_assets().items():
        with open(os.path.join(img_dir, name), "w", encoding="utf-8") as f:
            f.write(A.minify(svg) + "\n")

    print(f"wrote {out} ({os.path.getsize(out) / 1024:.1f} KB)")
    print(f"wrote {len(A.all_assets())} SVG assets to {img_dir}")


if __name__ == "__main__":
    main()

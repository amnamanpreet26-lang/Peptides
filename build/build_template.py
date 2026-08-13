#!/usr/bin/env python3
"""Generate the Elementor homepage template JSON.

Output: templates/peptides-homepage.json  (import via Elementor > Templates)

The template is built with classic Sections / Columns / Widgets rather than
Flexbox Containers so it imports and stays editable on every Elementor version,
and it only uses free core widgets - no Elementor Pro requirement.
"""

import hashlib
import itertools
import json
import os

import svg_assets as A

# ---------------------------------------------------------------------------
# Design tokens - change these in one place to re-skin the whole template
# ---------------------------------------------------------------------------
NAVY = "#0B1B3A"          # primary dark - headings, buttons, dark sections
NAVY_2 = "#132A50"        # raised surface on dark sections
TEAL = "#16A6A0"          # accent - highlighted words, stats, links
TEAL_2 = "#2FB8AF"        # lighter accent
BODY = "#5B6B7C"          # body copy
MUTED = "#8A99A8"         # captions, meta
BORDER = "#E6ECF2"        # hairlines and card borders
WHITE = "#FFFFFF"
SOFT = "#F5F8FB"          # soft page band
HERO_A = "#E7F2F9"        # hero gradient start
HERO_B = "#EDF5FA"        # hero gradient end

BADGE_GREEN_BG, BADGE_GREEN_FG = "#E9F4DA", "#4E7A1E"
BADGE_BLUE_BG, BADGE_BLUE_FG = "#DCEDFB", "#1A5C9E"
BADGE_ORANGE_BG, BADGE_ORANGE_FG = "#FCE6C9", "#94590F"

CAT_BLUE_A, CAT_BLUE_B = "#5FAEE9", "#3E8FD6"
CAT_MINT = "#DEF0E2"
CAT_PEACH = "#FBE3C6"

FONT = "Inter"            # single family, weights carry the hierarchy
WIDTH = 1200              # boxed content width

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


def shadow(v=6, blur=24, color="rgba(11,27,58,0.06)", h=0, spread=0):
    return {"horizontal": h, "vertical": v, "blur": blur,
            "spread": spread, "color": color}


def typo(p="typography_", size=None, weight=None, lh=None, ls=None,
         transform=None, tablet=None, mobile=None, family=FONT):
    """Build an Elementor typography group-control payload."""
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
# Element factories
# ---------------------------------------------------------------------------
def W(widget_type, **settings):
    return {"id": nid(), "elType": "widget", "widgetType": widget_type,
            "settings": settings, "elements": [], "isInner": False}


# Elementor ships width classes (.elementor-col-NN) only for these presets; an
# exact width still comes from _inline_size, this just keeps the fallback sane.
COL_PRESETS = [10, 11, 12, 14, 16, 20, 25, 30, 33, 40, 50,
               60, 66, 70, 75, 80, 83, 90, 100]


def COL(size, elements, **settings):
    preset = min(COL_PRESETS, key=lambda v: abs(v - size))
    s = {"_column_size": preset, "_inline_size": None}
    s.update(settings)
    return {"id": nid(), "elType": "column", "settings": s,
            "elements": elements, "isInner": False}


def SEC(columns, inner=False, **settings):
    if inner:
        for c in columns:
            c["isInner"] = True
    return {"id": nid(), "elType": "section", "settings": settings,
            "elements": columns, "isInner": inner}


def OUTER(columns, pad_top=64, pad_bottom=64, **settings):
    """A top-level boxed section with sensible page rhythm."""
    base = {
        "layout": "boxed",
        "content_width": sz(WIDTH),
        "padding": dim(pad_top, 20, pad_bottom, 20),
        "padding_mobile": dim(max(pad_top - 20, 28), 16,
                              max(pad_bottom - 20, 28), 16),
    }
    base.update(settings)
    return SEC(columns, **base)


CARD = {
    "gap": "no",
    "background_background": "classic",
    "background_color": WHITE,
    "border_border": "solid",
    "border_width": all_(1),
    "border_color": BORDER,
    "border_radius": all_(12),
    "padding": dim(14, 14, 16, 14),
    "box_shadow_box_shadow_type": "yes",
    "box_shadow_box_shadow": shadow(4, 16, "rgba(11,27,58,0.05)"),
}


# ---------------------------------------------------------------------------
# Widget shortcuts
# ---------------------------------------------------------------------------
def heading(title, size=30, color=NAVY, weight=700, tag="h2", align="left",
            lh=1.25, ls=None, tablet=None, mobile=None, margin=None, **extra):
    s = {
        "title": title,
        "header_size": tag,
        "align": align,
        "title_color": color,
    }
    s.update(typo(size=size, weight=weight, lh=lh, ls=ls,
                  tablet=tablet, mobile=mobile))
    if margin is not None:
        s["_margin"] = margin
    s.update(extra)
    return W("heading", **s)


def badge(text, bg, fg):
    """Small inline pill. Uses a heading with Advanced > Width: Inline (auto)."""
    return heading(
        text, size=10, color=fg, weight=700, tag="div", lh=1.4, ls=0.7,
        margin=dim(0, 0, 10, 0),
        text_transform="uppercase",
        _element_width="auto",
        _background_background="classic",
        _background_color=bg,
        _padding=dim(5, 10, 5, 10),
        _border_radius=all_(5),
    )


def text(html, size=15, color=BODY, lh=1.75, align="left", weight=None,
         margin=None, mobile=None):
    s = {"editor": html, "align": align, "text_color": color}
    s.update(typo(size=size, weight=weight, lh=lh, mobile=mobile))
    if margin is not None:
        s["_margin"] = margin
    return W("text-editor", **s)


def button(label, bg=NAVY, fg=WHITE, size=14, weight=600, align="left",
           icon="fas fa-arrow-right", radius=8, pad=(14, 26, 14, 26),
           border=None, hover_bg=None, hover_fg=None, url="#",
           margin=None, full=False, **extra):
    s = {
        "text": label,
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
    }
    s.update(typo(size=size, weight=weight, lh=1.2))
    if icon:
        s["selected_icon"] = {"value": icon, "library": "fa-solid"}
        s["icon_align"] = "right"
        s["icon_indent"] = sz(8)
    if border:
        s["border_border"] = "solid"
        s["border_width"] = all_(1)
        s["border_color"] = border
    if margin is not None:
        s["_margin"] = margin
    s.update(extra)
    return W("button", **s)


def image(uri, alt, width=100, align="center", max_w=None, margin=None, **extra):
    s = {
        "image": {"url": uri, "id": "", "alt": alt, "source": "library", "size": ""},
        "image_size": "full",
        "align": align,
        "width": sz(width, "%"),
        "link_to": "none",
        "caption_source": "none",
    }
    if max_w:
        s["space"] = sz(max_w)
    if margin is not None:
        s["_margin"] = margin
    s.update(extra)
    return W("image", **s)


def icon_box(icon, title, desc, icon_color=NAVY, icon_size=22, position="left",
             title_size=14, desc_size=12, view="default", bg=None,
             title_color=NAVY, desc_color=MUTED, **extra):
    s = {
        "selected_icon": {"value": icon, "library": "fa-solid"},
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


def circle_icon(icon, bg="#EEF3F8", fg=NAVY, size=12, pad=11, align="center"):
    return W("icon",
             selected_icon={"value": icon, "library": "fa-solid"},
             view="stacked", shape="circle", align=align,
             size=sz(size), primary_color=bg, secondary_color=fg,
             icon_padding=sz(pad))


def spacer(h=20):
    return W("spacer", space=sz(h))


def html_block(markup):
    return W("html", html=markup)


def accordion(items, icon_align="right"):
    return W(
        "accordion",
        tabs=[{"_id": nid(), "tab_title": q, "tab_content": f"<p>{a}</p>"}
              for q, a in items],
        selected_icon={"value": "fas fa-chevron-down", "library": "fa-solid"},
        selected_active_icon={"value": "fas fa-chevron-up", "library": "fa-solid"},
        icon_align=icon_align,
        title_html_tag="div",
        border_width=sz(1),
        border_color=BORDER,
        title_background="",
        title_color=NAVY,
        tab_active_color=TEAL,
        icon_color=MUTED,
        icon_active_color=TEAL,
        icon_space=sz(10),
        content_background_color="",
        content_color=BODY,
        **merge(typo("title_typography_", size=14, weight=500, lh=1.5),
                typo("content_typography_", size=13.5, weight=400, lh=1.75)),
    )


# ---------------------------------------------------------------------------
# Artwork (embedded as data URIs so the template has no external dependencies)
# ---------------------------------------------------------------------------
IMG = {name: A.data_uri(svg) for name, svg in A.all_assets().items()}


# ---------------------------------------------------------------------------
# 1. Hero
# ---------------------------------------------------------------------------
def s_hero():
    pills = SEC([
        COL(25, [badge('<i class="fas fa-check-circle"></i>&nbsp; FDA Compliant',
                       "#E4F1EC", "#1F7A63")],
            _inline_size=25, _inline_size_tablet=34, _inline_size_mobile=52),
        COL(75, [badge('<i class="fas fa-vial"></i>&nbsp; Lab Tested',
                       "#E4EFF7", "#1A5C9E")],
            _inline_size=75, _inline_size_tablet=66, _inline_size_mobile=48),
    ], inner=True, gap="no", structure="20",
        margin=dim(0, 0, 18, 0))

    ctas = SEC([
        COL(30, [button("Browse Catalog", bg=NAVY, fg=WHITE, full=False)],
            _inline_size=30, _inline_size_tablet=42, _inline_size_mobile=100),
        COL(70, [button("Research Standards", bg=WHITE, fg=NAVY, icon=None,
                        border="#D8E2EA", hover_bg=NAVY)],
            _inline_size=70, _inline_size_tablet=58, _inline_size_mobile=100),
    ], inner=True, gap="narrow", structure="20",
        margin=dim(28, 0, 26, 0))

    dots = html_block(
        '<div style="display:flex;gap:7px;align-items:center;">'
        f'<span style="width:24px;height:6px;border-radius:3px;background:{NAVY};'
        'display:inline-block;"></span>'
        '<span style="width:6px;height:6px;border-radius:50%;background:#C3D2DE;'
        'display:inline-block;"></span>'
        '<span style="width:6px;height:6px;border-radius:50%;background:#C3D2DE;'
        'display:inline-block;"></span></div>'
    )

    left = COL(55, [
        pills,
        heading(
            f'High-Purity Peptides<br>for <span style="color:{TEAL}">Advanced Research</span>',
            size=46, tag="h1", weight=700, lh=1.18, ls=-0.6,
            tablet=36, mobile=29, margin=dim(0, 0, 16, 0)),
        text("Pharmaceutical-grade peptides manufactured for research.<br>"
             "Verified for purity, potency, and reliability.",
             size=15, lh=1.75),
        ctas,
        dots,
    ], _inline_size=55, _inline_size_tablet=100, content_position="center")

    right = COL(45, [image(IMG["hero-vial.svg"], "High-purity research peptide vial",
                           width=100)],
                _inline_size=45, _inline_size_tablet=100, content_position="center")

    return SEC([left, right],
               layout="boxed",
               content_width=sz(WIDTH),
               structure="20",
               gap="default",
               content_position="middle",
               background_background="gradient",
               background_color=HERO_A,
               background_color_stop=sz(0, "%"),
               background_color_b=HERO_B,
               background_color_b_stop=sz(100, "%"),
               background_gradient_type="linear",
               background_gradient_angle=sz(160, "deg"),
               padding=dim(56, 20, 96, 20),
               padding_tablet=dim(44, 20, 80, 20),
               padding_mobile=dim(34, 16, 74, 16))


# ---------------------------------------------------------------------------
# 2. Trust bar (overlaps the hero)
# ---------------------------------------------------------------------------
TRUST = [
    ("fas fa-flask", "FDA Registered", "cGMP Compliant"),
    ("fas fa-shield-alt", "Third-Party Tested", "Independent Verification"),
    ("fas fa-lock", "Secure Checkout", "Encrypted &amp; Safe"),
    ("fas fa-truck", "Fast &amp; Reliable", "Worldwide Shipping"),
]


def s_trust():
    cols = []
    for i, (icon, title, desc) in enumerate(TRUST):
        extra = {}
        if i < len(TRUST) - 1:
            extra = {"border_border": "solid",
                     "border_width": dim(0, 1, 0, 0),
                     "border_color": "#EDF1F5",
                     "border_width_tablet": dim(0, 0, 0, 0),
                     "border_width_mobile": dim(0, 0, 0, 0)}
        cols.append(COL(25, [icon_box(icon, title, desc)],
                        _inline_size=25, _inline_size_tablet=50,
                        padding=dim(6, 18, 6, 18), **extra))

    card = SEC(cols, inner=True, structure="40", gap="no",
               content_position="middle")

    return SEC([COL(100, [card],
                    background_background="classic",
                    background_color=WHITE,
                    border_radius=all_(12),
                    padding=dim(20, 14, 20, 14),
                    box_shadow_box_shadow_type="yes",
                    box_shadow_box_shadow=shadow(10, 34, "rgba(11,27,58,0.08)"))],
               layout="boxed",
               content_width=sz(WIDTH),
               structure="10",
               gap="no",
               z_index=3,
               padding=dim(0, 20, 0, 20),
               margin=dim(-52, 0, 0, 0),
               margin_tablet=dim(-46, 0, 0, 0),
               margin_mobile=dim(-42, 0, 0, 0))


# ---------------------------------------------------------------------------
# Shared: section heading row with optional carousel arrows / link
# ---------------------------------------------------------------------------
def heading_row(title_html, right_widgets=None, right_size=14,
                right_size_mobile=35):
    left = COL(100 - right_size, [
        heading(title_html, size=27, tag="h2", weight=700, lh=1.3,
                tablet=24, mobile=21, margin=dim(0, 0, 0, 0)),
    ], _inline_size=100 - right_size, _inline_size_tablet=100 - right_size,
        _inline_size_mobile=100 - right_size_mobile)
    right = COL(right_size, right_widgets or [],
                _inline_size=right_size, _inline_size_tablet=right_size,
                _inline_size_mobile=right_size_mobile)
    return SEC([left, right], inner=True, structure="20", gap="no",
               content_position="middle", margin=dim(0, 0, 22, 0))


def arrows():
    return SEC([
        COL(50, [circle_icon("fas fa-arrow-left", bg="#EDF2F7", fg=NAVY)],
            _inline_size=50),
        COL(50, [circle_icon("fas fa-arrow-right", bg="#1D66C9", fg=WHITE)],
            _inline_size=50),
    ], inner=True, structure="20", gap="no")


# ---------------------------------------------------------------------------
# Product cards
# ---------------------------------------------------------------------------
def product_card(img_key, name, price, badge_text, badge_bg, badge_fg, alt):
    inner = SEC([COL(100, [
        badge(badge_text, badge_bg, badge_fg),
        image(IMG[img_key], alt, width=44, margin=dim(0, 0, 12, 0),
              _background_background="classic",
              _background_color="#F7FAFC",
              _border_radius=all_(10),
              _padding=dim(12, 10, 12, 10)),
        heading(name, size=14.5, weight=600, tag="h3", lh=1.4,
                margin=dim(0, 0, 6, 0)),
        heading(price, size=17, weight=700, tag="div", lh=1.3,
                margin=dim(0, 0, 14, 0)),
        button("Add to Cart", bg=NAVY, fg=WHITE, size=13, full=True,
               icon="fas fa-shopping-cart", radius=7, pad=(12, 18, 12, 18)),
    ])], inner=True, structure="10", **CARD)
    return inner


def product_row(products):
    cols = []
    for p in products:
        cols.append(COL(25, [product_card(*p)],
                        _inline_size=25, _inline_size_tablet=50))
    return SEC(cols, inner=True, structure="40", gap="wide")


ROW_ONE = [
    ("vial-bpc-157.svg", "BPC-157 5mg", "$59.99", "Bestseller",
     BADGE_GREEN_BG, BADGE_GREEN_FG, "BPC-157 5mg research vial"),
    ("vial-cjc-1295.svg", "CJC-1295 5mg", "$69.99", "Bestseller",
     BADGE_GREEN_BG, BADGE_GREEN_FG, "CJC-1295 5mg research vial"),
    ("vial-ipamorelin.svg", "Ipamorelin 5mg", "$54.99", "Bestseller",
     BADGE_GREEN_BG, BADGE_GREEN_FG, "Ipamorelin 5mg research vial"),
    ("vial-tb-500.svg", "TB-500 5mg", "$64.99", "Bestseller",
     BADGE_GREEN_BG, BADGE_GREEN_FG, "TB-500 5mg research vial"),
]

ROW_TWO = [
    ("vial-bpc-157.svg", "BPC-157 5mg", "$59.99", "In Stock",
     BADGE_GREEN_BG, BADGE_GREEN_FG, "BPC-157 5mg research vial"),
    ("vial-cjc-1295.svg", "CJC-1295 5mg", "$69.99", "In Stock",
     BADGE_GREEN_BG, BADGE_GREEN_FG, "CJC-1295 5mg research vial"),
    ("vial-ipamorelin.svg", "Ipamorelin 5mg", "$54.99", "Best Seller",
     BADGE_BLUE_BG, BADGE_BLUE_FG, "Ipamorelin 5mg research vial"),
    ("vial-tb-500.svg", "TB-500 5mg", "$64.99", "Low Stock",
     BADGE_ORANGE_BG, BADGE_ORANGE_FG, "TB-500 5mg research vial"),
]


def s_most_ordered():
    return OUTER([COL(100, [
        heading_row(f'Most-Ordered <span style="color:{TEAL}">By Research</span>',
                    [arrows()]),
        product_row(ROW_ONE),
    ])], pad_top=54, pad_bottom=44, structure="10", gap="no")


def s_catalog():
    return OUTER([COL(100, [
        heading_row(f'Explore Our <span style="color:{TEAL}">Catalog</span>',
                    [arrows()]),
        product_row(ROW_TWO),
    ])], pad_top=54, pad_bottom=44, structure="10", gap="no")


# ---------------------------------------------------------------------------
# 4. Browse by category
# ---------------------------------------------------------------------------
CATEGORIES = [
    dict(icon="fas fa-atom", title="Peptides<br>Category 1", img="category-peptides.svg",
         fg=WHITE, btn_bg=WHITE, btn_fg=NAVY, gradient=(CAT_BLUE_A, CAT_BLUE_B),
         alt="Research peptide vials"),
    dict(icon="fas fa-tint", title="Peptide Blends<br>Category 2", img="category-blends.svg",
         fg=NAVY, btn_bg=WHITE, btn_fg=NAVY, flat=CAT_MINT,
         alt="Peptide blend vials"),
    dict(icon="fas fa-dna", title="Bioregulators<br>Category 3", img="category-bioregulators.svg",
         fg=NAVY, btn_bg=WHITE, btn_fg=NAVY, flat=CAT_PEACH,
         alt="Bioregulator vials"),
]


def category_card(c):
    style = {"background_background": "classic"}
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
        style["background_color"] = c["flat"]

    left = COL(58, [
        W("icon", selected_icon={"value": c["icon"], "library": "fa-solid"},
          view="default", align="left", size=sz(20),
          primary_color=c["fg"], _margin=dim(0, 0, 10, 0)),
        heading(c["title"], size=17, color=c["fg"], weight=700, tag="h3",
                lh=1.32, margin=dim(0, 0, 14, 0)),
        button("Shop now", bg=c["btn_bg"], fg=c["btn_fg"], size=12, weight=600,
               radius=6, pad=(9, 15, 9, 15), hover_bg=NAVY, hover_fg=WHITE),
    ], _inline_size=58, padding=dim(4, 0, 4, 4))

    right = COL(42, [image(IMG[c["img"]], c["alt"], width=100)],
                _inline_size=42, content_position="bottom")

    return SEC([left, right], inner=True, structure="20", gap="no",
               content_position="middle",
               height="min-height", custom_height=sz(168),
               height_inner="min-height", custom_height_inner=sz(168),
               border_radius=all_(14),
               padding=dim(20, 14, 20, 20),
               **style)


def s_categories():
    cards = [COL(33, [category_card(c)], _inline_size_tablet=100)
             for c in CATEGORIES]
    return OUTER([COL(100, [
        heading_row(f'Browse <span style="color:{TEAL}">By Category</span>', []),
        SEC(cards, inner=True, structure="30", gap="wide"),
    ])], pad_top=20, pad_bottom=44, structure="10", gap="no")


# ---------------------------------------------------------------------------
# 5. Built for researchers (dark)
# ---------------------------------------------------------------------------
def s_quality():
    left = COL(50, [
        heading(
            f'Built <span style="color:{TEAL}">For Researchers</span> Who<br>'
            "Don&#39;t Compromise On Quality",
            size=27, color=WHITE, weight=700, tag="h2", lh=1.36,
            tablet=24, mobile=21, margin=dim(0, 0, 18, 0)),
        heading("100%", size=58, color=TEAL, weight=800, tag="div", lh=1,
                ls=-1.5, tablet=48, mobile=42, margin=dim(0, 0, 14, 0)),
        text("We don&#39;t ask you to take our word for it. Every batch we produce is "
             "third-party tested, verified, and exceeds industry standards for "
             "unmatched research reliability.",
             size=13.5, color="#A9B8CC", lh=1.8,
             margin=dim(0, 0, 24, 0)),
        button("See our testing", bg=NAVY_2, fg=WHITE, size=13,
               border="#2C4472", radius=7, pad=(12, 22, 12, 22),
               hover_bg=TEAL),
    ], _inline_size=50, _inline_size_tablet=100, content_position="center",
        padding=dim(0, 24, 0, 0))

    right = COL(50, [image(IMG["coa-certificate.svg"],
                           "Certificate of Analysis for BPC-157", width=100)],
                _inline_size=50, _inline_size_tablet=100,
                content_position="center")

    inner = SEC([left, right], inner=True, structure="20", gap="wide",
                content_position="middle",
                background_background="gradient",
                background_color=NAVY,
                background_color_stop=sz(0, "%"),
                background_color_b="#0F2547",
                background_color_b_stop=sz(100, "%"),
                background_gradient_type="linear",
                background_gradient_angle=sz(135, "deg"),
                border_radius=all_(16),
                padding=dim(44, 40, 44, 40),
                padding_mobile=dim(30, 22, 30, 22))

    return OUTER([COL(100, [inner])], pad_top=20, pad_bottom=24,
                 structure="10", gap="no")


# ---------------------------------------------------------------------------
# 7. Feature strip
# ---------------------------------------------------------------------------
FEATURES = [
    ("fas fa-certificate", "99.8% Purity", "Guaranteed high purity in every batch"),
    ("fas fa-vials", "Lab Verified", "Each batch tested for safety and purity"),
    ("fas fa-lock", "Secure Payment", "Safe &amp; encrypted checkout"),
    ("fas fa-shipping-fast", "Fast Shipping", "Worldwide shipping you can trust"),
]


def s_features():
    cols = [COL(25, [icon_box(i, t, d, icon_size=21)],
                _inline_size=25, _inline_size_tablet=50,
                padding=dim(8, 14, 8, 0))
            for i, t, d in FEATURES]
    return OUTER([COL(100, [SEC(cols, inner=True, structure="40", gap="no",
                                content_position="middle")])],
                 pad_top=8, pad_bottom=44, structure="10", gap="no")


# ---------------------------------------------------------------------------
# 8. Promo duo
# ---------------------------------------------------------------------------
def s_promos():
    new_arrivals = SEC([
        COL(56, [
            heading("New<br>Arrivals", size=30, color=WHITE, weight=700, tag="h3",
                    lh=1.2, tablet=26, mobile=24, margin=dim(0, 0, 18, 0)),
            button("View Catalog", bg=WHITE, fg=NAVY, size=12.5, weight=600,
                   radius=7, pad=(11, 18, 11, 18), hover_bg=NAVY, hover_fg=WHITE),
        ], _inline_size=56, content_position="center", padding=dim(4, 0, 4, 4)),
        COL(44, [image(IMG["new-arrivals-vial.svg"], "New arrival peptide vial",
                       width=42)],
            _inline_size=44, content_position="bottom"),
    ], inner=True, structure="20", gap="no", content_position="middle",
        height="min-height", custom_height=sz(178),
        height_inner="min-height", custom_height_inner=sz(178),
        background_background="gradient",
        background_color=CAT_BLUE_A,
        background_color_stop=sz(0, "%"),
        background_color_b=CAT_BLUE_B,
        background_color_b_stop=sz(100, "%"),
        background_gradient_type="linear",
        background_gradient_angle=sz(150, "deg"),
        border_radius=all_(14),
        padding=dim(26, 20, 26, 24))

    documented = SEC([COL(100, [
        heading("Every Peptide.<br>Every Batch.<br>Fully Documented.",
                size=21, color=WHITE, weight=700, tag="h3", lh=1.42,
                mobile=19, margin=dim(0, 0, 14, 0)),
        text("We supply research-grade peptides backed by real data, real batch "
             "records, and real science you can trust.",
             size=13, color="#A9B8CC", lh=1.8),
    ], padding=dim(0, 0, 0, 0))],
        inner=True, structure="10", gap="no", content_position="middle",
        height="min-height", custom_height=sz(178),
        height_inner="min-height", custom_height_inner=sz(178),
        background_background="classic",
        background_color=NAVY,
        border_radius=all_(14),
        padding=dim(30, 28, 30, 28))

    return OUTER([
        COL(50, [new_arrivals], _inline_size=50, _inline_size_tablet=100),
        COL(50, [documented], _inline_size=50, _inline_size_tablet=100),
    ], pad_top=8, pad_bottom=52, structure="20", gap="wide")


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
                      weight=600, align="right", radius=0,
                      pad=(0, 0, 0, 0), hover_bg="rgba(0,0,0,0)", hover_fg=NAVY)
    return OUTER([COL(100, [
        heading_row("Frequently Asked Questions", [view_all], right_size=18,
                    right_size_mobile=42),
        SEC([
            COL(50, [accordion(FAQ_LEFT)], _inline_size=50, _inline_size_tablet=100),
            COL(50, [accordion(FAQ_RIGHT)], _inline_size=50, _inline_size_tablet=100),
        ], inner=True, structure="20", gap="wide"),
    ])], pad_top=8, pad_bottom=52, structure="10", gap="no")


# ---------------------------------------------------------------------------
# 10. Newsletter
# ---------------------------------------------------------------------------
NEWSLETTER_FORM = (
    "<!-- Swap this HTML widget for your form widget (Elementor Pro Forms, "
    "WPForms, Mailchimp, Fluent Forms...) and keep the same styling. -->\n"
    '<form class="pep-subscribe" method="post" action="#" '
    'style="display:flex;gap:10px;flex-wrap:wrap;align-items:center;">'
    '<label for="pep-email" class="screen-reader-text" '
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
    inner = SEC([
        COL(55, [icon_box("fas fa-envelope", "Stay in the loop.",
                          "Be the first to know about new products, lab reports, "
                          "and exclusive updates.",
                          icon_color=WHITE, icon_size=20, view="stacked",
                          bg="rgba(255,255,255,0.18)",
                          title_size=19, desc_size=13,
                          title_color=WHITE, desc_color="#DCF0EE")],
            _inline_size=55, _inline_size_tablet=100, content_position="center"),
        COL(45, [html_block(NEWSLETTER_FORM)],
            _inline_size=45, _inline_size_tablet=100, content_position="center"),
    ], inner=True, structure="20", gap="wide", content_position="middle",
        background_background="gradient",
        background_color="#2E8B96",
        background_color_stop=sz(0, "%"),
        background_color_b=TEAL_2,
        background_color_b_stop=sz(100, "%"),
        background_gradient_type="linear",
        background_gradient_angle=sz(100, "deg"),
        border_radius=all_(14),
        padding=dim(26, 30, 26, 30),
        padding_mobile=dim(24, 20, 24, 20))

    return OUTER([COL(100, [inner])], pad_top=8, pad_bottom=64,
                 structure="10", gap="no")


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

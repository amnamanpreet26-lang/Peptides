#!/usr/bin/env python3
"""Render the peptide landing template to a static HTML preview.

Verification tool, not part of the deliverable. Reuses the container/CSS
emulation in render_preview.py and adds the widgets this page uses: nested Tabs,
Icon List, Social Icons, and a stand-in for the WooCommerce Products widget.

Usage: python3 build/render_landing.py
"""

import html
import json
import os
import sys

import render_preview as R
import svg_assets as V
import svg_landing as L

INK, TEAL, BODY, MUTED, LINE = "#00030E", "#019DA6", "#4A5160", "#8A8F9C", "#E6E8EC"

# Outline glyphs this page uses on top of the set render_preview already carries.
R.ICONS.update({
    "comments": '<path d="M20 12.6c0 3.1-3.2 5.6-7.2 5.6-.9 0-1.8-.1-2.6-.4L6 19.5l1.2-3.1'
                'C5.5 15.4 4.4 14.1 4.4 12.6c0-3.1 3.2-5.6 7.2-5.6s8.4 2.5 8.4 5.6z"/>',
})


def _svg(name, color, size):
    return R.icon_svg(name, color, size)


# --- extra widget renderers ---------------------------------------------------
def r_icon_list(st):
    items = []
    css = R.typo_css(st, "text_typography_") + f"color:{st.get('text_color', BODY)};"
    gap = R.s(st.get("space_between"), "10px")
    for item in st.get("icon_list", []):
        items.append(
            f'<li style="margin:0 0 {gap};list-style:none">'
            f'<a href="#" style="{css}text-decoration:none">{item["text"]}</a></li>'
        )
    return f'<ul style="margin:0;padding:0">{"".join(items)}</ul>'


def r_social_icons(st):
    out = []
    pad = R.s(st.get("icon_padding"), "10px")
    size = float((st.get("icon_size") or {}).get("size", 13))
    for item in st.get("social_icon_list", []):
        out.append(
            f'<span style="display:inline-flex;padding:{pad};border-radius:50%;'
            f'background:{st.get("icon_primary_color", "rgba(255,255,255,.08)")}">'
            f'{_svg("dot-circle", st.get("icon_secondary_color", "#fff"), size)}</span>'
        )
    gap = R.s(st.get("icon_spacing"), "8px")
    return f'<div style="display:flex;gap:{gap}">{"".join(out)}</div>'


PRODUCTS = [
    ("BPC-157 Peptide 10mg", "$59.99"),
    ("Tesamorelin Peptide 10mg", "$69.99"),
    ("IGF-C4 Peptide 10mg", "$64.99"),
    ("Multi-Peptide Complex 30ml", "$89.99"),
    ("GHK-Cu Peptide 10mg", "$54.99"),
]


def r_woo_products(st):
    cols = int(st.get("columns", 5))
    vial = V.data_uri(V.vial("bpc"))
    cards = []
    for name, price in PRODUCTS[:cols]:
        cards.append(
            '<div style="background:#fff;border-radius:14px;overflow:hidden;'
            f'border:1px solid {LINE}">'
            '<div style="background:#F6F7F8;aspect-ratio:1/1;display:flex;'
            'align-items:center;justify-content:center;padding:14px">'
            f'<img src="{vial}" alt="" style="width:76%;height:auto"></div>'
            '<div style="padding:14px 16px 16px">'
            f'<div style="font:400 13px/1.45 Satoshi,Arial,sans-serif;color:{INK};'
            f'margin-bottom:8px">{name}</div>'
            '<div style="display:flex;align-items:center;justify-content:space-between">'
            f'<span style="font:500 14px/1 Satoshi,Arial,sans-serif;color:{INK}">{price}</span>'
            f'<span style="width:30px;height:30px;border-radius:50%;background:{INK};'
            'display:inline-flex;align-items:center;justify-content:center">'
            f'{_svg("credit-card", "#fff", 12)}</span>'
            "</div></div></div>"
        )
    grid = (f'<div style="display:grid;grid-template-columns:repeat({cols},minmax(0,1fr));'
            f'gap:18px">{"".join(cards)}</div>')
    return R.stub("WooCommerce Products &mdash; pick a category in the widget", grid)


def r_nested_tabs(st, el):
    css = R.typo_css(st, "title_typography_")
    buttons = []
    for i, tab in enumerate(st.get("tabs", [])):
        active = i == 0
        buttons.append(
            f'<span style="{css}display:inline-flex;align-items:center;'
            f'padding:{R.d(st.get("tabs_title_padding"), "11px 20px")};border-radius:999px;'
            f'border:1px solid {INK if active else LINE};'
            f'background:{INK if active else "#fff"};'
            f'color:{"#fff" if active else BODY}">{html.escape(tab["tab_title"])}</span>'
        )
    space = R.s(st.get("tabs_title_space_between"), "8px")
    head = f'<div style="display:flex;flex-wrap:wrap;gap:{space}">{"".join(buttons)}</div>'
    # A real tabs widget shows one panel at a time; show the first.
    panel = render(el["elements"][0]) if el["elements"] else ""
    pad = R.d(st.get("box_padding"), "34px 0 0 0")
    return f'{head}<div style="padding:{pad}">{panel}</div>'


def r_nested_accordion(st, el):
    """Like render_preview's, but honours default_state so the first row shows
    its answer the way the design does."""
    border = st.get("accordion_border_normal_color", LINE)
    tcss = R.typo_css(st, "title_typography_")
    pad = R.d(st.get("accordion_padding"), "18px 0")
    open_first = "expanded" == st.get("default_state")
    rows = []
    for i, item in enumerate(st.get("items", [])):
        is_open = open_first and 0 == i
        colour = st.get("active_title_color") if is_open else st.get("normal_title_color")
        rows.append(
            f'<div style="border-bottom:1px solid {border}">'
            f'<div style="padding:{pad};display:flex;justify-content:space-between;'
            f'align-items:center;gap:12px">'
            f'<span style="{tcss}color:{colour}">{html.escape(item["item_title"])}</span>'
            f'{_svg("minus-square" if is_open else "plus-square", st.get("normal_icon_color", MUTED), 13)}'
            "</div>"
            + (render(el["elements"][i]) if is_open and i < len(el["elements"]) else "")
            + "</div>"
        )
    return "".join(rows)


EXTRA = {"icon-list": r_icon_list, "social-icons": r_social_icons,
         "woocommerce-products": r_woo_products}


# --- walker (mirrors render_preview.render, plus nested-tabs) -----------------
def render(el):
    if el["elType"] == "widget":
        w, st = el["widgetType"], el.get("settings", {})
        if w == "nested-tabs":
            body = r_nested_tabs(st, el)
        elif w == "nested-accordion":
            body = r_nested_accordion(st, el)
        elif w in EXTRA:
            body = EXTRA[w](st)
        else:
            fn = R.WIDGETS.get(w)
            body = fn(st) if fn else f"<div>[{w}]</div>"

        css = "width:100%;"
        if st.get("_element_width") == "auto":
            css = "max-width:fit-content;"
        if st.get("_margin"):
            css += f"margin:{R.d(st['_margin'])};"
        if st.get("_padding"):
            css += f"padding:{R.d(st['_padding'])};"
        css += R.box_css(st, "_")
        return f'<div style="{css}">{body}</div>'

    st = el.get("settings", {})
    direction = st.get("flex_direction", "column")
    gap = st.get("flex_gap") or {}
    flex = (f"display:flex;flex-direction:{direction};"
            f"gap:{gap.get('row', 0)}px {gap.get('column', 0)}px;"
            f"flex-wrap:{st.get('flex_wrap', 'nowrap')};")
    if st.get("flex_align_items"):
        flex += f"align-items:{st['flex_align_items']};"
    if st.get("flex_justify_content"):
        flex += f"justify-content:{st['flex_justify_content']};"

    outer = "position:relative;"
    outer += f"width:{R.s(st['width'])};" if st.get("width") else "width:100%;"
    if st.get("min_height"):
        outer += f"min-height:{R.s(st['min_height'])};"
    if st.get("margin"):
        outer += f"margin:{R.d(st['margin'])};"
    outer += f"padding:{R.d(st.get('padding'), '0')};"
    outer += R.box_css(st)

    kids = "".join(render(c) for c in el["elements"])

    if st.get("content_width") == "boxed":
        bw = R.s(st.get("boxed_width"), "1140px")
        return (f'<div style="{outer}display:flex;">'
                f'<div style="{flex}max-width:{bw};width:100%;margin-inline:auto;">'
                f"{kids}</div></div>")
    return f'<div style="{outer}{flex}">{kids}</div>'


HEAD = """<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Peptide landing preview</title><style>
*{box-sizing:border-box}
body{margin:0;background:#fff;font-family:Satoshi,Inter,'Helvetica Neue',Arial,sans-serif;
 -webkit-font-smoothing:antialiased}
p{margin:0}
img{display:block}
</style>"""


def main():
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data = json.load(open(os.path.join(root, "templates", "peptide-landing.json"),
                          encoding="utf-8"))
    body = "".join(render(el) for el in data["content"])
    out = os.path.join(root, "build", "landing-preview.html")
    with open(out, "w", encoding="utf-8") as f:
        f.write(f"<!doctype html><html><head>{HEAD}</head><body>{body}</body></html>")
    print("wrote", out)


if __name__ == "__main__":
    sys.exit(main())

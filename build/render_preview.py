#!/usr/bin/env python3
"""Render the generated Elementor JSON to a static HTML preview.

Verification tool, not part of the deliverable. It re-implements the subset of
Elementor's Flexbox Container CSS that the template uses so the result can be
screenshotted and compared against the reference design.

Two blocks are stand-ins, drawn with a corner label, because their real content
comes from a plugin at runtime:
  * the Slider Revolution shortcode (the hero)
  * the WooCommerce Products widget (the two product rows)
"""

import html
import json
import os
import sys

import svg_assets as A

# Outline icon stand-ins for the Font Awesome *Regular* set the template uses.
ICONS = {
    "file-alt": '<path d="M14 3H7a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V8z"/>'
                '<path d="M14 3v5h5"/><path d="M9 13h6M9 17h6"/>',
    "check-circle": '<circle cx="12" cy="12" r="9"/><path d="m8.4 12.4 2.6 2.6 4.6-5.2"/>',
    "credit-card": '<rect x="3" y="5" width="18" height="14" rx="2.5"/><path d="M3 10h18"/>',
    "paper-plane": '<path d="M21 3 3 9.6l7.2 3.2L13.4 21z"/><path d="m10.2 12.8 5.4-5.4"/>',
    "gem": '<path d="M6 3h12l3 6-9 12L3 9z"/><path d="M3 9h18M9 3 6.2 9l5.8 12M15 3l2.8 6L12 21"/>',
    "clipboard": '<rect x="6" y="4" width="12" height="17" rx="2.5"/>'
                 '<rect x="9" y="2" width="6" height="4" rx="1.4"/>',
    "clock": '<circle cx="12" cy="12" r="9"/><path d="M12 7v5.4l3.4 2"/>',
    "dot-circle": '<circle cx="12" cy="12" r="9"/><circle cx="12" cy="12" r="3.2"/>',
    "clone": '<rect x="8" y="8" width="12" height="12" rx="2.4"/>'
             '<path d="M16 8V6a2 2 0 0 0-2-2H6a2 2 0 0 0-2 2v8a2 2 0 0 0 2 2h2"/>',
    "snowflake": '<path d="M12 3v18M4.2 7.5l15.6 9M19.8 7.5l-15.6 9"/>'
                 '<path d="M12 6.6 9.7 4.7M12 6.6l2.3-1.9M12 17.4l-2.3 1.9M12 17.4l2.3 1.9"/>',
    "envelope": '<rect x="3" y="5" width="18" height="14" rx="2.5"/><path d="m3.6 6.6 8.4 5.9 8.4-5.9"/>',
    "arrow-alt-circle-left": '<circle cx="12" cy="12" r="9"/><path d="M13.4 8.4 9.8 12l3.6 3.6"/>',
    "arrow-alt-circle-right": '<circle cx="12" cy="12" r="9"/><path d="M10.6 8.4 14.2 12l-3.6 3.6"/>',
    "plus-square": '<rect x="4" y="4" width="16" height="16" rx="2.6"/><path d="M12 8.4v7.2M8.4 12h7.2"/>',
    "minus-square": '<rect x="4" y="4" width="16" height="16" rx="2.6"/><path d="M8.4 12h7.2"/>',
}

NAVY, TEAL, BODY, MUTED, BORDER = "#0B1B3A", "#16A6A0", "#5B6B7C", "#8A99A8", "#E6ECF2"


def icon_svg(value, color, size):
    name = value.replace("far fa-", "").replace("fas fa-", "")
    body = ICONS.get(name, ICONS["dot-circle"])
    return (f'<svg viewBox="0 0 24 24" width="{size}" height="{size}" fill="none" '
            f'stroke="{color}" stroke-width="1.6" stroke-linecap="round" '
            f'stroke-linejoin="round" style="display:block">{body}</svg>')


# --- setting readers ---------------------------------------------------------
def d(v, default=""):
    if not v:
        return default
    u = v.get("unit", "px")
    return f"{v['top']}{u} {v['right']}{u} {v['bottom']}{u} {v['left']}{u}"


def s(v, default=None):
    if not v or v.get("size") in ("", None):
        return default
    return f"{v['size']}{v.get('unit', 'px')}"


def bg_css(st, prefix=""):
    kind = st.get(prefix + "background_background")
    if kind == "classic":
        c = st.get(prefix + "background_color")
        return f"background-color:{c};" if c else ""
    if kind == "gradient":
        a = st.get(prefix + "background_color", "#fff")
        b = st.get(prefix + "background_color_b", "#fff")
        ang = st.get(prefix + "background_gradient_angle") or {"size": 180}
        return (f"background-image:linear-gradient({ang['size']}deg,{a} "
                f"{s(st.get(prefix + 'background_color_stop'), '0%')},"
                f"{b} {s(st.get(prefix + 'background_color_b_stop'), '100%')});")
    return ""


def box_css(st, prefix=""):
    out = bg_css(st, prefix)
    if st.get(prefix + "border_border"):
        out += (f"border-style:{st[prefix + 'border_border']};"
                f"border-width:{d(st.get(prefix + 'border_width'), '1px')};"
                f"border-color:{st.get(prefix + 'border_color', '#ddd')};")
    if st.get(prefix + "border_radius"):
        out += f"border-radius:{d(st[prefix + 'border_radius'])};"
    if st.get(prefix + "box_shadow_box_shadow_type") == "yes":
        sh = st.get(prefix + "box_shadow_box_shadow", {})
        out += (f"box-shadow:{sh.get('horizontal', 0)}px {sh.get('vertical', 0)}px "
                f"{sh.get('blur', 0)}px {sh.get('spread', 0)}px "
                f"{sh.get('color', 'rgba(0,0,0,.1)')};")
    return out


def typo_css(st, p="typography_"):
    out = ""
    if st.get(p + "font_family"):
        out += f"font-family:'{st[p + 'font_family']}',sans-serif;"
    if st.get(p + "font_size"):
        out += f"font-size:{s(st[p + 'font_size'])};"
    if st.get(p + "font_weight"):
        out += f"font-weight:{st[p + 'font_weight']};"
    if st.get(p + "line_height"):
        out += f"line-height:{st[p + 'line_height']['size']};"
    if st.get(p + "letter_spacing"):
        out += f"letter-spacing:{s(st[p + 'letter_spacing'])};"
    if st.get(p + "text_transform"):
        out += f"text-transform:{st[p + 'text_transform']};"
    return out


# --- widget renderers --------------------------------------------------------
def r_heading(st):
    tag = st.get("header_size", "h2")
    css = (typo_css(st) + f"color:{st.get('title_color', '#000')};"
           f"text-align:{st.get('align', 'left')};margin:0;")
    return f'<{tag} style="{css}">{st.get("title", "")}</{tag}>'


def r_text(st):
    css = (typo_css(st) + f"color:{st.get('text_color', '#000')};"
           f"text-align:{st.get('align', 'left')};")
    return f'<div style="{css}">{st.get("editor", "")}</div>'


def r_button(st):
    align = st.get("align", "left")
    wrap = f"text-align:{align};"
    btn = ("display:inline-flex;align-items:center;justify-content:center;"
           "text-decoration:none;white-space:pre;")
    btn += typo_css(st)
    btn += (f"background-color:{st.get('background_color', '#000')};"
            f"color:{st.get('button_text_color', '#fff')};"
            f"border-radius:{d(st.get('border_radius'), '0')};"
            f"padding:{d(st.get('text_padding'), '12px 24px')};")
    if st.get("border_border"):
        btn += (f"border:{d(st.get('border_width'), '1px').split()[0]} "
                f"{st['border_border']} {st.get('border_color', '#ddd')};")
    if align == "justify":
        btn += "width:100%;"
        wrap = ""
    return f'<div style="{wrap}"><a href="#" style="{btn}">{st.get("text", "")}</a></div>'


def r_image(st):
    img = st.get("image", {})
    just = {"left": "flex-start", "center": "center",
            "right": "flex-end"}[st.get("align", "center")]
    return (f'<div style="display:flex;justify-content:{just};">'
            f'<img src="{img.get("url", "")}" alt="{html.escape(img.get("alt", ""))}" '
            f'style="width:{s(st.get("width"), "100%")};height:auto;max-width:100%;"></div>')


def r_icon_box(st):
    pos = st.get("position", "left")
    view = st.get("view", "default")
    size = float((st.get("icon_size") or {}).get("size", 24))
    color = (st.get("secondary_color") if view == "stacked"
             else st.get("primary_color", "#000"))
    glyph = icon_svg(st["selected_icon"]["value"], color, size)
    if view == "stacked":
        glyph = (f'<span style="display:inline-flex;padding:{s(st.get("icon_padding"), "16px")};'
                 f'background:{st.get("primary_color")};border-radius:50%;">{glyph}</span>')
    t_css = typo_css(st, "title_typography_") + f"color:{st.get('title_color')};margin:0;"
    d_css = typo_css(st, "description_typography_") + f"color:{st.get('description_color')};margin:0;"
    return (f'<div style="display:flex;flex-direction:{"row" if pos == "left" else "column"};'
            f'gap:{s(st.get("icon_space"), "12px")};align-items:center;">'
            f'<div style="flex:0 0 auto;line-height:0;">{glyph}</div>'
            f'<div><h6 style="{t_css}">{st.get("title_text", "")}</h6>'
            f'<p style="{d_css}margin-top:{s(st.get("title_bottom_space"), "4px")};">'
            f'{st.get("description_text", "")}</p></div></div>')


def r_icon(st):
    size = float((st.get("size") or {}).get("size", 20))
    just = {"left": "flex-start", "center": "center",
            "right": "flex-end"}[st.get("align", "left")]
    return (f'<div style="display:flex;justify-content:{just};">'
            f'{icon_svg(st["selected_icon"]["value"], st.get("primary_color", "#000"), size)}</div>')


def r_nested_accordion(st, el):
    t_css = typo_css(st, "title_typography_") + f"color:{st.get('normal_title_color', NAVY)};"
    rows = []
    for item in st.get("items", []):
        rows.append(
            f'<div style="border:1px solid {st.get("accordion_border_normal_color", BORDER)};'
            f'border-bottom:0;padding:{d(st.get("accordion_padding"), "15px 16px")};'
            'display:flex;justify-content:space-between;align-items:center;gap:12px;">'
            f'<span style="{t_css}">{item["item_title"]}</span>'
            f'{icon_svg("far fa-plus-square", st.get("normal_icon_color", MUTED), 13)}</div>'
        )
    return (f'<div style="border-bottom:1px solid '
            f'{st.get("accordion_border_normal_color", BORDER)};">' + "".join(rows) + "</div>")


def r_html(st):
    return st.get("html", "")


def r_spacer(st):
    return f'<div style="height:{s(st.get("space"), "20px")}"></div>'


# --- plugin stand-ins --------------------------------------------------------
def stub(label, inner, tone="#1D66C9"):
    return (f'<div style="position:relative;">'
            f'<div style="position:absolute;top:-11px;left:0;z-index:5;background:{tone};'
            'color:#fff;font:600 10px/1 Inter,Arial,sans-serif;letter-spacing:.4px;'
            f'padding:5px 9px;border-radius:5px;">{label}</div>{inner}</div>')


def r_shortcode(st):
    """The hero lives in Slider Revolution; draw the intended slide."""
    code = st.get("shortcode", "")
    if "rev_slider" not in code:
        return f'<code>{html.escape(code)}</code>'
    pill = ('display:inline-flex;align-items:center;gap:6px;font:700 10px/1 Inter,Arial,'
            'sans-serif;letter-spacing:.7px;text-transform:uppercase;padding:6px 11px;'
            'border-radius:5px;')
    btn = ('display:inline-flex;align-items:center;text-decoration:none;'
           'font:600 14px/1.2 Inter,Arial,sans-serif;padding:14px 26px;border-radius:8px;')
    inner = (
        '<div style="display:flex;align-items:center;gap:24px;max-width:1200px;'
        'margin-inline:auto;padding:56px 20px 40px;">'
        '<div style="width:55%;">'
        f'<div style="display:flex;gap:10px;margin-bottom:18px;">'
        f'<span style="{pill}background:#E4F1EC;color:#1F7A63;">'
        f'{icon_svg("far fa-check-circle", "#1F7A63", 11)} FDA Compliant</span>'
        f'<span style="{pill}background:#E4EFF7;color:#1A5C9E;">'
        f'{icon_svg("far fa-clipboard", "#1A5C9E", 11)} Lab Tested</span></div>'
        f'<h1 style="font:700 46px/1.18 Inter,Arial,sans-serif;letter-spacing:-.6px;'
        f'color:{NAVY};margin:0 0 16px;">High-Purity Peptides<br>for '
        f'<span style="color:{TEAL}">Advanced Research</span></h1>'
        f'<p style="font:400 15px/1.75 Inter,Arial,sans-serif;color:{BODY};margin:0;">'
        'Pharmaceutical-grade peptides manufactured for research.<br>'
        'Verified for purity, potency, and reliability.</p>'
        f'<div style="display:flex;gap:12px;margin:28px 0 26px;">'
        f'<a href="#" style="{btn}background:{NAVY};color:#fff;">Browse Catalog &nbsp;&rarr;</a>'
        f'<a href="#" style="{btn}background:#fff;color:{NAVY};border:1px solid #D8E2EA;">'
        'Research Standards</a></div>'
        f'<div style="display:flex;gap:7px;align-items:center;">'
        f'<span style="width:24px;height:6px;border-radius:3px;background:{NAVY};"></span>'
        '<span style="width:6px;height:6px;border-radius:50%;background:#C3D2DE;"></span>'
        '<span style="width:6px;height:6px;border-radius:50%;background:#C3D2DE;"></span>'
        '</div></div>'
        f'<div style="width:45%;"><img src="{A.data_uri(A.hero())}" alt="" '
        'style="width:100%;height:auto;display:block;"></div></div>'
    )
    return stub("Slider Revolution &mdash; slider alias: peptides-hero", inner, "#C0392B")


PRODUCTS = [("vial-bpc-157.svg", "BPC-157 5mg", "$59.99"),
            ("vial-cjc-1295.svg", "CJC-1295 5mg", "$69.99"),
            ("vial-ipamorelin.svg", "Ipamorelin 5mg", "$54.99"),
            ("vial-tb-500.svg", "TB-500 5mg", "$64.99")]


def r_woo_products(st):
    """WooCommerce renders these at runtime from the chosen category."""
    assets = A.all_assets()
    cards = []
    for f, name, price in PRODUCTS[:int(st.get("columns", 4))]:
        cards.append(
            f'<div style="flex:1;border:1px solid {BORDER};border-radius:12px;'
            'padding:14px;background:#fff;box-shadow:0 4px 16px rgba(11,27,58,.05);">'
            f'<div style="background:#F7FAFC;border-radius:10px;padding:12px 10px;'
            'display:flex;justify-content:center;margin-bottom:12px;">'
            f'<img src="{A.data_uri(assets[f])}" alt="" style="width:44%;height:auto;"></div>'
            f'<div style="font:600 14.5px/1.4 Inter,Arial,sans-serif;color:{NAVY};'
            f'margin-bottom:6px;">{name}</div>'
            f'<div style="font:700 17px/1.3 Inter,Arial,sans-serif;color:{NAVY};'
            f'margin-bottom:14px;">{price}</div>'
            f'<a href="#" style="display:block;text-align:center;text-decoration:none;'
            f'background:{NAVY};color:#fff;font:600 13px/1.2 Inter,Arial,sans-serif;'
            'padding:12px 18px;border-radius:7px;">Add to cart</a></div>')
    inner = f'<div style="display:flex;gap:20px;">{"".join(cards)}</div>'
    return stub("WooCommerce Products &mdash; pick a category in the widget", inner)


WIDGETS = {"heading": r_heading, "text-editor": r_text, "button": r_button,
           "image": r_image, "icon-box": r_icon_box, "icon": r_icon,
           "html": r_html, "spacer": r_spacer, "shortcode": r_shortcode,
           "woocommerce-products": r_woo_products}


# --- tree walker -------------------------------------------------------------
def render(el):
    t = el["elType"]
    st = el.get("settings", {})

    if t == "widget":
        w = el["widgetType"]
        if w == "nested-accordion":
            body = r_nested_accordion(st, el)
        else:
            fn = WIDGETS.get(w)
            body = fn(st) if fn else f'<div>[{w}]</div>'
        css = "width:100%;"
        if st.get("_element_width") == "auto":
            css = "max-width:fit-content;"
        if st.get("_margin"):
            css += f"margin:{d(st['_margin'])};"
        if st.get("_padding"):
            css += f"padding:{d(st['_padding'])};"
        css += box_css(st, "_")
        return f'<div style="{css}">{body}</div>'

    # container
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
    if st.get("width"):
        outer += f"width:{s(st['width'])};"
    else:
        outer += "width:100%;"
    if st.get("min_height"):
        outer += f"min-height:{s(st['min_height'])};"
    if st.get("margin"):
        outer += f"margin:{d(st['margin'])};"
    if st.get("z_index"):
        outer += f"z-index:{st['z_index']};"
    outer += f"padding:{d(st.get('padding'), '0')};"
    outer += box_css(st)

    kids = "".join(render(c) for c in el["elements"])

    if st.get("content_width") == "boxed":
        bw = s(st.get("boxed_width"), "1140px")
        return (f'<div class="e-con" style="{outer}display:flex;">'
                f'<div style="{flex}max-width:{bw};width:100%;margin-inline:auto;">'
                f'{kids}</div></div>')
    return f'<div class="e-con" style="{outer}{flex}">{kids}</div>'


HEAD = """<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Preview</title><style>
*{box-sizing:border-box}
body{margin:0;background:#fff;font-family:Inter,'Helvetica Neue',Arial,sans-serif;
 -webkit-font-smoothing:antialiased}
p{margin:0}
img{display:block}
</style>"""


def main():
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data = json.load(open(os.path.join(root, "templates",
                                       "peptides-homepage.json"), encoding="utf-8"))
    body = "".join(render(el) for el in data["content"])
    out = os.path.join(root, "build", "preview.html")
    with open(out, "w", encoding="utf-8") as f:
        f.write(f"<!doctype html><html><head>{HEAD}</head><body>{body}</body></html>")
    print("wrote", out)


if __name__ == "__main__":
    sys.exit(main())

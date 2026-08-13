#!/usr/bin/env python3
"""Render the generated Elementor JSON to a static HTML preview.

This is a verification tool, not part of the deliverable. It re-implements the
subset of Elementor's layout CSS that the template uses so the result can be
screenshotted and compared against the reference design.
"""

import html
import json
import os
import sys

GAPS = {"no": 0, "narrow": 5, "extended": 7.5, "wide": 10, "wider": 15,
        "default": 10, "": 10}

# Rough stand-ins for the Font Awesome glyphs used by the template.
ICONS = {
    "fas fa-flask": "M9 3h6v2h-1v4.2l4.6 8.1A2 2 0 0 1 16.9 20H7.1a2 2 0 0 1-1.7-2.7L10 9.2V5H9V3z",
    "fas fa-vial": "M7 2h6v2h-1v13a3 3 0 1 1-6 0V4H5V2h2zm1 2v13a1 1 0 1 0 2 0V4H8z",
    "fas fa-vials": "M4 2h6v2H9v13a2 2 0 1 1-4 0V4H4V2zm10 0h6v2h-1v13a2 2 0 1 1-4 0V4h-1V2z",
    "fas fa-shield-alt": "M12 2l8 3v6c0 5-3.4 9.3-8 11-4.6-1.7-8-6-8-11V5l8-3zm-1 12l6-6-1.4-1.4L11 11.2 8.4 8.6 7 10l4 4z",
    "fas fa-lock": "M7 10V7a5 5 0 0 1 10 0v3h1a1 1 0 0 1 1 1v9a1 1 0 0 1-1 1H6a1 1 0 0 1-1-1v-9a1 1 0 0 1 1-1h1zm2 0h6V7a3 3 0 0 0-6 0v3z",
    "fas fa-truck": "M2 5h11v10H2V5zm12 3h4l3 4v3h-7V8zM6 20a2 2 0 1 1 0-4 2 2 0 0 1 0 4zm11 0a2 2 0 1 1 0-4 2 2 0 0 1 0 4z",
    "fas fa-shipping-fast": "M1 7h10v8H1V7zm11 2h4l3 4v2h-7V9zM6 19a2 2 0 1 1 0-4 2 2 0 0 1 0 4zm10 0a2 2 0 1 1 0-4 2 2 0 0 1 0 4zM0 9h4v1.5H0V9zm0 3h3v1.5H0V12z",
    "fas fa-certificate": "M12 1l2.6 2.1 3.3-.4 1 3.2 2.9 1.7-1.5 3 1.5 3-2.9 1.7-1 3.2-3.3-.4L12 21l-2.6-2.1-3.3.4-1-3.2L2.2 14.4l1.5-3-1.5-3 2.9-1.7 1-3.2 3.3.4L12 1z",
    "fas fa-shopping-cart": "M2 3h3l3 12h10v2H7L4 5H2V3zm6 16a2 2 0 1 1 0 4 2 2 0 0 1 0-4zm10 0a2 2 0 1 1 0 4 2 2 0 0 1 0-4zM9 6h12l-2 7H10L9 6z",
    "fas fa-arrow-right": "M4 11h11.2l-4.6-4.6L12 5l7 7-7 7-1.4-1.4 4.6-4.6H4v-2z",
    "fas fa-arrow-left": "M20 11H8.8l4.6-4.6L12 5l-7 7 7 7 1.4-1.4L8.8 13H20v-2z",
    "fas fa-atom": "M12 9.5a2.5 2.5 0 1 1 0 5 2.5 2.5 0 0 1 0-5zm0-7.5c3 0 9 3.6 9 10s-6 10-9 10-9-3.6-9-10 6-10 9-10zm0 2C9.8 4 5 6.9 5 12s4.8 8 7 8 7-2.9 7-8-4.8-8-7-8z",
    "fas fa-tint": "M12 2s7 8 7 12a7 7 0 1 1-14 0c0-4 7-12 7-12z",
    "fas fa-dna": "M6 2c0 4 12 6 12 10S6 18 6 22h2c0-3 12-5 12-10S8 5 8 2H6zm10 0c0 1-1 1.8-2.4 2.6h-3.2C9 3.8 8 3 8 2h8zM8.4 19.4h7.2c-.9.7-2 1.2-3.6 1.6-1.6-.4-2.7-.9-3.6-1.6z",
    "fas fa-envelope": "M2 5h20v14H2V5zm2 2v.2l8 5 8-5V7H4zm16 3.5-8 5-8-5V17h16v-6.5z",
    "fas fa-chevron-down": "M6 9l6 6 6-6-1.4-1.4L12 12.2 7.4 7.6 6 9z",
    "fas fa-chevron-up": "M6 15l6-6 6 6-1.4 1.4L12 11.8l-4.6 4.6L6 15z",
    "fas fa-check-circle": "M12 2a10 10 0 1 1 0 20 10 10 0 0 1 0-20zm-1 14 7-7-1.4-1.4L11 13.2l-2.6-2.6L7 12l4 4z",
}


def icon_svg(value, color, size):
    path = ICONS.get(value, ICONS["fas fa-certificate"])
    return (f'<svg viewBox="0 0 24 24" width="{size}" height="{size}" '
            f'fill="{color}" style="display:block"><path d="{path}"/></svg>')


# --- setting readers ---------------------------------------------------------
def d(v, default=""):
    """Dimensions control -> CSS shorthand."""
    if not v:
        return default
    u = v.get("unit", "px")
    return f"{v['top']}{u} {v['right']}{u} {v['bottom']}{u} {v['left']}{u}"


def s(v, default=None):
    """Slider control -> CSS length."""
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
        a_stop = s(st.get(prefix + "background_color_stop"), "0%")
        b_stop = s(st.get(prefix + "background_color_b_stop"), "100%")
        return (f"background-image:linear-gradient({ang['size']}deg,"
                f"{a} {a_stop},{b} {b_stop});")
    return ""


def box_css(st, prefix=""):
    out = ""
    out += bg_css(st, prefix)
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


ALIGN_MAP = {"top": "flex-start", "middle": "center", "center": "center",
             "bottom": "flex-end", "": "flex-start"}


# --- widget renderers --------------------------------------------------------
def r_heading(st):
    tag = st.get("header_size", "h2")
    css = typo_css(st) + f"color:{st.get('title_color', '#000')};"
    css += f"text-align:{st.get('align', 'left')};margin:0;"
    return f'<{tag} style="{css}">{st.get("title", "")}</{tag}>'


def r_text(st):
    css = typo_css(st) + f"color:{st.get('text_color', '#000')};"
    css += f"text-align:{st.get('align', 'left')};"
    return f'<div style="{css}">{st.get("editor", "")}</div>'


def r_button(st):
    align = st.get("align", "left")
    wrap = f"text-align:{align};"
    btn = ("display:inline-flex;align-items:center;justify-content:center;gap:"
           f"{s(st.get('icon_indent'), '8px')};text-decoration:none;")
    btn += typo_css(st)
    btn += f"background-color:{st.get('background_color', '#000')};"
    btn += f"color:{st.get('button_text_color', '#fff')};"
    btn += f"border-radius:{d(st.get('border_radius'), '0')};"
    btn += f"padding:{d(st.get('text_padding'), '12px 24px')};"
    if st.get("border_border"):
        btn += (f"border:{d(st.get('border_width'), '1px').split()[0]} "
                f"{st['border_border']} {st.get('border_color', '#ddd')};")
    if align == "justify":
        btn += "width:100%;"
        wrap = ""
    icon = ""
    if st.get("selected_icon", {}).get("value"):
        size = s(st.get("typography_font_size"), "14px")
        icon = icon_svg(st["selected_icon"]["value"],
                        st.get("button_text_color", "#fff"),
                        str(round(float(size.replace("px", "")) * 1.05)))
    return (f'<div style="{wrap}"><a href="#" style="{btn}">'
            f'<span>{st.get("text", "")}</span>{icon}</a></div>')


def r_image(st):
    img = st.get("image", {})
    w = s(st.get("width"), "100%")
    align = st.get("align", "center")
    just = {"left": "flex-start", "center": "center", "right": "flex-end"}[align]
    return (f'<div style="display:flex;justify-content:{just};">'
            f'<img src="{img.get("url", "")}" alt="{html.escape(img.get("alt", ""))}" '
            f'style="width:{w};height:auto;max-width:100%;"></div>')


def r_icon_box(st):
    pos = st.get("position", "left")
    view = st.get("view", "default")
    icon_size = float((st.get("icon_size") or {}).get("size", 24))
    color = (st.get("secondary_color") if view == "stacked"
             else st.get("primary_color", "#000"))
    icon_html = icon_svg(st["selected_icon"]["value"], color, icon_size)
    if view == "stacked":
        pad = s(st.get("icon_padding"), "16px")
        icon_html = (f'<span style="display:inline-flex;padding:{pad};'
                     f'background:{st.get("primary_color")};border-radius:50%;">'
                     f"{icon_html}</span>")
    title_css = typo_css(st, "title_typography_") + f"color:{st.get('title_color')};margin:0;"
    desc_css = typo_css(st, "description_typography_") + f"color:{st.get('description_color')};margin:0;"
    gap = s(st.get("icon_space"), "12px")
    tb = s(st.get("title_bottom_space"), "4px")
    direction = "row" if pos == "left" else "column"
    return (f'<div style="display:flex;flex-direction:{direction};gap:{gap};'
            f'align-items:center;">'
            f'<div style="flex:0 0 auto;line-height:0;">{icon_html}</div>'
            f'<div><h6 style="{title_css}">{st.get("title_text", "")}</h6>'
            f'<p style="{desc_css}margin-top:{tb};">{st.get("description_text", "")}</p>'
            f"</div></div>")


def r_icon(st):
    view = st.get("view", "default")
    size = float((st.get("size") or {}).get("size", 20))
    color = st.get("secondary_color") if view == "stacked" else st.get("primary_color", "#000")
    inner = icon_svg(st["selected_icon"]["value"], color, size)
    align = st.get("align", "left")
    just = {"left": "flex-start", "center": "center", "right": "flex-end"}[align]
    if view == "stacked":
        pad = s(st.get("icon_padding"), "12px")
        inner = (f'<span style="display:inline-flex;padding:{pad};'
                 f'background:{st.get("primary_color")};border-radius:50%;">{inner}</span>')
    return f'<div style="display:flex;justify-content:{just};">{inner}</div>'


def r_accordion(st):
    rows = []
    tcss = typo_css(st, "title_typography_") + f"color:{st.get('title_color')};"
    for t in st.get("tabs", []):
        rows.append(
            f'<div style="border:1px solid {st.get("border_color", "#eee")};'
            'border-bottom:0;padding:15px 16px;display:flex;'
            'justify-content:space-between;align-items:center;gap:12px;">'
            f'<span style="{tcss}">{t["tab_title"]}</span>'
            f'{icon_svg("fas fa-chevron-down", st.get("icon_color", "#999"), 13)}</div>'
        )
    return (f'<div style="border-bottom:1px solid {st.get("border_color", "#eee")};">'
            + "".join(rows) + "</div>")


def r_html(st):
    return st.get("html", "")


def r_spacer(st):
    return f'<div style="height:{s(st.get("space"), "20px")}"></div>'


WIDGETS = {"heading": r_heading, "text-editor": r_text, "button": r_button,
           "image": r_image, "icon-box": r_icon_box, "icon": r_icon,
           "accordion": r_accordion, "html": r_html, "spacer": r_spacer}


# --- tree walker -------------------------------------------------------------
def render(el):
    t = el["elType"]
    st = el.get("settings", {})

    if t == "widget":
        fn = WIDGETS.get(el["widgetType"])
        body = fn(st) if fn else f'<div>[{el["widgetType"]}]</div>'
        css = "width:100%;"
        if st.get("_element_width") == "auto":
            css = "max-width:fit-content;"
        if st.get("_margin"):
            css += f"margin:{d(st['_margin'])};"
        if st.get("_padding"):
            css += f"padding:{d(st['_padding'])};"
        css += box_css(st, "_")
        return f'<div style="{css}">{body}</div>'

    if t == "column":
        width = st.get("_inline_size") or st.get("_column_size") or 100
        gap_parent = el.get("_gap", 10)
        pad = d(st.get("padding"), f"{gap_parent}px")
        inner = "".join(render(c) for c in el["elements"])
        vpos = ALIGN_MAP.get(st.get("content_position", ""), "flex-start")
        wrap_css = (f"width:100%;display:flex;flex-direction:column;flex-wrap:wrap;"
                    f"align-content:flex-start;justify-content:{vpos};"
                    f"padding:{pad};{box_css(st)}")
        return (f'<div class="col" style="width:{width}%;display:flex;'
                f'min-height:1px;position:relative;">'
                f'<div style="{wrap_css}">{inner}</div></div>')

    # section
    gap = GAPS.get(st.get("gap", "default"), 10)
    for c in el["elements"]:
        c["_gap"] = gap
    cols = "".join(render(c) for c in el["elements"])
    outer = "position:relative;"
    if st.get("margin"):
        outer += f"margin:{d(st['margin'])};"
    if st.get("z_index"):
        outer += f"z-index:{st['z_index']};"
    outer += f"padding:{d(st.get('padding'), '0')};"
    outer += box_css(st)
    maxw = ""
    if st.get("layout") == "boxed" and st.get("content_width"):
        maxw = f"max-width:{s(st['content_width'])};"
    align = ALIGN_MAP.get(st.get("content_position", ""), "stretch")
    if st.get("content_position") == "":
        align = "stretch"
    # Elementor: .elementor-widget-wrap > .elementor-element { width: 100% }
    outer += "width:100%;"
    if st.get("height") == "min-height" and st.get("custom_height"):
        outer += f"min-height:{s(st['custom_height'])};"
    return (f'<section style="{outer}">'
            f'<div style="display:flex;margin-inline:auto;{maxw}'
            f'align-items:{align};">{cols}</div></section>')


HEAD = """<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Preview</title><style>
*{box-sizing:border-box}
body{margin:0;background:#fff;font-family:Inter,'Helvetica Neue',Arial,sans-serif;
 -webkit-font-smoothing:antialiased}
p{margin:0}
img{display:block}
@media(max-width:1024px){.col{width:100%!important}}
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

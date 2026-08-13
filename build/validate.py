#!/usr/bin/env python3
"""Structural checks on the generated Elementor template JSON."""

import base64
import json
import os
import re
import sys

# Widgets bundled with free Elementor. Anything outside this list would make the
# template require Elementor Pro.
# Widgets that come from a plugin rather than free Elementor. Allowed, but the
# README has to state the dependency.
PLUGIN_WIDGETS = {
    "woocommerce-products": "Elementor Pro + WooCommerce",
}

FREE_WIDGETS = {
    "heading", "image", "text-editor", "video", "button", "divider", "spacer",
    "google_maps", "icon", "image-box", "icon-box", "star-rating", "image-gallery",
    "image-carousel", "icon-list", "counter", "progress", "testimonial", "tabs",
    "accordion", "toggle", "social-icons", "alert", "audio", "shortcode", "html",
    "menu-anchor", "sidebar", "text-path", "read-more", "rating",
    "nested-accordion", "nested-tabs",
}

errors, warnings = [], []
deps = set()


def check(node, parent, depth, section_depth):
    t = node["elType"]

    if t == "widget":
        w = node["widgetType"]
        if parent not in ("column", "container"):
            errors.append(f"widget {w} not inside a column/container")
        if w in PLUGIN_WIDGETS:
            deps.add(PLUGIN_WIDGETS[w])
        elif w not in FREE_WIDGETS:
            errors.append(f"unknown widget: {w}")
        # only nested widgets may carry child containers
        if node["elements"] and not w.startswith("nested-"):
            errors.append(f"widget {w} has children")
        if w == "nested-accordion":
            n_items = len(node["settings"].get("items", []))
            if n_items != len(node["elements"]):
                errors.append(f"nested-accordion: {n_items} items but "
                              f"{len(node['elements'])} content containers")
            for c in node["elements"]:
                if c["elType"] != "container":
                    errors.append("nested-accordion child is not a container")
                check(c, "widget", depth + 1, section_depth)
        return

    if t == "container":
        cw = node["settings"].get("content_width")
        if cw not in (None, "boxed", "full"):
            errors.append(f"bad content_width: {cw}")
        fd = node["settings"].get("flex_direction")
        if fd not in (None, "row", "column", "row-reverse", "column-reverse"):
            errors.append(f"bad flex_direction: {fd}")
        if fd == "row":
            widths = [c["settings"].get("width", {}).get("size")
                      for c in node["elements"] if c["elType"] == "container"]
            widths = [w for w in widths if w]
            if widths and abs(sum(widths) - 100) > 1.5:
                warnings.append(f"row children sum to {round(sum(widths), 2)}%")
        for c in node["elements"]:
            check(c, "container", depth + 1, section_depth)
        return

    if t == "column":
        if parent != "section":
            errors.append("column not inside a section")
        for c in node["elements"]:
            check(c, "column", depth + 1, section_depth)
        return

    if t == "section":
        if node.get("isInner"):
            if section_depth >= 2:
                errors.append("inner section nested inside another inner section")
            for c in node["elements"]:
                if not c.get("isInner"):
                    errors.append("column of an inner section missing isInner")
        # column widths
        sizes = []
        for c in node["elements"]:
            st = c["settings"]
            sizes.append(st.get("_inline_size") or st.get("_column_size") or 0)
        total = sum(sizes)
        if node["elements"] and abs(total - 100) > 1.5:
            warnings.append(f"section columns sum to {total}% ({len(sizes)} cols)")
        structure = node["settings"].get("structure")
        if structure and int(structure[0]) != len(node["elements"]):
            errors.append(f"structure {structure} but {len(node['elements'])} columns")
        for c in node["elements"]:
            check(c, "section", depth + 1,
                  section_depth + (1 if node.get("isInner") else 0))
        return

    errors.append(f"unknown elType {t}")


def main():
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    path = os.path.join(root, "templates", "peptides-homepage.json")
    raw = open(path, encoding="utf-8").read()
    data = json.loads(raw)

    for key in ("content", "page_settings", "version", "title", "type"):
        if key not in data:
            errors.append(f"missing top-level key: {key}")

    ids, widgets = [], []

    def collect(e):
        ids.append(e["id"])
        if e["elType"] == "widget":
            widgets.append(e["widgetType"])
        for c in e.get("elements", []):
            collect(c)

    for el in data["content"]:
        if el["elType"] not in ("section", "container"):
            errors.append("top-level element is not a section/container")
        collect(el)
        check(el, "root", 0, 0)

    if len(ids) != len(set(ids)):
        errors.append("duplicate element ids")

    # every embedded image must be a decodable svg data uri
    uris = re.findall(r'data:image/svg\+xml;base64,([A-Za-z0-9+/=]+)', raw)
    for u in uris:
        svg = base64.b64decode(u).decode("utf-8")
        if not svg.startswith("<svg") or not svg.rstrip().endswith("</svg>"):
            errors.append("malformed embedded svg")
        if svg.count("<svg") != 1:
            errors.append("nested svg root")

    kinds = {}

    def count(e):
        kinds[e["elType"]] = kinds.get(e["elType"], 0) + 1
        for c in e.get("elements", []):
            count(c)

    for el in data["content"]:
        count(el)
    print(f"top-level       : {len(data['content'])}")
    print(f"containers      : {kinds.get('container', 0)}")
    print(f"legacy sections : {kinds.get('section', 0)}")
    print(f"elements        : {len(ids)}")
    print(f"widgets         : {len(widgets)}")
    print(f"widget types    : {', '.join(sorted(set(widgets)))}")
    print(f"embedded images : {len(uris)}")
    print(f"plugin deps     : {', '.join(sorted(deps)) or 'none'}")
    solid = re.findall(r'"(fas fa-[a-z0-9-]+)"', raw)
    if solid:
        errors.append(f"solid icons present: {sorted(set(solid))}")
    outline = sorted(set(re.findall(r'"far fa-([a-z0-9-]+)"', raw)))
    print(f"outline icons   : {', '.join(outline)}")
    print(f"file size       : {len(raw) / 1024:.0f} KB")
    for w in warnings:
        print("WARN :", w)
    for e in errors:
        print("FAIL :", e)
    print("RESULT:", "FAIL" if errors else "OK")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())

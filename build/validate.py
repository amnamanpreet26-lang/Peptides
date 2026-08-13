#!/usr/bin/env python3
"""Structural checks on the generated Elementor template JSON."""

import base64
import json
import os
import re
import sys

# Widgets bundled with free Elementor. Anything outside this list would make the
# template require Elementor Pro.
FREE_WIDGETS = {
    "heading", "image", "text-editor", "video", "button", "divider", "spacer",
    "google_maps", "icon", "image-box", "icon-box", "star-rating", "image-gallery",
    "image-carousel", "icon-list", "counter", "progress", "testimonial", "tabs",
    "accordion", "toggle", "social-icons", "alert", "audio", "shortcode", "html",
    "menu-anchor", "sidebar", "text-path", "read-more", "rating",
}

errors, warnings = [], []


def check(node, parent, depth, section_depth):
    t = node["elType"]

    if t == "widget":
        if parent != "column":
            errors.append(f"widget {node['widgetType']} not inside a column")
        if node["widgetType"] not in FREE_WIDGETS:
            errors.append(f"non-free widget: {node['widgetType']}")
        if node["elements"]:
            errors.append(f"widget {node['widgetType']} has children")
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
        if el["elType"] != "section":
            errors.append("top-level element is not a section")
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

    print(f"sections        : {len(data['content'])}")
    print(f"elements        : {len(ids)}")
    print(f"widgets         : {len(widgets)}")
    print(f"widget types    : {', '.join(sorted(set(widgets)))}")
    print(f"embedded images : {len(uris)}")
    print(f"file size       : {len(raw) / 1024:.0f} KB")
    for w in warnings:
        print("WARN :", w)
    for e in errors:
        print("FAIL :", e)
    print("RESULT:", "FAIL" if errors else "OK")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())

"""Vector artwork for the Peptides homepage template.

Every image used by the Elementor template is generated here as an SVG so the
template ships with artwork that matches the design and has zero external
dependencies. Images are embedded in the JSON as base64 data URIs and are also
written to assets/images/ so they can be uploaded to the Media Library.
"""

import base64
import re

# --- Brand palette (kept in sync with build_template.py) ----------------------
NAVY = "#0B1B3A"
TEAL = "#16A6A0"
FONT = "Inter, 'Helvetica Neue', Helvetica, Arial, sans-serif"
CAT_ASPECT = 1.24   # shared width:height frame for the three category images


# --- Vial presets -------------------------------------------------------------
# Each preset describes one product vial: the label gradient, the text colour
# used on the label, the accent colour of the logo mark, and the printed copy.
VIALS = {
    "bpc": dict(
        label_a="#123A73", label_b="#0C2650", fg="#FFFFFF",
        accent="#2BB3C0", name="BPC-157", dose="10 MG",
    ),
    "cjc": dict(
        label_a="#F2F6F3", label_b="#DFE9E2", fg="#12324F",
        accent="#2BB3C0", name="CJC-1295", dose="5 MG",
    ),
    "ipa": dict(
        label_a="#EAF5F4", label_b="#D5E8E6", fg="#12324F",
        accent="#16A6A0", name="IPAMORELIN", dose="5 MG",
    ),
    "tb": dict(
        label_a="#F3F3EA", label_b="#E3E6D9", fg="#12324F",
        accent="#2BB3C0", name="TB-500", dose="5 MG",
    ),
    "blend": dict(
        label_a="#1B7F86", label_b="#116068", fg="#FFFFFF",
        accent="#8FE3DC", name="BLEND", dose="10 MG",
    ),
}


def _mark(x, y, s, fill):
    """The small hexagon logo mark that sits before the brand name."""
    return (
        f'<path transform="translate({x},{y}) scale({s})" fill="{fill}" '
        'd="M9 0 18 5.2v10.4L9 20.8 0 15.6V5.2Z"/>'
    )


def vial_parts(uid, label_a, label_b, fg, accent, name, dose,
               cap="#161E2E", brand="Test"):
    """Return (defs, group) for one vial drawn in a 0 0 200 250 coordinate box.

    Split into defs + group so several vials can be composed into a single SVG
    (the category cards) without gradient id collisions.
    """
    defs = (
        f'<linearGradient id="g{uid}" x1="0" y1="0" x2="1" y2="0">'
        f'<stop offset="0" stop-color="#F4F8FC"/><stop offset=".45" stop-color="#FFFFFF"/>'
        f'<stop offset="1" stop-color="#D9E4EE"/></linearGradient>'
        f'<linearGradient id="c{uid}" x1="0" y1="0" x2="1" y2="0">'
        f'<stop offset="0" stop-color="#9AA7B6"/><stop offset=".35" stop-color="#E7EDF3"/>'
        f'<stop offset="1" stop-color="#8D9BAA"/></linearGradient>'
        f'<linearGradient id="l{uid}" x1="0" y1="0" x2="1" y2="1">'
        f'<stop offset="0" stop-color="{label_a}"/><stop offset="1" stop-color="{label_b}"/>'
        f'</linearGradient>'
    )

    chip = "#FFFFFF" if fg == "#FFFFFF" else NAVY
    g = (
        '<g>'
        f'<ellipse cx="100" cy="176" rx="47" ry="6.5" fill="{NAVY}" opacity=".12"/>'
        # glass body
        f'<rect x="58" y="32" width="84" height="140" rx="12" fill="url(#g{uid})"/>'
        # crimp + cap
        f'<rect x="79" y="19" width="42" height="14" rx="3" fill="url(#c{uid})"/>'
        f'<rect x="84" y="2" width="32" height="19" rx="5" fill="{cap}"/>'
        f'<rect x="84" y="2" width="10" height="19" rx="5" fill="#FFFFFF" opacity=".14"/>'
        # label
        f'<rect x="58" y="58" width="84" height="100" rx="3" fill="url(#l{uid})"/>'
        # brand lockup
        + _mark(66, 62, 0.42, accent) +
        f'<text x="78" y="70" font-family="{FONT}" font-size="7.5" font-weight="700" '
        f'fill="{fg}">{brand}</text>'
        f'<rect x="65" y="77" width="70" height="1" fill="{fg}" opacity=".22"/>'
        # product name
        f'<text x="65" y="94" font-family="{FONT}" font-size="10" font-weight="700" '
        f'fill="{fg}">{name}</text>'
        f'<text x="65" y="103" font-family="{FONT}" font-size="4.8" font-weight="500" '
        f'fill="{fg}" opacity=".7">Lyophilised Powder</text>'
        # dose chips
        f'<rect x="65" y="109" width="25" height="11" rx="2.5" fill="{chip}" opacity=".22"/>'
        f'<text x="68" y="117" font-family="{FONT}" font-size="6" font-weight="700" '
        f'fill="{fg}">{dose}</text>'
        f'<rect x="93" y="109" width="21" height="11" rx="2.5" fill="{chip}" opacity=".22"/>'
        f'<text x="96" y="117" font-family="{FONT}" font-size="6" font-weight="700" '
        f'fill="{fg}">99%</text>'
        # filler lines
        f'<rect x="65" y="128" width="56" height="2" rx="1" fill="{fg}" opacity=".2"/>'
        f'<rect x="65" y="134" width="46" height="2" rx="1" fill="{fg}" opacity=".16"/>'
        f'<rect x="65" y="140" width="51" height="2" rx="1" fill="{fg}" opacity=".12"/>'
        f'<text x="65" y="151" font-family="{FONT}" font-size="4.4" font-weight="600" '
        f'fill="{fg}" opacity=".75">FOR RESEARCH USE ONLY</text>'
        # glass highlights
        '<rect x="64" y="40" width="10" height="126" rx="5" fill="#FFFFFF" opacity=".38"/>'
        '<rect x="131" y="40" width="4" height="126" rx="2" fill="#FFFFFF" opacity=".2"/>'
        '</g>'
    )
    return defs, g


# The drawing only occupies x 51..149 of the 200-wide box, so product shots are
# cropped to a tight viewBox to avoid dead space inside the image widget.
def vial(preset, w=112, h=190):
    defs, g = vial_parts("a", **VIALS[preset])
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="44 0 112 190" '
        f'width="{w}" height="{h}" role="img"><defs>{defs}</defs>{g}</svg>'
    )


def _molecule():
    """Decorative molecular lattice used behind the hero product shot."""
    nodes = [(548, 96, 15), (622, 140, 11), (596, 214, 18), (512, 176, 10),
             (664, 82, 8), (520, 250, 9), (668, 208, 12)]
    edges = [(0, 1), (1, 2), (2, 3), (3, 0), (1, 4), (3, 5), (2, 6), (0, 3)]
    out = ['<g opacity=".9">']
    for a, b in edges:
        out.append(
            f'<line x1="{nodes[a][0]}" y1="{nodes[a][1]}" x2="{nodes[b][0]}" '
            f'y2="{nodes[b][1]}" stroke="#A9C9DF" stroke-width="1.6"/>'
        )
    for i, (cx, cy, r) in enumerate(nodes):
        fill = TEAL if i in (1, 5) else "#C4DBEB"
        op = ".55" if i in (1, 5) else ".85"
        out.append(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{fill}" opacity="{op}"/>')
    out.append('</g>')
    return "".join(out)


def hero():
    """Hero visual: soft blue field, molecule lattice, pedestal and hero vial."""
    defs, g = vial_parts("h", **VIALS["bpc"])
    return (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 720 600" '
        'width="720" height="600" role="img"><defs>' + defs +
        '<linearGradient id="ped" x1="0" y1="0" x2="0" y2="1">'
        '<stop offset="0" stop-color="#FFFFFF"/><stop offset="1" stop-color="#E4EDF4"/>'
        '</linearGradient>'
        '<radialGradient id="glow" cx=".5" cy=".45" r=".55">'
        '<stop offset="0" stop-color="#D6E9F5"/>'
        '<stop offset="1" stop-color="#D6E9F5" stop-opacity="0"/></radialGradient>'
        '</defs>'
        '<circle cx="360" cy="285" r="270" fill="url(#glow)"/>'
        + _molecule() +
        # pedestal
        '<ellipse cx="360" cy="470" rx="172" ry="32" fill="#FFFFFF"/>'
        '<rect x="188" y="470" width="344" height="44" fill="url(#ped)"/>'
        '<ellipse cx="360" cy="514" rx="172" ry="32" fill="#DCE7EF"/>'
        '<ellipse cx="360" cy="470" rx="120" ry="20" fill="#0B1B3A" opacity=".07"/>'
        # hero vial, scaled up and seated on the pedestal
        '<g transform="translate(160,126) scale(2)">' + g + '</g>'
        '</svg>'
    )


def _coa_row(y, test, spec, result, alt):
    band = f'<rect x="34" y="{y - 15}" width="632" height="30" fill="#F7FAFC"/>' if alt else ""
    return (
        band +
        f'<text x="50" y="{y + 4}" font-family="{FONT}" font-size="11.5" fill="{NAVY}">{test}</text>'
        f'<text x="286" y="{y + 4}" font-family="{FONT}" font-size="11.5" fill="#64748B">{spec}</text>'
        f'<text x="452" y="{y + 4}" font-family="{FONT}" font-size="11.5" font-weight="600" '
        f'fill="{NAVY}">{result}</text>'
        f'<rect x="584" y="{y - 9}" width="46" height="19" rx="9.5" fill="#E4F4E3"/>'
        f'<text x="597" y="{y + 4}" font-family="{FONT}" font-size="10" font-weight="700" '
        f'fill="#3D7A2E">Pass</text>'
    )


def coa():
    """Certificate of Analysis card shown in the quality section."""
    rows = [
        ("Appearance", "White lyophilised powder", "Conforms"),
        ("Peptide Purity (HPLC)", "≥ 98.0 %", "99.1 %"),
        ("Peptide Identity (MS)", "Conforms", "Conforms"),
        ("Water Content (KF)", "≤ 6.0 %", "3.4 %"),
        ("Acetate Content", "≤ 15.0 %", "8.2 %"),
        ("Bacterial Endotoxin", "&lt; 10 EU/mg", "&lt; 1 EU/mg"),
        ("Residual Solvents", "Conforms to ICH", "Conforms"),
    ]
    body = "".join(
        _coa_row(214 + i * 34, t, s, r, i % 2 == 0) for i, (t, s, r) in enumerate(rows)
    )
    return (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 700 500" '
        'width="700" height="500" role="img">'
        f'<rect x="14" y="18" width="672" height="470" rx="16" fill="{NAVY}" opacity=".18"/>'
        '<rect x="10" y="10" width="680" height="470" rx="16" fill="#FFFFFF"/>'
        # header
        f'<text x="34" y="62" font-family="{FONT}" font-size="21" font-weight="700" '
        f'fill="{NAVY}">Certificate of Analysis</text>'
        f'<text x="34" y="84" font-family="{FONT}" font-size="11.5" fill="#7A8899">'
        'Batch BPC-240118 &#183; Issued 12 Jan 2024 &#183; Third-party verified</text>'
        '<rect x="516" y="38" width="150" height="34" rx="17" fill="#1D66C9"/>'
        f'<text x="546" y="60" font-family="{FONT}" font-size="12" font-weight="600" '
        'fill="#FFFFFF">Download PDF</text>'
        '<rect x="34" y="104" width="632" height="1" fill="#E8EEF4"/>'
        # product line
        f'<text x="34" y="136" font-family="{FONT}" font-size="15" font-weight="700" '
        f'fill="{NAVY}">BPC-157</text>'
        f'<text x="34" y="156" font-family="{FONT}" font-size="11.5" fill="#7A8899">'
        '5 mg per vial &#183; Lyophilised &#183; CAS 137525-51-0</text>'
        '<rect x="560" y="122" width="106" height="26" rx="13" fill="#E4F4E3"/>'
        f'<text x="576" y="139" font-family="{FONT}" font-size="11" font-weight="700" '
        'fill="#3D7A2E">All tests pass</text>'
        # table head
        '<rect x="34" y="176" width="632" height="26" rx="6" fill="#EEF3F8"/>'
        f'<text x="50" y="194" font-family="{FONT}" font-size="10.5" font-weight="700" '
        'fill="#5A6B7D" letter-spacing="0.6">TEST</text>'
        f'<text x="286" y="194" font-family="{FONT}" font-size="10.5" font-weight="700" '
        'fill="#5A6B7D" letter-spacing="0.6">SPECIFICATION</text>'
        f'<text x="452" y="194" font-family="{FONT}" font-size="10.5" font-weight="700" '
        'fill="#5A6B7D" letter-spacing="0.6">RESULT</text>'
        f'<text x="584" y="194" font-family="{FONT}" font-size="10.5" font-weight="700" '
        'fill="#5A6B7D" letter-spacing="0.6">STATUS</text>'
        + body +
        '<rect x="34" y="452" width="632" height="1" fill="#E8EEF4"/>'
        f'<text x="34" y="470" font-family="{FONT}" font-size="9.5" fill="#93A2B1">'
        'Analysed by an ISO&#160;17025 accredited laboratory. Research use only.</text>'
        '</svg>'
    )


def cat_group(kind):
    """Vial arrangements used inside the three Browse By Category cards."""
    layouts = {
        1: [("cat1a", "bpc", 110, 4, 0.98)],
        2: [("cat2a", "ipa", 45, 40, 0.78), ("cat2b", "blend", 108, 12, 0.92),
            ("cat2c", "ipa", 165, 40, 0.78)],
        3: [("cat3a", "tb", 70, 30, 0.84), ("cat3b", "cjc", 140, 8, 0.95)],
    }[kind]
    defs, groups = [], []
    x0 = y0 = 1e9
    x1 = y1 = -1e9
    for uid, preset, x, y, s in layouts:
        d, g = vial_parts(uid, **VIALS[preset])
        defs.append(d)
        groups.append(f'<g transform="translate({x},{y}) scale({s})">{g}</g>')
        # the drawing occupies x 51..149, y 0..184 in its own 200-wide box
        x0, x1 = min(x0, x + 51 * s), max(x1, x + 149 * s)
        y0, y1 = min(y0, y + 0 * s), max(y1, y + 184 * s)

    # Frame every category image to one aspect ratio so all three cards render
    # at the same height for a given column width.
    aspect = CAT_ASPECT
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    w, h = (x1 - x0) + 16, (y1 - y0) + 12
    if w / h < aspect:
        w = h * aspect
    else:
        h = w / aspect
    vx, vy = round(cx - w / 2, 1), round(cy - h / 2, 1)
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'viewBox="{vx} {vy} {round(w, 1)} {round(h, 1)}" '
        f'width="{round(w)}" height="{round(h)}" role="img"><defs>'
        + "".join(defs) + '</defs>' + "".join(groups) + '</svg>'
    )


# --- helpers ------------------------------------------------------------------
def minify(svg):
    svg = re.sub(r">\s+<", "><", svg.strip())
    return re.sub(r"\s{2,}", " ", svg)


def data_uri(svg):
    raw = base64.b64encode(minify(svg).encode("utf-8")).decode("ascii")
    return "data:image/svg+xml;base64," + raw


def all_assets():
    """Every asset the template needs, keyed by the filename it is saved under."""
    return {
        "hero-vial.svg": hero(),
        "coa-certificate.svg": coa(),
        "vial-bpc-157.svg": vial("bpc"),
        "vial-cjc-1295.svg": vial("cjc"),
        "vial-ipamorelin.svg": vial("ipa"),
        "vial-tb-500.svg": vial("tb"),
        "category-peptides.svg": cat_group(1),
        "category-blends.svg": cat_group(2),
        "category-bioregulators.svg": cat_group(3),
        "new-arrivals-vial.svg": vial("bpc"),
    }

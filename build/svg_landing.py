"""Vector artwork for the peptide landing page template.

Two images carry the page: the hero product shot and the lab-testing splash.
Everything else on the page is either WooCommerce content or type, so there is
nothing else to draw. Images are embedded in the JSON as base64 data URIs and
written to assets/images/ as files.
"""

import base64
import re

INK = "#00030E"
TEAL = "#019DA6"
TEAL_DEEP = "#017A81"
TEAL_PALE = "#CFEAEC"
FONT = "Satoshi, Inter, 'Helvetica Neue', Helvetica, Arial, sans-serif"


def _vial(uid, x, y, s, body_a, body_b, cap, label_fg, name, brand="PATHWAYS"):
    """A standing vial, drawn in a 0..120 x 0..300 box then placed by transform."""
    return (
        f'<g transform="translate({x},{y}) scale({s})">'
        # shadow on the surface
        f'<ellipse cx="60" cy="292" rx="52" ry="9" fill="{INK}" opacity=".18"/>'
        # cap
        f'<rect x="34" y="0" width="52" height="30" rx="7" fill="{cap}"/>'
        f'<rect x="34" y="0" width="16" height="30" rx="7" fill="#FFFFFF" opacity=".16"/>'
        # crimp
        f'<rect x="30" y="26" width="60" height="18" rx="4" fill="url(#crimp{uid})"/>'
        # body
        f'<rect x="14" y="40" width="92" height="248" rx="16" fill="url(#body{uid})"/>'
        # brand set vertically, as on the reference bottle
        f'<text transform="translate(97,262) rotate(-90)" font-family="{FONT}" '
        f'font-size="13" font-weight="500" letter-spacing="3.2" fill="{label_fg}" '
        f'opacity=".85">{brand}</text>'
        # product name block
        f'<text x="28" y="118" font-family="{FONT}" font-size="17" font-weight="500" '
        f'fill="{label_fg}">{name}</text>'
        f'<rect x="28" y="130" width="44" height="18" rx="9" fill="{TEAL}"/>'
        f'<text x="36" y="143" font-family="{FONT}" font-size="9" font-weight="500" '
        f'fill="#FFFFFF">10 mg</text>'
        f'<rect x="28" y="164" width="52" height="2" rx="1" fill="{label_fg}" opacity=".28"/>'
        f'<rect x="28" y="172" width="40" height="2" rx="1" fill="{label_fg}" opacity=".2"/>'
        f'<text x="28" y="266" font-family="{FONT}" font-size="7" font-weight="400" '
        f'fill="{label_fg}" opacity=".6">RESEARCH USE ONLY</text>'
        # glass highlights
        f'<rect x="22" y="52" width="12" height="222" rx="6" fill="#FFFFFF" opacity=".22"/>'
        f'<rect x="94" y="52" width="5" height="222" rx="2.5" fill="#FFFFFF" opacity=".12"/>'
        '</g>'
    )


def _dropper(uid, x, y, s):
    """The small amber dropper bottle that sits in front of the hero vial."""
    return (
        f'<g transform="translate({x},{y}) scale({s})">'
        f'<ellipse cx="40" cy="176" rx="34" ry="7" fill="{INK}" opacity=".16"/>'
        f'<rect x="24" y="0" width="32" height="34" rx="5" fill="#1D1F26"/>'
        f'<rect x="30" y="30" width="20" height="14" fill="#C9CED6"/>'
        f'<rect x="8" y="42" width="64" height="130" rx="14" fill="url(#amber{uid})"/>'
        f'<rect x="14" y="52" width="8" height="110" rx="4" fill="#FFFFFF" opacity=".3"/>'
        f'<rect x="18" y="86" width="44" height="42" rx="4" fill="#FBF6EC"/>'
        f'<text x="26" y="102" font-family="{FONT}" font-size="8" font-weight="500" '
        f'fill="#6B5A34">LUNARA</text>'
        f'<text x="26" y="114" font-family="{FONT}" font-size="6" font-weight="400" '
        f'fill="#9A8759">NOURISH OIL</text>'
        '</g>'
    )


def hero():
    """Hero: soft field, frond shadows, stone plinth, vial, dropper, promo badge."""
    return (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 760 620" '
        'width="760" height="620" role="img"><defs>'
        '<radialGradient id="halo" cx=".5" cy=".45" r=".5">'
        '<stop offset="0" stop-color="#FFFFFF" stop-opacity=".55"/>'
        '<stop offset="1" stop-color="#FFFFFF" stop-opacity="0"/></radialGradient>'
        '<linearGradient id="bodyH" x1="0" y1="0" x2="1" y2="0">'
        f'<stop offset="0" stop-color="#12263A"/><stop offset=".55" stop-color="#1B3B55"/>'
        f'<stop offset="1" stop-color="#0C1B29"/></linearGradient>'
        '<linearGradient id="crimpH" x1="0" y1="0" x2="1" y2="0">'
        '<stop offset="0" stop-color="#8E97A3"/><stop offset=".4" stop-color="#E8ECF1"/>'
        '<stop offset="1" stop-color="#828C99"/></linearGradient>'
        '<linearGradient id="amberH" x1="0" y1="0" x2="1" y2="0">'
        '<stop offset="0" stop-color="#C8842F"/><stop offset=".5" stop-color="#E8AE5C"/>'
        '<stop offset="1" stop-color="#B87526"/></linearGradient>'
        '<linearGradient id="stone" x1="0" y1="0" x2="0" y2="1">'
        '<stop offset="0" stop-color="#BDBDB6"/><stop offset="1" stop-color="#8E8F8A"/>'
        '</linearGradient>'
        '</defs>'
        # No background plate - the section colour shows through, so the art sits
        # on the page rather than in a visible box.
        '<circle cx="470" cy="250" r="235" fill="url(#halo)"/>'
        # stone plinth
        '<ellipse cx="392" cy="470" rx="196" ry="42" fill="#00030E" opacity=".10"/>'
        '<path d="M214 452c8-34 44-52 96-56 74-6 168-2 214 14 34 12 44 34 30 54-16 22-88 '
        '36-176 36-96 0-176-18-164-48z" fill="url(#stone)"/>'
        '<path d="M214 452c10-30 46-48 96-52-30 16-52 34-60 56-14 4-32 2-36-4z" '
        'fill="#FFFFFF" opacity=".22"/>'
        # products
        + _vial('H', 300, 120, 1.18, '#12263A', '#0C1B29', '#151A22', '#FFFFFF', 'BPC-157')
        + _dropper('H', 520, 300, 1.0) +
        # promo badge
        '<circle cx="614" cy="196" r="66" fill="#FFFFFF"/>'
        f'<text x="614" y="182" text-anchor="middle" font-family="{FONT}" font-size="12" '
        f'font-weight="500" fill="{INK}">FREE MINI</text>'
        f'<text x="614" y="197" text-anchor="middle" font-family="{FONT}" font-size="12" '
        f'font-weight="500" fill="{INK}">BODY OIL</text>'
        f'<text x="614" y="212" text-anchor="middle" font-family="{FONT}" font-size="8" '
        f'font-weight="400" fill="#7C828E" letter-spacing="1">ON ORDERS</text>'
        f'<text x="614" y="230" text-anchor="middle" font-family="{FONT}" font-size="17" '
        f'font-weight="500" fill="{TEAL}">$79+</text>'
        '</svg>'
    )


def _splash():
    """Ribbons of liquid arcing around the lab-section bottle."""
    ribbons = (
        ('M60 250c40-120 150-190 250-150 90 36 120 130 88 210-24 60-84 96-150 92', '.9', 14),
        ('M84 300c20-108 118-176 208-150 80 24 116 104 92 176', '.55', 9),
        ('M120 132c60-52 150-58 214-6', '.4', 6),
    )
    out = []
    for d, op, w in ribbons:
        out.append(
            f'<path d="{d}" fill="none" stroke="url(#liquid)" stroke-width="{w}" '
            f'stroke-linecap="round" opacity="{op}"/>'
        )
    for cx, cy, r, op in ((402, 96, 9, '.7'), (438, 150, 6, '.55'), (96, 384, 7, '.5'),
                          (150, 92, 5, '.45'), (452, 300, 8, '.4')):
        out.append(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{TEAL}" opacity="{op}"/>')
    return "".join(out)


def lab():
    """Lab-testing visual: bottle with liquid ribbons, for the dark band."""
    return (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 520 560" '
        'width="520" height="560" role="img"><defs>'
        '<linearGradient id="liquid" x1="0" y1="0" x2="1" y2="1">'
        f'<stop offset="0" stop-color="{TEAL_PALE}"/><stop offset=".5" stop-color="{TEAL}"/>'
        f'<stop offset="1" stop-color="{TEAL_DEEP}"/></linearGradient>'
        '<linearGradient id="bodyL" x1="0" y1="0" x2="1" y2="0">'
        '<stop offset="0" stop-color="#F3EFE6"/><stop offset=".5" stop-color="#FFFDF8"/>'
        '<stop offset="1" stop-color="#E4DED1"/></linearGradient>'
        '<linearGradient id="crimpL" x1="0" y1="0" x2="1" y2="0">'
        f'<stop offset="0" stop-color="{TEAL_DEEP}"/><stop offset=".4" stop-color="{TEAL_PALE}"/>'
        f'<stop offset="1" stop-color="{TEAL_DEEP}"/></linearGradient>'
        '</defs>'
        + _splash()
        + _vial('L', 196, 148, 1.05, '#F3EFE6', '#E4DED1', TEAL, '#12263A',
                'BPC-157', 'PEPTIDE CO')
        + '</svg>'
    )


def minify(svg):
    svg = re.sub(r">\s+<", "><", svg.strip())
    return re.sub(r"\s{2,}", " ", svg)


def data_uri(svg):
    return "data:image/svg+xml;base64," + base64.b64encode(
        minify(svg).encode("utf-8")
    ).decode("ascii")


def all_assets():
    return {
        "landing-hero.svg": hero(),
        "landing-lab.svg": lab(),
    }

# Hero slider — Slider Revolution build sheet

The Elementor template does not contain the hero. It contains a Shortcode
widget holding:

```
[rev_slider alias="peptides-hero"]
```

Build the slider below in Slider Revolution and the hero appears. If you'd
rather use Slider Revolution's own Elementor widget, delete the Shortcode
widget and drop the **Slider Revolution** widget in its place — the container
around it is already set up.

> The Elementor container behind the slider already paints the hero gradient
> (`#E7F2F9 → #EDF5FA`, 160°) and adds 60px of bottom padding so the trust bar
> overlaps it. Set the slider background to **transparent** so the two line up.

---

## Slider settings

| Setting | Value |
|---------|-------|
| Slider alias | `peptides-hero` (Slider Settings → Slider Alias) |
| Slider type | Standard / Scene |
| Layout | Full Width |
| Grid size | 1200 × 560 |
| Background | Transparent |
| Height — desktop / tablet / mobile | 560 / 500 / 660 |
| Auto-rotate | 7000ms, stop on hover |
| Navigation → Bullets | On, bottom-left, offset x `0`, y `-60` |

**Bullet styling** — active `24 × 6`, radius `3px`, `#0B1B3A`; idle `6 × 6`,
radius `50%`, `#C3D2DE`; gap `7px`. Arrows off.

Everything below is one slide. Duplicate it for slides 2 and 3 and change the
copy and product image.

---

## Layers

Positions are from the **top-left** of the 1200 × 560 grid. Font is **Inter**
throughout — add it under Globals → Fonts if it isn't there already.

| # | Layer | Type | X | Y | Style |
|---|-------|------|---|---|-------|
| 1 | `FDA Compliant` | Text | 0 | 40 | Inter 700 · 10px · +0.7 tracking · uppercase · `#1F7A63` on `#E4F1EC` · padding 6/11 · radius 5 |
| 2 | `Lab Tested` | Text | 145 | 40 | same, `#1A5C9E` on `#E4EFF7` |
| 3 | Headline | Text | 0 | 86 | Inter 700 · 46px · line-height 1.18 · tracking -0.6 · `#0B1B3A` |
| 4 | Sub-copy | Text | 0 | 212 | Inter 400 · 15px · line-height 1.75 · `#5B6B7C` |
| 5 | `Browse Catalog  →` | Button | 0 | 284 | Inter 600 · 14px · `#FFFFFF` on `#0B1B3A` · padding 14/26 · radius 8 · hover bg `#16A6A0` |
| 6 | `Research Standards` | Button | 176 | 284 | Inter 600 · 14px · `#0B1B3A` on `#FFFFFF` · 1px border `#D8E2EA` · radius 8 · hover bg `#0B1B3A`, text `#FFFFFF` |
| 7 | Product shot | Image | 620 | -20 | width 560, auto height, align top |

**Headline markup** (paste into the text layer, keep the span):

```html
High-Purity Peptides<br>for <span style="color:#16A6A0">Advanced Research</span>
```

**Sub-copy:**

```html
Pharmaceutical-grade peptides manufactured for research.<br>Verified for purity, potency, and reliability.
```

### Product shot

Use `assets/images/hero-vial.svg` — it is the vial, pedestal and molecule
lattice from the design as one file. Upload it to the Media Library first
(Slider Revolution needs a real attachment). If SVG uploads are disabled on the
site, export it to a 1120 × 940 PNG on a transparent background instead, or
drop in your own product photography at the same layer position.

---

## Animations

Keep it restrained — this is the first thing a visitor sees.

| Layers | In | Timing |
|--------|----|--------|
| 1–2 (badges) | Fade + Y `+20` | start 300ms, 600ms |
| 3 (headline) | Fade + Y `+30` | start 450ms, 800ms |
| 4 (sub-copy) | Fade + Y `+20` | start 650ms, 700ms |
| 5–6 (buttons) | Fade + Y `+20` | start 800ms, 600ms |
| 7 (product) | Fade + Scale `0.94 → 1` | start 200ms, 1000ms |

Easing `Power2.easeOut` on all of them. Set loop/out animations to none.

---

## Responsive

Slider Revolution scales layers automatically, but the two-column hero needs
help on phones:

* **Tablet (768)** — headline 36px, product shot width 420, X 560.
* **Mobile (480)** — set the product shot to `Hidden`, or move it to X `0`,
  Y `330` and centre the text layers. Headline 29px, buttons full width and
  stacked (button 2 at Y `+62`).

---

## Checklist

- [ ] Slider alias is exactly `peptides-hero`
- [ ] Slider background is transparent
- [ ] Inter is loaded in Globals → Fonts
- [ ] Buttons link to the shop and the research/standards page
- [ ] Product image has alt text
- [ ] Checked at 1440, 1024, 768 and 390 wide

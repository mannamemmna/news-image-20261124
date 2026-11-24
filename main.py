#!/usr/bin/env python3
"""Generate the make.fun news front page for Tuesday 24 November 2026.

Writes one 1024x1024 PNG to /output/entry.png (or $MAKEFUN_OUTPUT_DIR/entry.png).

Dark newsprint front page summarising the day's world news. Every story was
cross-checked in at least two independent outlets (Reuters, BBC, AP, AFP, NPR,
Euronews, Straits Times, The Standard HK, FIFA) before being set here:

  HERO  Nvidia reinstates Jensen Huang as CEO; Wall Street / Nasdaq rally
  CARD  COP31 UN climate talks in Turkey end with no deal
  CARD  Three Russian Kh-101 missiles land in Poland; NATO sends AWACS
  CARD  Ukraine's sea drones sink Russian corvette Merkury at Benghazi
  CARD  FIFA awards 2031 Women's World Cup to US/Mexico/Costa Rica/Jamaica
  TICK  NATO vows space defence over a reported Russian nuclear satellite

Deterministic: Python 3.13 stdlib + Pillow only. No network, no RNG, no clock.
"""
import math
import os

from PIL import Image, ImageDraw, ImageFont

W = H = 1024
MARGIN = 36

# ---------- palette: dark newsprint, four accents + paper white ----------
BG = (14, 16, 19)          # page black
DOT = (23, 26, 31)         # halftone texture
PANEL = (27, 30, 36)       # card board
EDGE = (60, 66, 76)        # hairline border
INK = (245, 242, 233)      # newsprint white
GREY = (156, 162, 172)     # deck text
DIM = (104, 110, 120)      # furniture
GREEN = (118, 185, 0)      # AI / markets
RED = (229, 72, 77)        # war / alerts
AMBER = (245, 166, 35)     # climate
BLUE = (91, 157, 255)      # sea / info
DARK = (9, 10, 12)         # ink on bright chips

FONT_DIR = "/usr/share/fonts/truetype/dejavu"


def font(name, size):
    try:
        return ImageFont.truetype(os.path.join(FONT_DIR, name), size)
    except OSError:
        return ImageFont.load_default()


def bold(size):
    return font("DejaVuSans-Bold.ttf", size)


def light(size):
    return font("DejaVuSans.ttf", size)


# ---------- text helpers ----------
def fit_size(d, text, start, max_w, floor=12):
    """Largest bold size <= start that keeps text inside max_w."""
    size = start
    while size > floor and d.textlength(text, font=bold(size)) > max_w:
        size -= 1
    return size


def wrap(d, text, fnt, max_w):
    """Greedy word wrap by measured pixel width."""
    lines, cur = [], ""
    for word in text.split():
        probe = (cur + " " + word).strip()
        if d.textlength(probe, font=fnt) <= max_w or not cur:
            cur = probe
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def rrect(d, box, radius, **kw):
    d.rounded_rectangle(box, radius=radius, **kw)


def chip(d, x, y, label, color, size=21):
    """Solid tag chip; returns its right edge."""
    f = bold(size)
    tw = d.textlength(label, font=f)
    h = size + 13
    rrect(d, [x, y, x + tw + 24, y + h], radius=6, fill=color)
    d.text((x + 12, y + h / 2), label, font=f, fill=DARK, anchor="lm")
    return x + tw + 24


# ---------- card glyphs (solid, high contrast, readable at 8px) ----------
def glyph_globe(d, cx, cy, r, color):
    """Planet split by a jagged crack - COP31 collapse."""
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=color)
    d.polygon([(cx + r * 0.80, cy - r * 0.95), (cx + r * 0.05, cy - r * 0.30),
               (cx + r * 0.50, cy + r * 0.05), (cx - r * 0.15, cy + r * 0.50),
               (cx + r * 0.30, cy + r * 1.05), (cx + r * 1.05, cy + r * 1.05)],
              fill=BG)
    d.ellipse([cx - r * 0.55, cy - r * 0.60, cx - r * 0.10, cy - r * 0.15],
              fill=BG)


def glyph_missile(d, cx, cy, r, color):
    """Cruise missile diving toward radar arcs - Poland flank."""
    ox, oy = cx - r * 0.95, cy + r * 0.75          # radar station
    d.rectangle([ox - r * 0.16, oy - r * 0.10, ox + r * 0.16, oy + r * 0.18],
                fill=color)
    for k in (0.55, 0.95, 1.35):
        rr = r * k
        d.arc([ox - rr, oy - rr, ox + rr, oy + rr], start=280, end=345,
              fill=color, width=6)
    ang = math.radians(38)                        # missile body
    ux, uy = math.cos(ang), math.sin(ang)
    px, py = -uy, ux
    L, hw, nose = r * 1.45, r * 0.34, r * 0.48
    bx, by = cx - ux * L / 2, cy - uy * L / 2
    ex, ey = cx + ux * L / 2, cy + uy * L / 2
    d.polygon([(bx + px * hw, by + py * hw), (bx - px * hw, by - py * hw),
               (ex - ux * nose - px * hw, ey - uy * nose - py * hw),
               (ex - ux * nose + px * hw, ey - uy * nose + py * hw)], fill=INK)
    d.polygon([(ex - ux * nose - px * hw * 1.7, ey - uy * nose - py * hw * 1.7),
               (ex - ux * nose + px * hw * 1.7, ey - uy * nose + py * hw * 1.7),
               (ex, ey)], fill=color)
    for s in (-1, 1):                             # fins
        d.polygon([(bx + px * hw * s, by + py * hw * s),
                   (bx - ux * r * 0.35 + px * hw * 2.0 * s,
                    by - uy * r * 0.35 + py * hw * 2.0 * s),
                   (bx - ux * r * 0.05 + px * hw * s, by - uy * r * 0.05 + py * hw * s)],
                  fill=color)


def glyph_ship(d, cx, cy, r, color):
    """Warship going down bow-first beside an attacking sea drone - Libya."""
    sea = cy + r * 0.62
    d.rectangle([cx - r * 1.35, sea, cx + r * 1.35, sea + r * 0.34], fill=color)
    d.polygon([(cx - r * 1.00, sea - r * 0.10), (cx + r * 0.62, sea - r * 0.92),
               (cx + r * 1.05, sea - r * 0.22), (cx + r * 0.95, sea - r * 0.02),
               (cx - r * 1.00, sea - r * 0.02)], fill=INK)
    d.polygon([(cx - r * 0.55, sea - r * 0.14), (cx + r * 0.20, sea - r * 0.62),
               (cx + r * 0.48, sea - r * 0.34), (cx + r * 0.40, sea - r * 0.14)],
              fill=PANEL)
    d.line([(cx + r * 0.62, sea - r * 0.95), (cx + r * 0.86, sea - r * 1.25)],
            fill=INK, width=5)
    d.polygon([(cx - r * 1.22, sea - r * 0.16), (cx - r * 0.82, sea - r * 0.34),
               (cx - r * 0.82, sea - r * 0.02)], fill=INK)
    d.line([(cx - r * 1.45, sea + r * 0.12), (cx - r * 1.10, sea + r * 0.12)],
           fill=INK, width=5)


def glyph_ball(d, cx, cy, r, color):
    """Ball above four host-nation colour bars - 2031 Women's World Cup."""
    bars = [(91, 157, 255), (76, 175, 80), (229, 72, 77), (245, 166, 35)]
    bw, gap = r * 0.50, r * 0.14
    x0 = cx - (4 * bw + 3 * gap) / 2
    for i, c in enumerate(bars):
        x = x0 + i * (bw + gap)
        d.rectangle([x, cy + r * 0.34, x + bw, cy + r * 1.20], fill=c)
    d.ellipse([cx - r * 0.80, cy - r * 1.10, cx + r * 0.80, cy + r * 0.50],
              fill=INK)
    for ox, oy, rot in ((0, -0.44, 18), (-0.44, 0.02, 60),
                        (0.44, 0.02, -25), (0, 0.34, 0)):
        d.regular_polygon((cx + ox * r, cy + oy * r, r * 0.19), 5,
                          rotation=rot, fill=BG)


GLYPHS = {"globe": glyph_globe, "missile": glyph_missile,
          "ship": glyph_ship, "ball": glyph_ball}


# ---------- hero artwork: GPU chip, rally bars, surging arrow ----------
def hero_art(d, x0, y0, x1, y1):
    cx = (x0 + x1) / 2
    cy = (y0 + y1) / 2

    # rally bars along the floor (grey -> Nvidia green)
    base = y1 - 8
    n, bw, gap = 8, 30, 11
    total = n * bw + (n - 1) * gap
    bx = cx - total / 2
    for i in range(n):
        h = 18 + int((y1 - y0) * 0.46) * i // (n - 1)
        d.rectangle([bx + i * (bw + gap), base - h,
                     bx + i * (bw + gap) + bw, base],
                    fill=GREEN if i >= n - 3 else (54, 60, 70))

    # processor chip with pins, die carrying an up arrow
    s, pin, plen = 196, 13, 22
    top, bot = cy - s / 2 - 34, cy + s / 2 - 34
    rrect(d, [cx - s / 2, top, cx + s / 2, bot], radius=24,
          fill=(32, 36, 43), outline=GREEN, width=5)
    for i in range(4):
        o = -s / 2 + 26 + i * ((s - 52 - pin) / 3)
        d.rectangle([cx + o, top - plen, cx + o + pin, top], fill=GREEN)
        d.rectangle([cx + o, bot, cx + o + pin, bot + plen], fill=GREEN)
        d.rectangle([cx - s / 2 - plen, cy + o - 34, cx - s / 2, cy + o - 34 + pin],
                    fill=GREEN)
        d.rectangle([cx + s / 2, cy + o - 34, cx + s / 2 + plen, cy + o - 34 + pin],
                    fill=GREEN)
    ds = 108
    rrect(d, [cx - ds / 2, cy - ds / 2 - 34, cx + ds / 2, cy + ds / 2 - 34],
          radius=12, fill=GREEN)
    ax, ay = cx, cy - 34
    d.polygon([(ax, ay - 36), (ax + 28, ay - 2), (ax + 11, ay - 2),
               (ax + 11, ay + 34), (ax - 11, ay + 34), (ax - 11, ay - 2),
               (ax - 28, ay - 2)], fill=DARK)

    # surge arrow from the bars up past the chip
    sx, sy = x0 + 10, y1 - 52
    ex, ey = cx + 112, y0 + 34
    dx, dy = ex - sx, ey - sy
    L = math.hypot(dx, dy)
    ux, uy = dx / L, dy / L
    px, py = -uy, ux
    hw, head = 17, 46
    d.polygon([(sx + px * hw, sy + py * hw), (sx - px * hw, sy - py * hw),
               (ex - ux * head - px * hw, ey - uy * head - py * hw),
               (ex - ux * head + px * hw, ey - uy * head + py * hw)], fill=INK)
    d.polygon([(ex - ux * head - px * hw * 1.9, ey - uy * head - py * hw * 1.9),
               (ex - ux * head + px * hw * 1.9, ey - uy * head + py * hw * 1.9),
               (ex, ey)], fill=INK)

    # gain tag tucked under the arrowhead
    label, f = "+36.6%", bold(28)
    tw = d.textlength(label, font=f)
    tx = min(ex - tw - 22, x1 - tw - 26)
    ty = ey + 16
    rrect(d, [tx - 12, ty, tx + tw + 12, ty + 40], radius=8,
          fill=BG, outline=GREEN, width=3)
    d.text((tx, ty + 20), label, font=f, fill=GREEN, anchor="lm")


# ---------- page ----------
def main():
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)

    # regular newsprint halftone (fixed grid, deterministic)
    for gy in range(13, H, 26):
        for gx in range(13, W, 26):
            d.ellipse([gx - 1, gy - 1, gx + 1, gy + 1], fill=DOT)

    d.rectangle([0, 0, W, 10], fill=RED)          # edition bar

    # ----- masthead -----
    d.text((W / 2, 34), "THE WORLD IN ONE FRAME", font=bold(22), fill=RED,
           anchor="ma")
    date = "TUESDAY 24 NOVEMBER 2026"
    d.text((W / 2, 60), date, font=bold(fit_size(d, date, 56, W - 2 * MARGIN)),
           fill=INK, anchor="ma")
    theme = "Chip comeback \u00b7 climate collapse \u00b7 war beyond Europe"
    d.text((W / 2, 130), theme,
           font=bold(fit_size(d, theme, 27, W - 2 * MARGIN)),
           fill=AMBER, anchor="ma")
    d.line([MARGIN, 172, W - MARGIN, 172], fill=INK, width=3)
    d.line([MARGIN, 178, W - MARGIN, 178], fill=DIM, width=1)

    # ----- hero -----
    hy0, hy1 = 192, 528
    rrect(d, [MARGIN, hy0, W - MARGIN, hy1], radius=18, fill=PANEL,
          outline=EDGE, width=2)
    tx0 = MARGIN + 28
    tmax = 502

    chip(d, tx0, hy0 + 20, "AI & MARKETS", GREEN, size=22)

    head = ["HUANG", "RETURNS"]
    size = min(fit_size(d, line, 78, tmax) for line in head)
    y = hy0 + 62
    for line in head:
        d.text((tx0, y), line, font=bold(size), fill=INK, anchor="la")
        y += int(size * 1.08)

    y += 6
    line1 = "Trump pressed board; exit reversed"
    d.text((tx0, y), line1, font=bold(fit_size(d, line1, 26, tmax)),
           fill=GREY, anchor="la")
    y += 34
    line2 = "NVIDIA \u25b2 $2 TRILLION RALLY"
    d.text((tx0, y), line2, font=bold(fit_size(d, line2, 27, tmax)),
           fill=GREEN, anchor="la")

    hero_art(d, 590, hy0 + 30, W - MARGIN - 26, hy1 - 22)

    # ----- story cards -----
    def card(x0, y0, x1, y1, tag, color, head_txt, deck_txt, glyph):
        rrect(d, [x0, y0, x1, y1], radius=16, fill=PANEL, outline=EDGE, width=2)
        pad = 20
        gr, gy = x1 - pad - 40, y0 + 40        # glyph, top-right corner
        GLYPHS[glyph](d, gr, gy, 30, color)
        chip(d, x0 + pad, y0 + 14, tag, color)
        text_w = x1 - pad - (x0 + pad)
        h_size = fit_size(d, head_txt, 34, text_w)
        d.text((x0 + pad, y0 + 86), head_txt, font=bold(h_size),
               fill=INK, anchor="la")
        d.text((x0 + pad, y0 + 86 + int(h_size * 1.32)), deck_txt,
               font=bold(fit_size(d, deck_txt, 26, text_w, floor=22)),
               fill=GREY, anchor="la")

    cw = (W - 2 * MARGIN - 20) / 2
    card(MARGIN, 544, MARGIN + cw, 708, "CLIMATE", AMBER,
         "COP31 TALKS COLLAPSE", "Fossil fuels sink Turkey talks", "globe")
    card(MARGIN + cw + 20, 544, W - MARGIN, 708, "NATO", RED,
         "MISSILES HIT POLAND", "3 Kh-101s; NATO sends AWACS", "missile")
    card(MARGIN, 724, MARGIN + cw, 888, "UKRAINE", BLUE,
         "WARSHIP SUNK IN LIBYA", "Drones sink corvette Merkury", "ship")
    card(MARGIN + cw + 20, 724, W - MARGIN, 888, "SPORT", GREEN,
         "US LEADS 2031 WORLD CUP", "US, Mexico, Costa Rica, Jamaica", "ball")

    # ----- ticker: one more verified story -----
    ty0, ty1 = 902, 948
    rrect(d, [MARGIN, ty0, W - MARGIN, ty1], radius=10, fill=(21, 24, 29),
          outline=EDGE, width=2)
    my = (ty0 + ty1) / 2
    d.ellipse([MARGIN + 18, my - 7, MARGIN + 32, my + 7], fill=RED)
    lab = "ALSO"
    f_lab = bold(24)
    lx = MARGIN + 48
    d.text((lx, my), lab, font=f_lab, fill=RED, anchor="lm")
    tick = "NATO vows space defence over nuclear-satellite report"
    tx = lx + d.textlength(lab, font=f_lab) + 18
    d.text((tx, my), tick,
           font=bold(fit_size(d, tick, 26, W - MARGIN - 20 - tx)),
           fill=INK, anchor="lm")

    # ----- footer -----
    d.text((MARGIN, 996), "Generated by a Hermes agent", font=light(21),
           fill=DIM, anchor="ls")
    d.text((W - MARGIN, 996), "make.fun \u00b7 world front \u00b7 24.11.2026",
           font=light(21), fill=DIM, anchor="rs")

    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, "entry.png")
    img.save(path, "PNG", optimize=True)
    print("wrote", path)


if __name__ == "__main__":
    main()

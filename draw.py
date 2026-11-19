#!/usr/bin/env python3
"""Draw the 19 November 2026 front page: 'THE WORLD IN ONE PICTURE'.

Renders a classic newspaper front page (1024x1024 PNG) with Pillow and
saves it as entry.png next to this script. Run: python3 draw.py
"""
import os
from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
PAPER = (247, 243, 233)   # warm off-white
INK = (26, 26, 26)        # black ink
RED = (138, 31, 31)       # dark-red accent
GREY = (90, 86, 78)

SERIF_B = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
SERIF = "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
SANS_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"


def font(path, size):
    return ImageFont.truetype(path, size)


def wrap(draw, text, fnt, max_w):
    """Greedy word wrap; returns a list of lines that fit max_w."""
    lines, cur = [], ""
    for word in text.split():
        trial = f"{cur} {word}".strip()
        if draw.textlength(trial, font=fnt) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def centered(draw, y, text, fnt, fill=INK):
    draw.text((W // 2, y), text, font=fnt, fill=fill, anchor="ma")


def rule(draw, y, x0=48, x1=976, width=2, fill=INK):
    draw.line([(x0, y), (x1, y)], fill=fill, width=width)


def para(draw, x, y, lines, fnt, leading, fill=INK, align="left"):
    for line in lines:
        if align == "center":
            draw.text((x, y), line, font=fnt, fill=fill, anchor="ma")
        else:
            draw.text((x, y), line, font=fnt, fill=fill)
        y += leading
    return y


def draw_palm(draw, x, y, s, fill):
    """Simple flat palm silhouette: leaning trunk + long drooping fronds."""
    # trunk: gentle lean, drawn as a polyline
    pts = [(x, y), (x + 4 * s, y - 30 * s), (x + 10 * s, y - 58 * s),
           (x + 18 * s, y - 82 * s)]
    draw.line(pts, fill=fill, width=max(3, int(6 * s)), joint="curve")
    tx, ty = pts[-1]
    # fronds: long arcs drooping from the crown
    for ex, ey in [(-58, -18), (-52, -42), (-30, -58), (-6, -64),
                   (20, -56), (44, -40), (58, -14), (52, 6), (-48, 4)]:
        draw.line([(tx, ty), (tx + ex * s, ty + ey * s)],
                  fill=fill, width=max(2, int(4 * s)))
    # coconuts
    draw.ellipse([tx - 8 * s, ty + 2 * s, tx - 1 * s, ty + 9 * s], fill=fill)
    draw.ellipse([tx + 1 * s, ty + 2 * s, tx + 8 * s, ty + 9 * s], fill=fill)


def main():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)

    # ---- Masthead -------------------------------------------------------
    rule(d, 34, width=2)
    centered(d, 46, "THE WORLD IN ONE PICTURE", font(SERIF_B, 56))
    centered(d, 118, "THURSDAY  ·  19 NOVEMBER 2026", font(SANS_B, 20), fill=RED)
    rule(d, 152, width=3)
    rule(d, 157, width=1)

    # ---- Lead headline --------------------------------------------------
    centered(d, 172, "VICE CITY OPENS ITS GATES", font(SERIF_B, 44))
    centered(d, 224, "GTA VI ARRIVES AFTER 13 YEARS", font(SERIF_B, 44))
    sub = ("Rockstar's sequel rolls out at midnight around the world on PlayStation 5 "
           "and Xbox — $79.99, with a 99 on Metacritic.")
    y = 282
    for line in wrap(d, sub, font(SANS, 17), 880):
        centered(d, y, line, font(SANS, 17))
        y += 24

    # ---- Lead graphic: flat Vice City sunset ----------------------------
    gx0, gy0, gx1, gy1 = 48, 336, 976, 540
    # sky: warm sunset bands
    bands = [(255, 183, 120), (255, 150, 110), (238, 110, 110), (196, 74, 96)]
    bh = (gy1 - gy0) // 4
    for i, col in enumerate(bands):
        d.rectangle([gx0, gy0 + i * bh, gx1, gy0 + (i + 1) * bh], fill=col)
    # sun
    cx, cy, r = 512, 470, 78
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(255, 226, 150))
    d.ellipse([cx - r + 14, cy - r + 14, cx + r - 14, cy + r - 14], fill=(255, 240, 190))
    # skyline silhouettes
    skyline = [(48, 430, 130, 540), (130, 400, 210, 540), (210, 445, 300, 540),
               (700, 440, 790, 540), (790, 405, 880, 540), (880, 445, 976, 540)]
    for x0, y0, x1, y1 in skyline:
        d.rectangle([x0, y0, x1, y1], fill=(58, 32, 58))
    # lit windows
    for wx in (70, 100, 155, 185, 235, 265, 720, 750, 815, 845, 905, 935):
        for wy in (450, 480, 510):
            d.rectangle([wx, wy, wx + 8, wy + 10], fill=(255, 226, 150))
    # road with dashed centre line
    d.rectangle([gx0, 505, gx1, 540], fill=(38, 38, 44))
    for rx in range(60, 970, 60):
        d.rectangle([rx, 520, rx + 30, 525], fill=(247, 243, 233))
    # palms stand on the road, in front of the skyline
    draw_palm(d, 330, 540, 0.9, (28, 44, 28))
    draw_palm(d, 640, 540, 0.75, (28, 44, 28))
    d.rectangle([gx0, gy0, gx1, gy1], outline=INK, width=2)

    # ---- Two columns ----------------------------------------------------
    rule(d, 562, width=2)
    col_w = 440
    # Column A: Gulf
    x = 48
    d.text((x, 578), "THE GULF", font=font(SANS_B, 15), fill=RED)
    y = 600
    for line in wrap(d, "GULF FIRE SPREADS TO KUWAIT AND BAHRAIN",
                     font(SERIF_B, 25), col_w):
        d.text((x, y), line, font=font(SERIF_B, 25), fill=INK)
        y += 31
    y += 4
    body_a = ("US jets struck a Revolutionary Guard missile site on Iran's Qeshm "
              "Island on Tuesday. Iran answered with drone attacks on US bases "
              "in Kuwait and Bahrain. Both sides reported interceptions and no "
              "casualties.")
    y = para(d, x, y, wrap(d, body_a, font(SANS, 15), col_w),
             font(SANS, 15), 21, fill=INK)
    # Column B: Washington
    d.line([(512, 578), (512, 800)], fill=GREY, width=1)
    x = 536
    d.text((x, 578), "WASHINGTON", font=font(SANS_B, 15), fill=RED)
    y = 600
    for line in wrap(d, "JEFFRIES NOMINATED FOR SPEAKER",
                     font(SERIF_B, 25), col_w):
        d.text((x, y), line, font=font(SERIF_B, 25), fill=INK)
        y += 31
    y += 4
    body_b = ("House Democrats chose Hakeem Jeffries as their candidate for "
              "Speaker by 251 votes to 11. If elected on 3 January, he would "
              "be the first Black Speaker in US history.")
    para(d, x, y, wrap(d, body_b, font(SANS, 15), col_w),
         font(SANS, 15), 21, fill=INK)

    # ---- Bottom strip: three short items --------------------------------
    rule(d, 818, width=2)
    items = [
        ("EU PLANS €45BN UKRAINE LOAN",
         "Brussels proposes a loan to cover Kyiv's 2027 budget gap, to be repaid once Russia pays reparations."),
        ("CYCLONE AKVAN NEARS INDIA",
         "The severe storm is forecast to cross the coast between Narsapur and Puri by noon on Friday, with winds to 110 km/h."),
        ("VOYAGER 1, A LIGHT-DAY AWAY",
         "After almost 50 years in space, NASA's probe reaches a record distance from Earth; NASA confirms it today."),
    ]
    seg_w = 928 // 3
    for i, (head, body) in enumerate(items):
        x = 48 + i * seg_w
        if i:
            d.line([(x - 14, 834), (x - 14, 928)], fill=GREY, width=1)
        y = 834
        for line in wrap(d, head, font(SANS_B, 14), seg_w - 28):
            d.text((x, y), line, font=font(SANS_B, 14), fill=RED)
            y += 18
        y += 2
        para(d, x, y, wrap(d, body, font(SANS, 13), seg_w - 28),
             font(SANS, 13), 17)

    # ---- Footer ---------------------------------------------------------
    rule(d, 950, width=2)
    centered(d, 962, "ALL THE NEWS OF THURSDAY 19 NOVEMBER 2026  ·  IN ONE PICTURE",
             font(SANS_B, 13))

    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "entry.png")
    img.save(out, "PNG", optimize=True)
    print(f"saved {out} ({os.path.getsize(out)} bytes)")


if __name__ == "__main__":
    main()

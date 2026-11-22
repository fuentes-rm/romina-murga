#!/usr/bin/env python3
"""Generate the default 1200x630 Open Graph preview card (images/og-image.png).

Adapted from upstream AcademicPages scripts/make-og-image.py and customized for
Romina F. Murga's academic portfolio (https://murga-romina.github.io).

Usage:
    python3 scripts/make-og-image.py
"""
import math
import os
from PIL import Image, ImageDraw, ImageFont

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

W, H = 1200, 630
BG = (255, 255, 255)          # clean white background
NAVY = (24, 54, 96)           # deep academic navy accent
BLUE = (42, 98, 178)          # primary accent blue
DARK = (34, 41, 47)           # primary text
GREY = (92, 104, 115)         # secondary text
LIGHTBLUE = (236, 243, 252)   # pill background
BORDER = (222, 230, 240)      # subtle divider/border

FONT_DIR = os.environ.get("FONT_DIR", "/usr/share/fonts/truetype/dejavu")


def font(size, bold=False, serif=False):
    if serif:
        name = "DejaVuSerif-Bold.ttf" if bold else "DejaVuSerif.ttf"
    else:
        name = "DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf"
    p = os.path.join(FONT_DIR, name)
    if not os.path.exists(p):
        fallback_name = (
            ("LiberationSerif-Bold.ttf" if bold else "LiberationSerif-Regular.ttf")
            if serif
            else ("LiberationSans-Bold.ttf" if bold else "LiberationSans-Regular.ttf")
        )
        p = os.path.join("/usr/share/fonts/truetype/liberation", fallback_name)
    return ImageFont.truetype(p, size)


def paste_circular_avatar(base_img, avatar_path, box_xy, diameter):
    avatar = Image.open(avatar_path).convert("RGB")
    w, h = avatar.size
    side = min(w, h)
    left = (w - side) // 2
    top = 0 if h > w else (h - side) // 2
    avatar = avatar.crop((left, top, left + side, top + side))
    avatar = avatar.resize((diameter, diameter), Image.Resampling.LANCZOS)

    mask = Image.new("L", (diameter, diameter), 0)
    mask_draw = ImageDraw.Draw(mask)
    mask_draw.ellipse((0, 0, diameter - 1, diameter - 1), fill=255)

    ring_pad = 6
    ring_diam = diameter + ring_pad * 2
    draw = ImageDraw.Draw(base_img)
    rx, ry = box_xy[0] - ring_pad, box_xy[1] - ring_pad
    draw.ellipse((rx, ry, rx + ring_diam, ry + ring_diam), fill=(255, 255, 255), outline=BORDER, width=3)
    base_img.paste(avatar, box_xy, mask)


def draw_monogram_avatar(base_img, box_xy, diameter):
    """Render a supersampled circular 'RM' monogram matching images/profile.svg."""
    scale = 2
    size = diameter * scale
    tile = Image.new("RGBA", (size, size), (0, 0, 0, 0))

    # Diagonal navy-to-teal gradient matching profile.svg (#1e3a5f -> #2b547e -> #1b4353)
    c0 = (30, 58, 95)
    c1 = (43, 84, 126)
    c2 = (27, 67, 83)
    px = tile.load()
    denom = max(1, (size - 1) * 2)
    for y in range(size):
        for x in range(size):
            t = (x + y) / denom
            if t < 0.55:
                u = t / 0.55
                r = int(c0[0] + (c1[0] - c0[0]) * u)
                g = int(c0[1] + (c1[1] - c0[1]) * u)
                b = int(c0[2] + (c1[2] - c0[2]) * u)
            else:
                u = (t - 0.55) / 0.45
                r = int(c1[0] + (c2[0] - c1[0]) * u)
                g = int(c1[1] + (c2[1] - c1[1]) * u)
                b = int(c1[2] + (c2[2] - c1[2]) * u)
            px[x, y] = (r, g, b, 255)

    td = ImageDraw.Draw(tile)
    cx = cy = size // 2

    # Subtle orbital / nanoparticle ring motif
    r_outer = int(size * 0.39)
    r_inner = int(size * 0.35)
    td.ellipse((cx - r_outer, cy - r_outer, cx + r_outer, cy + r_outer), outline=(255, 255, 255, 42), width=3)
    td.ellipse((cx - r_inner, cy - r_inner, cx + r_inner, cy + r_inner), outline=(255, 255, 255, 24), width=2)

    for deg, rad_frac, dot_r, alpha in [(318, 0.39, 6, 125), (142, 0.39, 5, 100), (28, 0.35, 4, 90)]:
        ang = math.radians(deg)
        dx = int(cx + size * rad_frac * math.cos(ang))
        dy = int(cy + size * rad_frac * math.sin(ang))
        td.ellipse((dx - dot_r, dy - dot_r, dx + dot_r, dy + dot_r), fill=(144, 205, 244, alpha))

    # Centered serif monogram "RM"
    f_mono = font(int(size * 0.31), bold=True, serif=True)
    bbox = td.textbbox((0, 0), "RM", font=f_mono)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    tx = (size - tw) // 2 - bbox[0]
    ty = (size - th) // 2 - bbox[1]
    td.text((tx, ty), "RM", font=f_mono, fill=(255, 255, 255, 255))

    avatar = tile.resize((diameter, diameter), Image.Resampling.LANCZOS).convert("RGB")

    mask = Image.new("L", (diameter, diameter), 0)
    ImageDraw.Draw(mask).ellipse((0, 0, diameter - 1, diameter - 1), fill=255)

    ring_pad = 6
    ring_diam = diameter + ring_pad * 2
    draw = ImageDraw.Draw(base_img)
    rx, ry = box_xy[0] - ring_pad, box_xy[1] - ring_pad
    draw.ellipse((rx, ry, rx + ring_diam, ry + ring_diam), fill=(255, 255, 255), outline=BORDER, width=3)
    base_img.paste(avatar, box_xy, mask)


def main():
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)

    # Top accent bar
    d.rectangle([0, 0, W, 12], fill=NAVY)

    f_title = font(56, bold=True)
    f_role = font(30, bold=True)
    f_sub = font(27)
    f_pill = font(24, bold=True)
    f_domain = font(26, bold=True)

    # Circular profile photo (top-right) if available, otherwise custom RM monogram emblem
    profile_jpg = os.path.join(REPO_ROOT, "images", "profile.jpg")
    profile_png = os.path.join(REPO_ROOT, "images", "profile.png")
    if os.path.exists(profile_jpg):
        paste_circular_avatar(img, profile_jpg, (W - 220 - 70, 56), 220)
    elif os.path.exists(profile_png):
        paste_circular_avatar(img, profile_png, (W - 220 - 70, 56), 220)
    else:
        draw_monogram_avatar(img, (W - 220 - 70, 56), 220)

    # Name, affiliation, and research summary
    d.text((70, 62), "Romina F. Murga", font=f_title, fill=DARK)
    d.text((70, 142), "Ph.D. Candidate · University of Talca", font=f_role, fill=BLUE)
    d.text((70, 206), "Polymeric & Biodegradable Nanoparticles", font=f_sub, fill=GREY)
    d.text((70, 248), "for Mineral Processing and Froth Flotation", font=f_sub, fill=GREY)

    # Divider
    d.line([70, 344, W - 70, 344], fill=BORDER, width=2)

    # Topic / section pills
    pills = ["Publications", "Mineral Processing", "Nanomaterials", "Teaching", "People", "CV"]
    x = 70
    y = 380
    for label in pills:
        fw = int(d.textlength(label, font=f_pill)) + 44
        if x + fw > W - 70:
            x = 70
            y += 68
        d.rounded_rectangle([x, y, x + fw, y + 54], radius=27, fill=LIGHTBLUE, outline=BORDER, width=1)
        d.text((x + 22, y + 12), label, font=f_pill, fill=NAVY)
        x += fw + 16

    # Footer domain badge
    domain = "murga-romina.github.io"
    dw = int(d.textlength(domain, font=f_domain)) + 64
    d.rounded_rectangle([70, H - 92, 70 + dw, H - 40], radius=26, fill=NAVY)
    d.text((102, H - 82), domain, font=f_domain, fill=(255, 255, 255))

    out = os.path.join(REPO_ROOT, "images", "og-image.png")
    img.save(out, "PNG", optimize=True)
    print("wrote", os.path.normpath(out), img.size)


if __name__ == "__main__":
    main()

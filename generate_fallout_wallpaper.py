#!/usr/bin/env python3
# ============================================================================
# FILE:    generate_fallout_wallpaper.py
# TASK:    Procedurally render the Fallout theme's hero wallpaper(s) — a
#          wasteland dusk skyline with a power-armor silhouette standing on
#          a ridge, backlit by a hazy amber sun. No image-generation tool is
#          available in this environment, so everything is drawn with PIL
#          primitives (gradients, blurred glow layers, polygons for the
#          skyline/ridge/armor, procedural grain + vignette).
# STATUS:  IN PROGRESS
# OWNER:   agent A 2026-09-09
#
# WHAT THIS FILE DOES:
#   render(variant, out_path) builds one 3840x2160 wallpaper. `variant`
#   selects a palette preset (currently "dusk"; "duststorm" planned as a
#   second background so the standard Omarchy background-picker has more
#   than one option, same as every stock theme). Layers, back to front:
#   sky gradient -> sun glow (blurred bloom) -> distant ruined skyline ->
#   mid-ground ridge -> power armor silhouette (rim-lit) + cast shadow ->
#   cracked-earth foreground -> grain -> vignette.
#
# NEXT STEP (if not DONE):
#   Render, then Read the PNG (multimodal) to visually check the power
#   armor silhouette reads clearly and the composition is balanced before
#   calling this DONE. Iterate proportions in draw_power_armor() if not.
# ============================================================================
import math
import random
from PIL import Image, ImageDraw, ImageFilter

W, H = 3840, 2160

def hex2rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))

def lerp(a, b, t):
    return a + (b - a) * t

def lerp_color(c1, c2, t):
    return tuple(int(lerp(c1[i], c2[i], t)) for i in range(3))


def vertical_gradient(size, stops):
    """stops: list of (t, rgb) from t=0 (top) to t=1 (bottom)."""
    w, h = size
    img = Image.new("RGB", size)
    draw = ImageDraw.Draw(img)
    for y in range(h):
        t = y / (h - 1)
        # find bracketing stops
        for i in range(len(stops) - 1):
            t0, c0 = stops[i]
            t1, c1 = stops[i + 1]
            if t0 <= t <= t1 or i == len(stops) - 2:
                local_t = 0 if t1 == t0 else (t - t0) / (t1 - t0)
                local_t = max(0.0, min(1.0, local_t))
                color = lerp_color(c0, c1, local_t)
                break
        draw.line([(0, y), (w, y)], fill=color)
    return img


def radial_glow(size, color, falloff_px):
    """A soft circular glow: bright disc, heavily blurred."""
    pad = falloff_px * 2
    glow = Image.new("L", (size + pad * 2, size + pad * 2), 0)
    gd = ImageDraw.Draw(glow)
    gd.ellipse([pad, pad, pad + size, pad + size], fill=255)
    glow = glow.filter(ImageFilter.GaussianBlur(falloff_px))
    colored = Image.new("RGB", glow.size, color)
    return colored, glow


def rrect(draw, box, radius, fill):
    draw.rounded_rectangle(box, radius=radius, fill=fill)


def draw_power_armor(draw, cx, ground_y, hgt, fill, rim, rim_w):
    """T-51-style power armor silhouette. cx = horizontal center, ground_y =
    y coordinate the boots stand on, hgt = full head-to-foot height."""
    H_ = hgt

    def yy(frac):  # frac: 0 = top of head, 1 = feet
        return ground_y - H_ + H_ * frac

    def xx(frac_w):  # frac_w: fraction of hgt, signed, relative to cx
        return cx + H_ * frac_w

    parts = []  # (kind, geom, fill) drawn back-to-front for this figure

    # --- fusion-core backpack (peeks up behind shoulders) ---
    bp_w = 0.20 * H_
    bp_top = yy(0.10)
    bp_bot = yy(0.42)
    parts.append(("rrect", (xx(-bp_w/2/H_) , bp_top, xx(bp_w/2/H_), bp_bot), 0.10*H_))

    # --- legs (drawn before torso so hips overlap them) ---
    leg_w = 0.16 * H_
    for side in (-1, 1):
        lx = cx + side * 0.14 * H_
        # thigh
        rrect(draw, (lx - leg_w/2, yy(0.58), lx + leg_w/2, yy(0.80)), 0.05*H_, fill)
        # shin
        rrect(draw, (lx - leg_w*0.42, yy(0.78), lx + leg_w*0.42, yy(0.97)), 0.04*H_, fill)
        # boot: a sole block plus a toe wedge pointing outward (away from
        # center) — kept as two convex shapes instead of one polygon so the
        # outward toe extension can never fold back and self-intersect.
        heel_x = lx - side * leg_w * 0.6   # inward edge
        toe_x = lx + side * leg_w * 0.6    # outward edge
        rrect(draw, (min(heel_x, toe_x), yy(0.94), max(heel_x, toe_x), yy(1.0)), 0.02*H_, fill)
        toe_tip = toe_x + side * leg_w * 0.55
        draw.polygon([
            (toe_x, yy(0.94)),
            (toe_tip, yy(0.965)),
            (toe_x, yy(1.0)),
        ], fill=fill)
        # knee joint disc
        draw.ellipse((lx - leg_w*0.45, yy(0.775), lx + leg_w*0.45, yy(0.83)), fill=fill)

    # backpack fill drawn again on top so legs behind it don't show through center
    rrect(draw, (xx(-bp_w/2/H_), bp_top, xx(bp_w/2/H_), bp_bot), 0.10*H_, fill)
    # backpack vents (rim-colored notches)
    for i in range(3):
        vy = bp_top + (bp_bot-bp_top)*(0.25+0.22*i)
        draw.line([(cx-bp_w*0.3, vy), (cx+bp_w*0.3, vy)], fill=rim, width=max(2,int(0.006*H_)))

    # --- hip / waist ---
    rrect(draw, (xx(-0.19), yy(0.55), xx(0.19), yy(0.66)), 0.05*H_, fill)

    # --- torso / chest ---
    torso_top, torso_bot = yy(0.32), yy(0.60)
    rrect(draw, (xx(-0.27), torso_top, xx(0.27), torso_bot), 0.08*H_, fill)
    # chest reactor ring (rim-lit)
    rr = 0.09 * H_
    rcx, rcy = cx, (torso_top+torso_bot)/2 - 0.02*H_
    draw.ellipse((rcx-rr, rcy-rr, rcx+rr, rcy+rr), outline=rim, width=max(2, int(0.012*H_)))
    draw.ellipse((rcx-rr*0.45, rcy-rr*0.45, rcx+rr*0.45, rcy+rr*0.45), fill=rim)

    # --- shoulder pauldrons (big, iconic) ---
    for side in (-1, 1):
        sx = cx + side * 0.38 * H_
        box = (min(sx-0.19*H_, sx+0.19*H_), yy(0.23), max(sx-0.19*H_, sx+0.19*H_), yy(0.46))
        rrect(draw, box, 0.09*H_, fill)

    # --- arms hanging from shoulders to mid-thigh, slightly bent ---
    for side in (-1, 1):
        ax = cx + side * 0.40 * H_
        rrect(draw, (ax-0.09*H_, yy(0.40), ax+0.09*H_, yy(0.63)), 0.05*H_, fill)  # upper arm
        fx = ax + side*0.02*H_
        rrect(draw, (fx-0.085*H_, yy(0.60), fx+0.085*H_, yy(0.80)), 0.045*H_, fill)  # forearm
        # gauntlet fist
        draw.ellipse((fx-0.09*H_, yy(0.775), fx+0.09*H_, yy(0.855)), fill=fill)

    # --- neck / collar (trapezoid widening out to meet the shoulders, so
    # there's no gap of visible background between neck and pauldrons) ---
    rrect(draw, (xx(-0.09), yy(0.20), xx(0.09), yy(0.33)), 0.03*H_, fill)
    shoulder_inner = 0.38 - 0.19  # = 0.19, inner edge of each pauldron box
    draw.polygon([
        (xx(-0.09), yy(0.20)), (xx(0.09), yy(0.20)),
        (xx(shoulder_inner), yy(0.27)), (xx(-shoulder_inner), yy(0.27)),
    ], fill=fill)

    # --- helmet ---
    head_top, head_bot = yy(0.0), yy(0.20)
    head_w = 0.155
    draw.pieslice((xx(-head_w), head_top, xx(head_w), head_top + (head_bot-head_top)*1.6),
                  180, 360, fill=fill)
    rrect(draw, (xx(-head_w), head_top + (head_bot-head_top)*0.35, xx(head_w), head_bot), 0.02*H_, fill)
    # visor slit (rim-lit — the one warm-glow accent on the helmet)
    vw = head_w * 0.62
    vy0 = head_top + (head_bot - head_top) * 0.42
    vy1 = vy0 + (head_bot - head_top) * 0.16
    draw.rounded_rectangle((xx(-vw), vy0, xx(vw), vy1), radius=int(0.02*H_), fill=rim)
    # small antenna
    draw.line([(xx(head_w*0.5), head_top), (xx(head_w*0.5), head_top-0.05*H_)],
               fill=fill, width=max(2, int(0.01*H_)))

    # --- rim light: re-stroke the whole silhouette's outer edge isn't
    # practical without a mask pass here, so key edges (shoulder tops,
    # helmet dome, arm outer edges) get a thin rim highlight instead ---
    for side in (-1, 1):
        sx = cx + side * 0.38 * H_
        edge_x = sx + side*0.19*H_
        draw.line([(edge_x, yy(0.24)), (edge_x, yy(0.44))], fill=rim, width=max(2, int(0.008*H_)))
    draw.arc((xx(-head_w), head_top, xx(head_w), head_top + (head_bot-head_top)*1.6),
             180, 360, fill=rim, width=max(2, int(0.01*H_)))


def ruined_skyline(draw, base_y, color, seed):
    rnd = random.Random(seed)
    x = -50
    while x < W + 50:
        w = rnd.randint(40, 140)
        h = rnd.randint(60, 420)
        top = base_y - h
        broken = rnd.random() < 0.4
        if broken:
            jag = [(x, base_y)]
            steps = rnd.randint(2, 4)
            for i in range(steps):
                jag.append((x + w*(i+1)/(steps+1), top + rnd.randint(0, h//3)))
            jag.append((x + w, base_y))
            draw.polygon(jag, fill=color)
        else:
            draw.rectangle((x, top, x + w, base_y), fill=color)
            if rnd.random() < 0.5:
                for fy in range(top + 15, base_y - 10, rnd.randint(18, 30)):
                    if rnd.random() < 0.5:
                        draw.rectangle((x+6, fy, x+w-6, fy+6), fill=(0, 0, 0, 0))
        x += w + rnd.randint(4, 30)


def ridge(draw, base_y, amplitude, color, seed):
    rnd = random.Random(seed)
    pts = [(0, base_y + amplitude)]
    x = 0
    y = base_y
    while x < W:
        x += rnd.randint(150, 350)
        y = base_y + rnd.randint(-amplitude, amplitude)
        pts.append((x, y))
    pts.append((W, base_y + amplitude))
    pts.append((W, H))
    pts.append((0, H))
    draw.polygon(pts, fill=color)
    return pts


def cracked_earth(draw, base_y, color, seed):
    rnd = random.Random(seed)
    pts = [(0, base_y)]
    x = 0
    while x < W:
        x += rnd.randint(80, 220)
        pts.append((x, base_y + rnd.randint(-18, 24)))
    pts.append((W, H)); pts.append((0, H))
    draw.polygon(pts, fill=color)
    # crack lines
    crack_color = tuple(max(0, c-14) for c in color)
    for _ in range(26):
        sx = rnd.randint(0, W)
        sy = rnd.randint(base_y+20, H-40)
        pts2 = [(sx, sy)]
        for _ in range(rnd.randint(2, 4)):
            sx += rnd.randint(-60, 60)
            sy += rnd.randint(20, 60)
            pts2.append((sx, sy))
        draw.line(pts2, fill=crack_color, width=2)


PALETTES = {
    "dusk": dict(
        sky_stops=[
            (0.00, hex2rgb("140B08")),
            (0.35, hex2rgb("3A1F12")),
            (0.62, hex2rgb("7A431C")),
            (0.78, hex2rgb("C97A2E")),
            (0.90, hex2rgb("E8A94C")),
        ],
        sun_color=hex2rgb("FFE7B0"),
        sun_pos=(0.22, 0.44),
        sun_r=260,
        sun_falloff=380,
        skyline_color=hex2rgb("4A3018"),
        skyline_base=0.615,
        ridge_color=hex2rgb("1C0F08"),
        ridge_base=0.66,
        earth_color=hex2rgb("120A06"),
        earth_base=0.80,
        armor_fill=hex2rgb("0A0603"),
        armor_rim=hex2rgb("F4B860"),
    ),
    "duststorm": dict(
        sky_stops=[
            (0.00, hex2rgb("1A1410")),
            (0.30, hex2rgb("3D2C1A")),
            (0.60, hex2rgb("6E4E28")),
            (0.80, hex2rgb("9C6E32")),
            (0.92, hex2rgb("C99752")),
        ],
        sun_color=hex2rgb("E8C88C"),
        sun_pos=(0.78, 0.49),
        sun_r=190,
        sun_falloff=400,
        skyline_color=hex2rgb("4E3A20"),
        skyline_base=0.60,
        ridge_color=hex2rgb("1E150D"),
        ridge_base=0.655,
        earth_color=hex2rgb("15100A"),
        earth_base=0.80,
        armor_fill=hex2rgb("0C0805"),
        armor_rim=hex2rgb("D9822B"),
    ),
}


def render(variant, out_path, seed=7):
    p = PALETTES[variant]
    img = vertical_gradient((W, H), p["sky_stops"]).convert("RGB")

    # sun glow: two soft bloom layers (wide+faint, then tighter+brighter)
    # composited onto the sky, then a solid core disc on top.
    sun_x, sun_y = int(W * p["sun_pos"][0]), int(H * p["sun_pos"][1])

    def blend_glow(radius, falloff, strength):
        glow_color, glow_mask = radial_glow(int(radius), p["sun_color"], int(falloff))
        gx = sun_x - glow_color.width // 2
        gy = sun_y - glow_color.height // 2
        region = img.crop((gx, gy, gx + glow_color.width, gy + glow_color.height))
        lit = Image.composite(glow_color, region, glow_mask.point(lambda v: int(v * strength)))
        img.paste(lit, (gx, gy))

    blend_glow(p["sun_r"] * 1.8, p["sun_falloff"] * 1.6, 0.55)
    blend_glow(p["sun_r"], p["sun_falloff"], 0.85)

    core_r = int(p["sun_r"] * 0.5)
    draw0 = ImageDraw.Draw(img)
    draw0.ellipse((sun_x-core_r, sun_y-core_r, sun_x+core_r, sun_y+core_r), fill=p["sun_color"])

    draw = ImageDraw.Draw(img)

    # distant ruined skyline
    ruined_skyline(draw, int(H*p["skyline_base"]), p["skyline_color"], seed)

    # mid-ground ridge
    ridge_pts = ridge(draw, int(H*p["ridge_base"]), 40, p["ridge_color"], seed+1)

    # power armor standing on the ridge, right-of-center
    armor_cx = int(W * 0.60)
    # find ridge y near armor_cx
    ridge_y = int(H*p["ridge_base"])
    armor_h = int(H * 0.40)
    # cast shadow (long, toward lower-left, away from sun)
    shadow_len = int(armor_h * 1.6)
    shadow = [
        (armor_cx-armor_h*0.18, ridge_y),
        (armor_cx+armor_h*0.18, ridge_y),
        (armor_cx-armor_h*0.55-shadow_len*0.3, ridge_y+shadow_len*0.35),
        (armor_cx-armor_h*0.75-shadow_len*0.3, ridge_y+shadow_len*0.30),
    ]
    draw.polygon(shadow, fill=p["ridge_color"])

    draw_power_armor(draw, armor_cx, ridge_y+6, armor_h, p["armor_fill"], p["armor_rim"], 4)

    # cracked earth foreground
    cracked_earth(draw, int(H*p["earth_base"]), p["earth_color"], seed+2)

    # grain
    noise = Image.effect_noise((W, H), 14).convert("L")
    noise_rgb = Image.merge("RGB", (noise, noise, noise))
    img = Image.blend(img, noise_rgb, 0.035)

    # vignette
    vign = Image.new("L", (W, H), 0)
    vd = ImageDraw.Draw(vign)
    vd.ellipse((-W*0.25, -H*0.35, W*1.25, H*1.25), fill=255)
    vign = vign.filter(ImageFilter.GaussianBlur(220))
    dark = Image.new("RGB", (W, H), (0, 0, 0))
    img = Image.composite(img, dark, vign.point(lambda v: int(v*0.85+40)))

    img.save(out_path, quality=92, optimize=True)
    print(f"wrote {out_path} ({W}x{H}, variant={variant})")


if __name__ == "__main__":
    import sys, os
    out_dir = sys.argv[1] if len(sys.argv) > 1 else "theme/backgrounds"
    os.makedirs(out_dir, exist_ok=True)
    render("dusk", os.path.join(out_dir, "1-wasteland-dusk.jpg"))
    render("duststorm", os.path.join(out_dir, "2-wasteland-duststorm.jpg"))

#!/usr/bin/env python3
# ============================================================================
# FILE:    generate_fallout_preview.py
# TASK:    Build theme/preview.png for the Omarchy Fallout theme (the
#          thumbnail the theme selector / omarchy-theme-switcher shows).
# STATUS:  DONE
# OWNER:   agent A 2026-09-09
#
# WHAT THIS FILE DOES:
#   Takes the Matrix theme's preview.png (a real desktop screenshot of the
#   themed desktop — Neovim+Neo-tree, a terminal running ls, btop, Nautilus —
#   which the script's own repo built interactively per the recipe in
#   omarchy-matrix-rain's generate_matrix_preview.py header) and remaps its
#   color family from matrix-green to fallout amber/rust. The desktop scene
#   and window layout are shared between the two themes (same base apps, same
#   2x2 tiling); only the colors differ. NOT called by install.sh — preview.png
#   is a fixed, curated asset shipped in the repo (same as every stock Omarchy
#   theme). Re-run by hand only if the matrix preview or the palette changes.
#
#   What it does NOT do: it does not set up the desktop scene or capture a
#   screenshot (that's matrix's preview recipe, one-time interactive work —
#   see matrix's generate_matrix_preview.py header). To build the fallout
#   preview from an actual fallout-themed rebuild of that same scene instead
#   of a hue-shift, re-shoot the scene with the fallout theme applied and use
#   the quantity of that raw screenshot in place of --source.
#
# NEXT STEP (if not DONE):
#   none — file complete
# ============================================================================
#
# Color mapping:
#   Matrix greens all sit at hue ~0.36 (measured from the live matrix
#   preview). Fallout amber lives at hue ~0.08 (#D9822B family). So the
#   whole green ramp is rotated by -0.28 in hue space, saturation is boosted
#   ~15% (amber reads more vibrant at the same value than matrix green did),
#   and value/brightness is left untouched so the synthetic shading the
#   screenshot already has stays intact. Pixels that aren't green (black
#   desktop, gray UI chrome, purple nvim floating-window background, actual
#   magenta/blue syntax tokens) pass through unchanged.
#
# Green detection predicate (per-pixel):
#   saturation > 0.10 AND green channel dominates red AND
#   hue in [0.15, 0.50] AND value > 0.03
#   (the value floor keeps pure-black room for the true "black" most of the
#   matrix desktop already is — verified it maps 198K green pixels and leaves
#   1623K others untouched.)
#
# Output is quantized to a 256-color palette (MAXCOVERAGE) like the stock
# matrix/other-theme previews, keeping the file a few hundred KB, in line with
# what omarchy-theme-switcher expects to load at thumbnail size.
import argparse
import colorsys
from pathlib import Path

from PIL import Image

TARGET_W, TARGET_H = 1800, 1012

GREEN_HUE_CENTER = 0.36
AMBER_HUE_CENTER = 0.08
HUE_SHIFT = AMBER_HUE_CENTER - GREEN_HUE_CENTER  # -0.28
SATURATION_BOOST = 1.15

# Per-pixel green predicate — only these get recolored.
def is_greenish(hue, sat, val):
    return (
        sat > 0.10
        and hue > 0.15
        and hue < 0.50
        and val > 0.03
    )


def recolor_pixel(r, g, b):
    hue, sat, val = colorsys.rgb_to_hsv(r / 255, g / 255, b / 255)
    if not (is_greenish(hue, sat, val) and g > r):
        return (r, g, b)
    new_hue = (hue + HUE_SHIFT) % 1.0
    new_sat = min(1.0, sat * SATURATION_BOOST)
    nr, ng, nb = colorsys.hsv_to_rgb(new_hue, new_sat, val)
    return (round(nr * 255), round(ng * 255), round(nb * 255))


def build_preview(source_path, out_path):
    src = Image.open(source_path).convert("RGB")
    if src.size != (TARGET_W, TARGET_H):
        raise SystemExit(
            f"Source must already be {TARGET_W}x{TARGET_H} (matrix's preview.png "
            f"is); got {src.size}. Re-crop/scale with matrix's recipe first."
        )
    px = src.load()
    out = Image.new("RGB", src.size)
    opx = out.load()
    mapped = kept = 0
    for y in range(TARGET_H):
        for x in range(TARGET_W):
            r, g, b = px[x, y]
            nr, ng, nb = recolor_pixel(r, g, b)
            if (nr, ng, nb) != (r, g, b):
                mapped += 1
            else:
                kept += 1
            opx[x, y] = (nr, ng, nb)
    quant = out.quantize(colors=256, method=Image.Quantize.MAXCOVERAGE)
    quant.save(out_path, optimize=True)
    print(f"Wrote {out_path} ({TARGET_W}x{TARGET_H}), recolored {mapped}px, kept {kept}px")


def main():
    p = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    p.add_argument(
        "--source",
        default="~/Work/omarchy-matrix-rain/theme/preview.png",
        help="Matrix theme preview.png to recolor (default: the matrix repo's)",
    )
    p.add_argument(
        "--out",
        default=str(Path.home() / "Work/omarchy-fallout-theme/theme/preview.png"),
        help="Where to write the fallout preview.png",
    )
    args = p.parse_args()

    source = Path(args.source).expanduser()
    if not source.exists():
        raise SystemExit(f"Source not found: {source}")
    build_preview(source, Path(args.out).expanduser())


if __name__ == "__main__":
    main()
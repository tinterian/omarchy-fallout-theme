#!/usr/bin/env python3
# ============================================================================
# FILE:    generate_fallout_preview.py
# TASK:    Build theme/preview.png for the Omarchy Fallout theme (the
#          thumbnail the theme selector / omarchy-theme-switcher shows).
# STATUS:  DONE
# OWNER:   agent A 2026-09-09
#
# WHAT THIS FILE DOES:
#   Crops/scales/quantizes a RAW desktop screenshot (grim capture, typically
#   1920x1080) down to the standard Omarchy preview size 1800x1012, 256-color
#   palette. That is the FINAL step of building theme/preview.png — the scene
#   setup and capture are interactive/compositor work documented in the
#   recipe below and must be done BY HAND first (mirrors how every stock
#   theme's preview.png and omarchy-matrix-rain's generate_matrix_preview.py
#   work). NOT called by install.sh — preview.png is a fixed, curated asset
#   shipped in the repo. Re-run by hand only to regenerate after a
#   colors/icon/wallpaper change makes the shipped preview stale.
#
#   HISTORY: the very first version described a hue-shift of the Matrix
#   theme's preview (rotate matrix-green -> fallout amber) as a quick interim
#   preview. That approach was fully superseded ONCE the real desktop scene
#   could be built with the fallout theme applied live (amber nvim palette,
#   BeautyLine-Fallout home-folder icons, official-art wallpapers).
#   Hue-shifting shipped one image and is no longer used.
#
# NEXT STEP (if not DONE):
#   none — file complete
# ============================================================================
#
# RECIPE for producing --source (the fallout preview's final shot):
#   1. Ensure the fallout theme is live everywhere it matters: `omarchy theme
#      current` -> Fallout, and the nvim palette is amber via the repo's
#      theme/neovim.lua (aether-from-colors.toml — NOT shawilly/fallout.nvim,
#      which is Pip-Boy green). Generate+apply the folder icon set first so
#      the home folder shows themed icons:
#        python3 generate_fallout_icons.py
#        gsettings set org.gnome.desktop.interface icon-theme 'BeautyLine-Fallout'
#   2. Set the monitor to 1920x1080 (matches 1800x1012 aspect so the final
#      crop is near-zero):
#        hyprctl eval 'hl.monitor({ output = "<name>", mode = "1920x1080@60",
#                                   position = "0x0", scale = 1 })'
#   3. Make the compositor auto-hide the cursor for the capture (prevents the
#      mouse showing up in the shot AND prevents hover highlights):
#        hyprctl eval 'hl.config({ cursor = { inactive_timeout = 1000 } })'
#      then STOP moving the mouse ~4s before grim. Reset to 0 after.
#   4. Park any background windows OUT of the shot. On this Hyprland fork
#      `hl.dsp.workspace.move` no-ops (can't "move to desktop 2" — empty
#      workspaces don't exist and hl.dsp.workspace.change_id has a phantom
#      arg bug), so float the window then move it fully off-screen instead:
#        hyprctl eval 'hl.dispatch(hl.dsp.focus({window="class:^(...)$"}))'
#        hyprctl eval 'hl.dispatch(hl.dsp.window.float({}))'
#        hyprctl eval 'hl.dispatch(hl.dsp.window.move({x=2200,y=100}))'
#   5. Open + float + position 4 windows (all fully detached so shells return:
#      `setsid bash -c '...' >/dev/null 2>&1 </dev/null &`):
#        - top-left    (8,42)    992x818  — foot: nvim with 2 tabs + Neo-tree
#          (cd /usr/lib/python3.14 && foot --app-id nvim-preview nvim glob.py
#            -c "78" -c "normal! zz" -c "Neotree toggle"
#            -c "tabnew /usr/lib/python3.14/statistics.py" -c "tabfirst")
#        - bottom-left (8,868)   992x204  — foot: ls -la; exec $SHELL
#        - top-right  (1008,42)  904x658  — foot: btop (let graphs populate)
#        - bottom-right (1008,708) 904x364 — nautilus --new-window "$HOME"
#          (HOME folder is deliberate: shows the theme's folder icons)
#      Targeting gotcha on this fork: focus BY APP-CLASS fails for windows that
#      lack an app_id (btop), so focus by ADDRESS — read each window's address
#      from `hyprctl clients -j`, then for each: focus({window="address:<hex>"})
#      then window.float({}) / .resize({x=W,y=H}) / .move({x=X,y=Y}).
#      POSITION IN ORDER BUT LAUNCH ALL FIRST — positioning immediately after
#      each launch races the window mapping and usually hits the wrong window.
#      Window content should be NEUTRAL, not fallout-repo files (a public
#      preview shouldn't advertise the project): stdlib python files, ls of a
#      system dir, /usr/share/doc or $HOME for nautilus.
#   6. Wait ~4s with the mouse still (cursor hides via step 3), then:
#        grim <source.png>
#   7. If the fallout icon theme is already applied, the folders capture amber
#      (#D9822B-ish); a hover highlight/cursor shows as a localized diff
#      between two captures 3s apart — recapture if any static region differs.
#   8. Run THIS script with --source <that grim file>; quantize matches stock
#      preview look. Restore afterwards: cursor timeout 0, monitor to the
#      native mode, resurrect the parked window.
import argparse
from pathlib import Path

from PIL import Image

TARGET_W, TARGET_H = 1800, 1012


def build_preview(source_path, out_path):
    src = Image.open(source_path).convert("RGB")
    sw, sh = src.size
    scale = max(TARGET_W / sw, TARGET_H / sh)
    new_w, new_h = round(sw * scale), round(sh * scale)
    resized = src.resize((new_w, new_h), Image.LANCZOS)
    left = (new_w - TARGET_W) // 2
    top = (new_h - TARGET_H) // 2
    cropped = resized.crop((left, top, left + TARGET_W, top + TARGET_H))
    quant = cropped.quantize(colors=256, method=Image.Quantize.MAXCOVERAGE)
    quant.save(out_path, optimize=True)
    print(f"Wrote {out_path} ({TARGET_W}x{TARGET_H})")


def main():
    p = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    p.add_argument(
        "--source",
        required=True,
        help="Raw desktop screenshot (grim capture) to crop/scale/quantize "
        "(see the RECIPE in this file's header)",
    )
    p.add_argument(
        "--out",
        default=str(Path.home() / "Work/omarchy-fallout-theme/theme/preview.png"),
        help="Where to write the fallout preview.png",
    )
    args = p.parse_args()

    source = Path(args.source)
    if not source.exists():
        raise SystemExit(f"Source screenshot not found: {source}")
    build_preview(source, Path(args.out).expanduser())


if __name__ == "__main__":
    main()
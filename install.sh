#!/bin/bash
# ============================================================================
# FILE:    install.sh
# TASK:    Install the Fallout theme (wasteland+power-armor wallpapers,
#          amber/rust colors, file-manager icons, Neovim/VS Code colors,
#          lock screen, theme-switcher preview) into an existing Omarchy
#          setup.
# STATUS:  DONE
# OWNER:   agent A 2026-09-09
#
# WHAT THIS DOES, in order:
#   1. Check dependencies (python3, Pillow — needed only for the optional
#      icon-generation step; the wallpapers themselves are static PNGs
#      shipped in the repo, no live rendering needed, unlike the Matrix
#      theme's animated wallpaper).
#   2. Create ~/.config/omarchy/themes/fallout/ and install
#      theme/{colors.toml,icons.theme,neovim.lua,vscode.json,unlock.png,
#      preview.png} plus theme/backgrounds/*.png into it — each file
#      individually skipped if already present, never overwrites an
#      existing customization.
#   3. If an AUR helper (yay/paru) is available, or `beautyline` is already
#      installed, offer to generate "BeautyLine-Fallout" (see
#      generate_fallout_icons.py) into ~/.local/share/icons/ — covers every
#      icon a file manager can show. Skipped non-fatally with a note if
#      unavailable — icons.theme already points at BeautyLine-Fallout, so
#      icons just won't be themed until it's installed.
#
# Safe to re-run: every installed file is skip-if-exists.
#
# NEXT STEP (if not DONE):
#   none — file complete, not yet end-to-end tested against a clean state
#   (see PROGRESS.md).
# ============================================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
THEME_DIR="$HOME/.config/omarchy/themes/fallout"
BACKGROUNDS_DIR="$THEME_DIR/backgrounds"

echo "== Fallout theme installer =="
echo

# --- 1. Dependency check -----------------------------------------------
missing=()
command -v python3 >/dev/null || missing+=(python)
python3 -c "import PIL" 2>/dev/null || missing+=(python-pillow)

if (( ${#missing[@]} > 0 )); then
  echo "Missing dependencies (needed for icon generation): ${missing[*]}"
  read -r -p "Install with 'sudo pacman -S --needed ${missing[*]}'? [y/N] " reply
  if [[ $reply =~ ^[Yy]$ ]]; then
    sudo pacman -S --needed "${missing[@]}"
  else
    echo "Continuing without them — icon generation (step 3) will be skipped." >&2
  fi
fi
echo

# --- 2. Theme colors, wallpapers, per-app integration files --------------
mkdir -p "$BACKGROUNDS_DIR"
for f in colors.toml icons.theme neovim.lua vscode.json unlock.png preview.png; do
  if [[ -f "$THEME_DIR/$f" ]]; then
    echo "Existing $THEME_DIR/$f found — leaving it as-is."
  else
    cp "$SCRIPT_DIR/theme/$f" "$THEME_DIR/$f"
    echo "Installed theme/$f -> $THEME_DIR/$f"
  fi
done
for f in "$SCRIPT_DIR"/theme/backgrounds/*.png; do
  base=$(basename "$f")
  if [[ -f "$BACKGROUNDS_DIR/$base" ]]; then
    echo "Existing $BACKGROUNDS_DIR/$base found — leaving it as-is."
  else
    cp "$f" "$BACKGROUNDS_DIR/$base"
    echo "Installed backgrounds/$base -> $BACKGROUNDS_DIR/$base"
  fi
done
echo

# --- 3. Outline file/folder icons (optional, needs beautyline) -----------
AUR_HELPER=""
command -v yay >/dev/null && AUR_HELPER=yay
[[ -z $AUR_HELPER ]] && command -v paru >/dev/null && AUR_HELPER=paru

if ! python3 -c "import PIL" 2>/dev/null; then
  echo "Skipping icon generation — python-pillow not installed."
  echo "Run 'python3 $SCRIPT_DIR/generate_fallout_icons.py' yourself later."
elif [[ -d /usr/share/icons/BeautyLine ]]; then
  python3 "$SCRIPT_DIR/generate_fallout_icons.py" --theme-name fallout
  gtk-update-icon-cache -f -t "$HOME/.local/share/icons/BeautyLine-Fallout" >/dev/null 2>&1 || true
  echo "Generated BeautyLine-Fallout folder icons."
elif [[ -n $AUR_HELPER ]]; then
  read -r -p "Install the 'beautyline' outline icon pack from the AUR with $AUR_HELPER for themed folder icons? [y/N] " reply
  if [[ $reply =~ ^[Yy]$ ]]; then
    "$AUR_HELPER" -S --needed beautyline
    python3 "$SCRIPT_DIR/generate_fallout_icons.py" --theme-name fallout
    gtk-update-icon-cache -f -t "$HOME/.local/share/icons/BeautyLine-Fallout" >/dev/null 2>&1 || true
    echo "Generated BeautyLine-Fallout folder icons."
  else
    echo "Skipping folder icons — run 'python3 $SCRIPT_DIR/generate_fallout_icons.py' after installing beautyline yourself."
  fi
else
  echo "No AUR helper (yay/paru) found — skipping folder icons."
  echo "Install 'beautyline' from the AUR yourself, then run:"
  echo "  python3 $SCRIPT_DIR/generate_fallout_icons.py --theme-name fallout"
fi
echo

cat <<'EOF'
== Done ==

If the Fallout theme isn't already selected:
    omarchy-theme-set fallout
  or pick "Fallout" from the Omarchy theme menu.

Two wallpapers are included (Dusk / Dust Storm) — flip between them with the
standard Omarchy background switcher:
    SUPER CTRL + SPACE
or:
    omarchy-theme-bg-next

See README.md for troubleshooting.
EOF

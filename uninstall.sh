#!/bin/bash
# ============================================================================
# FILE:    uninstall.sh
# TASK:    Remove what install.sh added.
# STATUS:  DONE
# OWNER:   agent A 2026-09-09
#
# WHAT THIS DOES:
#   Removes ~/.local/share/icons/BeautyLine-Fallout (if generated). Leaves
#   ~/.config/omarchy/themes/fallout/ itself alone — delete that directory
#   yourself if you want the whole theme gone (colors.toml, backgrounds,
#   etc. — nothing else on the system depends on it once it's not the
#   active theme).
#
# NEXT STEP (if not DONE):
#   none — file complete
# ============================================================================
set -euo pipefail

rm -rf "$HOME/.local/share/icons/BeautyLine-Fallout"
echo "Removed ~/.local/share/icons/BeautyLine-Fallout (if it existed)."
echo "~/.config/omarchy/themes/fallout/ was left in place — remove it yourself"
echo "(and switch to a different theme first) if you want the theme fully gone."

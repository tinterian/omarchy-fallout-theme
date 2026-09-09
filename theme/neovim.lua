-- ============================================================================
-- FILE:    theme/neovim.lua
-- TASK:    Neovim integration for the Omarchy Fallout theme.
-- STATUS:  DONE
-- OWNER:   agent A 2026-09-09
--
-- WHAT THIS FILE DOES:
--   Points LazyVim at the Omarchy-standard colorscheme mechanism: the
--   `bjarneo/aether.nvim` plugin (v3 branch) with every palette color
--   templated straight from this theme's own colors.toml. This is the same
--   spec Omarchy generates for themes that don't ship a custom neovim.lua
--   (`/usr/share/omarchy/default/themed/neovim.lua.tpl`), rendered with the
--   fallout wasteland/amber palette.
--
--   Earlier choice replaced for a reason: the repo previously pointed at
--   shawilly/fallout.nvim, whose palette is Pip-Boy GREEN (#4afa4a fg,
--   green-black bg) — directly contrary to this theme's confirmed direction
--   (wasteland + amber/rust accent, explicitly NOT Pip-Boy green). Renders
--   read as "matrix colors" in use. aether-from-colors.toml gives a nvim
--   palette that actually matches the theme everywhere else.
--
-- NEXT STEP (if not DONE):
--   none — file complete
-- ============================================================================
return {
  {
    "bjarneo/aether.nvim",
    branch = "v3",
    name = "aether",
    priority = 1000,
    opts = {
      colors = {
        bg = "#0D0A07",
        dark_bg = "#080604",
        darker_bg = "#050403",
        lighter_bg = "#1A140D",

        fg = "#E8C99A",
        dark_fg = "#B8874F",
        light_fg = "#F2DDB0",
        bright_fg = "#FFEAC2",
        muted = "#7A6552",

        red = "#C0392B",
        yellow = "#D4A017",
        orange = "#D9822B",
        green = "#8A9A5B",
        cyan = "#5E8C8A",
        blue = "#5A7D8C",
        magenta = "#8C6B8F",
        brown = "#6B4A2F",

        bright_red = "#E0574A",
        bright_yellow = "#F0C13D",
        bright_green = "#AEC17F",
        bright_cyan = "#7FB0AD",
        bright_blue = "#7DA3B3",
        bright_magenta = "#B08CB3",

        accent = "#D9822B",
        cursor = "#FFEAC2",
        foreground = "#E8C99A",
        background = "#0D0A07",
        selection = "#3A2416",
        selection_foreground = "#FFEAC2",
        selection_background = "#3A2416",
      },
    },
  },
  {
    "LazyVim/LazyVim",
    opts = {
      colorscheme = "aether",
    },
  },
}
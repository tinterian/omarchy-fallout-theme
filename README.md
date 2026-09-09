# Omarchy Fallout Theme

A full [Omarchy](https://omarchy.org) desktop theme built around the
Fallout game series: a wasteland dusk skyline with a power-armor
silhouette standing on the ridge, rendered in a rust/amber warning-light
palette (deliberately not Pip-Boy green or Brotherhood-of-Steel red).

![preview](theme/preview.png)

Designed and tested on Omarchy specifically — don't assume it works
unmodified on a plain Hyprland/GTK setup.

## What this actually is

- Two hand-built 4K wallpapers (`Dusk` and `Dust Storm`) — wasteland
  horizon, a ruined skyline, and a power-armor figure backlit by a hazy
  sun. Procedurally rendered (see `generate_fallout_wallpaper.py`), not
  photos or AI-generated images.
- `theme/colors.toml` — the palette every other themed app pulls from:
  dusty rust-brown darks, warm parchment foreground, `#D9822B` amber
  accent. Every ANSI/terminal color is tinted toward the same wasteland
  family (olive drab, faded steel, weathered patina) while staying
  readable in a real terminal.
- File-manager icons (`BeautyLine-Fallout`, generated from the `beautyline`
  AUR package): default folders get a full parchment-to-black gradient,
  everything else (every device/file-type icon) keeps its own colors with
  a black fade at the bottom — same technique as this author's Matrix
  theme.
- Neovim colorscheme: [shawilly/fallout.nvim](https://github.com/shawilly/fallout.nvim)
  (colorscheme `fallout`) — a real plugin whose own palette is Pip-Boy
  green + wasteland browns/rust, the closest existing match to this
  theme's direction.
- VS Code: [`FcGod.fallout-pip-boy-theme`](https://marketplace.visualstudio.com/items?itemName=FcGod.fallout-pip-boy-theme)
  ("Fallout Pip-Boy Theme"), a real marketplace extension.
- Lock screen wordmark (`unlock.png`) recolored to the theme's accent.
- `theme/preview.png` — the theme-switcher thumbnail. Currently a curated
  crop of the Dusk wallpaper, not a full staged desktop screenshot (the
  Matrix theme's preview.png is a real desktop screenshot — see that
  repo's history for the technique; doing the same here is a possible
  follow-up, not done yet).

## Requirements

- Omarchy (Hyprland).
- `python3` + `python-pillow` — only needed for the optional icon
  generation step; the wallpapers themselves are static PNGs shipped in
  the repo, nothing renders at install time.
- Optional: `beautyline` (AUR) for themed folder/file icons.

## Install

```bash
git clone https://github.com/tinterian/omarchy-fallout-theme.git
cd omarchy-fallout-theme
./install.sh
```

`install.sh` is unattended except one optional y/N prompt if you want it to
install `beautyline` for you. It never overwrites a file that's already
there — safe to re-run.

Then select the theme:

```bash
omarchy-theme-set fallout
```

or pick "Fallout" from the Omarchy theme menu.

## Switching wallpapers

Two wallpapers are included. Flip between them with the standard Omarchy
background switcher:

```
SUPER CTRL + SPACE
```

or:

```bash
omarchy-theme-bg-next
```

## Theme components

| File | What it does |
|---|---|
| `theme/colors.toml` | Core palette — every other file below derives from this |
| `theme/backgrounds/*.jpg` | The two wallpapers |
| `theme/icons.theme` | Points GTK apps (Nautilus) at `BeautyLine-Fallout` |
| `theme/neovim.lua` | LazyVim colorscheme spec |
| `theme/vscode.json` | VS Code/VSCodium/Cursor extension + theme name |
| `theme/unlock.png` | Lock-screen OMARCHY wordmark, recolored |
| `theme/preview.png` | Theme-switcher thumbnail |
| `generate_fallout_wallpaper.py` | Regenerates the two wallpapers |
| `generate_fallout_icons.py` | Regenerates `BeautyLine-Fallout` from an installed `beautyline` |

## Customizing

Both generator scripts read from `theme/colors.toml` (or `--theme-name`
another installed Omarchy theme) and take `--top`/`--bottom` overrides for
the icon fade colors. See each script's own header comment for the full
design/rationale before changing it — the wallpaper generator in
particular documents the composition choices (sun placement relative to
the skyline, why the armor's neck has a collar trapezoid, etc.) so a
future edit doesn't reintroduce a fixed bug.

## Uninstall

```bash
./uninstall.sh
```

Removes the generated `BeautyLine-Fallout` icon theme. Leaves
`~/.config/omarchy/themes/fallout/` in place — remove that directory
yourself (after switching to a different theme) if you want the theme
fully gone.

## For an AI agent doing this install

Assume only a basic Omarchy install exists. Concrete steps, each with a
way to verify it worked:

1. `git clone https://github.com/tinterian/omarchy-fallout-theme.git && cd omarchy-fallout-theme`
2. `./install.sh` — answer `y` if it offers to install `python-pillow` or
   `beautyline`; both are safe, small packages.
   - Verify: `ls ~/.config/omarchy/themes/fallout/` should show
     `colors.toml`, `icons.theme`, `neovim.lua`, `vscode.json`,
     `unlock.png`, `preview.png`, `backgrounds/`.
3. `omarchy-theme-set fallout`
   - Verify: `cat ~/.local/state/omarchy/current/theme.name` should print
     `fallout`.
4. If icon generation ran: verify with
   `gsettings get org.gnome.desktop.interface icon-theme` — should print
   `'BeautyLine-Fallout'`.
5. This theme was designed and tested on Omarchy specifically — don't
   assume it works unmodified on a plain Hyprland/GTK setup without
   Omarchy's theming pipeline (`omarchy-theme-set-*` scripts) present.

## License

MIT — see `LICENSE`.

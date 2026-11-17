# dwl config

My [dwl](https://codeberg.org/dwl/dwl) setup for Wayland, plus the launcher I use
in place of dmenu.

## Contents

| Path | Notes |
| --- | --- |
| `dwl/` | Complete dwl v0.9 source tree with our `config.h` and `dwl.c` changes. |
| `fuzzel/fuzzel.ini` | dmenu replacement, bound to `Super+D` via `menucmd`. |

## dwl

This repo vendors the full dwl v0.9 source, not a patch, so `dwl/` can be built
directly. On top of upstream:

- Nordic-ish palette: background `#1D2021`, border `#282828`, focus/accent
  `#30B27A`, urgent `#FB4934`
- 2px borders, no snapping, sloppy focus
- `Super` as `MODKEY`; `caps:escape` and swapped `Alt`/`Super` for XKB
- tile + floating layouts
- floating rules for `flameshot` and `qemu-system-x86_64`
- media/brightness keys, screenshots via `grim` + `slurp` + `wl-copy`,
  power-profile cycling, and tag keys `Super+1..9`
- `Super+Return` → `alacritty`, `Super+D` → `fuzzel`

Source changes in `dwl.c`:

- Fullscreen fills the monitor's usable area instead of the whole output, so
  the bottom `somebar` stays visible. If the bar appears, disappears, or is
  resized, the fullscreen window follows the new usable area.
- While a window is fullscreen, `Super+j` / `Super+k` cycles windows and moves
  fullscreen to the newly focused window.
- `Super+Shift+U` unfloats the selected window. If it is fullscreen, it also
  leaves fullscreen and returns to the tiling layout. (Existing
  `Super+Shift+Space` still toggles floating.)

To build and install:

```sh
cd dwl
make clean
make
make install PREFIX="$HOME/.local"
```

`config.h` is tracked as the active configuration. `config.def.h` is kept as
the reference config, and `patch-dwl-config.py` can regenerate `config.h` from
a stock `config.def.h` if needed:

```sh
cp config.def.h config.h
python3 patch-dwl-config.py
```

## fuzzel

`fuzzel.ini` uses the same palette as the dwl config, JetBrainsMono Nerd Font,
Papirus-Dark icons, and alacritty as its terminal. `fuzzel` is spawned by dwl's
`menucmd` on `Super+D`; it can also be run directly.

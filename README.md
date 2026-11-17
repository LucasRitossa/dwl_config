# dwl config

My [dwl](https://codeberg.org/dwl/dwl) setup for Wayland, the bar that feeds off
it, and the launcher that starts the session.

`main` is the **desktop** configuration. The older laptop-oriented config is
frozen on the `laptop` branch.

## Contents

| Path | Notes |
| --- | --- |
| `dwl/` | Complete dwl v0.9 source tree with our `config.h` and `dwl.c` changes. |
| `somebar/` | [somebar](https://sr.ht/~raphi/somebar/) source with our `config.hpp`. |
| `fuzzel/fuzzel.ini` | dmenu replacement, bound to `Super+D` via `menucmd`. |
| `dwl-run` | Session launcher: environment, user services, output mode, dwl + bar. |

## dwl

This repo vendors the full dwl v0.9 source, not a patch, so `dwl/` can be built
directly. On top of upstream:

- Nordic-ish palette: background `#1D2021`, border `#282828`, focus/accent
  `#30B27A`, urgent `#FB4934`
- 2px borders, no snapping, sloppy focus
- `Super` as `MODKEY`, matching dwm's `Mod4Mask` — the physical Super key. XKB
  is `us` + `caps:escape` only: the `altwin:swap_lalt_lwin` option this config
  used to carry put Mod4 on the physical *Alt* key, which broke `Super+Return`
  (dwl saw `Alt+Return`) and `Ctrl+Alt+F1` (dwl saw `Ctrl+Super+F1`). X11 on this
  machine has no XKB options either, so the swap was pure muscle-memory drift.
- tile + floating layouts, `Super+Tab` cycles them
- floating rules for `flameshot` and `qemu-system-x86_64`
- media keys, screenshots via `grim` + `slurp` + `wl-copy`, lock via `swaylock`,
  and tag keys `Super+1..9`
- `Super+Return` → `alacritty`, `Super+D` → `fuzzel`

Desktop-specific choices:

- **XWayland is enabled** in `config.mk` (`-DXWAYLAND`). Steam/Proton and other
  X11-only clients need it; dwl spawns Xwayland on demand.
- **Monitor rules** pin `DP-1` (left, 240Hz panel) at `0,0` and `HDMI-A-1`
  (right) at `1920,0`. dwl always uses the *preferred* mode and DP-1's preferred
  mode is 60Hz, so `dwl-run` sets `1920x1080@239.76` with `wlr-randr` at startup.
- The pointer block (`tap_to_click`, click/scroll methods, …) is kept even though
  this is a desktop: `dwl.c` applies every one of those symbols to each libinput
  pointer device, so removing them fails the build. They report unsupported for a
  mouse, so only `accel_profile`/`accel_speed` actually matter here.
- Brightness keys and the `powermode` bindings are gone: this machine has no
  `/sys/class/backlight` and no battery.

Source changes in `dwl.c`:

- Fullscreen fills the monitor's usable area instead of the whole output, so the
  bottom `somebar` stays visible. If the bar appears, disappears, or is resized,
  the fullscreen window follows the new usable area. (Same intent as the
  `dwm-actualfullscreen` patch carried in `~/.config/dwm_config`.)
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

`config.h` is tracked as the active configuration. `config.def.h` is kept as the
reference config, and `patch-dwl-config.py` regenerates `config.h` from a stock
`config.def.h`:

```sh
cp config.def.h config.h
python3 patch-dwl-config.py
```

The script is kept in lockstep with `config.h`: running the two commands above
reproduces the tracked file byte for byte. Edit both when changing the config.

## somebar

dwl prints its state to stdout in dwm's status format, and its `-s` flag pipes
that into the startup command's stdin. somebar reads exactly that stream, so the
bar needs **no IPC patch and no fork**: `dwl -s somebar` is enough.

That stream is one-way, so clicks are restored the cheap way instead:
`contrib/clickable-tags-using-wtype.patch` (applied to the vendored tree) turns a
click into the keystrokes dwl already binds, via `wtype`:

| Click | Sends | Effect |
| --- | --- | --- |
| left on tag *N* | `Super+N` | `view` that tag |
| right on tag *N* | `Super+Shift+N` | move the focused window to tag *N* |

This depends on two things staying true: `MODKEY` in `config.hpp` must match
dwl's `MODKEY` (`logo`), and the `Super+1..9` tag bindings must stay in
`dwl/config.h`. The full IPC protocol (clicking without synthesising keys) is
still the documented upgrade path if `wtype` ever gets in the way.

`somebar/src/config.hpp` is the active config (palette matching `dwl/config.h`,
JetBrainsMono Nerd Font 14, **bottom** bar). `config.def.hpp` is the upstream
reference plus that contrib patch.

Tag indicators (`src/bar.cpp`) replace upstream's 1px client ticks:

- the **selected** tag, if it has windows, gets a thick line across the top of
  its cell — `indicatorHeight`, default 3px
- a tag that is **occupied but not selected** gets a dot at the top of its cell —
  `indicatorDotRadius`, default 2px

Both are in `config.hpp`; rebuild somebar after changing them.

```sh
cd somebar
meson setup build --prefix="$HOME/.local"
ninja -C build
ninja -C build install
```

## dwl-run

Starts the session. It sets the Wayland/EGL environment, starts `pipewire`,
`pipewire-pulse` and `wireplumber` (there is no systemd/elogind user session on
Artix), then runs `dbus-run-session -- dwl -s ...`.

dwl's `-s` command owns dwl's stdout, so everything started there must redirect
stdout or its output is parsed as bar status. `somebar` is `exec`'d last so it
keeps the stream. `mako`, `swaybg` and the polkit agent are started alongside it.

```sh
install -m 755 dwl-run "$HOME/.local/bin/dwl-run"
```

## Packages

Build: `wlroots0.20` (pkg-config name `wlroots-0.20`), `libinput`, `libxkbcommon`,
`wayland`, `wayland-protocols`, `pixman`, `libxcb` + `xcb-util-wm` (XWayland),
`meson`/`ninja` for somebar.

Runtime: `xorg-xwayland`, `alacritty`, `fuzzel`, `grim`, `slurp`, `wl-clipboard`,
`swaylock`, `papirus-icon-theme`, `wlr-randr`, `mako`, `swaybg`, `wtype`
(clickable tags), `xdg-desktop-portal-wlr`, `playerctl`, `brightnessctl`.

## Booting into dwl (not enabled yet)

The machine still boots to a TTY and starts `dwm` with `startx`. dwl is installed
and launched manually from a TTY. To boot straight into dwl instead, three small
changes outside this repo:

1. `/etc/conf.d/agetty.tty1`: `agetty_options="--autologin luke"`
2. `~/.zprofile`, guarded so a crash drops to a shell instead of looping:

   ```zsh
   if [ "$(tty)" = /dev/tty1 ] && [ -z "$DWL_ATTEMPTED" ] && [ -z "$WAYLAND_DISPLAY" ]; then
       export DWL_ATTEMPTED=1
       dwl-run
   fi
   ```

3. Keep `agetty.tty2`–`tty6` as-is: they stay password-protected, so
   `Ctrl+Alt+F2` → login → `startx` still reaches dwm.

Reverse it by clearing `agetty_options`.

## Known limits of this compositor

- No adaptive sync / VRR, no tearing control, no HDR: dwl does not implement
  them. Use `gamescope` for frame limiting/scaling, or a compositor with VRR
  support if 240Hz variable refresh matters more than the tiling model.
- No tablet support.
- Screenshots work through dwl's screencopy and image-copy-capture support;
  X11 apps that screenshot need the portal (`xdg-desktop-portal-wlr`).

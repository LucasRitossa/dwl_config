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
| `xdg-desktop-portal/portals.conf` | Picks the wlr backend for ScreenCast/Screenshot (dwl is not in its `UseIn` list). |
| `xdg-desktop-portal-wlr/config` | Screencast chooser: `none`, so the single output captures without a dialog. |
| `dwl-run` | Session launcher: environment, user services, output mode, dwl + bar. |
| `refresh-mode` | Re-applies DP-1's 240Hz mode; called by `dwl-run` and `Super+Shift+F`. |
| `spotify-notify` | mako popup with the album cover when the Spotify track changes. |
| `mako/config` | Notification theme: Nordic palette, 96px icons. |

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
- `Super+Return` → `kitty`, `Super+D` → `fuzzel`, `Super+Shift+F` → reapply the
  240Hz mode (see *Monitor rules* below)

Desktop-specific choices:

- **XWayland is enabled** in `config.mk` (`-DXWAYLAND`). Steam/Proton and other
  X11-only clients need it; dwl spawns Xwayland on demand.
- **Monitor rules** pin `DP-1` (left, 240Hz panel) at `0,0` and `HDMI-A-1`
  (right) at `1920,0`. dwl always uses the *preferred* mode and DP-1's preferred
  mode is 60Hz, so `refresh-mode` sets `1920x1080@239.76` with `wlr-randr`.
  `dwl-run` calls it once at startup, and `Super+Shift+F` calls it again — dwl
  re-applies the preferred mode whenever it re-creates an output (DPMS wake,
  hotplug, nudged cable), which drops the panel back to 60Hz mid-session.
- The pointer block (`tap_to_click`, click/scroll methods, …) is kept even though
  this is a desktop: `dwl.c` applies every one of those symbols to each libinput
  pointer device, so removing them fails the build. They report unsupported for a
  mouse, so only `accel_profile`/`accel_speed` actually matter here.
- **Keyboard repeat** is `repeat_rate 50` / `repeat_delay 300`, the Wayland
  equivalent of the old X11 `xset r rate 300 50` (upstream's 25/600 felt slow).
- Brightness keys and the `powermode` bindings are gone: this machine has no
  `/sys/class/backlight` and no battery.

Source changes in `dwl.c`:

- Fullscreen fills the monitor's usable area instead of the whole output, so the
  bottom `somebar` stays visible. If the bar appears, disappears, or is resized,
  the fullscreen window follows the new usable area. (Same intent as the
  `dwm-actualfullscreen` patch carried in `~/.config/dwm_config`.)
- While a window is fullscreen, `Super+j` / `Super+k` cycles windows and moves
  fullscreen to the newly focused window.
- `focusmon` (bound to `Super+M`, and `Super+,` / `Super+.`) warps the pointer to
  the center of the newly focused monitor, so the cursor follows the monitor
  switch. `Super+M` moves right and wraps from the right-hand monitor back to the
  left one, so it toggles between the two outputs.
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

Two fixes in `src/` keep the bar attached across monitor hotplug:

- `bar.cpp` fills the `closed` slot of the layer-surface listener. When an
  output goes away (unplug, or the monitor is switched off) dwl closes the bar's
  layer surface, and libwayland **aborts the process** if an event has no
  listener — `listener function for opcode 1 of zwlr_layer_surface_v1 is NULL`
  in `~/.local/state/dwl-run.log`, exit status 134. The bar went down there and
  stayed down for the rest of the session, on every monitor, because dwl starts
  it only once. The handler drops that surface; the monitor then leaves with its
  `wl_output` global.
- `main.cpp` replays dwl's status lines for a monitor name it does not know yet
  (`pendingStatus`). dwl prints a new output's status in `createmon()` *before*
  the `wl_output` global exists, so those lines used to be dropped: a replugged
  monitor's bar only appeared at dwl's next status print, i.e. after a window
  focus or tag change, which on an idle desktop can be a long wait.

The right end of the bar is the **date and time**, from `somebar-clock`. dwl's
status stream has no field for it, so the clock is a separate one-line writer:
it waits for somebar's FIFO, then sends `status Mon 16 Nov 11:32 PM EST` on
every minute boundary (`somebar -c status ...`). Eastern time and a 12-hour
clock are pinned in the script, so the bar does not follow the machine's
timezone. It holds no state, so there is nothing to restart or clean up, and it
exits on its own when the session ends. Change the format in `somebar-clock` and
reload the session to apply it.

```sh
cd somebar
meson setup build --prefix="$HOME/.local"
ninja -C build
ninja -C build install
```

## spotify-notify

`spotify-notify` shows a mako popup when the Spotify track changes: the title,
`artist — album`, and the album cover, for five seconds.

It reads MPRIS metadata through `playerctl` once a second (playerctl 2.4.1's
`--all-players --follow` emits the first track and then goes quiet) and reacts
only to `spotify` (the desktop app) and `spotifyd` (the headless Connect
daemon), so browser media and other players do not trigger it. The current track
is recorded at startup, which means logging in does not produce a popup; only a
later track change does.

`mpris:artUrl` points at `i.scdn.co`. The cover is downloaded once into
`~/.cache/spotify-notify/<sha256>.jpg` (covers older than two weeks are pruned)
and falls back to the Papirus Spotify icon if the fetch fails. Notifications
reuse the previous mako id via `--replace-id`, so skipping tracks replaces the
popup instead of stacking them.

The popup asks for `--expire-time=5000`. The mako config below leaves
`ignore-timeout` off, so mako honours the five seconds; other notifications
still use mako's default timeout. `--once` sends the current track and exits, for
testing:

```sh
spotify-notify --once
```

`mako/config` themes these popups and every other notification: Nordic colours
matching dwl and somebar, JetBrainsMono 11, 96px icons, top-right, 10px margins.

```sh
install -m 755 spotify-notify "$HOME/.local/bin/spotify-notify"
install -Dm 644 mako/config "$HOME/.config/mako/config"
makoctl reload
```

`spotify-notify` is started by `dwl-run` after `mako`. It needs `playerctl`,
`curl`, `libnotify` (`notify-send`) and an icon theme that has `spotify`
(Papirus is the fallback path); all are in the runtime packages below.

## dwl-run

Starts the session. It sets the Wayland/EGL environment, starts `pipewire`,
`pipewire-pulse` and `wireplumber` (there is no systemd/elogind user session on
Artix), then runs `dbus-run-session -- dwl -s ...`.

dwl's `-s` command owns dwl's stdout, so everything started there must redirect
stdout or its output is parsed as bar status. `somebar` is `exec`'d last so it
keeps the stream. `mako`, `spotify-notify`, `swaybg` and the polkit agent are
started alongside it.

It also waits for the GPU before starting dwl. At boot the kernel runs on
`simpledrm` (the firmware framebuffer, exposed as `card0`) and only hands the
console to `nvidia-drm` (`card1`) a second or two later — after tty1 autologin
has already fired. dwl launched in that window makes wlroots enumerate `card0`
while the kernel is tearing it down, find no usable GPU, and exit with
`Failed to open device: '/dev/dri/card0'`. `dwl-run` therefore waits (up to 20s)
for the PCI card node under `/dev/dri/by-path/` and passes it as
`WLR_DRM_DEVICES`, which sidesteps both the race and `simpledrm` entirely.

The startup command also publishes the session environment to D-Bus with
`dbus-update-activation-environment`. That matters because `dbus-run-session`
starts the session bus *before* dwl, so the bus never learns `WAYLAND_DISPLAY`:
every D-Bus-activated service (the xdg-desktop-portal backends above all) then
starts without a compositor to talk to and fails silently. Screen sharing in
Discord was the visible symptom — an empty display picker.

Screen sharing goes through `xdg-desktop-portal-wlr`; see
`~/.config/xdg-desktop-portal/portals.conf` for why `dwl` has to name it
explicitly, and `~/.config/xdg-desktop-portal-wlr/config` for the one-output
`chooser_type=none` choice. Both are tracked here:

```sh
install -Dm 644 xdg-desktop-portal/portals.conf "$HOME/.config/xdg-desktop-portal/portals.conf"
install -Dm 644 xdg-desktop-portal-wlr/config "$HOME/.config/xdg-desktop-portal-wlr/config"
```

Everything is logged to `~/.local/state/dwl-run.log` (last 200 lines kept):
`dwl`'s own stderr, the `refresh-mode` mode change, and the state at startup —
`/dev/dri`, the pinned device and the logind session. If a session fails to
start, that file has the reason, and the tty shows the tail of it.

```sh
install -m 755 dwl-run "$HOME/.local/bin/dwl-run"
install -m 755 refresh-mode "$HOME/.local/bin/refresh-mode"
install -m 755 somebar-clock "$HOME/.local/bin/somebar-clock"
install -m 755 spotify-notify "$HOME/.local/bin/spotify-notify"
```

## Packages

Build: `wlroots0.20` (pkg-config name `wlroots-0.20`), `libinput`, `libxkbcommon`,
`wayland`, `wayland-protocols`, `pixman`, `libxcb` + `xcb-util-wm` (XWayland),
`meson`/`ninja` for somebar.

Runtime: `xorg-xwayland`, `kitty`, `fuzzel`, `grim`, `slurp`, `wl-clipboard`,
`swaylock`, `papirus-icon-theme`, `wlr-randr`, `mako`, `swaybg`, `wtype`
(clickable tags), `xdg-desktop-portal-wlr`, `playerctl`, `brightnessctl`,
`curl`, `libnotify`.

## Boot

The machine boots into dwl on tty1. Two changes outside this repo make that
happen:

1. `/etc/conf.d/agetty.tty1`: `agetty_options="--autologin luke"`
2. `~/.zprofile`, after the `PATH` line (the guard matters — without
   `DWL_ATTEMPTED` a crashing compositor would relaunch forever and you'd never
   see a shell):

   ```zsh
   if [[ $TTY == /dev/tty1 && -z $DWL_ATTEMPTED && -z $WAYLAND_DISPLAY ]]; then
       export DWL_ATTEMPTED=1
       "$HOME/.local/bin/dwl-run"
   fi
   ```

tty2–tty6 stay password-protected. They are now plain recovery shells (there is
no X11 session left to start): log in there to restart `dwl-run`, inspect a log,
or fix the config. `Ctrl+Alt+F1` returns to dwl itself, since dwl owns tty1.

Revert with `sudo sed -i 's/^agetty_options=.*/#agetty_options=""/' /etc/conf.d/agetty.tty1` (a backup of the original file is at
`/etc/conf.d/agetty.tty1.bak`) and by removing the block above. Note that this
reverts the *autologin*; it does not bring back X11 (see below).

## X11

There is no X server, no `startx` and no window manager on this machine: the
whole X11 session stack was removed (`xorg-server` and its xephyr/xnest/xvfb
variants, `xorg-xinit`, the `xorg-*` utilities and 75/100dpi fonts, `dmenu`,
`sxhkd`, `picom`, `arandr`, `xdotool`, `xclip`, `feh`, `flameshot`, `xterm`,
`xcompmgr`, the Xorg input/video drivers, the Xfce suite, `tigervnc`/`x11vnc`).

What stays is what X11 *clients* need, and only that:

| Package | Why |
| --- | --- |
| `xorg-xwayland` | Steam/Proton, wine, Discord and other X11-only clients |
| `xorg-server-common`, `xorg-xkbcomp`, `xorg-setxkbmap`, `xorgproto` | dependencies of Xwayland |
| `xorg-xrandr`, `xorg-xprop`, `xorg-fonts-encodings` | dependencies of `steam`, `lutris`, `umu-launcher`, `at-spi2-core` |

Xwayland is spawned on demand by dwl on the first X11 client, so `DISPLAY=:0`
appears inside the session only once something needs it. Verified after the
purge with `DISPLAY=:0 xrandr --query`, which reported the real 3840x1080
two-output layout.

## Known limits of this compositor

- No adaptive sync / VRR, no tearing control, no HDR: dwl does not implement
  them. Use `gamescope` for frame limiting/scaling, or a compositor with VRR
  support if 240Hz variable refresh matters more than the tiling model.
- No tablet support.
- Screenshots work through dwl's screencopy and image-copy-capture support;
  X11 apps that screenshot need the portal (`xdg-desktop-portal-wlr`).

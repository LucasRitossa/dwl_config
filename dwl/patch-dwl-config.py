#!/usr/bin/env python3
"""Patch dwl v0.9 config.def.h into the user's config."""
import re
from pathlib import Path

p = Path("config.h")
src = p.read_text()

# Appearance / colours
src = src.replace(
    "static const unsigned int borderpx         = 1;",
    "static const unsigned int borderpx         = 2;",
)
src = src.replace(
    "static const unsigned int snap             = 32;",
    "static const unsigned int snap             = 0;",
)
src = src.replace("COLOR(0x222222ff)", "COLOR(0x1D2021ff)")
src = src.replace("COLOR(0x444444ff)", "COLOR(0x282828ff)")
src = src.replace("COLOR(0x005577ff)", "COLOR(0x30b27aff)")
src = src.replace("COLOR(0xff0000ff)", "COLOR(0xfb4934ff)")

# Modifier + commands
src = src.replace("#define MODKEY WLR_MODIFIER_ALT", "#define MODKEY WLR_MODIFIER_LOGO")
src = src.replace(
    'static const char *termcmd[] = { "foot", NULL };',
    'static const char *termcmd[] = { "alacritty", NULL };',
)
src = src.replace(
    'static const char *menucmd[] = { "wmenu-run", NULL };',
    'static const char *menucmd[] = { "fuzzel", NULL };',
)

# Layouts: tile + floating only
layouts = '''static const Layout layouts[] = {
\t/* symbol     arrange function */
\t{ "[]=",      tile },
\t{ "><>",      NULL },    /* floating clients only */
};'''
src = re.sub(r"static const Layout layouts\[\] = \{.*?\n\};", layouts, src, count=1, flags=re.S)

# Rules
rules = '''static const Rule rules[] = {
\t/* app_id             title       tags mask     isfloating   monitor */
\t{ "flameshot",        NULL,       0,            1,           -1 },
\t{ "qemu-system-x86_64", NULL,     1,            0,           -1 },
};'''
src = re.sub(r"static const Rule rules\[\] = \{.*?\n\};", rules, src, count=1, flags=re.S)

# Keyboard layout
xkb = '''static const struct xkb_rule_names xkb_rules = {
\t.layout = "us",
\t.options = "caps:escape,altwin:swap_lalt_lwin",
};'''
src = re.sub(
    r"static const struct xkb_rule_names xkb_rules = \{.*?\n\};",
    xkb, src, count=1, flags=re.S,
)

keys = r'''static const Key keys[] = {
	/* modifier                  key                  function          argument */
	{ MODKEY,                    XKB_KEY_d,           spawn,            {.v = menucmd} },
	{ MODKEY,                    XKB_KEY_Return,      spawn,            {.v = termcmd} },
	{ MODKEY|WLR_MODIFIER_SHIFT, XKB_KEY_r,           spawn,            SHCMD("alacritty -e htop") },
	{ MODKEY|WLR_MODIFIER_SHIFT, XKB_KEY_b,           spawn,            SHCMD("alacritty -e pulsemixer") },
	{ MODKEY,                    XKB_KEY_y,           spawn,            SHCMD("alacritty -e ncmpcpp") },
	{ MODKEY,                    XKB_KEY_r,           spawn,            SHCMD("alacritty -e lf") },
	{ MODKEY|WLR_MODIFIER_SHIFT, XKB_KEY_e,           spawn,            SHCMD("grim -g \"$(slurp)\" - | wl-copy") },
	{ MODKEY|WLR_MODIFIER_SHIFT, XKB_KEY_d,           spawn,            SHCMD("discord") },
	{ MODKEY,                    XKB_KEY_w,           spawn,            SHCMD("librewolf") },
	{ MODKEY,                    XKB_KEY_period,      spawn,            SHCMD("mpc next") },
	{ MODKEY,                    XKB_KEY_comma,       spawn,            SHCMD("mpc prev") },
	{ MODKEY,                    XKB_KEY_p,           spawn,            SHCMD("mpc toggle") },
	{ MODKEY,                    XKB_KEY_bracketleft, spawn,            SHCMD("mpc seek -10") },
	{ MODKEY,                    XKB_KEY_bracketright,spawn,            SHCMD("mpc seek +10") },
	{ MODKEY,                    XKB_KEY_b,           spawn,            SHCMD("somebar -c toggle selected") },

	{ MODKEY,                    XKB_KEY_j,           focusstack,       {.i = +1} },
	{ MODKEY,                    XKB_KEY_k,           focusstack,       {.i = -1} },
	{ MODKEY|WLR_MODIFIER_SHIFT, XKB_KEY_i,           incnmaster,       {.i = +1} },
	{ MODKEY|WLR_MODIFIER_SHIFT, XKB_KEY_o,           incnmaster,       {.i = -1} },
	{ MODKEY,                    XKB_KEY_h,           setmfact,         {.f = -0.05f} },
	{ MODKEY,                    XKB_KEY_l,           setmfact,         {.f = +0.05f} },
	{ MODKEY,                    XKB_KEY_q,           killclient,       {0} },
	{ MODKEY,                    XKB_KEY_f,           togglefullscreen, {0} },
	{ MODKEY,                    XKB_KEY_space,       zoom,             {0} },
	{ MODKEY|WLR_MODIFIER_SHIFT, XKB_KEY_space,       togglefloating,   {0} },
	{ MODKEY|WLR_MODIFIER_SHIFT, XKB_KEY_u,           unfloat,          {0} },
	{ MODKEY,                    XKB_KEY_0,           view,             {.ui = ~0} },
	{ MODKEY|WLR_MODIFIER_SHIFT, XKB_KEY_0,           tag,              {.ui = ~0} },
	{ MODKEY,                    XKB_KEY_comma,       focusmon,         {.i = WLR_DIRECTION_LEFT} },
	{ MODKEY,                    XKB_KEY_period,      focusmon,         {.i = WLR_DIRECTION_RIGHT} },
	{ MODKEY|WLR_MODIFIER_SHIFT, XKB_KEY_comma,       tagmon,           {.i = WLR_DIRECTION_LEFT} },
	{ MODKEY|WLR_MODIFIER_SHIFT, XKB_KEY_period,      tagmon,           {.i = WLR_DIRECTION_RIGHT} },
	{ MODKEY,                    XKB_KEY_m,           focusmon,         {.i = WLR_DIRECTION_RIGHT} },
	{ MODKEY|WLR_MODIFIER_SHIFT, XKB_KEY_m,           tagmon,           {.i = WLR_DIRECTION_RIGHT} },

	/* media, brightness, lock, screenshots */
	{ 0, XKB_KEY_XF86AudioRaiseVolume,  spawn, SHCMD("pactl set-sink-volume @DEFAULT_SINK@ +5%") },
	{ 0, XKB_KEY_XF86AudioLowerVolume,  spawn, SHCMD("pactl set-sink-volume @DEFAULT_SINK@ -5%") },
	{ 0, XKB_KEY_XF86AudioMute,         spawn, SHCMD("pactl set-sink-mute @DEFAULT_SINK@ toggle") },
	{ 0, XKB_KEY_XF86AudioMicMute,      spawn, SHCMD("pactl set-source-mute @DEFAULT_SOURCE@ toggle") },
	{ 0, XKB_KEY_XF86AudioPlay,         spawn, SHCMD("playerctl play-pause") },
	{ 0, XKB_KEY_XF86AudioNext,         spawn, SHCMD("playerctl next") },
	{ 0, XKB_KEY_XF86AudioPrev,         spawn, SHCMD("playerctl previous") },
	{ 0, XKB_KEY_XF86MonBrightnessUp,   spawn, SHCMD("brightnessctl set +5%") },
	{ 0, XKB_KEY_XF86MonBrightnessDown, spawn, SHCMD("brightnessctl set 5%-") },
	{ MODKEY|WLR_MODIFIER_SHIFT, XKB_KEY_l, spawn, SHCMD("swaylock -f") },
	{ 0, XKB_KEY_Print, spawn, SHCMD("grim -g \"$(slurp)\" - | wl-copy") },

	/* power mode (power-profiles-daemon): cycle saver -> balanced -> performance */
	{ MODKEY,                    XKB_KEY_F4, spawn, SHCMD("powermode cycle") },
	{ MODKEY|WLR_MODIFIER_SHIFT, XKB_KEY_F4, spawn, SHCMD("powermode hold toggle") },

	TAGKEYS(                     XKB_KEY_1,           0),
	TAGKEYS(                     XKB_KEY_2,           1),
	TAGKEYS(                     XKB_KEY_3,           2),
	TAGKEYS(                     XKB_KEY_4,           3),
	TAGKEYS(                     XKB_KEY_5,           4),
	TAGKEYS(                     XKB_KEY_6,           5),
	TAGKEYS(                     XKB_KEY_7,           6),
	TAGKEYS(                     XKB_KEY_8,           7),
	TAGKEYS(                     XKB_KEY_9,           8),
	{ MODKEY|WLR_MODIFIER_SHIFT, XKB_KEY_q,           quit,             {0} },

	/* Ctrl-Alt-Backspace and Ctrl-Alt-Fx used to be handled by X server */
	{ WLR_MODIFIER_CTRL|WLR_MODIFIER_ALT,XKB_KEY_BackSpace, quit, {0} },
	/* Ctrl-Alt-Fx is used to switch to another VT, if you don't know what a VT is
	 * do not remove them.
	 */
#define CHVT(n) { WLR_MODIFIER_CTRL|WLR_MODIFIER_ALT,XKB_KEY_F##n, chvt, {.ui = (n)} }
	CHVT(1), CHVT(2), CHVT(3), CHVT(4), CHVT(5), CHVT(6),
	CHVT(7), CHVT(8), CHVT(9), CHVT(10), CHVT(11), CHVT(12),
};'''

m = re.search(r"static const Key keys\[\] = \{.*?\n\};", src, flags=re.S)
if not m:
    raise SystemExit("keys[] block not found")
src = src[:m.start()] + keys + src[m.end():]

axes = '''static const Axis axes[] = {
\t{ MODKEY, AxisUp,   spawn, SHCMD("pactl set-sink-volume @DEFAULT_SINK@ +2%") },
\t{ MODKEY, AxisDown, spawn, SHCMD("pactl set-sink-volume @DEFAULT_SINK@ -2%") },
};'''
m = re.search(r"static const Axis axes\[\] = \{.*?\n\};", src, flags=re.S)
if m:
    src = src[:m.start()] + axes + src[m.end():]

p.write_text(src)
print("patched config.h")

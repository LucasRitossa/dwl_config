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

# Pointer devices: dwl.c applies all of these to every libinput pointer, so the
# symbols are mandatory on a desktop too. Kept at upstream values (inert for a
# mouse); the block is only annotated.
pointer = '''/* Pointer devices.
 *
 * dwl.c applies every one of these to each libinput pointer device, so the
 * symbols cannot be removed from the config on a desktop: the build fails on
 * undefined identifiers. They are kept at upstream values and are inert for a
 * mouse (tap/click/scroll-method settings report unsupported). Only
 * accel_profile/accel_speed affect the mouse here. */
static const int tap_to_click = 1;
static const int tap_and_drag = 1;
static const int drag_lock = 1;
static const int natural_scrolling = 0;
static const int disable_while_typing = 1;
static const int left_handed = 0;
static const int middle_button_emulation = 0;
/* You can choose between:
LIBINPUT_CONFIG_SCROLL_NO_SCROLL
LIBINPUT_CONFIG_SCROLL_2FG
LIBINPUT_CONFIG_SCROLL_EDGE
LIBINPUT_CONFIG_SCROLL_ON_BUTTON_DOWN
*/
static const enum libinput_config_scroll_method scroll_method = LIBINPUT_CONFIG_SCROLL_2FG;

/* You can choose between:
LIBINPUT_CONFIG_CLICK_METHOD_NONE
LIBINPUT_CONFIG_CLICK_METHOD_BUTTON_AREAS
LIBINPUT_CONFIG_CLICK_METHOD_CLICKFINGER
*/
static const enum libinput_config_click_method click_method = LIBINPUT_CONFIG_CLICK_METHOD_BUTTON_AREAS;

/* You can choose between:
LIBINPUT_CONFIG_SEND_EVENTS_ENABLED
LIBINPUT_CONFIG_SEND_EVENTS_DISABLED
LIBINPUT_CONFIG_SEND_EVENTS_DISABLED_ON_EXTERNAL_MOUSE
*/
static const uint32_t send_events_mode = LIBINPUT_CONFIG_SEND_EVENTS_ENABLED;

/* You can choose between:
LIBINPUT_CONFIG_ACCEL_PROFILE_FLAT
LIBINPUT_CONFIG_ACCEL_PROFILE_ADAPTIVE
*/
static const enum libinput_config_accel_profile accel_profile = LIBINPUT_CONFIG_ACCEL_PROFILE_ADAPTIVE;
static const double accel_speed = 0.0;

/* You can choose between:
LIBINPUT_CONFIG_TAP_MAP_LRM -- 1/2/3 finger tap maps to left/right/middle
LIBINPUT_CONFIG_TAP_MAP_LMR -- 1/2/3 finger tap maps to left/middle/right
*/
static const enum libinput_config_tap_button_map button_map = LIBINPUT_CONFIG_TAP_MAP_LRM;
'''
src = re.sub(
    r"/\* Trackpad \*/.*?static const enum libinput_config_tap_button_map button_map = LIBINPUT_CONFIG_TAP_MAP_LRM;\n",
    pointer,
    src,
    count=1,
    flags=re.S,
)

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
\t.options = "caps:escape",
};'''
src = re.sub(
    r"static const struct xkb_rule_names xkb_rules = \{.*?\n\};",
    xkb, src, count=1, flags=re.S,
)

# Monitor rules: desktop outputs with explicit placement (DP-1 left, HDMI-A-1 right).
monrules = '''static const MonitorRule monrules[] = {
   /* name        mfact  nmaster scale layout       rotate/reflect                x    y
    *
    * Two 1920x1080 outputs: DP-1 (left, 240Hz panel) and HDMI-A-1 (right).
    * Refresh rate is not configurable here -- dwl always picks the preferred
    * mode, so dwl-run sets DP-1's 239.76Hz mode with wlr-randr. */
\t{ "DP-1",     0.55f, 1,      1,    &layouts[0], WL_OUTPUT_TRANSFORM_NORMAL,    0,   0 },
\t{ "HDMI-A-1", 0.55f, 1,      1,    &layouts[0], WL_OUTPUT_TRANSFORM_NORMAL, 1920,   0 },
\t/* default monitor rule: can be changed but cannot be eliminated; at least one monitor rule must exist */
\t{ NULL,       0.55f, 1,      1,    &layouts[0], WL_OUTPUT_TRANSFORM_NORMAL,   -1,  -1 },
};'''
m = re.search(r"static const MonitorRule monrules\[\] = \{.*?\n\};", src, flags=re.S)
if not m:
    raise SystemExit("monrules[] block not found")
src = src[:m.start()] + monrules + src[m.end():]

keys = r'''static const Key keys[] = {
	/* modifier                  key                  function          argument */
	{ MODKEY,                    XKB_KEY_d,           spawn,            {.v = menucmd} },
	{ MODKEY,                    XKB_KEY_Return,      spawn,            {.v = termcmd} },
	{ MODKEY|WLR_MODIFIER_SHIFT, XKB_KEY_r,           spawn,            SHCMD("alacritty -e htop") },
	{ MODKEY|WLR_MODIFIER_SHIFT, XKB_KEY_b,           spawn,            SHCMD("alacritty -e pulsemixer") },
	{ MODKEY,                    XKB_KEY_r,           spawn,            SHCMD("alacritty -e lf") },
	{ MODKEY|WLR_MODIFIER_SHIFT, XKB_KEY_e,           spawn,            SHCMD("grim -g \"$(slurp)\" - | wl-copy") },
	{ MODKEY|WLR_MODIFIER_SHIFT, XKB_KEY_d,           spawn,            SHCMD("discord") },
	{ MODKEY,                    XKB_KEY_w,           spawn,            SHCMD("librewolf") },

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
	{ MODKEY,                    XKB_KEY_Tab,         setlayout,        {0} },
	{ MODKEY,                    XKB_KEY_0,           view,             {.ui = ~0} },
	{ MODKEY|WLR_MODIFIER_SHIFT, XKB_KEY_0,           tag,              {.ui = ~0} },
	{ MODKEY,                    XKB_KEY_comma,       focusmon,         {.i = WLR_DIRECTION_LEFT} },
	{ MODKEY,                    XKB_KEY_period,      focusmon,         {.i = WLR_DIRECTION_RIGHT} },
	{ MODKEY|WLR_MODIFIER_SHIFT, XKB_KEY_comma,       tagmon,           {.i = WLR_DIRECTION_LEFT} },
	{ MODKEY|WLR_MODIFIER_SHIFT, XKB_KEY_period,      tagmon,           {.i = WLR_DIRECTION_RIGHT} },
	{ MODKEY,                    XKB_KEY_m,           focusmon,         {.i = WLR_DIRECTION_RIGHT} },
	{ MODKEY|WLR_MODIFIER_SHIFT, XKB_KEY_m,           tagmon,           {.i = WLR_DIRECTION_RIGHT} },

	/* media, lock, screenshots */
	{ 0, XKB_KEY_XF86AudioRaiseVolume,  spawn, SHCMD("pactl set-sink-volume @DEFAULT_SINK@ +5%") },
	{ 0, XKB_KEY_XF86AudioLowerVolume,  spawn, SHCMD("pactl set-sink-volume @DEFAULT_SINK@ -5%") },
	{ 0, XKB_KEY_XF86AudioMute,         spawn, SHCMD("pactl set-sink-mute @DEFAULT_SINK@ toggle") },
	{ 0, XKB_KEY_XF86AudioMicMute,      spawn, SHCMD("pactl set-source-mute @DEFAULT_SOURCE@ toggle") },
	{ 0, XKB_KEY_XF86AudioPlay,         spawn, SHCMD("playerctl play-pause") },
	{ 0, XKB_KEY_XF86AudioNext,         spawn, SHCMD("playerctl next") },
	{ 0, XKB_KEY_XF86AudioPrev,         spawn, SHCMD("playerctl previous") },
	{ MODKEY|WLR_MODIFIER_SHIFT, XKB_KEY_l, spawn, SHCMD("swaylock -f") },
	{ 0, XKB_KEY_Print, spawn, SHCMD("grim -g \"$(slurp)\" - | wl-copy") },

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

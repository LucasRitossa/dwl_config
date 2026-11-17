// somebar - dwl bar
// See LICENSE file for copyright and license details.
//
// Active configuration. config.def.hpp is kept as the upstream reference
// (with contrib/clickable-tags-using-wtype.patch applied).
// Palette matches dwl/config.h, fuzzel.ini and ~/.config/dwm_config/config.h:
//   bg 1D2021 / fg aaaaaa / selected ffffff / accent 30b27a

#pragma once
#include "common.hpp"

// Clickable tags without the dwl IPC patch: clicks are turned into the
// keystrokes dwl already binds (Super+N / Super+Shift+N) via wtype.
// MODKEY must match dwl's MODKEY (WLR_MODIFIER_LOGO -> "logo").
#define WTYPE "/usr/bin/wtype"
#define MODKEY "logo"

constexpr bool topbar = false;

constexpr int paddingX = 10;
constexpr int paddingY = 2;

/* Tag indicators. Selected tags get a thick line across the top of the cell,
 * occupied tags that are not selected get a dot. */
constexpr int indicatorHeight = 3;
constexpr int indicatorDotRadius = 2;

// See https://docs.gtk.org/Pango/type_func.FontDescription.from_string.html
constexpr const char* font = "JetBrainsMono Nerd Font 14";

constexpr ColorScheme colorInactive = {Color(0xaa, 0xaa, 0xaa), Color(0x1d, 0x20, 0x21)};
constexpr ColorScheme colorActive = {Color(0xff, 0xff, 0xff), Color(0x1d, 0x20, 0x21)};
constexpr const char* termcmd[] = {"kitty", nullptr};

static std::vector<std::string> tagNames = {
	"1", "2", "3",
	"4", "5", "6",
	"7", "8", "9",
};

constexpr Button buttons[] = {
	{ ClkTagBar,       BTN_LEFT,   view,       {0} },
	{ ClkTagBar,       BTN_RIGHT,  tag,        {0} },
	{ ClkStatusText,   BTN_RIGHT,  spawn,      {.v = termcmd} },
};

// somebar - dwl bar
// See LICENSE file for copyright and license details.
//
// Active configuration. config.def.hpp is kept as the upstream reference.
// Palette matches dwl/config.h, fuzzel.ini and ~/.config/dwm_config/config.h:
//   bg 1D2021 / fg aaaaaa / selected ffffff / accent 30b27a

#pragma once
#include "common.hpp"

constexpr bool topbar = true;

constexpr int paddingX = 10;
constexpr int paddingY = 2;

// See https://docs.gtk.org/Pango/type_func.FontDescription.from_string.html
constexpr const char* font = "JetBrainsMono Nerd Font 14";

constexpr ColorScheme colorInactive = {Color(0xaa, 0xaa, 0xaa), Color(0x1d, 0x20, 0x21)};
constexpr ColorScheme colorActive = {Color(0xff, 0xff, 0xff), Color(0x1d, 0x20, 0x21)};
constexpr const char* termcmd[] = {"alacritty", nullptr};

static std::vector<std::string> tagNames = {
	"1", "2", "3",
	"4", "5", "6",
	"7", "8", "9",
};

constexpr Button buttons[] = {
	{ ClkStatusText,   BTN_RIGHT,  spawn,      {.v = termcmd} },
};

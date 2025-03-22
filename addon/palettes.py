from typing import Tuple, List, NamedTuple, Dict

# Color palettes can be defined in _4TONE_COLOR_PALETTES and _2TONE_COLOR_PALETTES lists
# to be dynamically loaded into enum properties and a COLOR_PALETTES lookup dictionary.
# Color tuple should include hex RGB colors from darkest to lightest.


class ColorPalette(NamedTuple):
    id: str
    label: str
    colors: Tuple[int, ...]


_4TONE_COLOR_PALETTES: List[ColorPalette] = [
    ColorPalette(
        "4tone_grayscale",
        "Grayscale",
        (0x000000, 0x545454, 0xA9A9A9, 0xFFFFFF),
    ),
    ColorPalette(
        "4tone_gb_dmg",
        "Game Boy DMG",
        (0x294139, 0x395849, 0x5A7942, 0x7B8210),
    ),
    ColorPalette(
        "4tone_gb_pocket",
        "Game Boy Pocket",
        (0x181818, 0x4A5038, 0x8C926B, 0xC6CBA5),
    ),
    ColorPalette(
        "4tone_gb_light",
        "Game Boy Light",
        (0x005138, 0x00694A, 0x009A73, 0x00B184),
    ),
    ColorPalette(
        "4tone_gbc_orange",
        "Game Boy Color Orange",
        (0x000000, 0xCE0031, 0xEFBE52, 0xFFFBFF),
    ),
    ColorPalette(
        "4tone_gbc_inverted",
        "Game Boy Color Inverted",
        (0xFFFBFF, 0xEFA64A, 0x18826B, 0x000000),
    ),
    ColorPalette(
        "4tone_gbc_pastel_mix",
        "Game Boy Color Pastel Mix",
        (0x0, 0x9CAED, 0xEF92A5, 0xF7E7BD),
    ),
    ColorPalette(
        "4tone_sgb_1a",
        "Super Game Boy 1A",
        (0x311852, 0xA52821, 0xD6924A, 0xF7E3C6),
    ),
    ColorPalette(
        "4tone_sgb_2b",
        "Super Game Boy 2B",
        (0x52005A, 0xF73000, 0xF7E352, 0xF7F3F7),
    ),
    ColorPalette(
        "4tone_sgb_3a",
        "Super Game Boy 3A",
        (0x314963, 0xF76129, 0x73BABD, 0xF7CB94),
    ),
    ColorPalette(
        "4tone_sgb_3c",
        "Super Game Boy 3C",
        (0x21205A, 0x00B2F7, 0xF7F37B, 0xDEA2C6),
    ),
    ColorPalette(
        "4tone_sgb_3f",
        "Super Game Boy 3F",
        (0x424142, 0xF7CB00, 0xF769F7, 0x7B79C6),
    ),
    ColorPalette(
        "4tone_sgb_4c",
        "Super Game Boy 4C",
        (0x080000, 0x949ADE, 0xD69ACE, 0xF7DBDE),
    ),
    ColorPalette(
        "4tone_sgb_4e",
        "Super Game Boy 4E",
        (0x002031, 0x7B598C, 0xDEA27B, 0xF7D3A5),
    ),
    ColorPalette(
        "4tone_sgb_4f",
        "Super Game Boy 4F",
        (0x390000, 0x84009C, 0xD682D6, 0xB5CBCE),
    ),
    ColorPalette(
        "4tone_arcade_sunrise1",
        "Arcade Sunrise 1",
        (0x3DC4E4, 0x94EFCC, 0xCBFFCE, 0xF0FFEC),
    ),
    ColorPalette(
        "4tone_arcade_sunrise2",
        "Arcade Sunrise 2",
        (0x9261CA, 0xD148BA, 0xF897B6, 0xB5D1F9),
    ),
    ColorPalette(
        "4tone_arcade_sunset1",
        "Arcade Sunset 1",
        (0xA728A9, 0xF2408A, 0xFFA26C, 0xFFDB83),
    ),
    ColorPalette(
        "4tone_arcade_sunset2",
        "Arcade Sunset 2",
        (0xF75759, 0xFF7F52, 0xFFBA4A, 0xFADE73),
    ),
    ColorPalette(
        "4tone_arcade_skyblue",
        "Arcade Sky Blue",
        (0x26A7FB, 0x45C3FD, 0xA0EBFF, 0xE7FAFF),
    ),
    ColorPalette(
        "4tone_arcade_evening",
        "Arcade Evening",
        (0x7D26E7, 0xA93CF1, 0xF479B8, 0xFFB88E),
    ),
    ColorPalette(
        "4tone_arcade_night1",
        "Arcade Night 1",
        (0x360B76, 0x5717B6, 0xA437F2, 0xD255FB),
    ),
    ColorPalette(
        "4tone_arcade_night2",
        "Arcade Night 2",
        (0x282246, 0x3D3669, 0x524885, 0x6D63AC),
    ),
]
"""4 tone color palettes definitions as a ColorPalette named tuple."""

_2TONE_COLOR_PALETTES = [
    ColorPalette(
        "2tone_gb_dmg",
        "Game Boy DMG",
        (0x294139, 0x7B8210),
    ),
    ColorPalette(
        "2tone_gb_pocket",
        "Game Boy Pocket",
        (0x181818, 0xC6CBA5),
    ),
    ColorPalette(
        "2tone_gb_light",
        "Game Boy Light",
        (0x005138, 0x00B184),
    ),
    ColorPalette(
        "2tone_gbc_orange",
        "Game Boy Color Orange",
        (0xCE0031, 0xEFBE52),
    ),
    ColorPalette(
        "2tone_gbc_inverted",
        "Game Boy Color Inverted",
        (0xEFA64A, 0x18826B),
    ),
    ColorPalette(
        "2tone_gbc_pastel_mix",
        "Game Boy Color Pastel Mix",
        (0x9CAED, 0xEF92A5),
    ),
    ColorPalette(
        "2tone_sgb_1a",
        "Super Game Boy 1A",
        (0x311852, 0xD6924A),
    ),
    ColorPalette(
        "2tone_sgb_2b",
        "Super Game Boy 2B",
        (0xF73000, 0xF7E352),
    ),
    ColorPalette(
        "2tone_sgb_3a",
        "Super Game Boy 3A",
        (0xF76129, 0x73BABD),
    ),
    ColorPalette(
        "2tone_sgb_3c",
        "Super Game Boy 3C",
        (0x00B2F7, 0xF7F37B),
    ),
    ColorPalette(
        "2tone_sgb_3f",
        "Super Game Boy 3F",
        (0x424142, 0x7B79C6),
    ),
    ColorPalette(
        "2tone_sgb_4c",
        "Super Game Boy 4C",
        (0x949ADE, 0xF7DBDE),
    ),
    ColorPalette(
        "2tone_sgb_4e",
        "Super Game Boy 4E",
        (0x7B598C, 0xF7D3A5),
    ),
    ColorPalette(
        "2tone_sgb_4f",
        "Super Game Boy 4F",
        (0x390000, 0xB5CBCE),
    ),
    ColorPalette(
        "2tone_arcade_sunrise1",
        "Arcade Sunrise 1",
        (0x3DC4E4, 0xF0FFEC),
    ),
    ColorPalette(
        "2tone_arcade_sunrise2",
        "Arcade Sunrise 2",
        (0x9261CA, 0xB5D1F9),
    ),
    ColorPalette(
        "2tone_arcade_sunset1",
        "Arcade Sunset 1",
        (0xF2408A, 0xFFDB83),
    ),
    ColorPalette(
        "2tone_arcade_sunset2",
        "Arcade Sunset 2",
        (0xF75759, 0xFADE73),
    ),
    ColorPalette(
        "2tone_arcade_skyblue",
        "Arcade Sky Blue",
        (0x26A7FB, 0xE7FAFF),
    ),
    ColorPalette(
        "2tone_arcade_evening",
        "Arcade Evening",
        (0x7D26E7, 0xFFB88E),
    ),
    ColorPalette(
        "2tone_arcade_night1",
        "Arcade Night 1",
        (0x360B76, 0xD255FB),
    ),
    ColorPalette(
        "2tone_arcade_night2",
        "Arcade Night 2",
        (0x282246, 0x6D63AC),
    ),
    ColorPalette(
        "2tone_bw",
        "Black & white",
        (0x000000, 0xFFFFFF),
    ),
    ColorPalette(
        "2tone_nokia_3310",
        "Nokia 3310",
        (0x021003, 0x73A582),
    ),
    ColorPalette(
        "2tone_nokia_3310_backlight",
        "Nokia 3310 backlight",
        (0x000302, 0xA1BB4C),
    ),
]
"""2 tone color palettes definitions as a ColorPalette named tuple."""


def generate_palette_data(
    palette_list: List[ColorPalette],
) -> Tuple[List[Tuple[float, float, float, float]], Dict[str, Tuple[int, ...]]]:
    """Generate palette data to prepare EnumProperty item list and lookup dictionary out of list of ColorPalette items."""

    enum_items: List[Tuple[float, float, float, float]] = []
    color_palette_dict: Dict[str, Tuple[int, ...]] = {}
    sorted_palettes = sorted(palette_list, key=lambda palette: palette.label)
    for idx, palette in enumerate(sorted_palettes):
        enum_items.append((palette.id, palette.label, "", idx + 1))
        color_palette_dict[palette.id] = palette.colors
    return enum_items, color_palette_dict


palette_2tone_enum_items, _2TONE_CP_DICT = generate_palette_data(_2TONE_COLOR_PALETTES)
palette_4tone_enum_items, _4TONE_CP_DICT = generate_palette_data(_4TONE_COLOR_PALETTES)
COLOR_PALETTES: Dict[str, Tuple[int, ...]] = _2TONE_CP_DICT | _4TONE_CP_DICT


class Color:
    """Class for interfacing with color palettes lookup dictionary and convert hex values to linear RGB."""

    black = (0.0, 0.0, 0.0, 1.0)
    white = (1.0, 1.0, 1.0, 1.0)

    def from_hex(hex_val: int) -> Tuple[float, float, float, float]:
        """Get (R,G,B,A) tuple compatible with Blender inputs."""

        r = ((hex_val >> 16) & 0xFF) / 255.0
        g = ((hex_val >> 8) & 0xFF) / 255.0
        b = (hex_val & 0xFF) / 255.0
        a = 1.0
        return (
            Color.srgb_to_linear(r),
            Color.srgb_to_linear(g),
            Color.srgb_to_linear(b),
            a,
        )

    def from_palette(palette_name: str) -> Tuple[Tuple[float, float, float, float]]:
        """Get tuple of (R,G,B,A) values from specified palette."""

        if palette_name in COLOR_PALETTES:
            hex_values = COLOR_PALETTES[palette_name]
            return tuple(Color.from_hex(val) for val in hex_values)
        else:
            raise ValueError(f"Palette '{palette_name}' not found")

    def srgb_to_linear(c: float) -> float:
        """Convert sRGB color component to linear space."""

        if c <= 0.04045:
            return c / 12.92
        return ((c + 0.055) / 1.055) ** 2.4

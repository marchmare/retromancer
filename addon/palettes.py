from typing import Tuple

palette_2tone_enum_items = [
    ("2tone_bw_pallette", "Black & white", "", 1),
    ("2tone_eink_pallette", "E-Ink", "", 2),
    ("2tone_3310_pallette", "Nokia 3310", "", 3),
    ("2tone_3310_backlight_pallette", "Nokia 3310 backlit", "", 4),
    ("2tone_arcade_sunrise_pallette", "Arcade sunrise ", "", 5),
    ("2tone_arcade_noon_pallette", "Arcade noon ", "", 6),
    ("2tone_arcade_sunset_pallette", "Arcade sunset ", "", 7),
    ("2tone_arcade_evening_pallette", "Arcade evening ", "", 8),
]
palette_4tone_enum_items = [
    (
        f"palette_name",
        "Full palette name",
        "",
        1,
    )
]

COLOR_PALETTES = {
    "2tone_bw_pallette": (0x000000FF, 0xFFFFFFFF),
    "2tone_eink_pallette": (0x47504BFF, 0xCAD1C9FF),
    "2tone_3310_pallette": (0x332F26FF, 0x576743FF),
    "2tone_3310_backlight_pallette": (0x283710FF, 0x8CC602FF),
    "2tone_arcade_sunrise_pallette": (0x283710FF, 0x8CC602FF),
    "2tone_arcade_noon_pallette": (0x283710FF, 0x8CC602FF),
    "2tone_arcade_sunset_pallette": (0x283710FF, 0x8CC602FF),
    "2tone_arcade_evening_pallette": (0x283710FF, 0x8CC602FF),
}


class Color:
    black = (0.0, 0.0, 0.0, 1.0)
    white = (1.0, 1.0, 1.0, 1.0)

    def from_hex(hex_val: int) -> Tuple[float, float, float, float]:
        # return (r, g, b, a)
        pass

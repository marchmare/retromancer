from bpy.props import EnumProperty, FloatProperty

from ..textures import threshold_enum_items
from ..palettes import palette_4tone_enum_items, Color as c
from ._tone_dither import _ToneDitherTemplate


class CompositorNodeRetromancer4ToneDither(_ToneDitherTemplate):
    """4 tone (2-bit) palette ordered dither effect using provided threshold map texture."""

    bl_idname = "CompositorNodeRetromancer4ToneDither"
    bl_label = "4-Tone Ordered Dither"
    bl_icon = "SHADERFX"
    bl_width_default = 210

    _CR_POS = (0.0, 0.0615, 0.2431, 1.0)
    _PRESET = "4tone_grayscale"

    def update_texture(self, context) -> None:
        """threshold_enum_prop update callback"""
        for i in list(range(len(self._CR_POS) - 1)) + ["alpha"]:
            dither_node = self.node_tree.nodes.get(f"dither_{i}")
            dither_node.threshold_enum_prop = self.threshold_enum_prop

    def _update_color_palette(self, preset: str) -> None:
        """Load color values from preset into color sockets."""
        preset_values = iter(c.from_palette(preset))
        for i in range(1, range(len(self._CR_POS) - 1)):
            self.inputs[f"Color {i}"].default_value = next(preset_values)

    def update_preset(self, context) -> None:
        """palette_presets_enum_prop update callback"""
        if not context.property:
            return
        prop = self.parse_datapath(context.property[1])
        preset = getattr(self, prop)
        self._update_color_palette(preset)

    def _update_ramp(self, name: str, property: str) -> None:
        """Update position of all color ramps' stops based on values from each tone_ramp_x_prop"""
        prop_val = getattr(self, property)
        elem_idx = int(property.split("_")[-2])
        color_ramp_node = self.node_tree.nodes.get(name)
        color_ramp_node.color_ramp.elements[elem_idx].position = prop_val

    def update_tone_ramps(self, context) -> None:
        """tone_ramp_x_prop update callback"""
        if not context.property:
            return
        for tone in list(range(len(self._CR_POS) - 1)):
            prop = self.parse_datapath(context.property[1])
            self._update_ramp(f"cr_mask_{tone}", prop)
            self._update_ramp(f"cr_gradient_{tone}", prop)

    threshold_enum_prop: EnumProperty(items=threshold_enum_items, name="", update=update_texture)  # type: ignore

    palette_presets_enum_prop: EnumProperty(  # type: ignore
        items=palette_4tone_enum_items, name="Preset", update=update_preset
    )

    _TONE_RAMP_KWARGS = dict(subtype="FACTOR", update=update_tone_ramps, min=0.0, max=1.0)
    tone_ramp_0_prop: FloatProperty(name="tone_pos_0", default=_CR_POS[0], **_TONE_RAMP_KWARGS)  # type: ignore
    tone_ramp_1_prop: FloatProperty(name="tone_pos_1", default=_CR_POS[1], **_TONE_RAMP_KWARGS)  # type: ignore
    tone_ramp_2_prop: FloatProperty(name="tone_pos_3", default=_CR_POS[2], **_TONE_RAMP_KWARGS)  # type: ignore
    tone_ramp_3_prop: FloatProperty(name="tone_pos_3", default=_CR_POS[3], **_TONE_RAMP_KWARGS)  # type: ignore

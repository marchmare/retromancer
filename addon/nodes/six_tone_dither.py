from bpy.props import EnumProperty, FloatProperty

from ..textures import threshold_enum_items
from ..palettes import Color as c
from ._tone_dither import _ToneDitherTemplate


class CompositorNodeRetromancer6ToneDither(_ToneDitherTemplate):
    """6 tone palette ordered dither effect using provided threshold map texture."""

    bl_idname = "CompositorNodeRetromancer6ToneDither"
    bl_label = "6-Tone Ordered Dither"
    bl_icon = "SHADERFX"
    bl_width_default = 300

    _CR_POS = (0.0, 0.0322, 0.0968, 0.226, 0.452, 1.0)
    _PRESET = "6tone_grayscale"

    def update_texture(self, context) -> None:
        """threshold_enum_prop update callback"""
        for i in list(range(len(self._CR_POS) - 1)) + ["alpha"]:
            dither_node = self.node_tree.nodes.get(f"dither_{i}")
            dither_node.threshold_enum_prop = self.threshold_enum_prop

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

    _TONE_RAMP_KWARGS = dict(subtype="FACTOR", update=update_tone_ramps, min=0.0, max=1.0)
    tone_ramp_0_prop: FloatProperty(name="tone_pos_0", default=_CR_POS[0], **_TONE_RAMP_KWARGS)  # type: ignore
    tone_ramp_1_prop: FloatProperty(name="tone_pos_1", default=_CR_POS[1], **_TONE_RAMP_KWARGS)  # type: ignore
    tone_ramp_2_prop: FloatProperty(name="tone_pos_3", default=_CR_POS[2], **_TONE_RAMP_KWARGS)  # type: ignore
    tone_ramp_3_prop: FloatProperty(name="tone_pos_3", default=_CR_POS[3], **_TONE_RAMP_KWARGS)  # type: ignore
    tone_ramp_4_prop: FloatProperty(name="tone_pos_4", default=_CR_POS[4], **_TONE_RAMP_KWARGS)  # type: ignore
    tone_ramp_5_prop: FloatProperty(name="tone_pos_5", default=_CR_POS[5], **_TONE_RAMP_KWARGS)  # type: ignore

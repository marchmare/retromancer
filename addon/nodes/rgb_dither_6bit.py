from bpy.props import EnumProperty, FloatProperty

from ..textures import threshold_enum_items
from ._rgb_dither import _RGBDitherTemplate


class CompositorNodeRetromancer6BitRGBDither(_RGBDitherTemplate):
    """6-bit RGB palette ordered dither effect using provided threshold map texture."""

    bl_idname = "CompositorNodeRetromancer6BitRGBDither"
    bl_label = "RGB Ordered Dither (6 bit, 64 colors)"
    bl_icon = "SHADERFX"
    bl_width_default = 210

    _CR_POS = (0.0, 0.0615, 0.2431, 1.0)
    _DITHER_NODE = "CompositorNodeRetromancer4ToneDither"

    def update_texture(self, context) -> None:
        """threshold_enum_prop update callback"""
        for c in self._RGBA.keys():
            dither_node = self.node_tree.nodes.get(f"dither_{c}")
            dither_node.threshold_enum_prop = self.threshold_enum_prop

    def update_tone_ramps(self, context) -> None:
        """tone_ramp_x_prop update callback"""
        if not context.property:
            return
        prop = self.parse_datapath(context.property[1])
        prop_val = getattr(self, prop)

        for c in self._RGBA.keys():
            if c == "a":
                return
            dither_node = self.node_tree.nodes.get(f"dither_{c}")
            setattr(dither_node, prop, prop_val)

    _TONE_RAMP_KWARGS = dict(subtype="FACTOR", update=update_tone_ramps, min=0.0, max=1.0)

    threshold_enum_prop: EnumProperty(items=threshold_enum_items, name="", update=update_texture)  # type: ignore

    tone_ramp_0_prop: FloatProperty(name="tone_pos_0", default=_CR_POS[0], **_TONE_RAMP_KWARGS)  # type: ignore
    tone_ramp_1_prop: FloatProperty(name="tone_pos_1", default=_CR_POS[1], **_TONE_RAMP_KWARGS)  # type: ignore
    tone_ramp_2_prop: FloatProperty(name="tone_pos_3", default=_CR_POS[2], **_TONE_RAMP_KWARGS)  # type: ignore
    tone_ramp_3_prop: FloatProperty(name="tone_pos_3", default=_CR_POS[3], **_TONE_RAMP_KWARGS)  # type: ignore

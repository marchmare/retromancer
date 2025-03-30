from bpy.types import CompositorNodeCustomGroup
from bpy.props import EnumProperty, FloatProperty

from ..textures import initialize_textures, threshold_enum_items
from ..node_utils import CustomNodeGroupBuilder

# defaults
_RGB = ["r", "g", "b"]
_CR_POS = (0.0, 0.0615, 0.2431, 1.0)


class CompositorNodeRetromancer6BitRGBDither(
    CompositorNodeCustomGroup,
    CustomNodeGroupBuilder,
):
    """6-bit RGB palette ordered dither effect using provided threshold map texture."""

    bl_idname = "CompositorNodeRetromancer6BitRGBDither"
    bl_label = "6-bit RGB Ordered Dither"
    bl_icon = "SHADERFX"
    bl_width_default = 210

    def update_texture(self, context) -> None:
        """threshold_enum_prop update callback"""
        for c in _RGB + ["a"]:
            dither_node = self.node_tree.nodes.get(f"dither_{c}")
            dither_node.threshold_enum_prop = self.threshold_enum_prop

    def update_tone_ramps(self, context) -> None:
        """tone_ramp_x_prop update callback"""
        prop_val = getattr(self, context.property[1])
        for c in _RGB:
            dither_node = self.node_tree.nodes.get(f"dither_{c}")
            setattr(dither_node, context.property[1], prop_val)

    threshold_enum_prop: EnumProperty(  # type: ignore
        items=threshold_enum_items, name="", update=update_texture
    )

    tone_ramp_0_prop: FloatProperty(
        subtype="FACTOR",
        update=update_tone_ramps,
        name="tone_pos_0",
        min=0.0,
        max=1.0,
        default=_CR_POS[0],
    )  # type: ignore
    tone_ramp_1_prop: FloatProperty(
        subtype="FACTOR",
        update=update_tone_ramps,
        name="tone_pos_1",
        min=0.0,
        max=1.0,
        default=_CR_POS[1],
    )  # type: ignore
    tone_ramp_2_prop: FloatProperty(
        subtype="FACTOR",
        update=update_tone_ramps,
        name="tone_pos_3",
        min=0.0,
        max=1.0,
        default=_CR_POS[2],
    )  # type: ignore
    tone_ramp_3_prop: FloatProperty(
        subtype="FACTOR",
        update=update_tone_ramps,
        name="tone_pos_3",
        min=0.0,
        max=1.0,
        default=_CR_POS[3],
    )  # type: ignore

    def init(self, context) -> None:
        initialize_textures()
        self.init_group_node()

    def draw_buttons(self, context, layout) -> None:
        layout.prop(self, "threshold_enum_prop")
        layout.label(text="Tone ramp controls:")
        row = layout.column_flow(columns=4, align=True)
        row.prop(self, "tone_ramp_0_prop", text="")
        row.prop(self, "tone_ramp_1_prop", text="")
        row.prop(self, "tone_ramp_2_prop", text="")
        row.prop(self, "tone_ramp_3_prop", text="")
        layout.row()

    def _configure_sockets(self) -> None:
        # INPUTS:
        self.node_tree.interface.new_socket(
            name="Image",
            in_out="INPUT",
            socket_type="NodeSocketColor",
        )

        # OUTPUTS:
        self.node_tree.interface.new_socket(
            name="Image",
            in_out="OUTPUT",
            socket_type="NodeSocketColor",
        )

    def _configure_nodes(self) -> None:
        nodes = self.nodes
        nodes.add("dither_r", "CompositorNodeRetromancer4ToneDither", f"dither_r")
        nodes.add("dither_g", "CompositorNodeRetromancer4ToneDither", f"dither_g")
        nodes.add("dither_b", "CompositorNodeRetromancer4ToneDither", f"dither_b")
        nodes.add("dither_a", "CompositorNodeRetromancer2ToneDither", f"dither_a")
        nodes.add("alpha", "CompositorNodeSetAlpha")
        nodes.add("separate", "CompositorNodeSeparateColor")
        nodes.add("combine", "CompositorNodeCombineColor")

    def _configure_links(self) -> None:
        nodes = self.nodes
        links = self.node_tree.links

        links.new(nodes.input.outputs["Image"], nodes.separate.inputs["Image"])
        links.new(nodes.separate.outputs["Red"], nodes.dither_r.inputs["Image"])
        links.new(nodes.separate.outputs["Green"], nodes.dither_g.inputs["Image"])
        links.new(nodes.separate.outputs["Blue"], nodes.dither_b.inputs["Image"])
        links.new(nodes.separate.outputs["Alpha"], nodes.dither_a.inputs["Image"])

        links.new(nodes.dither_r.outputs["Image"], nodes.combine.inputs["Red"])
        links.new(nodes.dither_g.outputs["Image"], nodes.combine.inputs["Green"])
        links.new(nodes.dither_b.outputs["Image"], nodes.combine.inputs["Blue"])
        links.new(nodes.dither_a.outputs["Image"], nodes.alpha.inputs["Alpha"])
        links.new(nodes.combine.outputs["Image"], nodes.alpha.inputs["Image"])
        links.new(nodes.alpha.outputs["Image"], nodes.output.inputs["Image"])

import bpy
from bpy.types import CompositorNodeCustomGroup
from bpy.props import EnumProperty

from ..textures import initialize_textures, threshold_enum_items
from ..node_utils import CustomNodeGroupBuilder


class CompositorNodeRetromancerBayerTexture(
    CompositorNodeCustomGroup,
    CustomNodeGroupBuilder,
):
    """Custom texture node providing Bayer threshold maps."""

    bl_idname = "CompositorNodeRetromancerBayerTexture"
    bl_label = "Bayer Texture"
    bl_icon = "SHADERFX"
    bl_width_default = 200
    show_preview = True

    def update_texture(self, context) -> None:
        texture_node = context.node.node_tree.nodes.get("Texture")
        texture_node.texture = bpy.data.textures.get(self.threshold_enum_prop)

    threshold_enum_prop: EnumProperty(  # type: ignore
        items=threshold_enum_items, name="", update=update_texture
    )

    def init(self, context) -> None:
        initialize_textures()
        self.init_group_node()
        self.show_preview = True
        self.show_texture = True

    def draw_buttons(self, context, layout) -> None:
        layout.label(text="Threshold map:")
        layout.prop(self, "threshold_enum_prop")

    def _configure_sockets(self) -> None:
        # INPUTS:

        # OUTPUTS:
        self.node_tree.interface.new_socket(
            name="Image",
            in_out="OUTPUT",
            socket_type="NodeSocketColor",
        )

    def _configure_nodes(self) -> None:
        nodes = self.nodes
        nodes.add("texture", type="CompositorNodeTexture")

        nodes.texture.texture = bpy.data.textures.get(self.threshold_enum_prop)

    def _configure_links(self) -> None:
        nodes = self.nodes
        links = self.node_tree.links
        links.new(nodes.texture.outputs["Color"], nodes.output.inputs["Image"])

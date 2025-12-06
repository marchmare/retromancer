from bpy.types import CompositorNodeCustomGroup

from ..textures import initialize_textures
from ..node_utils import CustomNodeGroupBuilder


class _RGBDitherTemplate(
    CompositorNodeCustomGroup,
    CustomNodeGroupBuilder,
):
    """
    RGB Dither template class.
    Override following attributes to alter it's contents:
        * _CR_POS - color ramp default positions. len() is used to dynamically draw controls input boxes in the node.
        * _DITHER_NODE - bl_idname of the node used to dither each RGB channel

    Callbacks and then custom properties still need to be added to the child class manually, I haven't figure it out yet if it's possible to
    add props dynamically.
    """

    _RGBA = {"r": "Red", "g": "Green", "b": "Blue", "a": "Alpha"}  # do not edit
    _CR_POS = (0.0, 1.0)
    _DITHER_NODE = ""

    def init(self, context) -> None:
        initialize_textures()
        self.init_group_node()

    def draw_buttons(self, context, layout) -> None:
        layout.prop(self, "threshold_enum_prop")
        layout.label(text="Tone ramp controls:")
        row = layout.column_flow(columns=len(self._CR_POS), align=True)
        for i in range(len(self._CR_POS)):
            row.prop(self, f"tone_ramp_{i}_prop", text="")
        layout.row()

    def _configure_sockets(self) -> None:
        # INPUTS:
        self.node_tree.interface.new_socket(name="Image", in_out="INPUT", socket_type="NodeSocketColor")

        # OUTPUTS:
        self.node_tree.interface.new_socket(name="Image", in_out="OUTPUT", socket_type="NodeSocketColor")

    def _configure_nodes(self) -> None:
        nodes = self.nodes
        for c in self._RGBA.keys():
            nodes.add(f"dither_{c}", self._DITHER_NODE, f"dither_{c}")
        nodes.add("alpha", "CompositorNodeSetAlpha")
        nodes.add("separate", "CompositorNodeSeparateColor")
        nodes.add("combine", "CompositorNodeCombineColor")
        nodes.add("posterize", type="CompositorNodePosterize")

        nodes.posterize.inputs["Steps"].default_value = 32

    def _configure_links(self) -> None:
        self.link(output=("input", "Image"), input=("separate", "Image"))
        for c in self._RGBA.items():
            self.link(output=("separate", c[1]), input=("posterize" if c[0] == "a" else f"dither_{c[0]}", "Image"))
        self.link(output=("posterize", "Image"), input=("dither_a", "Image"))

        for c in self._RGBA.items():
            self.link(output=(f"dither_{c[0]}", "Image"), input=("combine", c[1]))
        self.link(output=("combine", "Image"), input=("alpha", "Image"))
        self.link(output=("alpha", "Image"), input=("output", "Image"))

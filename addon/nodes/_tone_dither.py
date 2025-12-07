from bpy.types import CompositorNodeCustomGroup, Node
from typing import Dict, Tuple

from ..textures import initialize_textures
from ..palettes import Color as c
from ..node_utils import CustomNodeGroupBuilder


class _ToneDitherTemplate(CompositorNodeCustomGroup, CustomNodeGroupBuilder):
    """
    Tone Dither template class.
    Override following attributes to alter it's contents:
        * _CR_POS - color ramp default positions. len() is used to dynamically draw controls input boxes in the node.
        * _PRESET = default preset to use from palette

    Callbacks and then custom properties still need to be added to the child class manually, I haven't figure it out yet if it's possible to
    add props dynamically.
    """

    _CR_POS = (0.0, 1.0)
    _PRESET = ""

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

    def _configure_interface(self) -> None:
        preset_values = iter(c.from_palette(self._PRESET))
        for i in range(1, len(self._CR_POS) + 1):
            self.inputs[f"Color {i}"].default_value = next(preset_values)

    def _configure_sockets(self) -> None:
        # INPUTS:
        self.node_tree.interface.new_socket(name="Image", in_out="INPUT", socket_type="NodeSocketColor")
        for i in range(1, len(self._CR_POS) + 1):
            self.node_tree.interface.new_socket(name=f"Color {i}", in_out="INPUT", socket_type="NodeSocketColor")
        self.node_tree.interface.new_socket(name="Brightness", in_out="INPUT", socket_type="NodeSocketFloat")
        self.node_tree.interface.new_socket(name="Contrast", in_out="INPUT", socket_type="NodeSocketFloat")

        # OUTPUTS:
        self.node_tree.interface.new_socket(name="Image", in_out="OUTPUT", socket_type="NodeSocketColor")

    def _get_color_lookup(self) -> Dict[Node, Tuple[int, ...]]:
        """
        Helper method that generates a dictionary mapping each node to its
        gradient and mask color ramp. A mask is a tuple of 0/1 values, where each position
        corresponds to a color ramp picker.
        Example:

            (1, 1, 1, 0, 1, 1)

        means: set the 4th picker to white (0) and all others to black (1).
        """
        cr_color_lookup = dict()
        crs = len(self._CR_POS)
        for node in range(crs - 1):
            if node == 0:
                seq_mask = tuple(1 if i < crs - 2 else 0 for i in range(crs))
            else:
                seq_mask = tuple(1 if (i != crs - 2 - node) else 0 for i in range(crs))
            seq_gradient = tuple(1 if i != crs - 2 - node else 0 for i in range(crs))

            cr_color_lookup[getattr(self.nodes, f"cr_mask_{node}")] = seq_mask
            cr_color_lookup[getattr(self.nodes, f"cr_gradient_{node}")] = seq_gradient
        return cr_color_lookup

    def _configure_nodes(self) -> None:
        nodes = self.nodes

        for i in range(len(self._CR_POS) - 1):
            mask = nodes.add(f"cr_mask_{i}", type="CompositorNodeValToRGB", name=f"cr_mask_{i}")
            gradient = nodes.add(f"cr_gradient_{i}", type="CompositorNodeValToRGB", name=f"cr_gradient_{i}")
            multiply = nodes.add(f"multiply_{i}", type="CompositorNodeMixRGB", name=f"multiply_{i}")
            nodes.add(f"dither_{i}", type="CompositorNodeRetromancer2ToneDither", name=f"dither_{i}")

            mask.color_ramp.interpolation = "CONSTANT"
            [mask.color_ramp.elements.new(0) for _ in range(len(self._CR_POS) - 2)]

            gradient.color_ramp.interpolation = "EASE"
            [gradient.color_ramp.elements.new(0) for _ in range(len(self._CR_POS) - 2)]

            multiply.blend_type = "MULTIPLY"
            multiply.inputs[0].default_value = 1

        _cr_color_lookup = self._get_color_lookup()
        for node, colors in _cr_color_lookup.items():
            for i, color in enumerate(colors):
                node.color_ramp.elements[i].color = c.black if color == 1 else c.white
                node.color_ramp.elements[i].position = self._CR_POS[i]

        for i in range(len(self._CR_POS) - 2):
            nodes.add(f"add{i}", type="CompositorNodeMixRGB")
            node = nodes.get(f"add{i}")
            node.blend_type = "ADD"
            node.inputs[0].default_value = 1

        nodes.add("alpha", type="CompositorNodeSetAlpha")
        nodes.add("dither_alpha", type="CompositorNodeRetromancer2ToneDither", name="dither_alpha")
        nodes.add("sep_color", type="CompositorNodeSeparateColor")
        nodes.add("brightness", type="CompositorNodeBrightContrast")
        nodes.add("posterize", type="CompositorNodePosterize")

        nodes.posterize.inputs["Steps"].default_value = 32

    def _configure_links(self) -> None:
        self.link(output=("input", "Image"), input=("brightness", "Image"))
        self.link(output=("input", "Brightness"), input=("brightness", 1))
        self.link(output=("input", "Contrast"), input=("brightness", 2))

        for i in range(len(self._CR_POS) - 1):
            self.link(output=("brightness", "Image"), input=(f"cr_mask_{i}", "Fac"))
            self.link(output=("brightness", "Image"), input=(f"cr_gradient_{i}", "Fac"))
            self.link(output=(f"cr_mask_{i}", 0), input=(f"multiply_{i}", "Image"))
            self.link(output=(f"cr_gradient_{i}", 0), input=(f"dither_{i}", "Image"))
            self.link(output=(f"dither_{i}", "Image"), input=(f"multiply_{i}", "Image_001"))

            self.link(output=("input", f"Color {len(self._CR_POS)-i}"), input=(f"dither_{i}", "Color 1"))
            self.link(output=("input", f"Color {len(self._CR_POS)-1-i}"), input=(f"dither_{i}", "Color 2"))

        for i in range(len(self._CR_POS) - 2):
            self.link(output=(f"multiply_{i+1}", "Image"), input=(f"add{i}", "Image"))
            self.link(output=("multiply_0" if i == 0 else f"add{i-1}", "Image"), input=(f"add{i}", "Image_001"))

        self.link(output=(f"add{len(self._CR_POS) - 3}", "Image"), input=("alpha", "Image"))
        self.link(output=("brightness", "Image"), input=("sep_color", "Image"))
        self.link(output=("sep_color", 3), input=("posterize", "Image"))
        self.link(output=("posterize", "Image"), input=("dither_alpha", "Image"))
        self.link(output=("dither_alpha", "Image"), input=("alpha", "Alpha"))
        self.link(output=("alpha", "Image"), input=("output", "Image"))

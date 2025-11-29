import bpy
import sys
import unittest
import addon_utils
import io
import contextlib
from typing import List

sys.argv = [sys.argv[0]]
BL_ADDON = "retromancer"
NODES = [
    "CompositorNodeRetromancerQuantize",
    "CompositorNodeRetromancer2ToneDither",
    "CompositorNodeRetromancer4ToneDither",
    "CompositorNodeRetromancer6BitRGBDither",
    "CompositorNodeRetromancerBayerTexture",
]


class TestRetromancer(unittest.TestCase):
    """General Blender compatibilty tests"""

    def test_addon_present(self) -> None:
        """Test if addon is sourcable at .config/blender/<major_version>/scripts/addons path and detectable by Blender"""
        names = [mod.__name__ for mod in addon_utils.modules()]
        self.assertTrue("retromancer" in names, f"{BL_ADDON} was not found")

    def test_addon_enabled(self) -> None:
        """Test if addon can be enabled"""
        addon_utils.enable(
            BL_ADDON, default_set=True, persistent=True, handle_error=None
        )
        self.assertTrue(addon_utils.check(BL_ADDON)[1], f"'{BL_ADDON}' was not enabled")

    def test_addon_disabled(self) -> None:
        """Test if addon can be disabled"""
        addon_utils.enable(
            BL_ADDON, default_set=True, persistent=True, handle_error=None
        )
        addon_utils.disable(BL_ADDON, default_set=True, handle_error=None)
        self.assertFalse(
            addon_utils.check(BL_ADDON)[1], f"'{BL_ADDON}' was not disabled"
        )


def _get_node_by_id(node_tree: bpy.types.NodeTree, bl_id: str) -> bpy.types.Node:
    """Get node object from node tree using its identifier"""
    return next(node for node in node_tree.nodes.values() if node.bl_idname == bl_id)


def _get_node_props(node: bpy.types.Node, type: str) -> List[str]:
    """Get list of node's custom properties identifiers"""
    return [
        node.bl_rna.properties[prop]
        for prop in dir(node)
        if prop.endswith("_prop") and node.bl_rna.properties[prop].type == type
    ]


class TestNodes(unittest.TestCase):
    """Custom node-related tests"""

    @classmethod
    def setUpClass(cls) -> None:
        addon_utils.enable(
            BL_ADDON, default_set=True, persistent=True, handle_error=None
        )
        if not addon_utils.check(BL_ADDON)[1]:
            raise unittest.SkipTest("Addon not enabled - skipping node tests")

        bpy.context.scene.use_nodes = True
        cls.node_tree = bpy.context.scene.node_tree

    @classmethod
    def tearDownClass(cls):
        addon_utils.disable(BL_ADDON, default_set=True, handle_error=None)

    def test_add_node(self) -> None:
        """Test if node can be added to node tree"""
        for node in NODES:
            with self.subTest(node=node):
                _node = self.node_tree.nodes.new(type=node)
                self.assertIsNotNone(_node)

    def test_node_enum_props(self) -> None:
        """Test if custom enum properties can be changed and if they don't accept foreign values"""
        for node in NODES:
            _node = _get_node_by_id(self.node_tree, node)
            _props = _get_node_props(_node, "ENUM")
            for prop in _props:
                current = getattr(_node, prop.identifier)
                _item = next(item for item in prop.enum_items.keys() if item != current)
                with self.subTest(node=node, prop=prop):
                    with self.assertRaises(TypeError):
                        setattr(_node, prop.identifier, "a")

                    setattr(_node, prop.identifier, _item)
                    value = getattr(_node, prop.identifier)
                    self.assertEqual(value, _item)

    def test_node_float_props(self) -> None:
        """Test if custom float properties can be changed and if they don't accept non-numerical values"""
        for node in NODES:
            _node = _get_node_by_id(self.node_tree, node)
            _props = _get_node_props(_node, "FLOAT")
            for prop in _props:
                with self.subTest(node=node, prop=prop.identifier):
                    with self.assertRaises(TypeError):
                        setattr(_node, prop.identifier, "a")

                    setattr(_node, prop.identifier, prop.soft_max + 999)
                    value = getattr(_node, prop.identifier)
                    self.assertEqual(value, prop.soft_max)

    def test_datapath_parsing(self) -> None:
        """Test if datapath parsing works correctly and extracts property's identifier"""
        from retromancer.addon.node_utils import CustomNodeGroupBuilder

        NODE = "CompositorNodeRetromancerBayerTexture"
        PROP_STR = "threshold_enum_prop"
        _node = _get_node_by_id(self.node_tree, NODE)
        _prop = _node.bl_rna.properties[PROP_STR]
        datapath = _node.path_from_id(_prop.identifier)
        self.assertEqual(PROP_STR, CustomNodeGroupBuilder.parse_datapath(datapath))


class TestPropertiesPanel(unittest.TestCase):
    """Properties panel tests"""

    @classmethod
    def setUpClass(cls) -> None:
        addon_utils.enable(
            "retromancer", default_set=True, persistent=True, handle_error=None
        )
        if not addon_utils.check("retromancer")[1]:
            raise unittest.SkipTest("Addon not enabled - skipping node tests")

    @classmethod
    def tearDownClass(cls):
        addon_utils.disable(BL_ADDON, default_set=True, handle_error=None)

    def test_apply_resolution(self) -> None:
        """Test apply resolution operator"""
        TARGET_RESOLUTION = [64, 32]
        bpy.context.scene.retromancer.selected_resolution = (
            f"{TARGET_RESOLUTION[0]}x{TARGET_RESOLUTION[1]}"
        )
        result = bpy.ops.scene.retromancer_apply_resolution()
        self.assertEqual(result, {"FINISHED"})
        self.assertEqual(
            TARGET_RESOLUTION,
            [
                bpy.context.scene.render.resolution_x,
                bpy.context.scene.render.resolution_y,
            ],
        )

    def test_apply_isometric_camera(self) -> None:
        """Test apply isometric camera operator"""
        f = io.StringIO()
        DEFAULT_CAMERA = "Camera"
        DEFAULT_CUBE = "Cube"
        _camera = bpy.data.objects.get(DEFAULT_CAMERA)
        _cube = bpy.data.objects.get(DEFAULT_CUBE)

        # disables info and error console logs from Blender
        with contextlib.redirect_stdout(f), contextlib.redirect_stderr(f):
            bpy.context.view_layer.objects.active = _camera
            result = bpy.ops.scene.retromancer_make_camera_isometric()
            self.assertEqual(result, {"FINISHED"})

            result = bpy.ops.scene.retromancer_make_camera_isometric()
            self.assertEqual(result, {"CANCELLED"})

            bpy.context.view_layer.objects.active = _cube
            with self.assertRaisesRegex(
                RuntimeError, "Active object must be a camera."
            ):
                bpy.ops.scene.retromancer_make_camera_isometric()

    def test_disable_aa(self) -> None:
        """Test disable anti-aliasing operator"""
        result = bpy.ops.scene.retromancer_disable_anti_aliasing()
        self.assertEqual(result, {"FINISHED"})

    def test_handler_texture_resize(self) -> None:
        """Test automatic texture resize via app handler"""
        TARGET_RESOLUTION = [800, 600]
        bpy.context.scene.retromancer.auto_resize = True

        _textures = bpy.data.textures.values()
        depsgraph = bpy.context.evaluated_depsgraph_get()
        bpy.context.scene.render.resolution_x = TARGET_RESOLUTION[0]
        bpy.context.scene.render.resolution_y = TARGET_RESOLUTION[1]

        for texture in _textures:
            depsgraph.update()
            self.assertListEqual(TARGET_RESOLUTION, list(texture.image.size))

    def test_disable_texture_resize(self) -> None:
        """Test disabling automatic texture resize via app handler"""
        TARGET_RESOLUTION = [600, 800]
        bpy.context.scene.retromancer.auto_resize = False

        _textures = bpy.data.textures.values()
        depsgraph = bpy.context.evaluated_depsgraph_get()
        bpy.context.scene.render.resolution_x = TARGET_RESOLUTION[0]
        bpy.context.scene.render.resolution_y = TARGET_RESOLUTION[1]

        for texture in _textures:
            depsgraph.update()
            self.assertNotEqual(TARGET_RESOLUTION, list(texture.image.size))


if __name__ == "__main__":
    unittest.main()

from bpy.types import Menu
from bl_ui import node_add_menu


class NODE_MT_category_compositor_retromancer(Menu):
    """Retromancer compositor menu category."""

    bl_idname = "NODE_MT_category_compositor_retromancer"
    bl_label = "Retromancer"

    def draw(self, _context) -> None:
        node_add_menu.add_node_type(self.layout, "CompositorNodeRetromancerQuantize")
        node_add_menu.add_node_type(
            self.layout, "CompositorNodeRetromancerBayerTexture"
        )
        node_add_menu.add_node_type(self.layout, "CompositorNodeRetromancer2ToneDither")
        node_add_menu.add_node_type(self.layout, "CompositorNodeRetromancer4ToneDither")
        node_add_menu.draw_assets_for_catalog(self.layout, self.bl_label)


def update_add_menu(self, context) -> None:
    """Add menu layout update function."""
    self.layout.menu("NODE_MT_category_compositor_retromancer")

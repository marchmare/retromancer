from bpy.types import Menu, Panel, PropertyGroup
from bpy.props import BoolProperty, EnumProperty
from bl_ui import node_add_menu
from typing import Literal
import bpy


class NODE_MT_category_compositor_retromancer(Menu):
    """Retromancer compositor menu category."""

    bl_idname = "NODE_MT_category_compositor_retromancer"
    bl_label = "Retromancer"

    def draw(self, _context) -> None:
        node_add_menu.add_node_type(self.layout, "CompositorNodeRetromancerQuantize")
        node_add_menu.add_node_type(self.layout, "CompositorNodeRetromancerBayerTexture")
        self.layout.separator()
        node_add_menu.add_node_type(self.layout, "CompositorNodeRetromancer2ToneDither")
        node_add_menu.add_node_type(self.layout, "CompositorNodeRetromancer4ToneDither")
        node_add_menu.add_node_type(self.layout, "CompositorNodeRetromancer6BitRGBDither")
        node_add_menu.add_node_type(self.layout, "CompositorNodeRetromancer6ToneDither")
        node_add_menu.add_node_type(self.layout, "CompositorNodeRetromancer8BitRGBDither")


def update_add_menu(self, context) -> None:
    """Add menu layout update function."""
    self.layout.separator()
    self.layout.menu("NODE_MT_category_compositor_retromancer")


RETROMANCER_RESOLUTIONS = [
    ("64x32", "64x32 (CHIP-8)", "", 1),
    ("160x144", "160x140 (Gameboy/Gameboy Color)", "", 2),
    ("192x160", "192x160 (Atari 2600)", "", 3),
    ("240x160", "240x160 (Gameboy Advance)", "", 4),
    ("256x192", "256x192 (Nintendo DS)", "", 5),
    ("256x224", "256x224 (SNES/NES NTSC)", "", 6),
    ("256x240", "256x240 (NES PAL)", "", 7),
    ("320x200", "320x200 (DOS)", "", 8),
    ("320x224", "320x224 (Sega Genesis/Neo Geo)", "", 9),
    ("400x240", "400x240 (3DS)", "", 10),
    ("640x480", "640x480 (Playstation 1)", "", 11),
]


class RetromancerPropertyGroup(PropertyGroup):
    """Retromancer UI properties"""

    selected_resolution: EnumProperty(  # type: ignore
        name="Resolution presets",
        items=RETROMANCER_RESOLUTIONS,
        options=set(),
    )
    auto_resize: BoolProperty(  # type: ignore
        name="Auto-resize Retromancer textures",
        description="Enable resizing Retromancer's internal threshold map textures to current render resolution in the background.",
        default=True,
        options=set(),
    )


class UIRetromancerPanel(Panel):
    """Retromancer control panel"""

    bl_label = "Retromancer"
    bl_idname = "RENDER_PT_retromancer_panel"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "render"

    def draw(self, context) -> None:
        layout = self.layout
        scene = context.scene

        layout.use_property_split = True
        layout.prop(
            scene.retromancer,
            "selected_resolution",
            text="Resolution presets:",
        )
        layout.operator("scene.retromancer_apply_resolution")
        layout.separator()
        layout.operator("scene.retromancer_make_camera_isometric", icon="CON_CAMERASOLVER")
        layout.operator("scene.retromancer_disable_anti_aliasing", icon="MOD_SMOOTH")
        layout.separator()
        layout.prop(
            scene.retromancer,
            "auto_resize",
            text="Auto-resize Retromancer textures",
        )


def draw_popup(
    title: str = "Retromancer:",
    text: str = "null",
    icon: Literal["INFO", "WARNING", "ERROR"] = "INFO",
) -> None:
    """Wrapper for bpy.context.window_manager info/warning/error popups"""

    def draw(self, context):
        for line in text.splitlines():
            self.layout.label(text=line)

    bpy.context.window_manager.popup_menu(draw, title=title, icon=icon)

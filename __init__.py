from bpy.app.handlers import depsgraph_update_post
from bpy.types import NODE_MT_compositor_node_add_all, Scene, Depsgraph, Menu
from typing import Callable, List, Tuple

from .addon.nodes.quantize import CompositorNodeRetromancerQuantize
from .addon.nodes.monochrome_dither import CompositorNodeRetromancer2BitDither
from .addon.textures import regenerate_textures
from .addon.ui import NODE_MT_category_compositor_retromancer, update_add_menu

bl_info = {
    "name": "Retromancer",
    "author": "Marcel Nowicki <0x414n@gmail.com>",
    "version": (1, 0),
    "blender": (4, 2, 0),
    "location": "Compositor",
    "description": "Retromancer addon",
    "warning": "",
    "category": "Render",
}


def check_handler_appended(
    handler: List[Tuple[Scene, Depsgraph]], func: Callable
) -> bool:
    """Check if function wrapper is already added to specified app handler."""
    return handler.__name__ == func.__name__ and handler.__module__ == func.__module__


def add_handler(handler_list: List[Tuple[Scene, Depsgraph]], func: Callable) -> None:
    """Add handler function wrapper to specified app handler."""
    for i, handler in enumerate(handler_list):
        if check_handler_appended(handler, func):
            return
    handler_list.append(func)


def remove_handler(handler_list: List[Tuple[Scene, Depsgraph]], func: Callable) -> None:
    """Remove function wrapper from specified app handler."""
    for i, handler in enumerate(handler_list):
        if check_handler_appended(handler, func):
            del handler_list[i]


def check_menu_appended(menu: Menu, func: Callable) -> bool:
    """Check if function is already added to an existing menu."""
    return func.__name__ in (
        dyn_ui_func.__name__ for dyn_ui_func in menu._dyn_ui_initialize()
    )


def add_menu(menu: Menu, func: Callable) -> None:
    """Add custom menu elements layout function to existing Blender menu."""
    if not check_menu_appended(menu, func):
        menu.append(func)


def remove_menu(menu: Menu, func: Callable) -> None:
    """Remove custom menu elements layout function from existing Blender menu."""
    if check_menu_appended(menu, func):
        menu.remove(func)


classes = [
    CompositorNodeRetromancerQuantize,
    CompositorNodeRetromancer2BitDither,
    NODE_MT_category_compositor_retromancer,
]


def register() -> None:
    from bpy.utils import register_class, unregister_class

    for cls in classes:
        try:
            register_class(cls)
        except:
            unregister_class(cls)
            register_class(cls)

    add_menu(NODE_MT_compositor_node_add_all, update_add_menu)
    add_handler(depsgraph_update_post, regenerate_textures)


def unregister() -> None:
    from bpy.utils import unregister_class

    remove_handler(depsgraph_update_post, regenerate_textures)
    remove_menu(NODE_MT_compositor_node_add_all, update_add_menu)

    for cls in classes:
        unregister_class(cls)


if __name__ == "__main__":
    register()

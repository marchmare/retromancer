# Repository overview

The Retromancer addon adds a custom category to the compositing workspace node menu and a property panel inside _Render Properties_.

Blender’s Python API does not allow developers to implement new compositor node types with custom execution code. The only way to introduce a genuine new node is to alter Blender’s C++ source and recompile it. 

Retromancer avoids this limitation by relying on [`CompositorNodeCustomGroup`](https://docs.blender.org/api/3.2/bpy.types.CompositorNodeCustomGroup.html). This node type allows Python to build a node group and present it to the user as a single, compact custom node. The internal logic is still made from built-in compositor nodes, but the result behaves like a regular node from the user’s perspective.

This custom node group can be customized similarly to regular node by defining `bl_` metadata, adding custom [properties](https://docs.blender.org/api/current/bpy.props.html), adding UI elements with `draw` methods etc. The internal nodes cannot be accessed using `TAB` shortcut. The only way to inspect their contents is to add them to compositing workspace via _Data API > Node Groups_ tree.

## File structure

```
retromancer/
├─ blender_manifest.toml
├─ __init__.py
├─ addon/
│  ├─ nodes/
│  ├─ compatibility.py 
│  ├─ node_utils.py
│  ├─ operators.py
│  ├─ palettes.py
│  ├─ textures.py
│  └─ ui.py
├─ docs/
└─ README.md
```

* [`blender_manifest.toml`](../blender_manifest.toml) - Blender addon metadata file
* [`__init__.py`](../__init__.py) - main entry point of the Blender addon. Contains metadata (`bl_info`) and functions to register/unregister the addon’s classes. Required by Blender to detect and enable the addon.
* [`addon/`](../addon/) - directory containing addon's modules:
    * [`nodes/`](../addon/nodes/) - directory containing definitions of custom compositing nodes as separate Python files 
    * [`compatibility.py`](../addon/compatibility.py) - version compatibility functions for managing Blender API differences across multiple Blender releases
    * [`node_utils.py`](../addon/node_utils.py) - contains `CustomNodeGroupBuilder` helper class for building internal node trees programmatically
    * [`operators.py`](../addon/operators.py) - definitions of custom Blender operators used by the addon
    * [`palettes.py`](../addon/palettes.py) - color palette presets and utilities definitions 
    * [`textures.py`](../addon/textures.py) - Bayer texture generation module and render resolution state tracker
    * [`ui.py`](../addon/ui.py) - addon UI elements definitions (_Render Properties_ panel and _Add node_ menu)

## Node architecture

All Retromancer nodes inherit from `CustomNodeGroupBuilder` ([`node_utils.py`](../addon/node_utils.py)), which creates the custom node group, builds its internal node tree and provides a more structured and convenient way to define node elements and connections.
This results in clean, readable node definitions instead of working directly with Blender’s low-level node group API.

Whenever a node object is initialized, this utility class automatically handles creating internal node tree and adding _Group Input_ and _Group Output_ nodes to it. Then overridable configuration methods are called:

* `_configure_sockets()` – creates the exposed inputs and outputs
* `_configure_nodes()` – creates internal compositor nodes and sets their initial states
* `_configure_links()` – connects the internal nodes
* `_configure_interface()` – sets default values or states of custom added `bpy.props` UI elements

To support clean code and avoid repeated lookups through `node_tree.nodes`, `CustomNodeGroupBuilder` comes with internal `_Nodes` registry with named access to the created nodes.


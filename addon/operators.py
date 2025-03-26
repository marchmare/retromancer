from bpy.types import Operator, Object
from math import radians
from typing import Set


class ApplyRetromancerResolutionOperator(Operator):
    """Apply selected preset resolution"""

    bl_idname = "scene.retromancer_apply_resolution"
    bl_label = "Apply resolution"

    def execute(self, context) -> Set[str]:
        scene = context.scene
        preset = scene.retromancer.selected_resolution
        width, height = map(int, preset.split("x"))
        scene.render.resolution_x = width
        scene.render.resolution_y = height
        return {"FINISHED"}


class MakeCameraIsometricOperator(Operator):
    """Set make active camera isometric (switches camera to ORTHO and adds rotation constraint)"""

    bl_idname = "scene.retromancer_make_camera_isometric"
    bl_label = "Make camera isometric"
    bl_icon = "CAMERA"

    def execute(self, context) -> Set[str]:
        if not self.check_camera_active(context):
            self.report({"ERROR"}, "Active object must be a camera.")
            return {"CANCELLED"}
        camera = context.active_object
        if camera:
            camera.data.type = "ORTHO"

        if camera.constraints.get("Isometric Rotation"):
            self.report({"INFO"}, "Isometric rotation constraint already added.")
            return {"CANCELLED"}

        constraint = camera.constraints.new(type="LIMIT_ROTATION")
        constraint.name = "Isometric Rotation"
        constraint.use_limit_x = True
        constraint.use_limit_y = False
        constraint.use_limit_z = True
        constraint.min_x = radians(54.7)
        constraint.max_x = radians(54.7)
        constraint.min_z = radians(45)
        constraint.max_z = radians(45)

        return {"FINISHED"}

    def check_camera_active(self, context) -> bool:
        """Check if current active object is a camera"""
        print(context.active_object)
        return (
            isinstance(context.active_object, Object)
            and hasattr(context.active_object, "type")
            and context.active_object.type == "CAMERA"
        )


class DisableAntiAliasingOperator(Operator):
    """Set various properties for currently active rendering engine that reduce anti-aliasing in renders"""

    bl_idname = "scene.disable_anti_aliasing"
    bl_label = "Disable anti-aliasing"

    def execute(self, context) -> Set[str]:
        scene = context.scene

        if scene.render.engine == "BLENDER_WORKBENCH":
            scene.display.render_aa = "OFF"
            scene.display.viewport_aa = "OFF"

        if scene.render.engine == "CYCLES":
            scene.cycles.pixel_filter_type = "BLACKMAN_HARRIS"
            scene.cycles.filter_width = 0.01
            scene.cycles.use_denoising = False

        if scene.render.engine == "BLENDER_EEVEE_NEXT":
            scene.eevee.taa_render_samples = 1
            scene.eevee.taa_samples = 1
            scene.render.filter_size = 0.01

        return {"FINISHED"}

"""
Render cover: karakter melambai di samping mesin, latar transparan + bayangan lembut.

  blender -b design/showcase/video/usecase.blend -P design/showcase/deck/cover_render.py
Keluaran: design/showcase/deck/assets/cover.png
"""
import os
import bpy
from mathutils import Vector

HERE = os.path.dirname(os.path.abspath(__file__))
sc = bpy.context.scene
sc.frame_set(515)
for o in sc.objects:
    if o.name.startswith(("Meja_", "Kompor_", "Api_", "Selang_", "Latar")):
        o.hide_render = True
for o in sc.objects:  # matikan keyframe visibilitas props yang tersisa
    pass
sc.render.film_transparent = True
sc.render.engine = "CYCLES"
sc.cycles.samples = 128
sc.cycles.use_denoising = True
try:
    prefs = bpy.context.preferences.addons["cycles"].preferences
    prefs.compute_device_type = "OPTIX"
    prefs.get_devices()
    for d in prefs.devices:
        d.use = True
    sc.cycles.device = "GPU"
except Exception:
    pass
sc.render.resolution_x, sc.render.resolution_y = 1700, 1600
sc.render.image_settings.color_mode = "RGBA"
sc.render.use_motion_blur = False
for m in list(sc.timeline_markers):
    sc.timeline_markers.remove(m)
cam = bpy.data.objects.new("Cam_Cover", bpy.data.cameras.new("Cam_Cover"))
sc.collection.objects.link(cam)
cam.data.lens = 50
cam.location = (-1.25, -3.5, 1.3)
tgt = Vector((0.18, -0.25, 0.86))
cam.rotation_euler = (tgt - cam.location).to_track_quat("-Z", "Y").to_euler()
sc.camera = cam
sc.render.filepath = os.path.join(HERE, "assets", "cover.png")
bpy.ops.render.render(write_still=True)
print("[COVER] ok")

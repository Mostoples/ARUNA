"""
Render foto mesin berlatar transparan (dengan bayangan lantai) untuk dipakai di UI aplikasi.

  blender -b design/blender/aruna_mesin.blend -P design/blender/render_mesin_cutout.py
Keluaran: design/app/img/mesin.png
"""
import os
import bpy
from mathutils import Vector

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "app", "img", "mesin.png")
os.makedirs(os.path.dirname(OUT), exist_ok=True)

scene = bpy.context.scene
PROPS = ("Meja_", "Kompor_", "Api_", "Selang_", "Pot", "Daun_")
for o in scene.objects:
    if o.name.startswith(PROPS):
        o.hide_render = True
bpy.data.objects["Latar"].hide_render = True  # latar dibuang; bayangan dibuat di CSS

scene.render.film_transparent = True
scene.render.resolution_x, scene.render.resolution_y = 900, 1200
scene.render.image_settings.color_mode = "RGBA"
scene.cycles.samples = 128

cam_data = bpy.data.cameras.new("Cam_Cutout")
cam_data.lens = 58
cam = bpy.data.objects.new("Cam_Cutout", cam_data)
scene.collection.objects.link(cam)
cam.location = (1.5, -2.6, 1.35)
target = Vector((0.04, 0.0, 0.78))
cam.rotation_euler = (target - cam.location).to_track_quat("-Z", "Y").to_euler()
scene.camera = cam

scene.render.filepath = OUT
bpy.ops.render.render(write_still=True)
print("[ARUNA] cutout ->", OUT)

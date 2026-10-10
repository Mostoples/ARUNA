"""Ekspor karakter ber-rig + semua aksi ke GLB untuk web (three.js)."""
import bpy, os
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "web", "assets", "aruna_char.glb")
os.makedirs(os.path.dirname(OUT), exist_ok=True)
rig = bpy.data.objects["ARUNA_Rig"]
for b in rig.pose.bones:
    pass
bpy.ops.object.select_all(action="DESELECT")
for o in bpy.data.objects:
    if o.name == "ARUNA_Rig" or o.name.startswith("Karakter_"):
        o.select_set(True)
bpy.context.view_layer.objects.active = rig
rig.animation_data.action = None
bpy.ops.export_scene.gltf(filepath=OUT, export_format="GLB", use_selection=True,
                          export_def_bones=True, export_animation_mode="ACTIONS",
                          export_force_sampling=True, export_frame_step=2,
                          export_optimize_animation_size=True, export_apply=False,
                          export_image_format="WEBP" if hasattr(bpy.types, "Image") else "AUTO")
print("[GLB]", OUT)

"""
Render hardware ARUNA: (1) tampak luar transparan, (2) x-ray dengan komponen dalam + titik callout 2D.

  blender -b design/blender/aruna_mesin.blend -P design/showcase/deck/hw_xray.py
Keluaran: design/showcase/deck/assets/hw_outer.png, hw_xray.png, hw_points.json
"""
import bpy
import json
import math
import os

from bpy_extras.object_utils import world_to_camera_view
from mathutils import Vector

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "assets")
os.makedirs(OUT, exist_ok=True)
sc = bpy.context.scene
ob = bpy.data.objects

for o in sc.objects:
    if o.name.startswith(("Meja_", "Kompor_", "Api_", "Selang_", "Pot", "Daun_", "Latar")):
        o.hide_render = True

sc.render.film_transparent = True
sc.render.resolution_x, sc.render.resolution_y = 1500, 1800
sc.render.image_settings.color_mode = "RGBA"
sc.cycles.samples = 160

cam = bpy.data.objects.new("Cam_HW", bpy.data.cameras.new("Cam_HW"))
sc.collection.objects.link(cam)
cam.data.lens = 60
cam.location = (1.45, -2.55, 1.45)
tgt = Vector((0.02, 0.0, 0.66))
cam.rotation_euler = (tgt - cam.location).to_track_quat("-Z", "Y").to_euler()
sc.camera = cam

# tutup ditutup untuk tampilan produk
hinge = Vector((0, 0.208, 1.126))
for n in ("Tutup", "Tutup_Pegangan"):
    o = ob[n]
    mw = o.matrix_world.copy()
    from mathutils import Matrix
    R = Matrix.Translation(hinge) @ Matrix.Rotation(math.radians(100), 4, "X") @ Matrix.Translation(-hinge)
    o.matrix_world = R @ mw

sc.render.filepath = os.path.join(OUT, "hw_outer.png")
bpy.ops.render.render(write_still=True)


# ------------------------------------------------------------------ x-ray
def mat(name, color, rough=0.4, metallic=0.0, emit=None, strength=0.0):
    m = bpy.data.materials.new(name)
    if m.node_tree is None:
        m.use_nodes = True
    b = next(n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    b.inputs["Base Color"].default_value = (*color, 1)
    b.inputs["Roughness"].default_value = rough
    b.inputs["Metallic"].default_value = metallic
    if emit:
        b.inputs["Emission Color"].default_value = (*emit, 1)
        b.inputs["Emission Strength"].default_value = strength
    return m


ghost = bpy.data.materials.new("Ghost")
ghost.use_nodes = True if ghost.node_tree is None else True
nt = ghost.node_tree
for n in list(nt.nodes):
    nt.nodes.remove(n)
outn = nt.nodes.new("ShaderNodeOutputMaterial")
mix = nt.nodes.new("ShaderNodeMixShader")
tr = nt.nodes.new("ShaderNodeBsdfTransparent")
gl = nt.nodes.new("ShaderNodeBsdfPrincipled")
gl.inputs["Base Color"].default_value = (0.75, 0.92, 0.82, 1)
gl.inputs["Roughness"].default_value = 0.2
lw = nt.nodes.new("ShaderNodeLayerWeight")
lw.inputs["Blend"].default_value = 0.35
nt.links.new(lw.outputs["Facing"], mix.inputs["Fac"])
nt.links.new(tr.outputs[0], mix.inputs[1])
nt.links.new(gl.outputs[0], mix.inputs[2])
nt.links.new(mix.outputs[0], outn.inputs["Surface"])

SHELL = ("Modul_", "Laci_Kompos_Muka", "Tutup", "Alas", "Ceruk_Tatakan")
for o in sc.objects:
    if o.type == "MESH" and o.name.startswith(SHELL):
        o.data.materials.clear()
        o.data.materials.append(ghost)
        o.visible_shadow = False
for o in sc.objects:
    if o.name.startswith(("Logo_", "Label_", "Langkah_", "Ventilasi", "Tombol_Label")):
        o.hide_render = True

col = bpy.data.collections.new("Internal")
sc.collection.children.link(col)
M = {
    "tank": mat("Tangki_Dalam", (0.80, 0.82, 0.80), 0.35),
    "slurry": mat("Slurry", (0.30, 0.22, 0.08), 0.3),
    "steel": mat("Baja", (0.75, 0.76, 0.78), 0.25, 1.0),
    "pcb": mat("PCB", (0.03, 0.35, 0.2), 0.4),
    "chip": mat("Chip", (0.05, 0.05, 0.06), 0.3),
    "sensor": mat("Sensor", (0.08, 0.48, 0.42), 0.35),
    "motor": mat("Motor", (0.06, 0.07, 0.07), 0.45, 0.4),
    "gas": mat("PipaGas", (0.8, 0.55, 0.22), 0.3, 1.0),
    "glow": mat("Glow", (0.2, 0.8, 0.5), 0.3, emit=(0.2, 0.9, 0.55), strength=4),
    "blade": mat("Pisau", (0.85, 0.86, 0.88), 0.2, 1.0),
}


def put(o, m, name):
    for c in o.users_collection:
        c.objects.unlink(o)
    col.objects.link(o)
    o.name = name
    o.data.materials.append(m)
    for p in o.data.polygons:
        p.use_smooth = True
    return o


def cyl(name, r, d, loc, m, rot=(0, 0, 0), v=48):
    bpy.ops.mesh.primitive_cylinder_add(radius=r, depth=d, location=loc, rotation=rot, vertices=v)
    return put(bpy.context.active_object, m, name)


def box(name, s, loc, m, rot=(0, 0, 0)):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc, rotation=rot)
    o = bpy.context.active_object
    o.scale = s
    return put(o, m, name)


# pencacah (dua poros berpisau) di modul atas
for k, y in enumerate((-0.035, 0.035)):
    cyl(f"Poros_{k}", 0.008, 0.3, (0, y, 1.0), M["steel"], rot=(0, math.pi / 2, 0))
    for i in range(9):
        cyl(f"Pisau_{k}_{i}", 0.032, 0.006, (-0.12 + i * 0.03, y, 1.0), M["blade"], rot=(0, math.pi / 2, 0), v=10)
box("Motor_Pencacah", (0.07, 0.09, 0.07), (0.17, 0.0, 1.0), M["motor"])
# load cell di bawah ruang cacah
box("LoadCell", (0.12, 0.03, 0.02), (0, 0.0, 0.925), M["steel"])
# tangki digester
cyl("Tangki", 0.175, 0.3, (0, 0.03, 0.74), ghost, v=64)
bpy.ops.mesh.primitive_cone_add(radius1=0.06, radius2=0.175, depth=0.14, location=(0, 0.03, 0.52), vertices=64)
put(bpy.context.active_object, ghost, "Tangki_Kerucut")
cyl("Slurry", 0.168, 0.2, (0, 0.03, 0.69), M["slurry"], v=64)
# pengaduk
cyl("Pengaduk_Poros", 0.007, 0.36, (0, 0.03, 0.72), M["steel"])
for i, z in enumerate((0.62, 0.76)):
    box(f"Pengaduk_Daun_{i}", (0.22, 0.012, 0.035), (0, 0.03, z), M["steel"], rot=(0, 0, i * math.pi / 2))
box("Motor_Pengaduk", (0.06, 0.06, 0.05), (0, 0.03, 0.915), M["motor"])
# ESP32 di balik layar
box("ESP32_PCB", (0.12, 0.006, 0.07), (-0.06, -0.19, 1.05), M["pcb"])
box("ESP32_Chip", (0.035, 0.004, 0.035), (-0.06, -0.195, 1.05), M["chip"])
cyl("ESP32_LED", 0.004, 0.004, (-0.02, -0.196, 1.07), M["glow"], rot=(math.pi / 2, 0, 0))
# sensor
cyl("Sensor_Suhu", 0.006, 0.12, (-0.12, 0.03, 0.70), M["steel"], rot=(0, math.pi / 2, 0))
box("Sensor_Suhu_Kepala", (0.025, 0.025, 0.025), (-0.19, 0.03, 0.70), M["sensor"])
cyl("Sensor_pH", 0.008, 0.16, (0.09, 0.09, 0.74), M["sensor"])
box("Sensor_Gas", (0.04, 0.03, 0.025), (0.08, -0.03, 0.88), M["sensor"])
cyl("Sensor_Level", 0.02, 0.02, (-0.06, 0.08, 0.885), M["steel"])
# jalur gas & cairan
for i, (a, b) in enumerate((((0.1, 0.03, 0.89), (0.18, -0.06, 0.89)), ((0.18, -0.06, 0.89), (0.18, -0.06, 0.70)),
                            ((0.18, -0.06, 0.70), (0.22, -0.06, 0.70)))):
    a, b = Vector(a), Vector(b)
    d = b - a
    cyl(f"PipaGas_{i}", 0.007, d.length, (a + b) / 2, M["gas"],
        rot=Vector((0, 0, 1)).rotation_difference(d).to_euler(), v=16)
cyl("Pipa_Pupuk", 0.008, 0.08, (0, -0.12, 0.555), M["steel"])
box("Saluran_Kompos", (0.12, 0.12, 0.06), (0, 0.03, 0.4), M["tank"])

sc.render.filepath = os.path.join(OUT, "hw_xray.png")
bpy.ops.render.render(write_still=True)

# ------------------------------------------------------------------ titik callout (0..1, origin kiri-atas)
PTS = {
    "pencacah": ob["Pisau_0_4"], "loadcell": ob["LoadCell"], "esp32": ob["ESP32_Chip"],
    "layar": ob["Layar"], "pengaduk": ob["Pengaduk_Daun_1"], "tangki": ob["Slurry"],
    "suhu": ob["Sensor_Suhu_Kepala"], "ph": ob["Sensor_pH"], "gas": ob["Sensor_Gas"], "level": ob["Sensor_Level"],
    "gauge": ob["Gauge_Muka"], "katup": ob["Gas_Katup"], "keran": ob["Keran_Bodi"], "kompos": ob["Laci_Kompos_Muka"],
    "pedal": ob["Pedal"],
}
out = {}
for k, o in PTS.items():
    c = world_to_camera_view(sc, cam, o.matrix_world.translation)
    out[k] = [round(c.x, 4), round(1 - c.y, 4)]
json.dump(out, open(os.path.join(OUT, "hw_points.json"), "w"), indent=1)
print("[HW]", out)

"""
ARUNA — render mockup aplikasi mobile di model HP 3D.

Butuh screenshot di design/app/screens/{login,home,monitor,chat,device}.png
(dibuat dari design/app/index.html#<id> via Chrome headless, 390x844 @3x).

  blender -b -P design/blender/aruna_app_mockup.py -- [--preview]
Keluaran: design/app/renders/mockup_kipas.png, mockup_flatlay.png
"""
import bpy
import bmesh
import math
import os
import sys

from mathutils import Vector

ARGS = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
PREVIEW = "--preview" in ARGS
HERE = os.path.dirname(os.path.abspath(__file__))
SCREENS = os.path.join(HERE, "..", "app", "screens")
OUT = os.path.join(HERE, "..", "app", "renders")
os.makedirs(OUT, exist_ok=True)

bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene


def node_tree_of(idb):
    if idb.node_tree is None:
        try:
            idb.use_nodes = True
        except Exception:
            pass
    return idb.node_tree


def mat(name, color, metallic=0.0, rough=0.4, coat=0.0):
    m = bpy.data.materials.new(name)
    b = next(n for n in node_tree_of(m).nodes if n.type == "BSDF_PRINCIPLED")
    b.inputs["Base Color"].default_value = (*color, 1)
    b.inputs["Metallic"].default_value = metallic
    b.inputs["Roughness"].default_value = rough
    b.inputs["Coat Weight"].default_value = coat
    return m


M_FRAME = mat("Rangka_HP", (0.80, 0.82, 0.81), metallic=1.0, rough=0.22)
M_BACK = mat("Punggung_HP", (0.90, 0.92, 0.91), rough=0.3, coat=1.0)
M_GLASS = mat("Kaca_Hitam", (0.004, 0.004, 0.004), rough=0.05, coat=1.0)
M_LENS = mat("Lensa", (0.01, 0.01, 0.012), rough=0.05, coat=1.0)
M_FLOOR = mat("Lantai", (0.66, 0.73, 0.69), rough=0.9)


def screen_mat(key):
    m = bpy.data.materials.new(f"Layar_{key}")
    nt = node_tree_of(m)
    b = next(n for n in nt.nodes if n.type == "BSDF_PRINCIPLED")
    tex = nt.nodes.new("ShaderNodeTexImage")
    tex.image = bpy.data.images.load(os.path.join(SCREENS, f"{key}.png"), check_existing=True)
    tex.interpolation = "Cubic"
    b.inputs["Base Color"].default_value = (0.0, 0.0, 0.0, 1)
    b.inputs["Roughness"].default_value = 0.12
    if "Specular IOR Level" in b.inputs:
        b.inputs["Specular IOR Level"].default_value = 0.25
    b.inputs["Coat Weight"].default_value = 0.0
    nt.links.new(tex.outputs["Color"], b.inputs["Emission Color"])
    b.inputs["Emission Strength"].default_value = 1.0
    return m


SCREEN_M = {k: screen_mat(k) for k in ("login", "home", "monitor", "chat", "device")}

# ---------------------------------------------------------------- geometri HP (satuan meter)
SW, SH = 0.0680, 0.0680 * 844 / 390      # layar mengikuti rasio screenshot
BZ = 0.0019                               # bezel hitam
W, H, T = SW + 2 * BZ + 0.0008, SH + 2 * BZ + 0.0008, 0.0078
R_BODY, R_GLASS, R_SCREEN = 0.0108, 0.0104, 0.0090


def rrect_bm(w, h, r, z=0.0, seg=16):
    bm = bmesh.new()
    vs = [bm.verts.new((x, y, z)) for x, y in ((-w / 2, -h / 2), (w / 2, -h / 2), (w / 2, h / 2), (-w / 2, h / 2))]
    bm.faces.new(vs)
    bmesh.ops.bevel(bm, geom=vs, offset=r, segments=seg, affect="VERTICES", profile=0.5)
    return bm


def to_obj(name, bm, material, col):
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    me.materials.append(material)
    o = bpy.data.objects.new(name, me)
    col.objects.link(o)
    return o


def phone(key, col):
    root = bpy.data.objects.new(f"HP_{key}", None)
    col.objects.link(root)
    # badan
    bm = rrect_bm(W, H, R_BODY, -T / 2)
    bm.faces.ensure_lookup_table()
    f = bm.faces[0]
    ext = bmesh.ops.extrude_face_region(bm, geom=[f])
    bmesh.ops.translate(bm, vec=(0, 0, T), verts=[v for v in ext["geom"] if isinstance(v, bmesh.types.BMVert)])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    body = to_obj(f"HP_{key}_Badan", bm, M_FRAME, col)
    body.data.materials.append(M_BACK)
    for p in body.data.polygons:
        p.use_smooth = True
        if p.normal.z < -0.9:
            p.material_index = 1
    bev = body.modifiers.new("Bevel", "BEVEL")
    bev.width = 0.0022
    bev.segments = 6
    bev.limit_method = "ANGLE"
    bev.harden_normals = True
    body.parent = root
    # kaca depan + layar
    glass = to_obj(f"HP_{key}_Kaca", rrect_bm(W - 0.0012, H - 0.0012, R_GLASS, T / 2 + 0.00005), M_GLASS, col)
    glass.parent = root
    bm = rrect_bm(SW, SH, R_SCREEN, T / 2 + 0.00012)
    uv = bm.loops.layers.uv.verify()
    for fc in bm.faces:
        for l in fc.loops:
            l[uv].uv = (l.vert.co.x / SW + 0.5, l.vert.co.y / SH + 0.5)
    scr = to_obj(f"HP_{key}_Layar", bm, SCREEN_M[key], col)
    scr.parent = root
    # tombol samping
    for nm, x, y, ln in (("Power", 1, 0.022, 0.016), ("Vol1", -1, 0.028, 0.011), ("Vol2", -1, 0.014, 0.011)):
        bpy.ops.mesh.primitive_cube_add(size=1)
        b = bpy.context.active_object
        bpy.context.collection.objects.unlink(b)
        col.objects.link(b)
        b.name = f"HP_{key}_{nm}"
        b.scale = (0.0012, ln, 0.0032)
        b.location = (x * (W / 2 + 0.0003), y, 0)
        b.data.materials.append(M_FRAME)
        b.modifiers.new("Bevel", "BEVEL").width = 0.0005
        b.parent = root
    # kamera belakang
    bump = to_obj(f"HP_{key}_Kamera", rrect_bm(0.024, 0.024, 0.006, -T / 2 - 0.0009), M_BACK, col)
    bump.location = (-W / 2 + 0.017, H / 2 - 0.017, 0)
    bump.parent = root
    for dx, dy in ((-0.005, 0.005), (0.005, -0.005)):
        bpy.ops.mesh.primitive_cylinder_add(radius=0.0042, depth=0.0012, vertices=48)
        c = bpy.context.active_object
        bpy.context.collection.objects.unlink(c)
        col.objects.link(c)
        c.location = (-W / 2 + 0.017 + dx, H / 2 - 0.017 + dy, -T / 2 - 0.0012)
        c.data.materials.append(M_LENS)
        c.parent = root
    return root


def look(obj, target):
    obj.rotation_euler = (Vector(target) - obj.location).to_track_quat("-Z", "Y").to_euler()


def area(name, loc, target, power, size, col):
    ld = bpy.data.lights.new(name, "AREA")
    ld.energy, ld.size = power, size
    o = bpy.data.objects.new(name, ld)
    col.objects.link(o)
    o.location = loc
    o.visible_camera = False
    look(o, target)


def sweep(col, color_mat):
    bm = bmesh.new()
    prof = [(-3.0, 0.0), (0.18, 0.0)]
    for k in range(1, 17):
        a = k / 16 * math.pi / 2
        prof.append((0.18 + 0.35 * math.sin(a), 0.35 * (1 - math.cos(a))))
    prof.append((0.53, 3.0))
    L = [bm.verts.new((-3, y, z)) for y, z in prof]
    R = [bm.verts.new((3, y, z)) for y, z in prof]
    for i in range(len(prof) - 1):
        bm.faces.new((L[i], R[i], R[i + 1], L[i + 1]))
    o = to_obj("Latar", bm, color_mat, col)
    for p in o.data.polygons:
        p.use_smooth = True
    return o


# ---------------------------------------------------------------- render setup
r = scene.render
r.engine = "CYCLES"
scene.cycles.samples = 48 if PREVIEW else 256
scene.cycles.use_denoising = True
r.resolution_x, r.resolution_y = (1200, 800) if PREVIEW else (2400, 1600)
scene.view_settings.view_transform = "Standard"
scene.view_settings.look = "None"
world = bpy.data.worlds.new("Dunia")
scene.world = world
bg = next(n for n in node_tree_of(world).nodes if n.type == "BACKGROUND")
bg.inputs["Color"].default_value = (0.85, 0.9, 0.87, 1)
bg.inputs["Strength"].default_value = 1.05
try:
    prefs = bpy.context.preferences.addons["cycles"].preferences
    for t in ("OPTIX", "CUDA", "HIP"):
        try:
            prefs.compute_device_type = t
        except Exception:
            continue
        prefs.get_devices()
        if any(d.type != "CPU" for d in prefs.devices):
            for d in prefs.devices:
                d.use = True
            scene.cycles.device = "GPU"
            break
except Exception:
    pass


def new_col(name):
    c = bpy.data.collections.new(name)
    scene.collection.children.link(c)
    return c


def clear(col):
    for o in list(col.objects):
        bpy.data.objects.remove(o)
    bpy.data.collections.remove(col)


def render(name):
    r.filepath = os.path.join(OUT, name)
    bpy.ops.render.render(write_still=True)
    print("[ARUNA] render ->", r.filepath)


# ================================================================ 1. KIPAS: 5 HP berdiri
col = new_col("Kipas")
sweep(col, M_FLOOR)
LEAN = math.radians(8)
fan = [("login", -0.172, 0.105, 24), ("monitor", -0.088, 0.04, 12), ("home", 0.0, 0.0, 0),
       ("chat", 0.088, 0.04, -12), ("device", 0.172, 0.105, -24)]
for key, x, y, rz in fan:
    p = phone(key, col)
    p.rotation_euler = (math.pi / 2 - LEAN, 0, math.radians(rz))
    p.location = (x, y, H / 2 * math.cos(LEAN) + T / 2 * math.sin(LEAN) + 0.0005)
# penyangga tipis di belakang tiap HP tidak dimodelkan; kemiringan kecil tetap terbaca natural
cam = bpy.data.objects.new("Cam_Kipas", bpy.data.cameras.new("Cam_Kipas"))
col.objects.link(cam)
cam.data.lens = 50
cam.location = (0.0, -0.62, 0.16)
look(cam, (0.0, 0.05, 0.068))
scene.camera = cam
area("Key", (-0.5, -0.3, 0.6), (0, 0.05, 0.05), 1.9, 0.6, col)
area("Fill", (0.6, -0.3, 0.25), (0, 0.05, 0.07), 0.65, 0.8, col)
area("Rim", (0.2, 0.5, 0.5), (0, 0.05, 0.1), 1.0, 0.5, col)
render("mockup_kipas.png")
clear(col)

# ================================================================ 2. FLAT-LAY: HP rebah, tampak atas
col = new_col("Flatlay")
bpy.ops.mesh.primitive_plane_add(size=4)
fl = bpy.context.active_object
bpy.context.collection.objects.unlink(fl)
col.objects.link(fl)
fl.data.materials.append(M_FLOOR)
lay = [("login", -0.176, 0.012, 6), ("home", -0.088, -0.018, -4), ("monitor", 0.0, 0.016, 3),
       ("chat", 0.088, -0.014, -5), ("device", 0.176, 0.01, 4)]
for key, x, y, rz in lay:
    p = phone(key, col)
    p.rotation_euler = (0, 0, math.radians(rz))
    p.location = (x, y, T / 2 + 0.0012)
cam = bpy.data.objects.new("Cam_Flatlay", bpy.data.cameras.new("Cam_Flatlay"))
col.objects.link(cam)
cam.data.type = "ORTHO"
cam.data.ortho_scale = 0.46
cam.location = (0.0, 0.0, 0.8)
cam.rotation_euler = (0, 0, 0)
scene.camera = cam
area("Key", (-0.7, 0.45, 0.4), (0, 0, 0), 3.4, 0.7, col)
area("Fill", (0.7, -0.5, 0.3), (0, 0, 0), 1.05, 0.9, col)
render("mockup_flatlay.png")

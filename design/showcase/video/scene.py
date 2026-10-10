"""
ARUNA — scene video use case portrait (1080x1920, 30 fps).

  blender -b design/blender/aruna_mesin.blend -P design/showcase/video/scene.py -- [--test] [--frames a-b]
Basis   : aruna_mesin.blend (mesin, kompor, pot, studio)
Karakter: design/showcase/char/char_rigged.blend (Rigify, aksi Idle/Walk/WalkCarry/Drop/Phone/Pour/Wave)
Keluaran: design/showcase/video/frames/f_####.png  (lalu dirakit oleh edit.py)
"""
import bpy
import math
import os
import sys

from mathutils import Vector, Matrix

ARGS = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
TEST = "--test" in ARGS
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
CHAR = os.path.join(ROOT, "design", "showcase", "char", "char_rigged.blend")
APP_HOME = os.path.join(ROOT, "design", "app", "screens", "home.png")
FRAMES = os.path.join(HERE, "test" if TEST else "frames")
os.makedirs(FRAMES, exist_ok=True)

scene = bpy.context.scene
scene.render.fps = 30

# ---------------------------------------------------------------- karakter (append)
with bpy.data.libraries.load(CHAR, link=False) as (src, dst):
    dst.objects = [n for n in src.objects if n == "ARUNA_Rig" or n.startswith("Karakter_")]
    dst.actions = list(src.actions)
col_char = bpy.data.collections.new("Karakter")
scene.collection.children.link(col_char)
for o in dst.objects:
    col_char.objects.link(o)
rig = bpy.data.objects["ARUNA_Rig"]
rig.scale = (0.9, 0.9, 0.9)             # 1,89 m -> 1,70 m
for b in rig.pose.bones:
    b.rotation_mode = "QUATERNION"
for side in ("L", "R"):
    for par in (f"upper_arm_parent.{side}", f"thigh_parent.{side}"):
        if par in rig.pose.bones:
            rig.pose.bones[par]["IK_FK"] = 1.0

# ---------------------------------------------------------------- timeline (frame)
SHOTS = [  # (mulai, kamera)
    (1, "Cam_Datang"), (58, "Cam_Buang"), (121, "Cam_Layar"), (201, "Cam_HP"), (291, "Cam_Siram"), (381, "Cam_Api"), (471, "Cam_Hero"),
]
END = 560
scene.frame_start, scene.frame_end = 1, END

# NLA: satu track per klip (track atas menimpa), tumpang 5 frame untuk blend
ad = rig.animation_data or rig.animation_data_create()
ad.action = None
CLIPS = [  # (aksi, mulai, selesai)
    ("WalkCarry", 1, 50), ("Idle", 46, 62), ("Drop", 60, 121),
    ("Idle", 121, 204), ("Phone", 201, 294), ("Pour", 291, 352), ("Idle", 350, 384),
    ("Idle", 381, 474), ("Wave", 471, END + 1),
]
for i, (name, a, b) in enumerate(CLIPS):
    act = bpy.data.actions[name]
    st = ad.nla_tracks.new().strips.new(f"{name}_{a}", a, act)
    length = act.frame_range[1] - act.frame_range[0]
    st.repeat = max(1.0, (b - a) / max(length, 1))
    st.blend_in = st.blend_out = 5 if i else 0
    st.extrapolation = "NOTHING"

# transform rig per shot (potong kamera = boleh teleport)
def key_rig(f, loc, rz):
    rig.location = loc
    rig.rotation_euler = (0, 0, math.radians(rz))
    rig.keyframe_insert("location", frame=f)
    rig.keyframe_insert("rotation_euler", frame=f)


key_rig(1, (-1.55, -0.62, 0), 90)
key_rig(46, (-0.05, -0.62, 0), 90)
key_rig(60, (0.0, -0.58, 0), 180)
key_rig(120, (0.0, -0.58, 0), 180)
key_rig(121, (3.5, -0.8, 0), 0)         # keluar frame selama close-up layar
key_rig(200, (3.5, -0.8, 0), 0)
key_rig(201, (0.48, -0.78, 0), 0)       # di samping mesin, menghadap kamera (HP)
key_rig(290, (0.48, -0.78, 0), 0)
key_rig(291, (-0.6, -0.62, 0), 180)      # di depan pot (tangan kanan tepat di atas pot)
key_rig(380, (-0.6, -0.62, 0), 180)
key_rig(381, (0.66, -0.62, 0), 180)     # di depan kompor
key_rig(470, (0.66, -0.62, 0), 180)
key_rig(471, (0.42, -0.5, 0), -12)      # hero, menghadap kamera
key_rig(END, (0.42, -0.5, 0), -12)
# jalan pertama perlu linear, sisanya potong
def fcurves_of(obj):
    act = obj.animation_data.action
    out = []
    for layer in getattr(act, "layers", []):
        for strip in layer.strips:
            for bag in strip.channelbags:
                out += list(bag.fcurves)
    return out or list(getattr(act, "fcurves", []))


for fc in fcurves_of(rig):
    for kp in fc.keyframe_points:
        kp.interpolation = "LINEAR" if kp.co[0] < 60 else "CONSTANT"


# ---------------------------------------------------------------- material bantu
def mat(name, color, rough=0.4, emit=None, strength=0.0, metallic=0.0):
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


col_prop = bpy.data.collections.new("Properti")
scene.collection.children.link(col_prop)


def add(obj, material=None, smooth=True):
    for c in obj.users_collection:
        c.objects.unlink(obj)
    col_prop.objects.link(obj)
    if material:
        obj.data.materials.clear()
        obj.data.materials.append(material)
    if smooth and obj.type == "MESH":
        for p in obj.data.polygons:
            p.use_smooth = True
    return obj


def vis(obj, ranges):
    """Tampilkan obj hanya pada rentang frame [(a,b), ...]."""
    for f in range(1, END + 2):
        on = any(a <= f <= b for a, b in ranges)
        if f == 1 or on != prev:
            obj.hide_render = obj.hide_viewport = not on
            obj.keyframe_insert("hide_render", frame=f)
            obj.keyframe_insert("hide_viewport", frame=f)
        prev = on


def attach(obj, bone, loc, rot=(0, 0, 0)):
    obj.parent = rig
    obj.parent_type = "BONE"
    obj.parent_bone = bone
    obj.matrix_parent_inverse = Matrix.Identity(4)
    obj.location = loc
    obj.rotation_euler = rot


M_BOWL = mat("Mangkuk", (0.85, 0.87, 0.86), 0.3)
M_RICE = mat("Nasi", (0.92, 0.9, 0.82), 0.7)
M_VEG = mat("Sayur", (0.1, 0.4, 0.06), 0.6)
M_PEEL = mat("Kulit_Buah", (0.85, 0.55, 0.08), 0.5)
M_BOTTLE = bpy.data.materials.get("Jeriken") or mat("Botol", (0.62, 0.22, 0.02), 0.45)
M_STREAM = mat("Aliran_Pupuk", (0.35, 0.22, 0.05), 0.1)
M_PHONE = mat("HP_Bodi", (0.82, 0.84, 0.83), 0.25, metallic=1.0)

# mangkuk berisi sisa makanan (di tangan kanan sampai dibuang)
bpy.ops.mesh.primitive_uv_sphere_add(radius=0.085, segments=32, ring_count=16)
bowl = add(bpy.context.active_object, M_BOWL)
bowl.name = "Mangkuk"
bpy.ops.object.mode_set(mode="EDIT")
bpy.ops.mesh.select_all(action="DESELECT")
bpy.ops.object.mode_set(mode="OBJECT")
for v in bowl.data.vertices:
    v.select = v.co.z > 0.0
bpy.ops.object.mode_set(mode="EDIT")
bpy.ops.mesh.delete(type="VERT")
bpy.ops.object.mode_set(mode="OBJECT")
sol = bowl.modifiers.new("Tebal", "SOLIDIFY")
sol.thickness = 0.006
bowl.scale = (1, 1, 0.6)
food = []
for i, (m, off) in enumerate([(M_RICE, (0, 0, -0.01)), (M_VEG, (0.03, 0.02, 0.0)), (M_PEEL, (-0.03, -0.01, 0.005)),
                              (M_RICE, (0.01, -0.03, 0.0)), (M_VEG, (-0.02, 0.03, 0.002))]):
    bpy.ops.mesh.primitive_ico_sphere_add(radius=0.03 if i == 0 else 0.022, subdivisions=2, location=off)
    s = add(bpy.context.active_object, m)
    s.name = f"Makanan_{i}"
    s.parent = bowl
    food.append(s)
attach(bowl, "DEF-hand.R", (0.0, 0.07, 0.06), (math.radians(90), 0, 0))
vis(bowl, [(1, 98)])

# makanan jatuh ke corong
for i in range(5):
    bpy.ops.mesh.primitive_ico_sphere_add(radius=0.022, subdivisions=2)
    s = add(bpy.context.active_object, [M_RICE, M_VEG, M_PEEL][i % 3])
    s.name = f"Jatuh_{i}"
    x0, y0 = -0.04 + i * 0.02, -0.12 + (i % 2) * 0.03
    s.location = (x0, y0, 1.32)
    s.keyframe_insert("location", frame=92 + i)
    s.location = (x0 * 0.6, y0 * 0.5 + 0.02, 1.08)
    s.keyframe_insert("location", frame=104 + i)
    vis(s, [(92 + i, 106 + i)])
for s in food:
    vis(s, [(1, 92)])

# HP (layar = screenshot Beranda)
bpy.ops.mesh.primitive_cube_add(size=1)
ph = add(bpy.context.active_object, M_PHONE)
ph.name = "HP"
ph.scale = (0.072, 0.152, 0.008)
bpy.ops.object.transform_apply(scale=True)
bev = ph.modifiers.new("Bevel", "BEVEL")
bev.width, bev.segments = 0.008, 6
bpy.ops.mesh.primitive_plane_add(size=1)
scr = add(bpy.context.active_object, None, smooth=False)
scr.name = "HP_Layar"
scr.scale = (0.066, 0.143, 1)
bpy.ops.object.transform_apply(scale=True)
scr.location = (0, 0, 0.0042)
scr.parent = ph
ms = mat("HP_Layar_Mat", (0, 0, 0), 0.15)
nt = ms.node_tree
tex = nt.nodes.new("ShaderNodeTexImage")
tex.image = bpy.data.images.load(APP_HOME)
bsdf = next(n for n in nt.nodes if n.type == "BSDF_PRINCIPLED")
nt.links.new(tex.outputs["Color"], bsdf.inputs["Emission Color"])
bsdf.inputs["Emission Strength"].default_value = 1.2
scr.data.materials.append(ms)
attach(ph, "DEF-hand.R", (0.0, 0.08, 0.035), (math.radians(-90), math.radians(180), 0))
vis(ph, [(201, 290)])
vis(scr, [(201, 290)])

# botol pupuk + aliran
bpy.ops.mesh.primitive_cube_add(size=1)
bt = add(bpy.context.active_object, M_BOTTLE)
bt.name = "Botol_Tangan"
bt.scale = (0.1, 0.08, 0.13)
bpy.ops.object.transform_apply(scale=True)
bt.modifiers.new("Bevel", "BEVEL").width = 0.015
attach(bt, "DEF-hand.R", (0.0, 0.07, 0.0))
vis(bt, [(291, 380)])
bpy.ops.mesh.primitive_cylinder_add(radius=0.008, depth=0.62, vertices=16)
stream = add(bpy.context.active_object, M_STREAM)
stream.name = "Aliran"
stream.location = (-0.42, -0.2, 0.52)
vis(stream, [(312, 340)])

# ---------------------------------------------------------------- animasi mesin & properti
ob = bpy.data.objects
hinge = Vector((0, 0.22 - 0.012, 1.12 + 0.006))
piv = bpy.data.objects.new("Engsel_Tutup", None)
scene.collection.objects.link(piv)
piv.location = hinge
bpy.context.view_layer.update()
for n in ("Tutup", "Tutup_Pegangan"):
    o = ob[n]
    mw = o.matrix_world.copy()
    o.parent = piv
    o.matrix_parent_inverse = piv.matrix_world.inverted()
    o.matrix_world = mw
for f, ang in ((1, 100), (62, 100), (74, 0), (112, 0), (126, 100)):
    piv.rotation_euler = (math.radians(ang), 0, 0)
    piv.keyframe_insert("rotation_euler", frame=f)

liq = ob["Jendela_Level_Cairan"]
z0 = liq.location.z - liq.dimensions.z / 2
liq_h = liq.dimensions.z
for f, k in ((1, 0.45), (135, 0.45), (195, 1.0)):
    liq.scale.z = k
    liq.location.z = z0 + liq_h * k / 2
    liq.keyframe_insert("scale", frame=f)
    liq.keyframe_insert("location", frame=f)

for o in [o for o in ob if o.name.startswith("Api_")]:
    for f, k in ((1, 0.0), (398, 0.0), (408, 1.25), (414, 1.0)):
        o.scale = (k, k, k)
        o.keyframe_insert("scale", frame=f)
for o in [o for o in ob if o.name.startswith("Daun_")]:
    s0 = o.scale.copy()
    for f, k in ((1, 1.0), (325, 1.0), (378, 1.18)):
        o.scale = s0 * k
        o.keyframe_insert("scale", frame=f)

led = bpy.data.materials.get("LED_Hijau")
if led:
    b = next(n for n in led.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    for f in range(121, 205, 14):
        b.inputs["Emission Strength"].default_value = 3.0
        b.inputs["Emission Strength"].keyframe_insert("default_value", frame=f)
        b.inputs["Emission Strength"].default_value = 14.0
        b.inputs["Emission Strength"].keyframe_insert("default_value", frame=f + 7)

# ---------------------------------------------------------------- kamera
def cam(name, keys, lens):
    c = bpy.data.objects.new(name, bpy.data.cameras.new(name))
    scene.collection.objects.link(c)
    c.data.lens = lens
    c.data.dof.use_dof = True
    c.data.dof.aperture_fstop = 2.8
    for f, pos, tgt in keys:
        c.location = pos
        c.rotation_euler = (Vector(tgt) - Vector(pos)).to_track_quat("-Z", "Y").to_euler()
        c.keyframe_insert("location", frame=f)
        c.keyframe_insert("rotation_euler", frame=f)
        c.data.dof.focus_distance = (Vector(tgt) - Vector(pos)).length
        c.data.dof.keyframe_insert("focus_distance", frame=f)
    return c


CAMS = {
    "Cam_Datang": cam("Cam_Datang", [(1, (-0.2, -3.6, 1.15), (-0.6, -0.3, 0.85)),
                                     (57, (0.1, -3.3, 1.2), (-0.15, -0.3, 0.9))], 30),
    "Cam_Buang": cam("Cam_Buang", [(58, (1.35, -1.35, 1.78), (-0.02, -0.2, 1.05)),
                                   (120, (1.2, -1.2, 1.7), (-0.02, -0.2, 1.08))], 32),
    "Cam_Layar": cam("Cam_Layar", [(121, (-0.15, -1.35, 1.25), (-0.02, -0.22, 0.92)),
                                   (200, (0.05, -1.1, 1.12), (-0.04, -0.22, 0.9))], 40),
    "Cam_Siram": cam("Cam_Siram", [(291, (-1.75, -0.95, 0.95), (-0.42, -0.3, 0.55)),
                                   (380, (-1.55, -1.1, 0.85), (-0.42, -0.3, 0.5))], 32),
    "Cam_Api": cam("Cam_Api", [(381, (0.95, -0.62, 0.72), (0.66, -0.02, 0.56)),
                               (470, (0.88, -0.55, 0.68), (0.66, -0.02, 0.56))], 40),
    "Cam_Hero": cam("Cam_Hero", [(471, (0.2, -3.7, 1.05), (0.2, -0.2, 0.85)),
                                 (END, (0.2, -3.1, 1.0), (0.2, -0.2, 0.84))], 40),
}
# kamera over-shoulder HP: dihitung dari pose sebenarnya
scene.frame_set(245)
P = ph.matrix_world.translation.copy()
n = (ph.matrix_world.to_3x3() @ Vector((0, 0, 1))).normalized()
side = Vector((1, 0, 0))
print("[VID] HP di", tuple(round(x, 3) for x in P), "normal", tuple(round(x, 2) for x in n))
CAMS["Cam_HP"] = cam("Cam_HP", [(201, P + n * 0.55 + side * 0.28 + Vector((0, 0, 0.12)), P),
                                (290, P + n * 0.45 + side * 0.22 + Vector((0, 0, 0.1)), P)], 35)
# aliran pupuk: dari mulut botol ke pot
scene.frame_set(330)
B = bt.matrix_world.translation
top, bot = B.z - 0.06, 0.21
stream.location = (B.x, B.y, (top + bot) / 2)
stream.scale.z = (top - bot) / 0.62
print("[VID] botol di", tuple(round(x, 3) for x in B))

for f, n in SHOTS:
    m = scene.timeline_markers.new(n, frame=f)
    m.camera = CAMS[n]
scene.camera = CAMS["Cam_Datang"]

# ---------------------------------------------------------------- render
r = scene.render
r.engine = "BLENDER_EEVEE"
r.resolution_x, r.resolution_y = (540, 960) if TEST else (1080, 1920)
r.resolution_percentage = 100
r.image_settings.file_format = "PNG"
r.use_overwrite = False
r.use_placeholder = True
r.use_motion_blur = True
try:
    scene.eevee.taa_render_samples = 16 if TEST else 32
    scene.eevee.use_shadows = True
except Exception:
    pass
r.filepath = os.path.join(FRAMES, "f_")
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(HERE, "usecase.blend"))
print("[VID] scene siap:", END, "frame")

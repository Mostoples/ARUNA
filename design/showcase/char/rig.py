"""
Rigging karakter Sketchfab dengan addon Rigify + aksi animasi FK.

  blender -b -P design/showcase/char/rig.py
Masukan : source.glb ("Casual Male 3D Character – T-Pose" — sthaarpit, Sketchfab, CC-BY 4.0)
Keluaran: char_rigged.blend (rig Rigify + mesh ber-weight + aksi), char_anim.glb (untuk web)
"""
import bpy
import math
import os
import addon_utils
from mathutils import Vector, Quaternion, Matrix

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "source.glb")
FPS = 30

bpy.ops.wm.read_factory_settings(use_empty=True)
addon_utils.enable("rigify", default_set=True)
scene = bpy.context.scene
scene.render.fps = FPS

# ---------------------------------------------------------------- impor & bersihkan
bpy.ops.import_scene.gltf(filepath=SRC)
for o in [o for o in scene.objects if o.name.startswith("Icosphere")]:   # objek liar dari sumber
    bpy.data.objects.remove(o)
for img in bpy.data.images:                                              # tekstur ringan untuk web
    if img.size[0] > 1024:
        img.scale(1024, int(1024 * img.size[1] / img.size[0]))
meshes = [o for o in scene.objects if o.type == "MESH"]
for o in meshes:
    mw = o.matrix_world.copy()
    o.parent = None
    o.matrix_world = mw
for o in meshes:                                   # buang rig/bobot bawaan sumber
    for m in list(o.modifiers):
        o.modifiers.remove(m)
    o.vertex_groups.clear()
for o in [o for o in scene.objects if o.type in ("EMPTY", "ARMATURE")]:
    bpy.data.objects.remove(o)
bpy.ops.object.select_all(action="DESELECT")
for o in meshes:
    o.select_set(True)
bpy.context.view_layer.objects.active = meshes[0]
bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
for i, o in enumerate(meshes):
    o.name = f"Karakter_{i:02d}_{o.data.materials[0].name if o.data.materials else 'x'}"

# ---------------------------------------------------------------- landmark tubuh (m), dari mesh T-pose
verts = [o.matrix_world @ v.co for o in meshes for v in o.data.vertices]
arm = [v for v in verts if abs(v.x) > 0.45]
ARM_Z = sorted(v.z for v in arm)[len(arm) // 2]
ARM_Y = sorted(v.y for v in arm)[len(arm) // 2]
body = [v for v in verts if abs(v.x) < 0.12 and 0.9 < v.z < 1.4]
BY = sorted(v.y for v in body)[len(body) // 2]
print(f"[RIG] ARM_Z={ARM_Z:.3f} ARM_Y={ARM_Y:.3f} BODY_Y={BY:.3f}")

L = {  # titik sendi pria 1,89 m (x untuk sisi kiri/+X, dicerminkan untuk kanan); diukur dari render grid
    "hips": (0, BY, 1.00), "spine1": (0, BY, 1.10), "spine2": (0, BY, 1.24), "spine3": (0, BY, 1.38),
    "chest": (0, BY, 1.50), "neck": (0, BY - 0.01, 1.57), "neck2": (0, BY - 0.005, 1.63), "head": (0, BY, 1.67),
    "top": (0, BY, 1.89),
    "clav": (0.03, BY - 0.01, ARM_Z + 0.03), "shoulder": (0.18, ARM_Y, ARM_Z + 0.01), "elbow": (0.47, ARM_Y + 0.01, ARM_Z),
    "wrist": (0.75, ARM_Y, ARM_Z - 0.01), "hand_end": (0.86, ARM_Y, ARM_Z - 0.02),
    "hip": (0.10, BY, 0.97), "knee": (0.095, BY - 0.02, 0.51), "ankle": (0.10, BY + 0.03, 0.09),
    "toe": (0.10, BY - 0.10, 0.025), "toe_end": (0.10, BY - 0.16, 0.02),
    "heel_a": (0.06, BY + 0.08, 0.0), "heel_b": (0.14, BY + 0.08, 0.0),
}


def P(key, side=1):
    x, y, z = L[key]
    return Vector((x * side, y, z))


# ---------------------------------------------------------------- metarig Rigify
bpy.ops.object.armature_human_metarig_add()
meta = bpy.context.active_object
meta.name = "metarig"
bpy.ops.object.mode_set(mode="EDIT")
eb = meta.data.edit_bones
keep_prefix = ("spine", "shoulder", "upper_arm", "forearm", "hand", "thigh", "shin", "foot", "toe", "heel")
for b in list(eb):
    base = b.name.split(".")[0]
    if base not in keep_prefix:
        eb.remove(b)


def setb(name, head, tail, roll=None):
    b = eb[name]
    b.head, b.tail = head, tail
    if roll is not None:
        b.roll = roll


setb("spine", P("hips"), P("spine1"))
setb("spine.001", P("spine1"), P("spine2"))
setb("spine.002", P("spine2"), P("spine3"))
setb("spine.003", P("spine3"), P("chest"))
setb("spine.004", P("chest"), P("neck"))
setb("spine.005", P("neck"), P("neck2"))
setb("spine.006", P("head"), P("top"))
eb["spine.006"].head = P("neck2")
for s, sf in ((1, "L"), (-1, "R")):
    setb(f"shoulder.{sf}", P("clav", s), P("shoulder", s))
    setb(f"upper_arm.{sf}", P("shoulder", s), P("elbow", s))
    setb(f"forearm.{sf}", P("elbow", s), P("wrist", s))
    setb(f"hand.{sf}", P("wrist", s), P("hand_end", s))
    setb(f"thigh.{sf}", P("hip", s), P("knee", s))
    setb(f"shin.{sf}", P("knee", s), P("ankle", s))
    setb(f"foot.{sf}", P("ankle", s), P("toe", s))
    setb(f"toe.{sf}", P("toe", s), P("toe_end", s))
    hb = Vector(L["heel_a"]); hb.x *= s
    he = Vector(L["heel_b"]); he.x *= s
    setb(f"heel.02.{sf}", hb, he)
# roll konsisten: lengan sumbu-Z mengarah ke belakang (+Y) agar tekuk siku ke depan
bpy.ops.armature.select_all(action="SELECT")
bpy.ops.armature.calculate_roll(type="GLOBAL_POS_Y")
for n in ("spine", "spine.001", "spine.002", "spine.003", "spine.004", "spine.005", "spine.006"):
    eb[n].roll = 0
bpy.ops.object.mode_set(mode="OBJECT")
print("[RIG] metarig bones:", len(meta.data.bones))

# ---------------------------------------------------------------- generate rig
bpy.ops.object.select_all(action="DESELECT")
meta.select_set(True)
bpy.context.view_layer.objects.active = meta
bpy.ops.pose.rigify_generate()
rig = next(o for o in scene.objects if o.type == "ARMATURE" and o is not meta)
rig.name = "ARUNA_Rig"
meta.hide_viewport = meta.hide_render = True

# ---------------------------------------------------------------- skinning (bone heat), fallback transfer
# Mesh asli tidak manifold (pakaian berlapis), bone heat gagal. Jadi: proxy voxel remesh yang rapat
# -> bone heat di proxy -> transfer bobot ke mesh asli (Data Transfer, nearest face interpolated).
bpy.ops.object.select_all(action="DESELECT")
for o in meshes:
    o.select_set(True)
bpy.context.view_layer.objects.active = meshes[0]
bpy.ops.object.duplicate()
bpy.ops.object.join()
proxy = bpy.context.active_object
proxy.name = "Proxy_Skin"
rm = proxy.modifiers.new("Remesh", "REMESH")
rm.mode = "VOXEL"
rm.voxel_size = 0.012
bpy.ops.object.modifier_apply(modifier=rm.name)
bpy.ops.object.select_all(action="DESELECT")
proxy.select_set(True)
rig.select_set(True)
bpy.context.view_layer.objects.active = rig
bpy.ops.object.parent_set(type="ARMATURE_AUTO")
print(f"[RIG] proxy: {sum(1 for v in proxy.data.vertices if v.groups)}/{len(proxy.data.vertices)} berbobot")
for o in meshes:
    for vg in proxy.vertex_groups:
        o.vertex_groups.new(name=vg.name)
    dt = o.modifiers.new("Bobot", "DATA_TRANSFER")
    dt.object = proxy
    dt.use_vert_data = True
    dt.data_types_verts = {"VGROUP_WEIGHTS"}
    dt.vert_mapping = "POLYINTERP_NEAREST"
    dt.layers_vgroup_select_src = "ALL"
    dt.layers_vgroup_select_dst = "NAME"
    bpy.context.view_layer.objects.active = o
    bpy.ops.object.modifier_apply(modifier=dt.name)
    o.parent = rig
    am = o.modifiers.new("Armature", "ARMATURE")
    am.object = rig
bpy.data.objects.remove(proxy)
# vertex tanpa bobot (ujung jari tipis yang hilang di proxy) -> salin bobot vertex berbobot terdekat
from mathutils.kdtree import KDTree
for o in meshes:
    vs = o.data.vertices
    ok = [v for v in vs if sum(g.weight for g in v.groups) > 1e-4]
    kd = KDTree(len(ok))
    for i, v in enumerate(ok):
        kd.insert(v.co, i)
    kd.balance()
    for v in vs:
        if sum(g.weight for g in v.groups) > 1e-4:
            continue
        _, i, _ = kd.find(v.co)
        for g in ok[i].groups:
            o.vertex_groups[g.group].add([v.index], g.weight, "REPLACE")
for o in meshes:
    n = sum(1 for v in o.data.vertices if v.groups)
    print(f"[RIG] {o.name}: {n}/{len(o.data.vertices)} vertex berbobot")

# ---------------------------------------------------------------- utilitas pose
pb = rig.pose.bones
for side in ("L", "R"):
    for par in (f"upper_arm_parent.{side}", f"thigh_parent.{side}"):
        if par in pb and "IK_FK" in pb[par]:
            pb[par]["IK_FK"] = 1.0  # pakai FK
for b in pb:
    b.rotation_mode = "QUATERNION"


def R(axis, deg):
    return Quaternion(Vector(axis), math.radians(deg))


def to_local(name, q_world):
    """Rotasi dalam kerangka armature (rest) -> rotasi lokal pose bone."""
    B = rig.data.bones[name].matrix_local.to_quaternion()
    return B.inverted() @ q_world @ B


X, Y, Z = (1, 0, 0), (0, 1, 0), (0, 0, 1)
ARM_DOWN = 74


def arm_q(side, down=ARM_DOWN, fwd=0.0, out=0.0):
    s = 1 if side == "L" else -1
    return R(X, -fwd) @ R(Z, s * out) @ R(Y, s * down)


def base_pose():
    return {
        "upper_arm_fk.L": arm_q("L"), "upper_arm_fk.R": arm_q("R"),
        "forearm_fk.L": R(Z, -8), "forearm_fk.R": R(Z, 8),
    }


def key_pose(frame, pose, loc=None):
    for b in pb:
        if b.name in ("upper_arm_fk.L", "upper_arm_fk.R", "forearm_fk.L", "forearm_fk.R", "hand_fk.L", "hand_fk.R",
                      "thigh_fk.L", "thigh_fk.R", "shin_fk.L", "shin_fk.R", "foot_fk.L", "foot_fk.R",
                      "hips", "chest", "neck", "head", "torso"):
            q = pose.get(b.name, Quaternion())
            b.rotation_quaternion = to_local(b.name, q)
            b.keyframe_insert("rotation_quaternion", frame=frame)
    t = pb["torso"]
    t.location = loc or (0, 0, 0)
    t.keyframe_insert("location", frame=frame)


def merge(*ds):
    out = {}
    for d in ds:
        for k, v in d.items():
            out[k] = (out[k] @ v) if k in out else v
    return out


def new_action(name):
    act = bpy.data.actions.new(name)
    act.use_fake_user = True
    rig.animation_data_create()
    rig.animation_data.action = act
    return act


def walk_pose(phase):
    """phase 0..1 satu siklus jalan."""
    a = math.sin(phase * 2 * math.pi)
    c = math.cos(phase * 2 * math.pi)
    lift_l = max(0, -c) * 38
    lift_r = max(0, c) * 38
    return merge(base_pose(), {
        "thigh_fk.L": R(X, -24 * a), "thigh_fk.R": R(X, 24 * a),
        "shin_fk.L": R(X, lift_l + 4), "shin_fk.R": R(X, lift_r + 4),
        "foot_fk.L": R(X, -6 * a), "foot_fk.R": R(X, 6 * a),
        "upper_arm_fk.L": R(X, 18 * a), "upper_arm_fk.R": R(X, -18 * a),
        "forearm_fk.L": R(Z, -14), "forearm_fk.R": R(Z, 14),
        "chest": R(Z, 4 * a), "hips": R(Z, -5 * a),
    })


# ---- Idle (loop 90f)
new_action("Idle")
for f in range(0, 91, 15):
    k = math.sin(f / 90 * 2 * math.pi)
    key_pose(f + 1, merge(base_pose(), {"chest": R(X, -1.5 * k), "head": R(Z, 3 * k), "hips": R(Y, 1.2 * k)}),
             loc=(0, 0, 0.004 * k))

# ---- Walk (loop 32f)
new_action("Walk")
for i in range(9):
    ph = i / 8
    key_pose(1 + i * 4, walk_pose(ph), loc=(0, 0, 0.018 * abs(math.cos(ph * 2 * math.pi))))

def ov(base, d):
    """Timpa (bukan komposisi) — untuk pose lengan absolut dari arm_q()."""
    out = dict(base)
    out.update(d)
    return out


# ---- Drop: membuang sisa makanan ke corong (60f)
new_action("Drop")
hold = ov(base_pose(), {
    "upper_arm_fk.L": arm_q("L", down=86, fwd=28, out=-6), "forearm_fk.L": R(Z, -72),
    "upper_arm_fk.R": arm_q("R", down=86, fwd=28, out=-6), "forearm_fk.R": R(Z, 72),
})
reach = ov(base_pose(), {
    "chest": R(X, 18), "hips": R(X, 8), "head": R(X, 14),
    "upper_arm_fk.L": arm_q("L", down=88, fwd=62, out=-8), "forearm_fk.L": R(Z, -18),
    "upper_arm_fk.R": arm_q("R", down=88, fwd=62, out=-8), "forearm_fk.R": R(Z, 18),
})
key_pose(1, hold)
key_pose(18, reach, loc=(0, 0, -0.03))
key_pose(36, merge(reach, {"hand_fk.L": R(X, 50), "hand_fk.R": R(X, -50)}), loc=(0, 0, -0.035))
key_pose(60, base_pose())

# ---- WalkCarry: berjalan sambil membawa mangkuk (loop 32f)
new_action("WalkCarry")
arms_hold = {k: hold[k] for k in ("upper_arm_fk.L", "upper_arm_fk.R", "forearm_fk.L", "forearm_fk.R")}
for i in range(9):
    ph = i / 8
    key_pose(1 + i * 4, ov(walk_pose(ph), arms_hold), loc=(0, 0, 0.018 * abs(math.cos(ph * 2 * math.pi))))

# ---- Phone: melihat HP di tangan kanan (loop 90f)
new_action("Phone")
phone = ov(base_pose(), {
    "upper_arm_fk.R": arm_q("R", down=86, fwd=14, out=-10), "forearm_fk.R": R(Z, 104),
    "head": R(X, 22), "neck": R(X, 8),
})
for f in (1, 46, 91):
    k = 1 if f == 46 else 0
    key_pose(f, merge(phone, {"head": R(Z, 4 * k), "chest": R(X, -1 * k)}))

# ---- Pour: menuang pupuk ke pot (60f)
new_action("Pour")
pour0 = ov(base_pose(), {"upper_arm_fk.R": arm_q("R", down=88, fwd=48, out=4), "forearm_fk.R": R(Z, 22),
                         "chest": R(X, 10), "head": R(X, 16)})
pour1 = ov(pour0, {"hand_fk.R": R(X, -80)})
key_pose(1, pour0)
key_pose(20, pour1)
key_pose(45, pour1)
key_pose(60, pour0)

# ---- Wave: menyapa (loop 40f)
new_action("Wave")
for i, f in enumerate((1, 11, 21, 31, 41)):
    sgn = 1 if i % 2 else -1
    key_pose(f, ov(base_pose(), {
        "upper_arm_fk.R": arm_q("R", down=-25), "forearm_fk.R": R(Y, 95 + 18 * sgn),
        "head": R(Z, -6), "chest": R(Z, -4),
    }))

rig.animation_data.action = bpy.data.actions["Idle"]
for a in bpy.data.actions:
    for fc in a.fcurves if hasattr(a, "fcurves") else []:
        pass

bpy.ops.wm.save_as_mainfile(filepath=os.path.join(HERE, "char_rigged.blend"))
print("[RIG] saved char_rigged.blend")

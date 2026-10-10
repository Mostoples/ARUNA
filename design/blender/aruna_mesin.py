"""
ARUNA — model 3D mesin smart biodigester rumahan, format vertikal (prosedural).

Satu unit menara 44 x 44 x 112 cm. Alur pakai bernomor di muka depan:
  1 masukkan sisa makanan (tutup atas / pedal kaki) -> 2 ambil pupuk cair (ceruk botol)
  -> 3 ambil kompos (laci bawah). Biogas keluar di sisi kanan ke kompor.

Jalankan (dari root repo):
  "C:\\Program Files\\Blender Foundation\\Blender 5.2\\blender.exe" -b -P design/blender/aruna_mesin.py -- [--preview] [--no-render]

Keluaran di design/blender/:
  aruna_mesin.blend, aruna_mesin.glb, renders/*.png

Satuan: meter. Sumbu: X kanan, Y belakang, Z atas (depan mesin menghadap -Y).
"""
import bpy
import bmesh
import math
import os
import sys

import numpy as np
from mathutils import Vector, Matrix, Euler

ARGS = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
PREVIEW = "--preview" in ARGS
NO_RENDER = "--no-render" in ARGS

OUT_DIR = os.path.dirname(os.path.abspath(__file__))
RENDER_DIR = os.path.join(OUT_DIR, "renders")
os.makedirs(RENDER_DIR, exist_ok=True)

# ---------------------------------------------------------------- scene reset
bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene
scene.unit_settings.system = "METRIC"


def collection(name):
    col = bpy.data.collections.new(name)
    scene.collection.children.link(col)
    return col


COL_MESIN = collection("ARUNA_Mesin")
COL_ENV = collection("Studio")


def use_collection(col):
    bpy.context.view_layer.active_layer_collection = \
        bpy.context.view_layer.layer_collection.children[col.name]


# ---------------------------------------------------------------- materials
def srgb(hexstr):
    h = hexstr.lstrip("#")
    out = []
    for i in (0, 2, 4):
        c = int(h[i:i + 2], 16) / 255
        out.append(c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4)
    return tuple(out)


def node_tree_of(idblock):
    if idblock.node_tree is None:
        try:
            idblock.use_nodes = True
        except Exception:
            pass
    return idblock.node_tree


def make_mat(name, color, metallic=0.0, rough=0.5, coat=0.0, transmission=0.0,
             emission=None, strength=0.0, alpha=1.0, ior=1.45):
    m = bpy.data.materials.new(name)
    nt = node_tree_of(m)
    bsdf = next(n for n in nt.nodes if n.type == "BSDF_PRINCIPLED")
    vals = {
        "Base Color": (*color, 1.0),
        "Metallic": metallic,
        "Roughness": rough,
        "Coat Weight": coat,
        "Transmission Weight": transmission,
        "IOR": ior,
        "Alpha": alpha,
    }
    if emission is not None:
        vals["Emission Color"] = (*emission, 1.0)
        vals["Emission Strength"] = strength
    for k, v in vals.items():
        if k in bsdf.inputs:
            bsdf.inputs[k].default_value = v
    m.diffuse_color = (*color, alpha)
    m.metallic = metallic
    m.roughness = rough
    return m


GREEN = srgb("#158a52")
TEAL = srgb("#0e7a6a")

M = {
    "body": make_mat("Bodi_Putih", (0.80, 0.82, 0.80), rough=0.32, coat=0.35),
    "green": make_mat("Aksen_Hijau", GREEN, rough=0.35, coat=0.4),
    "teal": make_mat("Aksen_Teal", TEAL, rough=0.35, coat=0.4),
    "steel": make_mat("Stainless", (0.78, 0.79, 0.80), metallic=1.0, rough=0.28),
    "brushed": make_mat("Stainless_Kasar", (0.62, 0.64, 0.66), metallic=1.0, rough=0.45),
    "frame": make_mat("Rangka_Gelap", (0.035, 0.04, 0.042), metallic=0.6, rough=0.45),
    "rubber": make_mat("Karet", (0.012, 0.012, 0.012), rough=0.75),
    "plastic_dark": make_mat("Plastik_Gelap", (0.02, 0.025, 0.025), rough=0.5),
    "glass": make_mat("Kaca", (0.9, 0.95, 0.95), rough=0.03, transmission=1.0, ior=1.5),
    "liquid": make_mat("Cairan_Digestat", (0.22, 0.30, 0.03), rough=0.15, transmission=0.35),
    "compost": make_mat("Kompos", (0.05, 0.03, 0.015), rough=0.95),
    "red": make_mat("Tuas_Merah", (0.55, 0.02, 0.015), rough=0.35, coat=0.5),
    "brass": make_mat("Kuningan", (0.8, 0.55, 0.22), metallic=1.0, rough=0.3),
    "jerry": make_mat("Jeriken", (0.62, 0.22, 0.02), rough=0.45),
    "white": make_mat("Label_Putih", (0.9, 0.9, 0.9), rough=0.4),
    "dial": make_mat("Muka_Gauge", (0.92, 0.92, 0.9), rough=0.5),
    "led": make_mat("LED_Hijau", GREEN, emission=srgb("#2fb673"), strength=8.0),
    "led_amber": make_mat("LED_Amber", (0.8, 0.4, 0.02), emission=(1.0, 0.45, 0.02), strength=6.0),
    "lens": make_mat("Lensa", (0.01, 0.01, 0.02), rough=0.05, coat=1.0),
    "floor": make_mat("Lantai_Studio", (0.55, 0.58, 0.56), rough=0.85),
}


def screen_material():
    """Layar panel kontrol: UI dashboard kecil digambar dengan numpy."""
    W, H = 640, 400
    img = bpy.data.images.new("Layar_UI", W, H, alpha=False)
    a = np.zeros((H, W, 4), dtype=np.float32)
    a[..., 3] = 1.0
    bg = np.array([0.03, 0.07, 0.06])
    a[..., :3] = bg
    g = np.array([0.18, 0.71, 0.45])
    t = np.array([0.12, 0.62, 0.53])
    amber = np.array([0.95, 0.65, 0.15])
    card = np.array([0.07, 0.14, 0.12])

    def rect(x0, y0, x1, y1, c):
        a[y0:y1, x0:x1, :3] = c

    yy, xx = np.mgrid[0:H, 0:W]
    # header (origin bawah-kiri)
    rect(0, H - 44, W, H, np.array([0.05, 0.11, 0.09]))
    rect(20, H - 30, 120, H - 16, g)
    rect(W - 60, H - 30, W - 20, H - 16, t)
    # tiga kartu metrik
    for i, c in enumerate((g, t, amber)):
        x0 = 20 + i * 205
        rect(x0, 200, x0 + 190, 330, card)
        rect(x0 + 16, 300, x0 + 90, 312, c * 0.6)
        rect(x0 + 16, 230, x0 + 16 + [150, 110, 70][i], 260, c)
    # grafik garis riwayat
    rect(20, 20, W - 180, 180, card)
    xs = np.arange(40, W - 200)
    ys = (100 + 45 * np.sin((xs - 40) / 45.0) + 15 * np.sin((xs - 40) / 13.0)).astype(int)
    for dy in range(-2, 3):
        a[np.clip(ys + dy, 0, H - 1), xs, :3] = g
    # gauge donat (level digester)
    cx, cy, r = W - 90, 100, 62
    d = np.hypot(xx - cx, yy - cy)
    ang = (np.arctan2(yy - cy, xx - cx) + 2 * np.pi) % (2 * np.pi)
    ring = (d > r - 14) & (d < r)
    a[ring, :3] = card * 1.6
    a[ring & (ang < 2 * np.pi * 0.68), :3] = t
    img.pixels.foreach_set(a.ravel())
    img.pack()

    m = make_mat("Layar", (0.02, 0.05, 0.04), rough=0.15, coat=1.0)
    nt = m.node_tree
    bsdf = next(n for n in nt.nodes if n.type == "BSDF_PRINCIPLED")
    tex = nt.nodes.new("ShaderNodeTexImage")
    tex.image = img
    nt.links.new(tex.outputs["Color"], bsdf.inputs["Base Color"])
    nt.links.new(tex.outputs["Color"], bsdf.inputs["Emission Color"])
    bsdf.inputs["Emission Strength"].default_value = 2.5
    return m


M["screen"] = screen_material()

# ---------------------------------------------------------------- primitives
use_collection(COL_MESIN)


def finish(obj, name, mat, bevel=0.0, segments=3, smooth=True):
    obj.name = name
    if obj.data is not None:
        obj.data.name = name
    if mat is not None:
        obj.data.materials.clear()
        obj.data.materials.append(mat)
    if smooth:
        for p in obj.data.polygons:
            p.use_smooth = True
    if bevel > 0:
        mod = obj.modifiers.new("Bevel", "BEVEL")
        mod.width = bevel
        mod.segments = segments
        mod.limit_method = "ANGLE"
        mod.harden_normals = True
    return obj


def box(name, size, loc, mat, bevel=0.006, rot=(0, 0, 0), segments=3):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc, rotation=rot)
    o = bpy.context.active_object
    o.scale = size
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    return finish(o, name, mat, bevel, segments)


def cyl(name, r, depth, loc, mat, rot=(0, 0, 0), verts=64, bevel=0.003, fill="NGON"):
    bpy.ops.mesh.primitive_cylinder_add(vertices=verts, radius=r, depth=depth,
                                        location=loc, rotation=rot, end_fill_type=fill)
    return finish(bpy.context.active_object, name, mat, bevel)


def cone(name, r1, r2, depth, loc, mat, rot=(0, 0, 0), verts=64, fill="NGON", bevel=0.0):
    bpy.ops.mesh.primitive_cone_add(vertices=verts, radius1=r1, radius2=r2, depth=depth,
                                    location=loc, rotation=rot, end_fill_type=fill)
    return finish(bpy.context.active_object, name, mat, bevel)


def sphere(name, r, loc, mat, scale=(1, 1, 1), segs=64):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=segs, ring_count=segs // 2, radius=r, location=loc)
    o = bpy.context.active_object
    o.scale = scale
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    return finish(o, name, mat)


def torus(name, R, r, loc, mat, rot=(0, 0, 0)):
    bpy.ops.mesh.primitive_torus_add(major_radius=R, minor_radius=r, location=loc, rotation=rot,
                                     major_segments=96, minor_segments=16)
    return finish(bpy.context.active_object, name, mat)


def rod(name, p1, p2, r, mat, verts=32):
    """Silinder lurus dari p1 ke p2."""
    p1, p2 = Vector(p1), Vector(p2)
    d = p2 - p1
    rot = Vector((0, 0, 1)).rotation_difference(d.normalized()).to_euler()
    return cyl(name, r, d.length, (p1 + p2) / 2, mat, rot=rot, verts=verts, bevel=0)


def pipe(name, pts, r, mat, joint_mat=None):
    """Pipa poligonal dengan sambungan elbow bulat."""
    parts = []
    for i in range(len(pts) - 1):
        parts.append(rod(f"{name}_{i}", pts[i], pts[i + 1], r, mat))
    for i in range(1, len(pts) - 1):
        parts.append(sphere(f"{name}_elbow{i}", r * 1.25, pts[i], joint_mat or mat, segs=24))
    return parts


def text_mesh(name, body, size, extrude, mat):
    cu = bpy.data.curves.new(name, "FONT")
    cu.body = body
    cu.size = size
    cu.extrude = extrude
    cu.align_x = "CENTER"
    cu.align_y = "CENTER"
    cu.resolution_u = 6
    try:
        cu.font = bpy.data.fonts.load(r"C:\Windows\Fonts\segoeuib.ttf", check_existing=True)
    except Exception:
        pass
    tmp = bpy.data.objects.new(name + "_tmp", cu)
    COL_MESIN.objects.link(tmp)
    bpy.context.view_layer.update()
    dg = bpy.context.evaluated_depsgraph_get()
    me = bpy.data.meshes.new_from_object(tmp.evaluated_get(dg))
    bpy.data.objects.remove(tmp)
    bpy.data.curves.remove(cu)
    me.name = name
    me.materials.append(mat)
    return me


def text_on_cylinder(name, body, size, center, R, z, mat, azimuth=0.0, extrude=0.0025):
    """Teks melengkung di permukaan silinder vertikal (menghadap -Y bila azimuth=0)."""
    me = text_mesh(name, body, size, extrude, mat)
    cx, cy = center
    for v in me.vertices:
        x, y, zz = v.co
        a = x / R + azimuth
        r = R + extrude + zz
        v.co = Vector((cx + r * math.sin(a), cy - r * math.cos(a), z + y))
    me.update()
    o = bpy.data.objects.new(name, me)
    COL_MESIN.objects.link(o)
    return o


def text_flat(name, body, size, loc, mat, rot=(math.pi / 2, 0, 0), extrude=0.002):
    me = text_mesh(name, body, size, extrude, mat)
    o = bpy.data.objects.new(name, me)
    o.location = loc
    o.rotation_euler = rot
    COL_MESIN.objects.link(o)
    return o


def on_tank(cx, cy, R, az_deg, z, out=0.0):
    """Titik di dinding silinder; azimuth 0 = depan (-Y), positif ke kanan."""
    a = math.radians(az_deg)
    return (cx + (R + out) * math.sin(a), cy - (R + out) * math.cos(a), z)


# ================================================================ UNIT VERTIKAL RUMAHAN
# Alur gravitasi atas -> bawah:
#   tutup + corong (1) -> pencacah & digester di badan -> keran pupuk cair (2) -> laci kompos (3)
# Gas biogas keluar dari sisi kanan (gauge + katup) ke kompor rumah.
HW = 0.22            # setengah lebar & dalam bodi (tapak 44 x 44 cm)
FY = -HW             # bidang depan
BV = 0.014            # radius tepi bodi
Z_A, Z_B, Z_C, Z_D, Z_TOP = 0.10, 0.30, 0.58, 0.90, 1.12

M["terracotta"] = make_mat("Pot_Tanah_Liat", (0.45, 0.16, 0.07), rough=0.8)
M["soil"] = make_mat("Tanah", (0.04, 0.025, 0.012), rough=1.0)
M["leaf"] = make_mat("Daun", (0.05, 0.25, 0.04), rough=0.5, coat=0.2)
M["flame"] = make_mat("Api_Biru", (0.1, 0.3, 1.0), emission=(0.15, 0.4, 1.0), strength=25.0,
                      transmission=0.6)
M["wood"] = make_mat("Kayu", (0.35, 0.2, 0.1), rough=0.6)

COL_CUT = collection("Pemotong")


def section(name, z0, z1, mat):
    return box(name, (2 * HW, 2 * HW, z1 - z0 - 0.002), (0, 0, (z0 + z1) / 2), mat, bevel=BV, segments=6)


def badge(num, x, z, bg, fg, r=0.024, y=FY):
    """Lencana langkah bernomor di muka depan."""
    cyl(f"Langkah_{num}", r, 0.004, (x, y - 0.002, z), bg, rot=(math.pi / 2, 0, 0), bevel=0.001)
    text_flat(f"Langkah_{num}_Angka", str(num), r * 1.3, (x, y - 0.0042, z - r * 0.02), fg, extrude=0.0008)


def hose(name, pts, r, mat):
    cu = bpy.data.curves.new(name, "CURVE")
    cu.dimensions = "3D"
    cu.bevel_depth = r
    cu.bevel_resolution = 4
    cu.use_fill_caps = True
    sp = cu.splines.new("NURBS")
    sp.points.add(len(pts) - 1)
    for p, co in zip(sp.points, pts):
        p.co = (*co, 1.0)
    sp.use_endpoint_u = True
    sp.order_u = 4
    sp.resolution_u = 24
    tmp = bpy.data.objects.new(name + "_tmp", cu)
    COL_MESIN.objects.link(tmp)
    bpy.context.view_layer.update()
    me = bpy.data.meshes.new_from_object(tmp.evaluated_get(bpy.context.evaluated_depsgraph_get()))
    bpy.data.objects.remove(tmp)
    bpy.data.curves.remove(cu)
    me.name = name
    me.materials.append(mat)
    for p in me.polygons:
        p.use_smooth = True
    o = bpy.data.objects.new(name, me)
    COL_MESIN.objects.link(o)
    return o


# ---- roda & alas
for i, x in enumerate((-0.17, 0.17)):
    for j, y in enumerate((-0.17, 0.17)):
        box(f"Roda_Braket_{i}{j}", (0.04, 0.035, 0.025), (x, y, 0.07), M["brushed"], bevel=0.003)
        cyl(f"Roda_{i}{j}", 0.03, 0.022, (x, y, 0.03), M["rubber"], rot=(0, math.pi / 2, 0), bevel=0.004)
        cyl(f"Roda_Hub_{i}{j}", 0.013, 0.026, (x, y, 0.03), M["steel"], rot=(0, math.pi / 2, 0))
box("Alas", (2 * HW - 0.04, 2 * HW - 0.04, 0.04), (0, 0, 0.08), M["frame"], bevel=0.012)
# pedal kaki pembuka tutup (seperti tempat sampah dapur)
box("Pedal", (0.13, 0.06, 0.018), (0, FY - 0.02, 0.075), M["brushed"], bevel=0.006)
box("Pedal_Karet", (0.11, 0.045, 0.004), (0, FY - 0.022, 0.085), M["rubber"], bevel=0.0015)

# ---- A: laci kompos
section("Modul_Kompos", Z_A, Z_B, M["teal"])
box("Laci_Kompos_Muka", (2 * HW - 0.06, 0.012, Z_B - Z_A - 0.03), (0, FY - 0.004, (Z_A + Z_B) / 2),
    M["teal"], bevel=0.008, segments=4)
box("Laci_Kompos_Pegangan", (0.16, 0.014, 0.016), (0, FY - 0.008, Z_B - 0.04), M["plastic_dark"], bevel=0.007)
badge(3, -0.1, 0.185, M["white"], M["teal"])
text_flat("Label_Kompos", "KOMPOS", 0.042, (0.035, FY - 0.0105, 0.185), M["white"])

# ---- B: ceruk pupuk cair
secB = section("Modul_Pupuk", Z_B, Z_C, M["body"])
use_collection(COL_CUT)
cutter = box("Ceruk_Pemotong", (0.26, 0.2, 0.18), (0, FY + 0.06, 0.43), M["plastic_dark"], bevel=0)
cutter.hide_render = True
cutter.display_type = "WIRE"
use_collection(COL_MESIN)
bmod = secB.modifiers.new("Ceruk", "BOOLEAN")
bmod.operation = "DIFFERENCE"
bmod.object = cutter
bmod.solver = "EXACT"
bmod.material_mode = "TRANSFER"
box("Ceruk_Tatakan", (0.24, 0.14, 0.006), (0, FY + 0.08, 0.343), M["brushed"], bevel=0.002)
for k in range(7):
    box(f"Ceruk_Kisi_{k}", (0.004, 0.13, 0.002), (-0.09 + k * 0.03, FY + 0.08, 0.3465), M["plastic_dark"],
        bevel=0)
rod("Keran_Pipa", (0, FY + 0.1, 0.52), (0, FY + 0.1, 0.495), 0.008, M["steel"])
box("Keran_Bodi", (0.028, 0.028, 0.022), (0, FY + 0.1, 0.49), M["brass"], bevel=0.005)
box("Keran_Tuas", (0.012, 0.06, 0.008), (0, FY + 0.075, 0.503), M["red"], bevel=0.003)
cone("Keran_Mulut", 0.007, 0.005, 0.018, (0, FY + 0.1, 0.471), M["brass"])
bx, by = 0.0, FY + 0.075
box("Botol_Pupuk", (0.13, 0.1, 0.1), (bx, by, 0.346 + 0.05), M["jerry"], bevel=0.018, segments=4)
cyl("Botol_Leher", 0.016, 0.03, (bx, FY + 0.1, 0.455), M["jerry"])
box("Botol_Pegangan", (0.03, 0.05, 0.02), (bx - 0.04, by - 0.015, 0.455), M["jerry"], bevel=0.008)
badge(2, -0.125, 0.552, M["green"], M["white"], r=0.02)
text_flat("Label_Pupuk", "PUPUK CAIR", 0.034, (0.025, FY - 0.001, 0.55), M["green"])

# ---- C: digester + jendela level
section("Modul_Digester", Z_C, Z_D, M["body"])
lx = -0.15
box("Jendela_Level_Bingkai", (0.046, 0.008, 0.25), (lx, FY - 0.003, 0.74), M["plastic_dark"], bevel=0.006)
box("Jendela_Level_Kaca", (0.03, 0.004, 0.23), (lx, FY - 0.0075, 0.74), M["glass"], bevel=0.002)
box("Jendela_Level_Cairan", (0.026, 0.003, 0.15), (lx, FY - 0.0065, 0.625 + 0.075), M["liquid"], bevel=0)
for k in range(5):
    box(f"Jendela_Level_Skala_{k}", (0.008, 0.002, 0.002), (lx + 0.011, FY - 0.0099, 0.65 + k * 0.045),
        M["white"], bevel=0)
text_flat("Logo_ARUNA", "ARUNA", 0.095, (0.045, FY - 0.001, 0.765), M["green"], extrude=0.003)
text_flat("Logo_Sub", "SMART BIODIGESTER", 0.021, (0.045, FY - 0.001, 0.705), M["teal"], extrude=0.0012)
box("LED_Status", (0.34, 0.004, 0.006), (0, FY - 0.002, Z_D + 0.001), M["led"], bevel=0)

# ---- D: modul atas (layar + tombol + langkah 1)
section("Modul_Atas", Z_D, Z_TOP, M["green"])
SW, SHh = 0.17, 0.09
box("Layar_Bezel", (SW + 0.02, 0.006, SHh + 0.018), (-0.06, FY - 0.002, 1.045), M["plastic_dark"], bevel=0.006)
scr = box("Layar", (SW, 0.002, SHh), (-0.06, FY - 0.0055, 1.045), M["screen"], bevel=0)
bm = bmesh.new()
bm.from_mesh(scr.data)
uv = bm.loops.layers.uv.verify()
for f in bm.faces:
    for l in f.loops:
        co = l.vert.co
        l[uv].uv = (co.x / SW + 0.5, co.z / SHh + 0.5)
bm.to_mesh(scr.data)
bm.free()
cyl("Tombol_Cincin", 0.034, 0.006, (0.12, FY - 0.003, 1.05), M["led"], rot=(math.pi / 2, 0, 0), bevel=0.002)
cyl("Tombol_Mulai", 0.027, 0.016, (0.12, FY - 0.008, 1.05), M["white"], rot=(math.pi / 2, 0, 0), bevel=0.005)
text_flat("Tombol_Label", "MULAI", 0.018, (0.12, FY - 0.001, 1.0), M["white"], extrude=0.0008)
badge(1, -0.175, 0.945, M["white"], M["green"], r=0.02)
text_flat("Label_Masukkan", "MASUKKAN SISA MAKANAN", 0.025, (0.025, FY - 0.001, 0.945), M["white"],
          extrude=0.0008)

# ---- bukaan input + tutup
box("Input_Lubang", (0.28, 0.26, 0.004), (0, -0.01, Z_TOP - 0.001), M["plastic_dark"], bevel=0.001)
for k, (sz, loc) in enumerate((((0.3, 0.012, 0.008), (0, -0.14 - 0.006, Z_TOP + 0.002)),
                               ((0.3, 0.012, 0.008), (0, 0.12 + 0.006, Z_TOP + 0.002)),
                               ((0.012, 0.26, 0.008), (-0.146, -0.01, Z_TOP + 0.002)),
                               ((0.012, 0.26, 0.008), (0.146, -0.01, Z_TOP + 0.002)))):
    box(f"Input_Bingkai_{k}", sz, loc, M["steel"], bevel=0.002)
for k in range(2):
    box(f"Input_Kisi_{k}", (0.008, 0.25, 0.006), (-0.047 + k * 0.094, -0.01, Z_TOP + 0.001), M["brushed"],
        bevel=0.002)
hinge = Vector((0, HW - 0.012, Z_TOP + 0.006))
LID_A = math.radians(-100)
lrot = Matrix.Rotation(LID_A, 4, "X")


def on_lid(v):
    return hinge + (lrot @ Vector(v).to_4d()).to_3d()


box("Tutup", (2 * HW - 0.01, 2 * HW - 0.02, 0.022), on_lid((0, -HW + 0.012, 0.011)), M["body"],
    bevel=0.01, segments=4, rot=(LID_A, 0, 0))
box("Tutup_Pegangan", (0.14, 0.018, 0.014), on_lid((0, -2 * HW + 0.035, 0.026)), M["green"], bevel=0.006,
    rot=(LID_A, 0, 0))
cyl("Tutup_Engsel", 0.008, 0.3, hinge, M["steel"], rot=(0, math.pi / 2, 0))

# ---- sisi kanan: gas
GZ, GYy = 0.80, -0.06
rod("Gauge_Tangkai", (HW, GYy, GZ), (HW + 0.015, GYy, GZ), 0.006, M["brass"])
cyl("Gauge_Rumah", 0.042, 0.022, (HW + 0.026, GYy, GZ), M["steel"], rot=(0, math.pi / 2, 0), bevel=0.005)
cyl("Gauge_Muka", 0.036, 0.002, (HW + 0.0375, GYy, GZ), M["dial"], rot=(0, math.pi / 2, 0), bevel=0)
for k in range(7):
    a = math.radians(-120 + k * 40)
    box(f"Gauge_Tik_{k}", (0.002, 0.0025, 0.007), (HW + 0.039, GYy + 0.028 * math.sin(a), GZ + 0.028 * math.cos(a)),
        M["frame"], bevel=0, rot=(-a, 0, 0))
box("Gauge_Zona_Hijau", (0.002, 0.018, 0.004), (HW + 0.039, GYy - 0.012, GZ + 0.02), M["led"], bevel=0,
    rot=(math.radians(30), 0, 0))
box("Gauge_Jarum", (0.002, 0.0025, 0.028), (HW + 0.0405, GYy - 0.008, GZ + 0.008), M["red"], bevel=0,
    rot=(math.radians(45), 0, 0))
cyl("Gauge_Kaca", 0.037, 0.003, (HW + 0.041, GYy, GZ), M["glass"], rot=(0, math.pi / 2, 0), bevel=0)
text_flat("Label_Biogas", "BIOGAS", 0.03, (HW + 0.0005, 0.09, GZ), M["teal"], rot=(math.pi / 2, 0, math.pi / 2))
VZ = 0.70
rod("Gas_Pipa", (HW, GYy, VZ), (HW + 0.06, GYy, VZ), 0.008, M["brass"])
box("Gas_Katup", (0.03, 0.03, 0.03), (HW + 0.03, GYy, VZ), M["brass"], bevel=0.005)
box("Gas_Katup_Tuas", (0.01, 0.07, 0.008), (HW + 0.03, GYy - 0.025, VZ + 0.022), M["red"], bevel=0.003)
cone("Gas_Nosel", 0.008, 0.006, 0.03, (HW + 0.075, GYy, VZ), M["brass"], rot=(0, math.pi / 2, 0))
for k in range(5):
    box(f"Ventilasi_Kiri_{k}", (0.004, 0.2, 0.008), (-HW - 0.0005, 0.0, 0.66 + k * 0.022), M["plastic_dark"],
        bevel=0.001)

# ================================================================ KONTEKS RUMAH: kompor + pot tanaman
KX, KY, KZ = 0.66, -0.02, 0.46
box("Meja_Kecil", (0.38, 0.36, 0.025), (KX, KY, KZ - 0.0125), M["wood"], bevel=0.006)
for sx in (-1, 1):
    for sy in (-1, 1):
        rod("Meja_Kaki", (KX + sx * 0.16, KY + sy * 0.15, 0), (KX + sx * 0.16, KY + sy * 0.15, KZ - 0.025),
            0.012, M["frame"])
box("Kompor_Bodi", (0.28, 0.3, 0.07), (KX, KY, KZ + 0.035), M["frame"], bevel=0.012)
box("Kompor_Panel", (0.2, 0.004, 0.035), (KX, KY - 0.151, KZ + 0.035), M["brushed"], bevel=0.002)
cyl("Kompor_Kenop", 0.014, 0.016, (KX + 0.06, KY - 0.158, KZ + 0.035), M["steel"], rot=(math.pi / 2, 0, 0))
cyl("Kompor_Tungku", 0.05, 0.02, (KX, KY + 0.01, KZ + 0.08), M["brushed"], bevel=0.003)
torus("Kompor_Penyangga", 0.09, 0.005, (KX, KY + 0.01, KZ + 0.1), M["frame"])
for k in range(4):
    a = k * math.pi / 2 + math.pi / 4
    box(f"Kompor_Jari_{k}", (0.07, 0.008, 0.012),
        (KX + 0.08 * math.cos(a), KY + 0.01 + 0.08 * math.sin(a), KZ + 0.1), M["frame"], bevel=0.002,
        rot=(0, 0, a))
for k in range(16):
    a = k / 16 * 2 * math.pi
    cone(f"Api_{k}", 0.006, 0.0, 0.03, (KX + 0.045 * math.cos(a), KY + 0.01 + 0.045 * math.sin(a), KZ + 0.105),
         M["flame"], verts=12)
hose("Selang_Gas", [(HW + 0.09, GYy, VZ), (HW + 0.13, GYy, VZ - 0.01), (0.4, -0.02, 0.62), (0.38, 0.1, 0.5),
                    (0.44, 0.12, KZ + 0.03), (KX - 0.14, 0.1, KZ + 0.035)], 0.009, M["teal"])
# pot tanaman (penerima pupuk cair)
PX, PY = -0.42, -0.08
cone("Pot", 0.085, 0.115, 0.2, (PX, PY, 0.1), M["terracotta"], fill="NGON", bevel=0.004)
torus("Pot_Bibir", 0.116, 0.012, (PX, PY, 0.2), M["terracotta"])
cyl("Pot_Tanah", 0.108, 0.01, (PX, PY, 0.19), M["soil"], bevel=0)
import random
random.seed(7)
for k in range(11):
    a = k / 11 * 2 * math.pi + random.uniform(-0.2, 0.2)
    tilt = random.uniform(0.35, 0.8)
    L = random.uniform(0.16, 0.24)
    d = Vector((math.sin(tilt) * math.cos(a), math.sin(tilt) * math.sin(a), math.cos(tilt)))
    base = Vector((PX, PY, 0.2))
    leaf = sphere(f"Daun_{k}", 1.0, base + d * (L / 2), M["leaf"], scale=(0.035, 0.008, L / 2), segs=24)
    leaf.rotation_euler = Vector((0, 0, 1)).rotation_difference(d).to_euler()
    leaf.rotation_euler.rotate_axis("Z", a)

# ================================================================ STUDIO
use_collection(COL_ENV)
bm = bmesh.new()
prof = [(-12.0, 0.0), (1.2, 0.0)]
for k in range(1, 17):
    a = k / 16 * math.pi / 2
    prof.append((1.2 + 2.5 * math.sin(a), 2.5 * (1 - math.cos(a))))
prof.append((3.7, 9.0))
left = [bm.verts.new((-12, y, z)) for y, z in prof]
right = [bm.verts.new((12, y, z)) for y, z in prof]
for i in range(len(prof) - 1):
    bm.faces.new((left[i], right[i], right[i + 1], left[i + 1]))
me = bpy.data.meshes.new("Latar")
bm.to_mesh(me)
bm.free()
latar = bpy.data.objects.new("Latar", me)
COL_ENV.objects.link(latar)
me.materials.append(M["floor"])
for p in me.polygons:
    p.use_smooth = True

world = bpy.data.worlds.new("Dunia")
scene.world = world
wn = node_tree_of(world)
bg = next(n for n in wn.nodes if n.type == "BACKGROUND")
bg.inputs["Color"].default_value = (0.42, 0.45, 0.44, 1)
bg.inputs["Strength"].default_value = 0.22


def area_light(name, loc, target, power, size, color=(1, 1, 1)):
    ld = bpy.data.lights.new(name, "AREA")
    ld.energy = power
    ld.size = size
    ld.color = color
    o = bpy.data.objects.new(name, ld)
    COL_ENV.objects.link(o)
    o.location = loc
    o.rotation_euler = (Vector(target) - Vector(loc)).to_track_quat("-Z", "Y").to_euler()
    return o


area_light("Key", (-2.4, -2.6, 3.2), (0, 0, 0.7), 900, 2.5, (1.0, 0.97, 0.93))
area_light("Fill", (3.2, -1.8, 1.6), (0, 0, 0.7), 300, 3.0, (0.9, 0.97, 1.0))
area_light("Rim", (0.8, 3.0, 2.8), (0, 0, 0.9), 600, 1.5)
area_light("Top", (0, 0, 4.0), (0, 0, 0), 250, 4.0)


def camera(name, loc, target, lens):
    cd = bpy.data.cameras.new(name)
    cd.lens = lens
    o = bpy.data.objects.new(name, cd)
    COL_ENV.objects.link(o)
    o.location = loc
    o.rotation_euler = (Vector(target) - Vector(loc)).to_track_quat("-Z", "Y").to_euler()
    return o


CAMS = [
    camera("Cam_Hero", (1.75, -2.7, 1.5), (0.1, 0, 0.6), 50),
    camera("Cam_Depan", (0.1, -5.2, 0.7), (0.1, 0, 0.64), 85),
    camera("Cam_Samping", (3.0, -1.9, 1.05), (0.22, 0, 0.6), 60),
    camera("Cam_Detail_Atas", (0.55, -1.15, 1.75), (0, -0.02, 0.98), 50),
]

# ---------------------------------------------------------------- render settings
r = scene.render
r.engine = "CYCLES"
r.resolution_x, r.resolution_y = (640, 800) if PREVIEW else (1600, 2000)
r.resolution_percentage = 100
r.image_settings.file_format = "PNG"
scene.cycles.samples = 32 if PREVIEW else 160
scene.cycles.use_denoising = True
scene.cycles.max_bounces = 8
scene.cycles.transmission_bounces = 8
scene.view_settings.view_transform = "AgX"
try:
    scene.view_settings.look = "AgX - Punchy"
except Exception:
    pass
scene.view_settings.exposure = -0.35

try:
    prefs = bpy.context.preferences.addons["cycles"].preferences
    for dev_type in ("OPTIX", "CUDA", "HIP", "ONEAPI", "METAL"):
        try:
            prefs.compute_device_type = dev_type
        except Exception:
            continue
        prefs.get_devices()
        gpus = [d for d in prefs.devices if d.type != "CPU"]
        if gpus:
            for d in prefs.devices:
                d.use = True
            scene.cycles.device = "GPU"
            print(f"[ARUNA] GPU render: {dev_type} -> {[d.name for d in gpus]}")
            break
    else:
        print("[ARUNA] Render pakai CPU")
except Exception as e:
    print("[ARUNA] Deteksi GPU gagal:", e)

scene.camera = CAMS[0]

# ---------------------------------------------------------------- save / export
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT_DIR, "aruna_mesin.blend"))

bpy.ops.object.select_all(action="DESELECT")
for o in COL_MESIN.objects:
    o.select_set(True)
bpy.context.view_layer.objects.active = COL_MESIN.objects[0]
bpy.ops.export_scene.gltf(filepath=os.path.join(OUT_DIR, "aruna_mesin.glb"), export_format="GLB",
                          use_selection=True, export_apply=True)
print("[ARUNA] .blend dan .glb tersimpan")

if not NO_RENDER:
    for cam in CAMS:
        scene.camera = cam
        r.filepath = os.path.join(RENDER_DIR, f"{cam.name.replace('Cam_', '').lower()}.png")
        bpy.ops.render.render(write_still=True)
        print("[ARUNA] render ->", r.filepath)

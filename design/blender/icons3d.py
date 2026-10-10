"""
Ikon 3D "clay" ARUNA (latar transparan) + loop animasi.

  blender -b -P design/blender/icons3d.py -- [still|anim] [nama...]
Keluaran: public/assets/3d/<nama>.png (512 px) dan design/blender/_anim/<nama>/f_###.png (dirakit ke WebP oleh pack_icons.py)
"""
import bpy
import math
import os
import sys

from mathutils import Vector

ARGS = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else ["still"]
MODE = ARGS[0]
ONLY = set(ARGS[1:])
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
OUT = os.path.join(ROOT, "public", "assets", "3d")
ANIM = os.path.join(HERE, "_anim")
os.makedirs(OUT, exist_ok=True)

PAL = {"green": "#1FA567", "deep": "#0F6B40", "teal": "#14A08C", "saff": "#F2A93B", "flame": "#FF7A2F", "yellow": "#FFD166",
       "coral": "#EF6B57", "sky": "#3A8DDE", "soil": "#6B4A2E", "cream": "#FFF4E2", "white": "#E9EEEB", "mint": "#BFE8D0", "peach": "#FFD8BF", "glass": "#DDF3FF", "dark": "#1B2B24"}


def lin(h):
    h = h.lstrip("#")
    c = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    return tuple(x / 12.92 if x <= .04045 else ((x + .055) / 1.055) ** 2.4 for x in c)


def mat(name, hexcol, rough=.38, emit=0.0, trans=0.0, coat=.6):
    m = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    if m.node_tree is None:
        m.use_nodes = True
    b = next(n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    b.inputs["Base Color"].default_value = (*lin(hexcol), 1)
    b.inputs["Roughness"].default_value = rough
    b.inputs["Coat Weight"].default_value = coat
    b.inputs["Coat Roughness"].default_value = .15
    b.inputs["Subsurface Weight"].default_value = .08
    if emit:
        b.inputs["Emission Color"].default_value = (*lin(hexcol), 1)
        b.inputs["Emission Strength"].default_value = emit
    if trans:
        b.inputs["Transmission Weight"].default_value = trans
        b.inputs["IOR"].default_value = 1.45
    return m


def reset():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    sc.render.engine = "CYCLES"
    sc.cycles.samples = 96 if MODE == "still" else 40
    sc.cycles.use_denoising = True
    try:
        pr = bpy.context.preferences.addons["cycles"].preferences
        pr.compute_device_type = "OPTIX"
        pr.get_devices()
        for d in pr.devices:
            d.use = True
        sc.cycles.device = "GPU"
    except Exception:
        pass
    sc.render.film_transparent = True
    sc.render.resolution_x = sc.render.resolution_y = 512 if MODE == "still" else 320
    sc.render.image_settings.color_mode = "RGBA"
    sc.view_settings.view_transform = "Standard"
    sc.view_settings.exposure = -.35
    w = bpy.data.worlds.new("w")
    sc.world = w
    if w.node_tree is None:
        w.use_nodes = True
    w.node_tree.nodes["Background"].inputs[0].default_value = (*lin("#EAF6EF"), 1)
    w.node_tree.nodes["Background"].inputs[1].default_value = .45
    for nm, loc, e, size, col in (("key", (-2.5, -3, 4), 380, 3, "#FFFFFF"), ("rim", (3, 2.5, 3), 260, 2, "#BDE6FF"),
                                  ("fill", (3, -3, 1), 90, 3, "#FFE9C9")):
        ld = bpy.data.lights.new(nm, "AREA")
        ld.energy, ld.size, ld.color = e, size, lin(col)
        o = bpy.data.objects.new(nm, ld)
        sc.collection.objects.link(o)
        o.location = loc
        o.rotation_euler = (Vector((0, 0, .6)) - Vector(loc)).to_track_quat("-Z", "Y").to_euler()
        o.visible_camera = False
    cam = bpy.data.objects.new("cam", bpy.data.cameras.new("cam"))
    sc.collection.objects.link(cam)
    cam.data.type = "ORTHO"
    cam.data.ortho_scale = 2.9
    cam.location = (0, -6, 3.2)
    cam.rotation_euler = (Vector((0, 0, .75)) - cam.location).to_track_quat("-Z", "Y").to_euler()
    sc.camera = cam
    root = bpy.data.objects.new("root", None)
    sc.collection.objects.link(root)
    return sc, root


def add(o, m, root, smooth=True, sub=2):
    o.data.materials.clear()
    o.data.materials.append(m)
    if smooth:
        for p in o.data.polygons:
            p.use_smooth = True
    if sub:
        mo = o.modifiers.new("s", "SUBSURF")
        mo.levels = mo.render_levels = sub
    o.parent = root
    return o


def sph(r, loc, m, root, scale=(1, 1, 1), seg=48):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=r, location=loc, segments=seg, ring_count=seg // 2)
    o = bpy.context.active_object
    o.scale = scale
    return add(o, m, root, sub=0)


def cyl(r, d, loc, m, root, rot=(0, 0, 0), bev=.06, v=48):
    bpy.ops.mesh.primitive_cylinder_add(radius=r, depth=d, location=loc, rotation=rot, vertices=v)
    o = bpy.context.active_object
    bm = o.modifiers.new("b", "BEVEL")
    bm.width, bm.segments = bev, 5
    return add(o, m, root, sub=0)


def box(s, loc, m, root, bev=.12, rot=(0, 0, 0)):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc, rotation=rot)
    o = bpy.context.active_object
    o.scale = s
    bpy.ops.object.transform_apply(scale=True)
    bm = o.modifiers.new("b", "BEVEL")
    bm.width, bm.segments = bev, 6
    return add(o, m, root, sub=0)


def drop(r, loc, m, root, tip=1.9):
    """Tetes air: bola dengan belahan atas ditarik ke ujung lancip."""
    bpy.ops.mesh.primitive_uv_sphere_add(radius=r, segments=64, ring_count=32, location=(0, 0, 0))
    o = bpy.context.active_object
    for v in o.data.vertices:
        if v.co.z > 0:
            t = v.co.z / r
            k = (1 - t) ** 1.25
            v.co.x *= max(k, 0) if t < .999 else 0
            v.co.y *= max(k, 0) if t < .999 else 0
            v.co.z = r * t * tip
    o.location = loc
    return add(o, m, root, sub=1)


def base_disc(root, col="mint"):
    return cyl(1.0, .14, (0, 0, -.02), mat("base_" + col, PAL[col], rough=.55, coat=.2), root, bev=.07, v=96)


# ------------------------------------------------------------------ ikon
def i_flame(root):
    base_disc(root)
    cyl(.55, .22, (0, 0, .17), mat("burner", PAL["dark"], rough=.3), root, bev=.05)
    drop(.50, (0, 0, .62), mat("fl1", PAL["flame"], rough=.25, emit=.8), root, tip=2.2)
    drop(.24, (.0, -.34, .52), mat("fl2", PAL["yellow"], rough=.2, emit=1.2), root, tip=1.8)
    drop(.17, (.25, .05, .45), mat("fl1", PAL["flame"]), root, tip=2.2)


def i_drop(root):
    base_disc(root)
    drop(.62, (0, 0, .7), mat("drop", PAL["teal"], rough=.08, trans=.35, coat=1), root, tip=1.85)
    sph(.11, (-.2, -.5, 1.02), mat("hl", "#FFFFFF", rough=.05, emit=1.5), root, scale=(.6, .6, 1.2))
    cyl(.12, .04, (.6, -.3, .1), mat("drop", PAL["teal"]), root, bev=.02)


def i_leaf(root):
    base_disc(root)
    cyl(.42, .5, (0, 0, .3), mat("pot", PAL["coral"], rough=.45), root, bev=.08)
    cyl(.38, .06, (0, 0, .55), mat("soil", PAL["soil"], rough=.9), root, bev=.02)
    cyl(.035, .6, (0, 0, .85), mat("stem", PAL["deep"]), root, bev=.0)
    for ang, sx in ((35, 1), (-35, -1)):
        o = sph(.32, (sx * .28, 0, 1.12), mat("leaf", PAL["green"], rough=.3), root, scale=(1, .35, .55))
        o.rotation_euler = (0, math.radians(ang), 0)


def i_compost(root):
    base_disc(root, "peach")
    box((1.3, .9, .5), (0, 0, .3), mat("tray", PAL["coral"], rough=.4), root, bev=.12)
    for x, y, r in ((-.3, 0, .32), (.15, .05, .36), (.4, -.1, .24), (-.05, -.2, .26)):
        sph(r, (x, y, .58), mat("soil", PAL["soil"], rough=.9), root, scale=(1, 1, .6), seg=24)
    cyl(.03, .3, (.1, 0, .9), mat("stem", PAL["deep"]), root, bev=0)
    o = sph(.16, (.2, 0, 1.05), mat("leaf", PAL["green"]), root, scale=(1, .4, .6))
    o.rotation_euler = (0, math.radians(30), 0)


def i_therm(root):
    base_disc(root)
    cyl(.17, 1.3, (0, 0, .85), mat("glass", "#9FD6F2", rough=.05, trans=.4, coat=1), root, bev=.17)
    sph(.3, (0, 0, .32), mat("bulb", PAL["coral"], rough=.25), root)
    cyl(.08, .75, (0, 0, .7), mat("bulb", PAL["coral"]), root, bev=.08)
    for k in range(4):
        cyl(.07, .02, (.2, 0, .85 + k * .17), mat("tick", PAL["deep"]), root, rot=(0, math.pi / 2, 0), bev=0, v=12)


def i_phone(root):
    base_disc(root)
    box((.95, .14, 1.55), (0, 0, .9), mat("phone", PAL["white"], rough=.3), root, bev=.16)
    box((.8, .02, 1.32), (0, -.075, .9), mat("screen", PAL["green"], rough=.2, emit=.6), root, bev=.1)
    for z, w, c in ((1.3, .5, "white"), (1.1, .62, "yellow"), (.9, .4, "white"), (.6, .62, "saff")):
        box((w, .02, .1), (-(.62 - w) / 2, -.09, z), mat("ui_" + c, PAL[c], emit=.8), root, bev=.04)


def i_ch4(root):
    base_disc(root)
    sph(.42, (0, 0, .85), mat("c", PAL["deep"], rough=.3), root)
    ms = mat("h", PAL["white"], rough=.3)
    mb = mat("bond", PAL["saff"], rough=.4)
    for v in ((.6, .3, 1.2), (-.6, .35, 1.15), (.05, -.62, 1.15), (0, .2, .32)):
        p = Vector(v)
        c = Vector((0, 0, .85))
        d = p - c
        sph(.24, p, ms, root)
        bpy.ops.mesh.primitive_cylinder_add(radius=.06, depth=d.length, location=(c + p) / 2,
                                            rotation=Vector((0, 0, 1)).rotation_difference(d.normalized()).to_euler())
        add(bpy.context.active_object, mb, root, sub=0)


def i_bowl(root):
    base_disc(root, "peach")
    bpy.ops.mesh.primitive_uv_sphere_add(radius=.7, segments=64, ring_count=32, location=(0, 0, .72))
    o = bpy.context.active_object
    bpy.ops.object.mode_set(mode="EDIT")
    bpy.ops.mesh.select_all(action="DESELECT")
    bpy.ops.object.mode_set(mode="OBJECT")
    for v in o.data.vertices:
        v.select = v.co.z > 0
    bpy.ops.object.mode_set(mode="EDIT")
    bpy.ops.mesh.delete(type="VERT")
    bpy.ops.object.mode_set(mode="OBJECT")
    s = o.modifiers.new("t", "SOLIDIFY")
    s.thickness = .06
    add(o, mat("bowl", PAL["sky"], rough=.35), root, sub=0)
    for x, y, r, c in ((-.2, 0, .26, "cream"), (.18, .1, .22, "green"), (.05, -.2, .2, "saff"), (.3, -.15, .15, "coral"), (-.3, -.2, .16, "green")):
        sph(r, (x, y, .78), mat("f_" + c, PAL[c], rough=.5), root, seg=32)


def i_gear(root):
    base_disc(root)
    cyl(.62, .3, (0, 0, .75), mat("gear", PAL["teal"], rough=.35), root, rot=(math.pi / 2, 0, 0), bev=.06, v=64)
    for k in range(8):
        a = k / 8 * 2 * math.pi
        box((.26, .3, .24), (.66 * math.cos(a), 0, .75 + .66 * math.sin(a)), mat("gear", PAL["teal"]), root, bev=.06, rot=(0, -a, 0))
    cyl(.25, .36, (0, 0, .75), mat("hub", PAL["saff"]), root, rot=(math.pi / 2, 0, 0), bev=.05)


ICONS = {"flame": i_flame, "drop": i_drop, "leaf": i_leaf, "compost": i_compost, "therm": i_therm,
         "phone": i_phone, "ch4": i_ch4, "bowl": i_bowl, "gear": i_gear}
ANIMATE = {"flame", "drop", "leaf", "ch4"}

for name, fn in ICONS.items():
    if ONLY and name not in ONLY:
        continue
    if MODE == "anim" and name not in ANIMATE:
        continue
    sc, root = reset()
    fn(root)
    if MODE == "still":
        root.rotation_euler = (0, 0, math.radians(-18))
        sc.render.filepath = os.path.join(OUT, name + ".png")
        bpy.ops.render.render(write_still=True)
    else:
        N = 48
        d = os.path.join(ANIM, name)
        os.makedirs(d, exist_ok=True)
        for f in range(N):
            t = f / N
            root.rotation_euler = (0, 0, math.radians(-18) + 2 * math.pi * t)
            root.location.z = .08 * math.sin(2 * math.pi * t)
            sc.render.filepath = os.path.join(d, f"f_{f:03d}.png")
            bpy.ops.render.render(write_still=True)
    print("[ICON]", name)

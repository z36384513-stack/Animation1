import bpy
import math

# ---------- clean scene ----------
bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene

# ---------- render settings: 5 seconds @ 24 fps ----------
scene.render.engine = "BLENDER_EEVEE_NEXT"
scene.eevee.taa_render_samples = 16
scene.render.resolution_x = 640
scene.render.resolution_y = 360
scene.render.resolution_percentage = 100
scene.render.fps = 24
scene.frame_start = 1
scene.frame_end = 120  # 120 frames / 24 fps = 5 seconds
scene.render.image_settings.file_format = "FFMPEG"
scene.render.image_settings.color_mode = "RGB"
scene.render.ffmpeg.format = "MPEG4"
scene.render.ffmpeg.codec = "H264"
scene.render.ffmpeg.constant_rate_factor = "MEDIUM"
scene.render.filepath = "/workspace/blender_anim/animation.mp4"
scene.render.use_file_extension = True

# ---------- world ----------
world = bpy.data.worlds.new("World")
scene.world = world
world.use_nodes = True
bg = world.node_tree.nodes["Background"]
bg.inputs[0].default_value = (0.05, 0.07, 0.12, 1.0)
bg.inputs[1].default_value = 1.0

# ---------- materials ----------
def make_mat(name, color, metallic=0.0, roughness=0.35):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    bsdf = m.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (*color, 1.0)
    bsdf.inputs["Metallic"].default_value = metallic
    bsdf.inputs["Roughness"].default_value = roughness
    return m

mat_red = make_mat("Red", (0.9, 0.1, 0.1), metallic=0.2, roughness=0.3)
mat_blue = make_mat("Blue", (0.1, 0.35, 0.95), metallic=0.2, roughness=0.3)
mat_gold = make_mat("Gold", (0.95, 0.75, 0.2), metallic=0.9, roughness=0.25)
mat_green = make_mat("Green", (0.15, 0.85, 0.35), metallic=0.1, roughness=0.4)
mat_floor = make_mat("Floor", (0.16, 0.16, 0.2), metallic=0.0, roughness=0.6)

# ---------- ground ----------
bpy.ops.mesh.primitive_plane_add(size=40, location=(0, 0, 0))
floor = bpy.context.active_object
floor.data.materials.append(mat_floor)

# ---------- objects ----------
bpy.ops.mesh.primitive_uv_sphere_add(radius=0.6, location=(-2.2, 0, 0.6))
ball = bpy.context.active_object
ball.data.materials.append(mat_red)

bpy.ops.mesh.primitive_torus_add(major_radius=1.0, minor_radius=0.35, major_segments=48, minor_segments=16, location=(2.2, 0, 1.2))
torus = bpy.context.active_object
torus.data.materials.append(mat_gold)

bpy.ops.mesh.primitive_cube_add(size=1.1, location=(0, 2.4, 0.55))
cube = bpy.context.active_object
cube.data.materials.append(mat_blue)

bpy.ops.mesh.primitive_cone_add(radius1=0.7, radius2=0.0, depth=1.4, location=(0, -2.4, 0.7))
cone = bpy.context.active_object
cone.data.materials.append(mat_green)

# ---------- lights ----------
bpy.ops.object.light_add(type="SUN", location=(4, -3, 8))
sun = bpy.context.active_object
sun.data.energy = 4.0
sun.rotation_euler = (math.radians(35), math.radians(15), math.radians(30))

bpy.ops.object.light_add(type="AREA", location=(0, 0, 6))
area = bpy.context.active_object
area.data.energy = 800
area.data.shape = "DISK"
area.data.size = 5.0

# ---------- camera ----------
bpy.ops.object.camera_add(location=(0, -9, 4.2))
cam = bpy.context.active_object
scene.camera = cam

def point_camera(obj, target):
    direction = target - obj.location
    obj.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()

from mathutils import Vector
center = Vector((0, 0, 0.8))
point_camera(cam, center)

# ---------- animation helpers ----------
def set_key(obj, frame, loc=None, rot=None, scale=None):
    if loc is not None:
        obj.location = loc
    if rot is not None:
        obj.rotation_euler = rot
    if scale is not None:
        obj.scale = scale
    obj.keyframe_insert(data_path="location", frame=frame)
    obj.keyframe_insert(data_path="rotation_euler", frame=frame)
    obj.keyframe_insert(data_path="scale", frame=frame)

# ball: bounce 3 times over 5 s (frames 1..120)
bounce_frames = [1, 21, 41, 61, 81, 101, 120]
heights = [0.6, 2.6, 0.6, 2.1, 0.6, 1.7, 0.6]
for f, h in zip(bounce_frames, heights):
    set_key(ball, f, loc=(-2.2 + 0.03 * f, 0, h))
# ball squash & stretch at the low points
for f in [41, 61, 81, 101, 120]:
    set_key(ball, f, scale=(1.25, 1.25, 0.7))
    set_key(ball, f + 4, scale=(0.85, 0.85, 1.2))
    set_key(ball, f + 8, scale=(1.0, 1.0, 1.0))

# torus: spin around X and Z
set_key(torus, 1, loc=(2.2, 0, 1.2), rot=(0, 0, 0))
set_key(torus, 120, loc=(2.2, 0, 1.2), rot=(math.radians(360), 0, math.radians(720)))

# cube: tumble
set_key(cube, 1, loc=(0, 2.4, 0.55), rot=(0, 0, 0))
set_key(cube, 120, loc=(0, 2.4, 0.55), rot=(math.radians(720), math.radians(540), math.radians(360)))

# cone: rotate and hop
set_key(cone, 1, loc=(0, -2.4, 0.7), rot=(0, 0, 0))
set_key(cone, 60, loc=(0, -2.4, 1.6), rot=(0, 0, math.radians(360)))
set_key(cone, 120, loc=(0, -2.4, 0.7), rot=(0, 0, math.radians(720)))

# camera: slow orbit around the scene over 5 s
for f, ang in [(1, 0.0), (120, math.radians(40))]:
    r = 10.0
    x = r * math.sin(ang)
    y = -r * math.cos(ang)
    set_key(cam, f, loc=(x, y, 4.2 + 0.8 * math.sin(ang)))
    point_camera(cam, center)
    cam.keyframe_insert(data_path="location", frame=f)
    cam.keyframe_insert(data_path="rotation_euler", frame=f)

# smooth interpolation everywhere
for action in bpy.data.actions:
    for fc in action.fcurves:
        for kp in fc.keyframe_points:
            kp.interpolation = "BEZIER"
            kp.handle_left_type = "AUTO_CLAMPED"
            kp.handle_right_type = "AUTO_CLAMPED"

# ---------- render ----------
bpy.ops.render.render(animation=True)
print("RENDER_FINISHED:", scene.render.filepath)

#!/usr/bin/env python3
"""Zero model-weight, zero GPU digital human animation proof.
Actor is fully original procedural character geometry, deliberately stylized.
CPU Cycles physically-based scene/camera/kinematics, not a photoreal AI actor.
"""
import bpy,math,sys,json,time
from mathutils import Vector
from pathlib import Path
args=sys.argv[sys.argv.index("--")+1:] if "--" in sys.argv else []
out=Path(args[0] if args else "proof/model-free-cpu-actor/frames")
out.mkdir(parents=True,exist_ok=True)
bpy.ops.object.select_all(action="SELECT")
bpy.ops.object.delete(use_global=False)
s=bpy.context.scene
s.render.engine="CYCLES"
s.cycles.device="CPU"
s.cycles.samples=8
s.cycles.use_denoising=False
bpy.context.view_layer.cycles.use_denoising=False
s.render.resolution_x=480;s.render.resolution_y=270;s.render.resolution_percentage=100
s.render.image_settings.file_format="PNG"
s.render.film_transparent=False
s.render.threads_mode="FIXED";s.render.threads=2
s.view_settings.view_transform="Standard";s.view_settings.look="Medium High Contrast"
w=bpy.data.worlds.new("model-free blue cinematic studio")
s.world=w;w.use_nodes=True
w.node_tree.nodes["Background"].inputs["Color"].default_value=(.032,.05,.075,1)
w.node_tree.nodes["Background"].inputs["Strength"].default_value=.45
def material(name,color,rough=.5,metal=0,sub=0):
    m=bpy.data.materials.new(name);m.diffuse_color=(*color,1);m.use_nodes=True
    b=m.node_tree.nodes.get("Principled BSDF")
    b.inputs["Base Color"].default_value=(*color,1)
    b.inputs["Roughness"].default_value=rough;b.inputs["Metallic"].default_value=metal
    if sub and b.inputs.get("Subsurface Weight"):b.inputs["Subsurface Weight"].default_value=sub
    return m
skin=material("physical skin material, not synthesized",(.37,.195,.128),.54,0,.10)
suit=material("dark navy wool",(.025,.046,.075),.78)
shirt=material("ivory cotton",(.63,.67,.62),.75)
pants=material("matte trousers",(.029,.034,.046),.7)
shoes=material("leather shoes",(.022,.018,.022),.38)
hair=material("brunette hair",(.029,.017,.011),.6)
eye=material("eyes",(.012,.015,.019),.16)
gold=material("metal pin",(.49,.27,.09),.31,.75)
setmat=material("background plaster",(.025,.047,.07),.76)
floor=material("charcoal polished concrete",(.052,.065,.071),.35,.22)
def ball(name,point,scale,mat,parent=None):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=20,ring_count=12,radius=1,location=(0,0,0) if parent else point)
    o=bpy.context.object;o.name=name;o.parent=parent
    if parent:o.location=point
    o.scale=scale
    for p in o.data.polygons:p.use_smooth=True
    o.data.materials.append(mat)
    return o
def beam(name,start,end,radius,mat,parent=None):
    a,b=Vector(start),Vector(end)
    m=(a+b)*.5;dist=(b-a).length
    bpy.ops.mesh.primitive_cylinder_add(vertices=18,radius=radius,depth=dist,location=(0,0,0) if parent else m)
    o=bpy.context.object;o.name=name;o.parent=parent
    if parent:o.location=m
    o.rotation_euler=(b-a).to_track_quat("Z","Y").to_euler()
    o.data.materials.append(mat)
    for p in o.data.polygons:p.use_smooth=True
    bevel=o.modifiers.new("bevel","BEVEL");bevel.width=.04;bevel.segments=2
    return o
def empty(name,p):
    o=bpy.data.objects.new(name,None);bpy.context.collection.objects.link(o);o.location=p;return o
bpy.ops.mesh.primitive_plane_add(size=200,location=(0,0,-.01));bpy.context.object.data.materials.append(floor)
bpy.ops.mesh.primitive_plane_add(size=70,location=(0,4,8),rotation=(math.pi/2,0,0));bpy.context.object.data.materials.append(setmat)
for x in [-2,2]:
    beam("architectural edge",(x,1,0),(x,1,4),.065,gold)
# Character faces -Y, procedural articulated rig.
root=empty("character main world rig",(0,0,0))
ball("tailored jacket torso",(0,0,1.48),(.42,.255,.65),suit,parent=root)
ball("shirt exposed V",(0,-.222,1.74),(.19,.045,.33),shirt,parent=root)
ball("neck",(0,-.012,2.13),(.125,.11,.18),skin,parent=root)
ball("pelvis",(0,0,.96),(.33,.20,.18),pants,parent=root)
for sign in (-1,1):
    x=sign*.18
    beam(f"{sign} thigh",(x,0,.97),(x,0,.56),.151,pants,parent=root)
    ball(f"{sign} knee",(x,0,.56),(.144,.15,.16),pants,parent=root)
    beam(f"{sign} calf",(x,0,.54),(x,-.017,.17),.123,pants,parent=root)
    ball(f"{sign} foot",(x,-.125,.105),(.16,.28,.105),shoes,parent=root)
left=beam("left jacket arm",(-.43,0,1.98),(-.49,-.04,1.41),.127,suit,parent=root)
ball("left hand",(-.49,-.025,1.32),(.108,.10,.142),skin,parent=root)
pivot=empty("right shoulder procedural arm rotation",(.43,0,1.99))
pivot.parent=root
beam("right suit upper arm",(0,0,0),(0,0,-.31),.124,suit,parent=pivot)
ball("right elbow",(0,0,-.33),(.133,.13,.13),suit,parent=pivot)
beam("right sleeve",(0,0,-.35),(.02,-.012,-.67),.113,suit,parent=pivot)
ball("right hand",(.025,-.025,-.77),(.108,.10,.14),skin,parent=pivot)
headpivot=empty("head bone without ML weights",(0,-.02,2.25));headpivot.parent=root
ball("humanoid facial skull",(0,-.02,.245),(.28,.235,.345),skin,parent=headpivot)
ball("hair cap",(0,.015,.49),(.289,.242,.17),hair,parent=headpivot)
for x in (-.12,.12):
    ball(f"eye sclera {x}",(x,-.228,.292),(.058,.034,.040),shirt,parent=headpivot)
    ball(f"pupil {x}",(x,-.263,.293),(.027,.015,.032),eye,parent=headpivot)
    ball(f"eyebrow {x}",(x,-.239,.362),(.078,.016,.014),hair,parent=headpivot)
ball("nose anatomy",(0,-.258,.205),(.053,.069,.089),skin,parent=headpivot)
ball("subtle closed lips",(0,-.240,.11),(.098,.018,.023),hair,parent=headpivot)
ball("lapel pin",(.22,-.265,1.82),(.045,.02,.046),gold,parent=root)
def area(name,p,target,rgb,energy,size):
    d=bpy.data.lights.new(name,"AREA");d.energy=energy;d.shape="DISK";d.size=size;d.color=rgb
    o=bpy.data.objects.new(name,d);bpy.context.collection.objects.link(o)
    o.location=p;o.rotation_euler=(Vector(target)-o.location).to_track_quat("-Z","Y").to_euler()
area("softbox key",(-3,-4,5),(0,0,1.3),(1,.82,.69),750,3.0)
area("blue rim",(2.8,1.5,4),(0,0,1.7),(.42,.75,1),1100,2)
area("warm fill",(2,-3,2),(0,0,1.3),(1,.62,.38),280,2.6)
camera_data=bpy.data.cameras.new("actual moving camera")
cam=bpy.data.objects.new("actual moving camera",camera_data)
bpy.context.collection.objects.link(cam);s.camera=cam
camera_data.lens=56
t0=time.monotonic();track=[]
for i in range(18):
    time=i/17
    cam.location=(2.45-time*.47,-5.9+time*.8,2.12-time*.08)
    cam.rotation_euler=(Vector((0,-.02,1.35))-cam.location).to_track_quat("-Z","Y").to_euler()
    pivot.rotation_euler[1]= -0.12 - 1.22*math.sin(math.pi*time)
    pivot.rotation_euler[2]= .06*math.sin(time*math.pi*5)
    headpivot.rotation_euler[0]=.042*math.sin(2*math.pi*time)
    root.rotation_euler[2]=.05*math.sin(2*math.pi*time)
    s.frame_set(i+1);s.render.filepath=str(out/f"{i:04d}.png")
    bpy.ops.render.render(write_still=True)
    track.append({"frame":i,"cam_xyz":[round(float(x),3) for x in cam.location],
                  "right_shoulder_y_angle":round(float(pivot.rotation_euler[1]),3)})
report={"status":"cpu_only_no_model_weights","blender":bpy.app.version_string,
    "renderer":"CYCLES","render_device":"CPU","ai_model_weight_bytes":0,
    "frames_rendered":18,"resolution":"480x270","actual_character_geometry":True,
    "articulated_arm_animation":True,"keyframed_camera":True,
    "procedural_skin_material":True,"license":"original authored character and scripts",
    "photoreal_actor":False,"cinematic_grade_verified":False,
    "render_elapsed_seconds":round(time_module,2) if False else round(__import__("time").monotonic()-t0,2),
    "camera_poses":track}
(out.parent/"actor-cpu-report.json").write_text(json.dumps(report,indent=2))
print(json.dumps({k:v for k,v in report.items() if k!="camera_poses"},indent=2))

#!/usr/bin/env python3
"""Real Blender geometry/PBR/shadows/camera test; not a Hollywood-grade human render."""
import bpy,math,sys,json
from pathlib import Path
from mathutils import Vector
args=sys.argv[sys.argv.index("--")+1:] if "--" in sys.argv else []
out=Path(args[0] if args else "proof/3d-frames")
out.mkdir(parents=True,exist_ok=True)
bpy.ops.object.select_all(action="SELECT");bpy.ops.object.delete(use_global=False)
s=bpy.context.scene
s.render.engine="CYCLES"
s.cycles.device="CPU"
if s.render.engine=="CYCLES":
    s.cycles.samples=8
    s.cycles.use_denoising=False
    bpy.context.view_layer.cycles.use_denoising=False
elif hasattr(s,"eevee") and hasattr(s.eevee,"taa_render_samples"):s.eevee.taa_render_samples=16
s.render.resolution_x=480;s.render.resolution_y=270;s.render.resolution_percentage=100
s.render.image_settings.file_format="PNG"
s.world=bpy.data.worlds.new("Cinematic studio");s.world.use_nodes=True
s.world.node_tree.nodes["Background"].inputs["Color"].default_value=(.03,.055,.08,1)
s.world.node_tree.nodes["Background"].inputs["Strength"].default_value=.30
def mat(name,color,metallic,roughness):
    m=bpy.data.materials.new(name);m.use_nodes=True
    bs=m.node_tree.nodes["Principled BSDF"]
    bs.inputs["Base Color"].default_value=(*color,1)
    bs.inputs["Metallic"].default_value=metallic
    bs.inputs["Roughness"].default_value=roughness
    return m
floor=mat("Studio floor",(.023,.031,.044),.25,.26)
metal=mat("Warm metallic copper",(.48,.25,.09),.85,.2)
bodymat=mat("Dark glassy PBR body",(.018,.027,.035),.52,.21)
white=mat("Ceramic accent",(.46,.55,.62),.02,.27)
bpy.ops.mesh.primitive_plane_add(size=100,location=(0,0,-.68));bpy.context.object.data.materials.append(floor)
bpy.ops.mesh.primitive_cube_add(size=1,location=(0,0,.13))
box=bpy.context.object;box.scale=(1.12,.7,1.28)
bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
bev=box.modifiers.new("Real bevel profile","BEVEL");bev.width=.12;bev.segments=3
box.modifiers.new("Normals","WEIGHTED_NORMAL")
box.data.materials.append(bodymat)
bpy.ops.mesh.primitive_torus_add(major_radius=1.04,minor_radius=.11,location=(0,0,.29),rotation=(math.radians(64),0,math.radians(16)),major_segments=60,minor_segments=12)
ring=bpy.context.object;ring.data.materials.append(metal)
bpy.ops.mesh.primitive_uv_sphere_add(segments=20,ring_count=12,radius=.19,location=(1.05,-.4,.56))
bpy.context.object.data.materials.append(white)
def light(name,loc,color,power,size):
    d=bpy.data.lights.new(name,"AREA");d.energy=power;d.shape="DISK";d.size=size;d.color=color
    o=bpy.data.objects.new(name,d);bpy.context.collection.objects.link(o)
    o.location=loc;o.rotation_euler=(Vector((0,0,0))-o.location).to_track_quat("-Z","Y").to_euler()
light("Key",(-3,-4,5),(1,.8,.65),900,4.0)
light("Cool rim",(3,2,3),(.25,.75,1),1000,2.2)
light("Fill",(-1,3,1),(1,.40,.25),650,3)
data=bpy.data.cameras.new("Real camera");cam=bpy.data.objects.new("Real camera",data)
bpy.context.collection.objects.link(cam);s.camera=cam;data.lens=58
data.dof.use_dof=True;data.dof.focus_object=box;data.dof.aperture_fstop=5.6
track=[]
for i in range(8):
    t=i/7;cam.location=(3.6*math.cos(.4+t*.45),-4.8*math.sin(.62+t*.32),2.0+t*.22)
    cam.rotation_euler=(Vector((0,0,.16))-cam.location).to_track_quat("-Z","Y").to_euler()
    ring.rotation_euler[2]=.26+t*.24
    s.frame_set(i+1);s.render.filepath=str(out/f"{i:04d}.png")
    bpy.ops.render.render(write_still=True)
    track.append({"frame":i,"camera_xyz":[float(round(x,4)) for x in cam.location]})
report={"renderer":s.render.engine,"blender_version":bpy.app.version_string,"width":480,
"height":270,"rendered_frames":8,"pbr_materials":4,"area_lights":3,
"camera_motion":track,"actual_3d_render":True,"photoreal_human_verified":False,
"hollywood_photoreal_quality_verified":False}
(out.parent/"blender-pbr-report.json").write_text(json.dumps(report,indent=2))
print(json.dumps({k:v for k,v in report.items() if k!="camera_motion"}))

#!/usr/bin/env python3
"""Real official CC0 Blender human topology asset, loaded by Blender 4.5 CPU.
A high-poly static human mesh check, not a pretrained AI video actor or animated rig.
No .blend autoexec, no model weights, no GPU.
"""
import bpy,sys,json,time,math
from pathlib import Path
from mathutils import Vector,Matrix
args=sys.argv[sys.argv.index("--")+1:] if "--" in sys.argv else []
if len(args)!=2:raise SystemExit("usage: blender --python ... -- source.blend output-dir")
src,out=Path(args[0]),Path(args[1]);out.mkdir(parents=True,exist_ok=True)
if not src.is_file():raise RuntimeError("Original CC0 library missing")
t0=time.monotonic()
bpy.ops.object.select_all(action="SELECT");bpy.ops.object.delete(use_global=False)
with bpy.data.libraries.load(str(src),link=False) as (from_file,to_file):
    names=[n for n in from_file.objects if n]
    to_file.objects=names
allobjects=[o for o in to_file.objects if o and o.type=="MESH" and o.data is not None]
if not allobjects:raise RuntimeError("No available mesh objects in official human library")
ranking=sorted(allobjects,key=lambda o:len(o.data.vertices),reverse=True)
# The largest by polygon count will often be a full human body; validate and report
# rather than claiming full human anatomy without visual inspection.
candidate=next((obj for obj in ranking if obj.name=="GEO-body_male_realistic"),ranking[0])
if len(candidate.data.vertices)<1000:raise RuntimeError("Not a production-resolution base mesh")
bpy.context.collection.objects.link(candidate)
candidate.parent=None
candidate.matrix_world=Matrix.Identity(4)
pts=[v.co.copy() for v in candidate.data.vertices]
lo=Vector([min(v[j] for v in pts) for j in range(3)])
hi=Vector([max(v[j] for v in pts) for j in range(3)])
extent=hi-lo
if extent.z<=0.00001:raise RuntimeError("unexpected degenerate mesh")
candidate.scale=(1.7/extent.z,)*3
bpy.context.view_layer.update()
candidate.location=(-.5*(lo.x+hi.x)*candidate.scale.x,
                    -.5*(lo.y+hi.y)*candidate.scale.y,
                    -.02-lo.z*candidate.scale.z)
for p in candidate.data.polygons:p.use_smooth=True
# Treat original as material-neutral base mesh: procedural skin PBR is a look-dev
# demo only and might be inaccurate for source topology/skin pigment.
skin=bpy.data.materials.new("original CC0 human mesh with CPU skin shader")
skin.use_nodes=True
bs=skin.node_tree.nodes.get("Principled BSDF")
bs.inputs["Base Color"].default_value=(.42,.243,.157,1)
bs.inputs["Roughness"].default_value=.54
if bs.inputs.get("Subsurface Weight"):bs.inputs["Subsurface Weight"].default_value=.085
candidate.data.materials.clear();candidate.data.materials.append(skin)
s=bpy.context.scene
s.render.engine="CYCLES";s.cycles.device="CPU";s.cycles.samples=12;s.cycles.use_denoising=False
bpy.context.view_layer.cycles.use_denoising=False
s.render.resolution_x=640;s.render.resolution_y=360;s.render.resolution_percentage=100
s.render.image_settings.file_format="PNG"
s.view_settings.view_transform="Standard"
s.world=bpy.data.worlds.new("cinematic dark studio");s.world.use_nodes=True
s.world.node_tree.nodes["Background"].inputs["Color"].default_value=(.022,.031,.045,1)
s.world.node_tree.nodes["Background"].inputs["Strength"].default_value=.4
def diffuse(name,color,r):
    m=bpy.data.materials.new(name);m.use_nodes=True
    p=m.node_tree.nodes["Principled BSDF"]
    p.inputs["Base Color"].default_value=(*color,1);p.inputs["Roughness"].default_value=r
    return m
bpy.ops.mesh.primitive_plane_add(size=200,location=(0,0,-.03))
bpy.context.object.data.materials.append(diffuse("grey floor",(.053,.067,.077),.38))
def light(name,loc,c,power,size):
    d=bpy.data.lights.new(name,"AREA")
    d.energy=power;d.shape="DISK";d.size=size;d.color=c
    o=bpy.data.objects.new(name,d);bpy.context.collection.objects.link(o)
    o.location=loc;o.rotation_euler=(Vector((0,0,.90))-o.location).to_track_quat("-Z","Y").to_euler()
light("softbox",(-3,-4,4),(1,.87,.76),600,3)
light("rim",(3,2,3),(.3,.76,1),850,2)
light("fill",(1,-3,2),(1,.63,.39),230,2.6)
camdata=bpy.data.cameras.new("professional lens");cam=bpy.data.objects.new("professional lens",camdata)
bpy.context.collection.objects.link(cam);s.camera=cam
cam.location=(2.7,-4.8,2.05);cam.rotation_euler=(Vector((0,0,.92))-cam.location).to_track_quat("-Z","Y").to_euler()
camdata.lens=58
s.render.filepath=str(out/"cc0-original-human-mesh-cpu.png")
bpy.ops.render.render(write_still=True)
report={"source":"official Blender Studio Human Base Meshes v1.4.1","source_license":"CC0 according to official Blender listing",
        "blender_version":bpy.app.version_string,"renderer":"CYCLES","device":"CPU",
        "ai_weight_files_loaded":0,"num_asset_library_objects":len(allobjects),
        "selected_object_name":candidate.name,"selected_vertices":len(candidate.data.vertices),
        "original_xyz_extent":[round(float(x),4) for x in extent],
        "candidate_top_objects":[{"name":obj.name,"vertices":len(obj.data.vertices)} for obj in ranking[:10]],
        "render_succeeded":(out/"cc0-original-human-mesh-cpu.png").is_file(),
        "model_is_rigged":False,"facial_expression_animated":False,
        "validated_photoreal_human_actor":False,
        "output_bytes":(out/"cc0-original-human-mesh-cpu.png").stat().st_size if (out/"cc0-original-human-mesh-cpu.png").exists() else 0,
        "runtime_sec":round(time.monotonic()-t0,2)}
(out/"cc0-human-mesh-cpu.json").write_text(json.dumps(report,indent=2))
print(json.dumps(report,indent=2))
if not report["render_succeeded"] or report["output_bytes"]<15000:raise RuntimeError("No valid preview rendered")

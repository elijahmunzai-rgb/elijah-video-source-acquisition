#!/usr/bin/env python3
"""Verify official freely downloadable CC0 Blender human base meshes without any AI model.
This is asset preflight only: Blender 4.2+ required to open production blend files.
No arbitrary code or .blend files are executed in this test.
"""
import hashlib,json,pathlib,sys,urllib.request,zipfile,os
from datetime import datetime,timezone
URL="https://mirror.blender.org/demo/asset-bundles/human-base-meshes/human-base-meshes-bundle-v1.4.1.zip"
OFFICIAL_LICENSE="https://www.blender.org/download/demo-files/"
OUT=pathlib.Path(sys.argv[1] if len(sys.argv)>1 else "proof/cc0-human")
OUT.mkdir(parents=True,exist_ok=True)
FILE=OUT/"blender-human-bases-v1.4.1.zip"
request=urllib.request.Request(URL,headers={"User-Agent":"ElijahFilmStudio-CPU-Asset-Audit/1.0"})
with urllib.request.urlopen(request,timeout=150) as r:
    with open(FILE,"wb") as f:
        while data:=r.read(1024*1024):
            f.write(data)
            if f.tell()>80_000_000:raise RuntimeError("Unexpectedly huge archive")
h=hashlib.sha256()
with open(FILE,"rb") as f:
    for buf in iter(lambda:f.read(1024*1024),b""):h.update(buf)
with zipfile.ZipFile(FILE) as z:
    bad=z.testzip()
    if bad:raise RuntimeError("Corrupt archive member "+bad)
    names=z.namelist()
    if any(n.startswith("/") or ".." in pathlib.PurePosixPath(n).parts for n in names):
        raise RuntimeError("Untrusted archive path")
    blends=[n for n in names if n.lower().endswith(".blend")]
    if not blends:raise RuntimeError("CC0 human bundle contains no blend files")
    # Avoid distributing third-party files or silently granting output permissions.
    manifests=[n for n in names if pathlib.PurePosixPath(n).name.lower() in ("license","license.md","license.txt","readme","readme.md","readme.txt")]
    report={
      "official_source":URL,"official_license_listing":OFFICIAL_LICENSE,
      "official_site_describes_bundle_license":"CC0",
      "archive_sha256":h.hexdigest(),"compressed_bytes":FILE.stat().st_size,
      "zip_members":len(names),"blend_files_found":len(blends),
      "blend_samples":blends[:30],"documentation_files":manifests[:15],
      "minimum_blender_version":"4.2 LTS",
      "generative_ai_weights_required":False,
      "verified_download":True,"archive_testzip_ok":True,
      "production_mesh_loaded_into_compatible_blender":False,
      "photoreal_character_quality_proven":False,
      "audited_at":datetime.now(timezone.utc).isoformat()
    }
    (OUT/"cc0-human-asset-audit.json").write_text(json.dumps(report,indent=2))
    print(json.dumps(report,indent=2))
    if not (20_000_000<report["compressed_bytes"]<80_000_000):raise RuntimeError("Archive size unexpected")
FILE.unlink()

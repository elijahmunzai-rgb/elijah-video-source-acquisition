# CPU-First Filmmaking: GPU-optional, no paid models (October 22, 2026)

## Decision
**Never require NVIDIA/CUDA, external diffusion weights or commercial AI-video APIs to render or edit a movie.** Canonical production order:

1. **Photoreal humans = recorded and rights-cleared actors**, or licensed plate footage. A real actor in footage is actual photorealism at no compute cost; actor/camera tracking uses OpenCV feature tracking, compositing and FFmpeg. Obtain actor permission and review release, privacy and likeness conditions.
2. **CG humans = MakeHuman core CC0 exported meshes/skins + Blender Cycles CPU**, articulated face/body rigging, camera, light rigs and PBR. The bundled MakeHuman assets are CC0; distinguish them from third-party assets and app code (AGPL). Source: https://github.com/makehumancommunity/makehuman/blob/master/LICENSE.md. You need rigged mesh/skin textures/animation assets; these are **3D resources**, **not pretrained diffusion model weights**. [Blender CC0 49 MB Human Base Meshes v1.4.1](https://www.blender.org/download/demo-files/) require **Blender 4.2 LTS+**. Ubuntu apt Blender 4.0.2 is too old; do not claim that asset was loaded/rendered without upgrading the Blender version. Explicitly audit compatibility, asset license and 4.2 version before attempting.
3. **Original procedural stand-ins = no weights/assets/GPU** using `studio/proofs/cpu_only_character.py` and `cpu-only-human.yml`. This produces a stylized character, articulated hand gesture, keyframed moving camera and physically-based CPU lighting. This proves technically working digital actors **without AI** but **does not** prove realistic skin, human expression, speech, cinematic acting, hair or Hollywood image quality.
4. **Editing = FFmpeg + Remotion + OpenCV** on standard public `ubuntu-latest` CPU runner. Reuse output and scene segments to avoid rerendering expensive frames.
5. **Optional CPU generative inference (separate branch, opt-in) = OpenVINO/ONNX/INT8/FP16 + pretrained compatible open weights**. These STILL REQUIRE model files (learned parameters, sometimes many GB) and model-specific license/security vetting. Good for generating individual key art or still backgrounds before animation, **not** a promise of high-quality multi-shot synthetic human video on 4 CPU cores.

## Weights explained
- **Program code** tells the software how to calculate. **Generative model weights** are learned parameter data (often `.safetensors`, `.onnx`, `.pt`, `.pth`), usually too large/expensive to train from scratch on a GitHub CPU runner.
- A **3D mesh** (`.blend`, `.obj`, `.fbx`, `.glb`) is not a generative AI model. A 3D **rig's vertex skinning weights** only specify which bones influence mesh vertices. Do not confuse these with neural-network model weights.
- **Model weights can be free to download**, but check intellectual property, license, model provenance, storage, safe format and CPU speed. No tool can infer pretrained faces without training data or an authored 3D human/footage alternative.
- **No generative weight requirement** means no text-to-photoreal-person generator; real recorded people, hand-authored 3D characters and render-time effects remain possible.

## Actual free runner resources
Standard public GitHub Ubuntu runner: 4 CPU cores, 16 GB RAM, 14 GB SSD. Standard hosted runners are free in public repositories, but artifacts/storage policies and individual workflow limits still apply. Never configure a larger paid runner, persistent provider account, GPU rental or premium video service. Source: https://docs.github.com/en/actions/reference/runners/github-hosted-runners.

## Scaling without GPU
- Keep characters/shot shaders deterministic, static scenery as persistent prerendered layers, moving objects in small 2–6 second segments.
- Render in parallel using a bounded CPU job matrix with per-frame low-sample draft render before film quality review; only upscale/resample **after** a shot passes creative acceptance.
- Use native render passes + depth for composite rather than rerender full environments; avoid 16-bit EXR archives unless a specific shot needs them.
- 24 fps to 1080p only when the asset and visual detail actually support it; do not call upscaling new information.
- Make film milestones: 1. clean still+skin test, 2. mouth/emotion acting test, 3. real 3D body motion, 4. compositing on actual actor plate with robust occlusion, 5. consistent 30-second complete film, 6. original longer film. Each includes critical human visual QC.

## Evidence status
- Zero-GPU procedure: **workflow created**; only call pass when GitHub job concludes success and MP4, JSON evidence exist.
- Previously completed: 318 historical snapshot audit, Remotion MP4 render, Blender CPU 3D, recorded-human tracking; three original upstream repo test suites (31 tests). This does not establish any generated actor photorealism.
- For output types requiring photoreal human presence immediately, prioritize real licensed footage. For fully synthetic photoreal human performance without a GPU, the best quality path is **authored high-quality CC0 rigged meshes, shaders, hand-driven animation, CPU Cycles render**; cost is substantial artist/time effort and possibly slow scene rendering.

## Model-free character test
```bash
sudo apt-get install -y blender ffmpeg
blender -b -t 2 --python studio/proofs/cpu_only_character.py -- proof/cpu-character/frames
ffmpeg -framerate 9 -i proof/cpu-character/frames/%04d.png -c:v libx264 -pix_fmt yuv420p proof/cpu-character/actor-CPU-no-weights.mp4
```
This script performs genuine CPU ray-traced 3D image creation, not a title-card animation or a prerendered stock clip. Its models are intentionally stylized.

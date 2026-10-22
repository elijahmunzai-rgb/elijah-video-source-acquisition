# Film Studio / Dan's remote NVIDIA GPU (consented workstation)

**Implementation state:** safe CPU-side preparation and diagnostics on this feature branch. Dan's GPU has NOT been probed, ComfyUI has NOT been installed there, no tunnel exists, and no remote GPU render is certified. Owner permission is established by user, but device-side setup still requires Dan (or someone operating his PC). Distance US→Pakistan does not prevent this architecture.

## Truth about the 318 resources

The frozen 318 sources are **318 upstream source catalog snapshots, not 318 installed skills or GPU models**. Evidence from reference audits:
- 318/318 Git source archives verified, 303 with code-like files, 197 detected dependency manifests.
- Three upstream projects had selected original code tests. This is **not 318/318 runtime installed**, not 318 running production agents.
- Film Studio has **26 internal skills descriptions**, of which execution is only realized when a workflow or human explicitly invokes the relevant methods.
- Eight production-worker stages are deterministic code (script/shot metadata, storyboard, rights, camera, motion, audio, QA), not eight independently reasoning neural networks.
- Relevant engines already proven individually: Blender Cycles CPU technical test, FFmpeg, Remotion, OpenCV. Currently routine public render is an original 6-second H.264/AAC editorial animation at 1920x1080, not a natural-language-to-feature-film pipeline.

**Best use of the 318**: prioritize licensed sources implementing story and shot planning, asset licensing, Remotion/motion design, 3D Blender, video diffusion in ComfyUI, real-camera compositing, color grading, high-quality sound and technical/subjective QC. Avoid wrapping all 318 blindly: license incompatibilities, irrelevant wrappers, costly API dependencies, vulnerabilities, and GPU memory conflicts will *lower* quality, not maximize it.

## Architecture

Pakistan: user interacts with existing lightweight Hostinger command room.
US: Dan's personally owned, permissioned Windows workstation hosts local ComfyUI/Blender GPU compute.
Private transport: a VPN mesh (e.g., Tailscale's device sharing) with Dan granting access ONLY to the intended machine/port. No router port forwarding, no ComfyUI internet exposure and no remote Windows administrator access.
Control: first complete a local trial with Dan on his PC. Later use a mutually authenticated *private* job queue and private object storage, with user approval, quotas, signed workflow templates and automatic job expiry.
Public GitHub: only generic source, tests and PUBLIC demo artifacts; **never** actual client scripts, footage, private assets, credentials or private job metadata.
Do NOT register Dan's personal Windows machine as a self-hosted runner on this public GitHub project. GitHub explicitly warns this can expose private workstation data through malicious PR/workflow execution.

## Initial setup on Dan's PC (one-time, authorized by Dan)

1. Save the provided readiness kit into an ordinary dedicated folder, for example `C:\FilmStudioWorker\`. It is not an installer.
2. Open Windows PowerShell inside the folder and run:
   ```powershell
   powershell -NoProfile -ExecutionPolicy Bypass -File .\Check-FilmStudioGPU.ps1
   ```
   It produces a local `film-studio-gpu-readiness.json` containing GPU model, VRAM, driver, CPU count, RAM and free disk; **no hostname, IP address, Windows username or credentials**. Review the JSON before sharing. If Windows blocks the script, Dan should inspect its source and run via an approved policy, not weaken system-wide security settings.
3. Verify driver and 16 GB VRAM. The informal phrase "ASUS RTX 470 16 GB" is not an exact NVIDIA model. Possible candidates include **ASUS RTX 4070 Ti SUPER 16GB** or **RTX 5070 Ti 16GB**. Do not choose a CUDA/PyTorch stack until the real GPU model is known.
4. Install a CURRENT official supported NVIDIA display/studio driver (Dan only, after normal Windows backup/rollback). Install [ComfyUI Desktop](https://comfy.org/download) from the official source, then start it bound to local loopback rather than `0.0.0.0`. Validate that ComfyUI GUI is accessible locally. Model downloads can be many gigabytes and may have usage/license restrictions, so select only after checking free disk and Dan's approval.
5. Start with **Wan 2.2 TI2V-5B** via the official ComfyUI video workflow templates as a *feasibility candidate*, not a quality or speed guarantee. ComfyUI documents low-memory offloading for the 5B workflow and presents separate heavier 14B versions. Test one 3–5-second 480p/720p proof, then upscale/postprocess with permission. A 16GB card does not guarantee all 14B models, all frame lengths or native full-HD video generation.
6. Review the ComfyUI workflow JSON and installed custom nodes, then record its exact SHA256 in an **untracked, Dan-local** `approved-workflows.json`, e.g. `{"approved_sha256":["<64 hex sha256>"]}`. Never upload private workflow prompts/models/licenses to public GitHub.
7. Run offline permission validation:
   ```powershell
   python .\comfy_local_worker.py --workflow .\audited-api-workflow.json --approvals .\approved-workflows.json --dry-run
   ```
   Then Dan explicitly opts into one render:
   ```powershell
   python .\comfy_local_worker.py --workflow .\audited-api-workflow.json --approvals .\approved-workflows.json --submit --output .\render-output
   ```
   This client connects **only** to `http://127.0.0.1:8188`, submits the approved workflow, polls one local job, and downloads media to the explicit folder. It never accepts remote command execution, writes firewall rules, starts a listener, downloads models, or copies tokens. No automatic polling/background work is configured.
8. Optional after first success: Dan uses [Tailscale device sharing](https://tailscale.com/docs/features/sharing) to share only this machine with an authorized account, applying strict access rules. Its pricing/eligibility depend on actual use and plan. Keep public internet ports CLOSED. Access, runtime cost (electricity), model license compliance, disk space and PC sleep state are Dan-controlled.

## Future milestones

**GPU P0:** proof of real GPU capabilities, CUDA/PyTorch versions, 3–5-second model-native video, VRAM peak, latency, artifact QA and consent. 
**Creative P1:** story → cinematography shot list → character/place references → short generated video plates → continuity edits → licensed VO/audio → Full-HD mastered 30-second output; all with explicit rights gates and human review.
**Production P2:** private queue, authenticated permissions/roles, encrypted media, expiring signed URLs, upload size limits, budgets, per-job GPU time quotas, cancellation/health reporting, auditable revisions.
**R&D P3:** prioritize/source-validate the 318 catalog entries by relevance; a component is marked integrated only when licensing, install, security, and actual functional/quality tests pass.

## Explicit nonclaims

Dan's exact NVIDIA card and permissioned access are not yet technically verified from this environment. No ComfyUI server, installed model, remote tunnel, private queue or GPU render is connected today. The existing Film Studio Hostinger deployment and IO Agency WordPress/sites are untouched by this feature branch. No paid GPU instance/VPS or subscription was purchased.

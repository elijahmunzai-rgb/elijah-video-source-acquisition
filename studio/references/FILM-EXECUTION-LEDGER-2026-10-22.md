# Film Studio — 22 Oct 2026 engineering handoff

**Free resources only. No paid model, hosted generator, API credits or subscriptions.** Canonical repo: [Elijah Film Studio](https://github.com/elijahmunzai-rgb/elijah-video-source-acquisition).

## Completed and verified

- **Original upstream provenance:** 318/318 snapshots (317 direct, 1 restored from exact historical Git fork commit and 58 source file hashes). [Passing original snapshot audit](https://github.com/elijahmunzai-rgb/elijah-video-source-acquisition/actions/runs/39666091478).
- **Per-project source/static feasibility:** 318/318 Git trees inspected; **303** contain recognized code files; **197** advertise a detected dependency manifest. [Passing 318 audit](https://github.com/elijahmunzai-rgb/elijah-video-source-acquisition/actions/runs/39669103072).
- **Representative real upstream code execution:** pinned MIT-licensed `hacimertgokhan/geomotion` at commit `88c1c1c4f8946309f961ef6e7983171da7a95d07`, actual 9/9 original Node tests passed; generated `sunrise.svg` and `sunrise.lottie.json` using its original CLI. [Passing pinned original upstream test](https://github.com/elijahmunzai-rgb/elijah-video-source-acquisition/actions/runs/39673204987). This is **1 of 318 independently runtime-certified original upstream projects**, **not 318 installed**.
- **Independent production stack:** Blender Cycles CPU ray-traced 3D moving-camera MP4, licensed recorded human footage optical flow, Remotion Node install/MP4, OpenCV and FFmpeg all separately executed and passed. [3D + footage](https://github.com/elijahmunzai-rgb/elijah-video-source-acquisition/actions/runs/39670561081) · [Remotion](https://github.com/elijahmunzai-rgb/elijah-video-source-acquisition/actions/runs/39669757842).
- **Calibrated PnP RANSAC QA:** 24-frame geometric *synthetic ground-truth* test passed, median ~0.25px reprojection; its reported camera rotation/translation are measured against synthetic known values. **This does NOT prove calibrated 3D motion tracking from actual recorded actors.** [Passing camera geometry test](https://github.com/elijahmunzai-rgb/elijah-video-source-acquisition/actions/runs/39673293506).
- **Edited 30-second technical reel:** produced 10 distinct story/title beats with previously verified 1–3 second reusable source plates and an independently synthesized stereo score. FFprobe: 960×540, 24 fps, H.264 and AAC, 30.0 seconds. The 120-second and 600-second H.264/AAC outputs passed duration stress QA but loop the same 30-second material repeatedly. **Duration benchmarks are not independently scripted features.** Deliverables/source script and manifest supplied as ChatGPT conversation files, not uploaded to public GitHub.
- **Public repo safety:** no private agency/customer footage, branding or credentials committed.

## Current unavoidable quality/resource limits

- The free GitHub runner is CPU-only: 4 cores, ~15.61 GiB RAM, **no NVIDIA CUDA device or photoreal actor diffusion model weights**. A Hollywood-quality **synthetic human actor** has **not** been generated and cannot be certified from the available proofs. Real recorded actor footage is distinct from synthetic human generation.
- A full authored **120-second narrative film** and **600-second feature/short** with original footage/individual scenes/voice performances **remain incomplete**. The long duration MP4s are loops for technical continuity testing only.
- **317 upstream repos are still NOT individually runtime-installed/certified.** Many are skills, documentation, optional paid-service wrappers or have uncertain licenses; running all unseen installers on a public runner is unsafe and sometimes not meaningful.
- Automated GitHub SPDX metadata summary: 203 MIT, 24 Apache-2.0, 2 MIT-0, 8 AGPL-3.0, 1 CC-BY-SA-4.0, 40 NOASSERTION, 40 missing. Metadata is not a complete file-level redistribution/commercial-rights audit. **89 projects** require additional license consideration even under preliminary labels. Asset/model licenses always separately audited.

## Real production acceptance gate

Real photoreal cinematic acceptance needs intentionally shot/consented plates, high-end scene design/characters, correct calibrated live-footage camera moves and occlusion, narrative continuity and acting, sound/dialogue plus visual reference review. Do **not** claim it is Hollywood-level from short technical reels, MP4 codec tests, 318 source trees or mere presence of skill files.

All further original-upstream runtime testing must be security-vetted, pinned to commits, run in no-secret isolation, respect rights, and report a separate pass count. No cost-bearing actions authorized.

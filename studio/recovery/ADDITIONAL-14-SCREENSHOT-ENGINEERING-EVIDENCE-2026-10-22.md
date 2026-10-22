# Additional prior-chat screenshots: CPU-only agent network, source-recovery proofs and history

**Source:** 14 screenshots newly shared on 22 October 2026, from the earlier *Coding Video Creation* chat. This document preserves **paraphrased project facts and decisions only**, not the personal chat images, which must NOT be uploaded to the public GitHub repository. Technical proof claims have been compared with the existing [Film Execution Ledger](../references/FILM-EXECUTION-LEDGER-2026-10-22.md) and [Realism/318 Acceptance](../references/REALISM-AND-318-RUNTIME-ACCEPTANCE.md). Numbers taken only from a screenshot without a corresponding verified artifact are labeled *historical screenshot report*.

## 1. Architecture and approved operations recovered

- Earlier user explicitly wanted a film studio able to be controlled from the user's **phone or laptop without requiring local rendering**. Heavy CPU jobs run elsewhere. Moving the rendering workload from personal device to GitHub Actions does **NOT eliminate computational demand**.
- Confirmed intended split: **Hostinger** (Film Studio site/dashboard, projects, approvals, previews and outputs), **GitHub Actions** (free public-repo CPU workers, Blender/FFmpeg/Remotion, QA), **storage/retention** (approved completed outputs and project files) and **human release approval**. Public runners have quotas; confidential footage is not permitted inside public logs/artifacts.
- Existing Hostinger Business historical specs: 2 CPU / 3GB RAM / 50GB storage, no VPS or paid infrastructure. Any no-cost CPU inference is **optional**, not mandatory; a proposed `llama.cpp + Qwen3 0.6B` CPU creative helper and quoted ~484MB quantized weights were exploratory from the screenshot, **not evidence of installed weights or autonomous creative director**. Validate model/version/license/current hosting resources before trying.
- Eight specialist **scripted workflow** stages under a studio director: **Screenwriter, Storyboard, Asset Rights, Camera & VFX, Motion, Audio, QA & Delivery**, with potential future **Production Manager**, **3D/Character Crew**, **Postproduction Crew**, **Quality Supervisor** and **Delivery Manager**. The separate future crew roles are requested architecture, not existing independent neural agents.
- Historical stage pipeline: `Hostinger Studio Dashboard → GitHub Agent Orchestrator → Parallel free CPU render workers → QA → human approval → delivery`. On current public staging, direct web dispatch stays login/token-locked; GitHub request-file bridge already works for PUBLIC demos.
- User demanded **no upgrades, paid subscriptions, credits or extra GitHub Actions charges**; agency/sales repositories must remain **PRIVATE and distinct**. Dedicated video source/production repository intentionally stays **PUBLIC** for free public-repo runners. Never migrate that repository to private or move film source into an unrelated sales repository without explicit approval.

## 2. Original film-engine proofs recovered and corrected

| Historical screenshot report / proof | Evidence cross-check | Interpretation and limitation |
|---|---|---|
| Early Blender CPU articulated human test: 18 frames, ~20.4s to render, H264 output, 0 model-weight bytes | Screenshot; additional linked Blender proof exists in reference ledger | Procedural/STYLIZED character and moving-camera technical demonstration; **not** convincing photoreal actor |
| Blender Studio **CC0** human base model: 10,582 vertices, CPU Cycles, 640×360 still | Screenshot | Geometry/material rendering proof only; no proven facial acting, expressions, voice lip-sync, clothing, multi-shot performance or real human likeness |
| Recorded-human optical flow | Repo acceptance ledger: 72 frames, 71/71 valid RANSAC flow pairs, median ~140 inliers, ~0.17px error; sampled faces detected | Real-footage 2D motion tracking; does **not** prove solved/calibrated 3D face or actor tracking |
| Calibrated camera pose PnP/RANSAC | Execution ledger: 24 **synthetic** frames, ~0.25px median reprojection error | Working synthetic geometry algorithm; **not** calibrated real-scene camera tracking, even if camera rotation/translation synthetic test passed |
| Blender physically based 3D moving camera | Repo ledger links run `39670561081`; actual 24-frame 640×360 CPU render | Rendering stack functionality, not guaranteed film art direction |
| Remotion Node/Chromium build | Repo ledger links run `39669757842`, 3-second 640×360 actual H264 | Real Remotion functional integration proof, not every plugin/skill installed |
| Seven-second combined production proof | Repo acceptance: 960×540 24fps H264/AAC, real licensed recorded footage + Blender 3D + Remotion | Technical cross-engine proof, not an audience-quality-approved cinematic film |
| Thirty-second reel | Execution ledger: 960×540 24fps H264/AAC, 10 beats, mixed real footage/3D/Remotion and synthetic score | Rendered technical reel; no evidence that whole audiovisual creative quality was user approved |
| 2-minute and 10-minute H264 demonstrations | Repo ledger: repeated 30-second content in loops | **Duration-stress proofs only**; must never claim real original 120s/600s authored movies |
| Four CPU cores / 16GB RAM on GitHub runner | Historical screenshot; ledger measured 4 cores, approximately **15.61GiB** | Historical Ubuntu runner CPU footprint, **not** unlimited render resources or machine performance guarantee |

The original screenshot stated 318/318 *compatibility* passed. This was **static source/tree/dependency scanning**, not 318 runtime installations. Refer to immutable ledger: **318 historic source snapshots confirmed, 303 code-like repositories, 197 detected manifests, selected original upstream tests performed on 3 projects only**.

## 3. The challenging 318th repository recovery

The screenshots show a specific missing **Motion Video Director**-related original upstream repository returning 404 at the time of recovery. Earlier text proposed a nonidentical replacement implementation; user correctly rejected silently replacing the original source and demanded **exact original historical code**.

Final historical screenshot report asserts:
- **317 direct originals + 1 exact historical Git-fork/commit recovery = 318/318 verified**.
- The exceptional recovered original had **58 source files**, and matching hashes were independently checked on important originals including README, its `Motion Video Director` skill documentation, and LICENSE.
- Historical screenshot text references `Miftahul-Islam-Efaz/Motion-graphics-skill` and `mysticals1n/Motion-graphics-skill` in different recovery stages; these are **historical names/transcripts, not an assertion of current URL reachability or ownership equivalence**. Do not substitute either for the pinned original unless archive SHA/source provenance matches.
- The authoritative GitHub Actions source verification proof is [run 39666091478](https://github.com/elijahmunzai-rgb/elijah-video-source-acquisition/actions/runs/39666091478). The screenshots' claimed 58-file source recovery agrees with the canonical repo execution ledger.
- User explicitly required full original sources, submodules/LFS and all checksums wherever applicable, not metadata-only aliases. **318 recovered snapshots still do not imply 318 runtime packages installed or useful filmmaking engines**.

## 4. GitHub repository separation and safety

The screenshot sequence documented an earlier move from temporary video-related files in the agency sales repo into the dedicated public film source repo:
`https://github.com/elijahmunzai-rgb/elijah-video-source-acquisition`.

It claimed 44 production-related files migrated and source-acquisition execution restored. The **sales `main` branch was reported untouched**, agency/website repositories remained private, and the dedicated Film Studio public repository was approved to stay public for free GitHub CPU runners. Avoid retroactively turning the sales repo public. Public means **no confidential client footage, no source credentials, no private strategy/assets**.

Later Hostinger architecture has already advanced beyond old screenshot's “dashboard not yet built” status: the **Phase 2 dashboard is LIVE** at `https://video-production.inboundoutbound.io`. Old screenshot statements about *pending deployment* are historic, not current status.

## 5. Lessons and release rules recovered

- **Artistry ≠ technical test:** a stylized 3D base mesh, 3D camera tracking synthetic reprojection, or well-encoded montage is not proof of realistic Hollywood acting. The user rejected subsequent elementary 640×360 silent title videos, so pixel-resolution upgrades are insufficient without real story/shot/audio quality.
- **CPU/free is preferred** over model-weight-dependent GPU models, but cannot guarantee photoreal generation. Prefer authentic rights-cleared actor footage, CPU Blender PBR, scene-aware Remotion motion, FFmpeg editing, OpenCV optical flow, real narration and custom licensed audio.
- **Always scope expensive compute honestly:** automated renders require a CPU/GPU somewhere, typically a free GitHub runner with platform limits. Hostinger web app is not the worker; phone/laptop controls the system.
- **Content approvals:** technical QA first, then **human creative review and rights clearance**, then publication only with permission. No public client/private uploads.
- **Daniel's permitted US 16GB GPU remains last resort** with exact model unverified, no remote access connected or installed. An isolated readiness kit exists but is not on his machine.
- All 318 preserved, but actual activation is **quality-first, source-reviewed and stage-specific** rather than launching 318 arbitrary scripts.

## 6. Next production gap prioritized

The recovery demonstrates real cross-engine **proofs** already happened, so don't waste effort merely repeating 640×360 proof renders. The missing user-value milestone is a **director-reviewed real-footage-led 3–6 second sequence with authentic audio**, then a genuinely original 30-second IO Agency commercial, then distinct authored 2- and 10-minute works. Stage-specific shortlisting and 318-source integration tests should serve that creative goal.

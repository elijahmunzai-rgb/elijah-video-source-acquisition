# Elijah Film Studio — Code-First Video Production

Dedicated **public, no-paid-API** filmmaking engineering repository. This is the canonical home for generic code-first film-production tools previously scattered across experiments. It is **separate** from the private IO Agency website and OutboundForge sales code.

## Studio modules

| Directory | Purpose |
| --- | --- |
| `studio/engine/` | deterministic video rendering, motion/compositing, audio mixing, sound synthesis, ffprobe-based QC and source-acquisition engines |
| `studio/skills/` | filmmaking role skills: creative director, screenwriter, cinematographer, motion/3D director, editor, sound designer, narration, avatar direction, brand/QC |
| `studio/tests/` | engine tests, including source integrity checks |
| `studio/references/` | production standards and provenance notes |
| `film-vault/` | pinned 318-repository full-source importer, submodules and Git LFS audits, strict 318/318 verifier |
| `.github/workflows/` | free-runner diagnostics and acquisition workflow |

## Production flow

Brief → screenplay and shot list → art direction / visual references → camera and scene specification → authored visual assets / permitted footage → frame-exact animation / compositing → narration / sound design → music mix → render → scene-by-scene QA → delivery.

Run locally using Python 3.12, FFmpeg and, where needed, `pip install -r studio/requirements.txt`. CLI tools are explicitly invoked, not automatically executed simply because they are present.

## 318 external repositories (source status)

The fixed manifest comes from `zhuyansen/awesome-claude-video-skills` at commit `ffdf99cbc7879f611abba186e933695904cd638f` (2026-10-19). A name in this catalog is **not** equivalent to full source, a functioning installation or a production-quality renderer.

`film-vault/import_sources.py` attempts original Git clones, recursive submodules, Git LFS and file hashes. `film-vault/verify_sources.py` only passes with all 318 unique repositories independently verified.

**VERIFIED: 318/318 historical original source snapshots** (317 directly from their original GitHub locations, 1 from the identical Git commit/tree preserved in a surviving fork). Full file-level and three known historical SHA-256 checks passed for the recovered 58-file source. See [successful final recovery run](https://github.com/elijahmunzai-rgb/elijah-video-source-acquisition/actions/runs/39666091478), the hash-only artifact `318-original-source-recovery-audit-only`, and [original run (317 direct verified)](https://github.com/elijahmunzai-rgb/elijah-video-source-acquisition/actions/runs/39658143891). This is a **source snapshot audit**, not evidence that 318 packages are installed, safe to run, license-redistributable, or production-cinema quality. Public workflows may still be restricted by the GitHub account's runner provisioning or artifact limits. No paid services will be purchased.

## Privacy and upstream licensing

This public repository contains generic studio scripts, skill playbooks and public-source import infrastructure only. Client footage, unreleased campaigns, private agency credentials, real avatar assets, brand files and paid-license media stay outside public Git. Original upstream projects retain their own licenses; they are **not** relicensed by this repository.

Do not use this repo for website or CRM deployments. Do not include private business content in any generated artifacts or logs.

## Legacy project migration

The old, isolated `outboundforge-agent` video-source sandbox branch was only a temporary staging location. Its standalone `film-vault` scripts and workflows have been migrated here, and the original generic Film Production Mastery plugin's code and skill content is mirrored under `studio/`. Future video production belongs here.

## Render proof and quality bar

Technical success (valid codec, duration, resolution, correct loudness) is not equivalent to cinematic quality (acting, camera motion, pacing, realism, visual storytelling). Require both for acceptance. Code-only approaches can deliver professional design and animation, but photorealistic humans/environment simulation depend on actual image/scene/renderer data and computational capacity, not simply the number of skills installed.


## Historical original source #318 — recovered, with rights preserved

The original `Miftahul-Islam-Efaz/Motion-graphics-skill` URL now returns 404. We recovered **the exact original Git commit** `4fe427bcda356b8a53ce65705eecced2e10be572` via surviving fork `mysticalsin/Motion-graphics-skill` and verified tree `fe56211a50c8123afc42efc87a9659730c8ddd52`. The original commit contains **58 tracked source files** (~13.1 MB uncompressed). Historical external independently recorded SHA-256 digests for `README.md`, `skills/motion-video-director/SKILL.md`, and `LICENSE.md` all matched exactly; all tracked files received SHA-256 inventory and no LFS pointers or missing files were present.

Do **not** vendor the original protected skill here: its original LICENSE limits redistribution of protected materials. The public repository retains only our independent skills, immutable source identifiers, hash-only verification, and the recovery workflow. Source can be restored reproducibly from the surviving fork at its original commit while that fork remains available, subject to its license. This does not imply a perpetual backup.

The [source recovery issue](https://github.com/elijahmunzai-rgb/elijah-video-source-acquisition/issues/1) tracks provenance and rights. 318 source snapshots verified does not mean all upstream video-processing workflows were executed.


## Actual runtime evidence (Oct 21, 2026)

Verified free-system proofs: [recorded human optical tracking and Blender Cycles rendering](https://github.com/elijahmunzai-rgb/elijah-video-source-acquisition/actions/runs/39670561081), [actual Remotion 4 npm install + real H.264 export](https://github.com/elijahmunzai-rgb/elijah-video-source-acquisition/actions/runs/39669757842), and [all 318 public source trees / manifest audit](https://github.com/elijahmunzai-rgb/elijah-video-source-acquisition/actions/runs/39669103072). The full [Hollywood-realism acceptance ledger](studio/references/REALISM-AND-318-RUNTIME-ACCEPTANCE.md) distinguishes real visual proof from catalog entries. **197 projects advertise install manifests, 303 have code-like files, but individual 318 upstream dependency installations and performance have not been certified.** A 7-second multi-system technical reel was compiled separately; not a Hollywood grade or generated-photoreal-actor proof.

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

**Current verified 318-source count: NOT YET COMPLETED.** Do not claim full acquisition before examining passing artifacts and independent file inventories. Public workflows may still be restricted by the GitHub account's runner provisioning or artifact limits. No paid services will be purchased.

## Privacy and upstream licensing

This public repository contains generic studio scripts, skill playbooks and public-source import infrastructure only. Client footage, unreleased campaigns, private agency credentials, real avatar assets, brand files and paid-license media stay outside public Git. Original upstream projects retain their own licenses; they are **not** relicensed by this repository.

Do not use this repo for website or CRM deployments. Do not include private business content in any generated artifacts or logs.

## Legacy project migration

The old, isolated `outboundforge-agent` video-source sandbox branch was only a temporary staging location. Its standalone `film-vault` scripts and workflows have been migrated here, and the original generic Film Production Mastery plugin's code and skill content is mirrored under `studio/`. Future video production belongs here.

## Render proof and quality bar

Technical success (valid codec, duration, resolution, correct loudness) is not equivalent to cinematic quality (acting, camera motion, pacing, realism, visual storytelling). Require both for acceptance. Code-only approaches can deliver professional design and animation, but photorealistic humans/environment simulation depend on actual image/scene/renderer data and computational capacity, not simply the number of skills installed.

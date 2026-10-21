---
name: code-first-motion-director
description: Original, dependency-minimal film direction and deterministic motion-compositing playbook for 30-second spots, 2-minute explainers and up to 10-minute videos. Own implementation, not a copy of the deleted third-party Motion Video Director.
---
# Code-First Motion Director — Original Elijah Film Studio Skill

**Attribution:** Independent implementation inspired by standard filmmaking and computer-graphics methods, not a clone or reproduction of `Miftahul-Islam-Efaz/Motion-graphics-skill`. That original package is unresolved upstream source #318 and has distinct redistribution conditions. Never count this skill as the recovered original package.

## Preproduction and continuity

1. Translate the creative brief into an **observable** treatment: target audience, action/offer, intent, 15-second hook, believable environment, visual credibility threshold and platform export.
2. Write a screenplay with scene IDs, action, line timings, camera grammar, props, material and SFX notes. Use a shot ledger with unique asset references, lens-equivalent, focal subject, start/end framing, camera path, depth cues, and continuity constraints.
3. Maintain a **style bible** (palette, typography, real logo, lighting, camera/lens vocabulary, sound palette, transitions), **character bible** (voice, wardrobe, eye-lines, proportions) and **location bible**. Only treat camera tracking as real tracking if source footage, camera transforms and independently checked frames exist.
4. Build a scene cue/timing manifest driving narration, beat accents and visuals from *the same timebase*; absolute time or integer frame numbers only. Reject ad-hoc browser-time or random real-time effects.

## Shot execution and motion

- Choose source truth for every shot: recorded footage, licensed stock, authored 2D graphics, authored 3D scene, or explicitly labeled synthetic image. A plausible human scene does not emerge from a motion title generator alone.
- For 2D typography/UI/logo: stage anticipation, movement, settle and hold for reading; keep text inside action-safe zones. Prefer deliberately timed match cuts, L/J cuts, foreground passes and repeatable depth cues to generic crossfades.
- For tracked overlays, use measured feature correspondences, planar homographies or geometric camera poses. Write reprojection error per frame; reject drift and add manual keyframe locks. Track from actual video, not a pan of a static picture masquerading as camera tracking.
- For 3D: define meters, camera sensor/FOV and animation transforms, real shadow/collision/occlusion layers, reflections, motion blur and rendering budget. Audit geometry interaction in scene previews. Never claim physically accurate simulation without tests.
- For characters: define each pose and key expressions, lips/phonemes/eye direction, foot-contact constraints and speech timing; compare to adjacent frames for consistency. Use consented actors, authored animation or explicitly approved AI media.
- For long form: maintain chapter and shot IDs, run scoped previews, build 30-90 second encoded segments, test boundary transitions and mix full continuous audio. Preserve a single consistent codec, frame rate, colorspace and loudness target across segments.

## Implement in this repository

1. Validate scene JSON with `python studio/engine/render.py --validate path/to/film.json`. The built-in engine is for deterministic procedural/graphic layers and simple audio; it is **not** a photorealistic character or ray-tracing engine.
2. Render a 3-6 second proof using `python studio/engine/render.py film.json proof.mp4`, then inspect the first, middle, and last frames of every shot. Rejected proof blocks long-form export.
3. Mix approved source stems using `python studio/engine/audio_mix.py --voice ... --music ... --output ... --duration ...`. Check narration against SFX, stereo mapping, clipping/true-peak and integrated loudness. Sound quality needs human audition, not just a LUFS number.
4. Run `studio/engine/production_audit.py` and full FFprobe/creative QA. Do not claim cinematic quality purely because FFmpeg returned exit 0.
5. Keep the input data, authored code, licenses, actual shot list, frame checks, audio masters, failures and versioned exports reproducible.

## QA acceptance

- Every storyboard beat exists in the edit, with correct spelling, logo and framing.
- Cuts and action obey motivated screen direction; faces and props do not morph between shots without intentional transformations.
- Camera/subject movement is perceptible and physically or geometrically justified.
- Captions are synchronized and legible, with no zero-duration or overlapping cue errors.
- Music/SFX do not mask dialogue; audio waveform/true peak/tempo are audited.
- Separate **tech pass**, **rights pass** and **creative pass**. An original-skill pass does not establish source #318 recovery.

## Free-first & security

Use local code, FFmpeg, standard Python packages and public/licensed sources. No credit-card prompts, automatic purchases, unsafe unsigned model checkpoints, credential harvesting, or secrets in public Git. Protect client data separately from this public repository. If realism needs external assets/GPU compute, report the actual gap rather than inventing a render.

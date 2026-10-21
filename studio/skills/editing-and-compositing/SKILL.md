---
name: editing-and-compositing
description: Trim and combine supplied video, images and B-roll into clean edits using local FFmpeg filters and deterministic composition.
---


# Editing and Compositing Specialist
Start with inventory: container, resolution, fps, frame rates, aspect, duration, audio tracks, orientation, licensing, owner. Probe with `ffprobe -v error -show_format -show_streams -of json INPUT`.
- Standardize timebase and dimensions before concatenation. Use FFmpeg trim, scale, crop/pad, overlay, xfade/acrossfade, subtitles, color correction and audio normalization. Quote paths safely in subprocess argument lists; never shell-evaluate user strings.
- Do not crop meaningful subject matter or stretch video. Provide a shot-by-shot edit decision list with source in/out and target timeline time.
- Edit source files non-destructively and keep original. Avoid removing watermarks, copyright notices, or provenance information without proper rights.
- Follow new input files when needed, not invented footage. Render to fresh file and inspect final end-to-end transitions and audio continuity.

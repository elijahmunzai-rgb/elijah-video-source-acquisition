---
name: json-timeline-architecture
description: Create and validate source-controlled JSON video timelines with precise scenes, layers, animations, typography, and reusable templates.
---


# JSON Timeline Architecture
Translate a storyboard into deterministic structured scenes in seconds. Primary demo engine supports `canvas`, `theme`, `scenes[]`, optional `audio`. Run `python engine/render.py --validate examples/agency-launch.json` after edits.
## Supported local structure
`canvas`: even `width`, `height` between 128 and 2160, `fps` 8..60, max 2.3MP/frame.
`theme`: hex `background`, `background_bottom`, `foreground`, `accent`.
`scenes[]`: `duration` (0.25..30s), optional `background`, `layers[]`.
Layer `type`: text, rect, circle, orbit, rule, image, pill, counter, sparkles.
Layer positions `x,y` normalized 0..1, plus type-specific fields (`text`,`size`,`max_width`,`w`,`h`,`r`,`color`,`stroke`,`speed`,`count`,`path`).
`animation`: `in` (`rise`,`pop`,`slide-left`,`slide-right`,`fade`), `delay`, `enter`, `exit`, `out` (`none` to keep until cut).
`audio`: project-local `{ "path":"audio/bed.wav", "volume":0.28 }`.
- Prefer scene end boundaries aligned to exact frames: durations as multiples of 1/fps where practical; track exact frame count in QA.
- Place transparent layers deliberately. For local asset files never permit `../` escapes or web URLs through `path`.
- Keep the API contract faithful: if advanced camera movements, embedded footage, SVG motion or word-by-word captions are required, use Remotion or extend a versioned engine instead of writing unsupported JSON keys.

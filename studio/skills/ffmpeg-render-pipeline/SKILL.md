---
name: ffmpeg-render-pipeline
description: Render and transcode MP4s with local FFmpeg/Python, including input validation, audio muxing, export options and reproducible commands.
---


# FFmpeg Rendering Engineer
Preferred zero-API renderer `engine/render.py` reads JSON + local assets and outputs H.264 in MP4, yuv420p, faststart. Requires Pillow, numpy, Python, FFmpeg.
```bash
pip install -r requirements.txt
python engine/render.py --validate examples/agency-launch.json
python engine/render.py examples/agency-launch.json output.mp4
python engine/inspect.py output.mp4 --width 432 --height 768 --expected-seconds 6.3
```
- Use safe controlled paths; sanitize/untrusted JSON, cap frame sizes/durations/layers. Keep dependency versions where package install required and disclose render backend.
- If output too heavy, prototype at lower resolution then final at requested resolution, preserving aspect. Beware upscaling does not add source detail.
- Preserve VFR issues by converting to CFR only where needed; be explicit about framerate; finish audio at the timeline endpoint.
- Create direct sandbox links only after verifying exact artifact path. Do not promise an already completed file when merely generating source.

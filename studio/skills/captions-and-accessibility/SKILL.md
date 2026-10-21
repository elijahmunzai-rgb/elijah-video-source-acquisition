---
name: captions-and-accessibility
description: Create readable, synchronized subtitles and safe-area checks for social and presentation video.
---


# Captions, Localization & Accessibility
Use verified transcript/voiceover timing, not guesses disguised as timestamps. For silent motion graphics, on-screen copy does not automatically equal dialogue captions.
- Caption rules: 1-2 short lines; legible high contrast, background treatment or stroke when busy, speaker labeling if necessary; avoid covering faces, logos, charts or buttons.
- Produce UTF-8 `.srt` or `.vtt`; keep captions source-controlled, test timing against waveform/ASR alignment as available. Mark machine-derived timestamps as estimates pending human QA.
- Check 9:16 title/CTA inside platform-safe center regions, not tight to bottom and top UI areas. Account for reduced motion, flashing and photosensitivity; avoid strobing above safety guidelines.
- Localize meaning, numbers, units and RTL rendering with actual font support and verified glyphs. Never assert glyph correctness without frame inspection.

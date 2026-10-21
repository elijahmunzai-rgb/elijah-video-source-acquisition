---
name: video-quality-control
description: Validate final film creative quality, actual sound, source footage, frame readability and technical properties
---

# Video Quality Control

Two independent gates: technical (playback/codec/resolution/bitrate/frames/audio/loudness/true peak) and creative (story, shot variety, actual visual substance, audio quality, brand, originality). A valid MP4 does not pass creative QA. Check `engine/production_audit.py FILE --voice-required` and inspect rendered frames at each scene and boundary. Test all words at mobile scale and CTA holds. A music-only audio stream doesn't prove a professional mix or VO. Confirm no false client screens, claims, logos or fake avatar lip-sync.

Score: story, cinematography, source image quality, typography, soundtrack/voice, originality/brand, each 0-5. Require all >=4 to label premium ad approved. Record FAIL honestly when user rejects a version. Do not label it final high quality unless actually reviewed, including start, middle and end listening.

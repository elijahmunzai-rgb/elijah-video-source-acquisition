---
name: audio-and-sound-design
description: Supervise narrative sound, professionally mix actual music, voice and effects and verify loudness and dynamics
---

# Audio And Sound Design

Use real or correctly licensed soundtrack/recorded instruments/performances, not a series of sine-wave beeps disguised as production music. Build an audio cue sheet for each shot; choose track emotional contour, sound effects caused by on-screen events, dynamic rises/holds and an ending resolution.

Keep voice, music, effects and ambience as separate stems. The voice is intelligible and foregrounded; music ducked beneath voice with sidechain; dialog high-pass/compression/de-ess where appropriate. `engine/audio_mix.py --voice voice.wav --music music.wav --effects fx.wav --duration 30 --output master.wav` is the production mixer; it does not create songs or voice. Target social ad roughly -16 LUFS integrated and true peak below -1.5 dBTP; listen as well as meter. Basic synthesized bed may be an animatic only. Never claim voiceover when missing, or clone identity without permission.

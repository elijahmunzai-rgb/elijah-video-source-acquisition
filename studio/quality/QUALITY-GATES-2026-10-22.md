# Film Studio quality-recovery review (22 October 2026)

## Original failed video and why
Uploaded preview was a six-second 640x360, 24fps, 63KB H264 MP4 without audio. It contained three mostly-static text cards, a small orbit, and no actual story-specific footage, actors, camera coverage or sound design. The former test proved basic encoding, not cinematic quality. Eight "workers" are deterministic planning stages, not eight independent reasoning/video-generation models.

## Implemented improvement
- Renderer: studio/agents/premium_preview.py (public and open code).
- Genuine 1920x1080 landscape, 24fps, H264 High/CRF17, original AAC synthesized ambience.
- Continuously animated perspective terrain, kinetic typography, moving ring sculpture, changing compositions and brand/brief titles.
- Demo renderer uses only CPU, original graphics and sound; no stock footage or paid inference.
- True exported canvas and renderer recorded in the motion-preview manifest; human visual-review flag added to QA.
- Automated quality gates: dimensions 1920x1080, actual H264 + AAC tracks, 6 seconds, >750KB, bitrate >=850Kbps, actual within-scene and across-scene frame movement, no confidential demo materials, no auto publishing.
- Verified success in GitHub Actions run 39721852396: actual 1920x1080, H264 video ~6.94Mbps, AAC, duration 6.000 seconds, file 5,292,745 bytes. This replaces old 360p/63KB silent template.
- Tested code promoted to studio-operator-phase2-20261022 beta branch by guarded fast-forward, preserving existing healthy Hostinger app and main branch. No Hostinger ZIP required to list future public GitHub demo runs.

## Honest limitations and next milestones
The upgraded output is still a premium-styled motion-graphics demo, NOT a complete cinematic film or photoreal prompt-to-video renderer. To reach commercial quality, implement creative story generation that drives individual shots; consented/licensed imagery and real footage or acceptable 3D assets; real scene continuity, consistent subjects, qualified sound design and mix, master color/codec QC, human review, and private client isolation. Text-to-photoreal-video inference ordinarily requires separately validated GPU/model licenses and possibly cost, not unlimited free CPU runners or basic Hostinger web app. A planning duration of 15 to 600 seconds does not mean the preview is a film of that duration.

## Safety
Public GitHub Actions takes PUBLIC non-confidential demo material only. No client footage, private prompts, tokens or sensitive assets. Automatic film publication remains disabled. Existing IO Agency website, CRM, DNS, and other apps are out of scope.

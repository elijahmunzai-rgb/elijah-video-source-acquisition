# Film Studio real-source-footage cinematic proof, V1 (22 October 2026)

**Status: RENDERED and independently technically QA PASSED; USER CREATIVE APPROVAL PENDING.** Do not represent this as a professional final, IO Agency employee endorsement, or a complete 30s agency commercial.

## Completed in this real implementation

- Feature-only branch: `film-real-footage-hook-v1-20261022`, forked from recovered original 318-source master plan.
- **Media**: two independently sourced recorded call-center actors in 1920x1080 H264 Mixkit video clips under the Stock Video **Free** License. In the public concept teaser, these people are **illustrative stock actors**, not actual IO Agency staff. Specific source and rights terms:
  - Clip 4610: https://mixkit.co/free-stock-video/woman-and-man-working-at-a-call-center-4610/
  - Clip 4603: https://mixkit.co/free-stock-video/a-pair-of-employees-working-in-a-call-center-4603/
  - Free video license: https://mixkit.co/license/modal/videoFree/
  - `SOURCE_AND_LICENSE_LEDGER.json` inside artifact records both URLs, metadata and real downloaded SHA256 digests. Do not automatically assume other Mixkit clips are commercially licensed; some have restricted terms.
- **Actual editing**: a two-camera-angle, six-second footage-led scene with editorial cut/crossfade, very restrained graphical lower thirds and genuine brand copy without made-up performance claims; no graphical UI mockups, no AI-generated synthetic actor pretended to be real.
- **Audio**: synthesized ambient royalty-free/fully original 48kHz stereo concept score and scene swells, normalized for preview. It is NOT professional human-recorded narration and has not passed human sound-design review. A six-second opener can work without VO, but the final agency spot likely needs VO and dynamic film soundtrack.
- **Render**: actual 1920x1080, 24fps, H.264 + AAC, exactly 6 seconds, approximately 4.46 MB MP4, built entirely on GitHub Actions public CPU. No paid APIs, GPU, subscription, or Hostinger machine changes.
- **CI**: first full source acquisition and render [39727882259](https://github.com/elijahmunzai-rgb/elijah-video-source-acquisition/actions/runs/39727882259) succeeded. Strengthened CI includes visual frame motion and freeze test and re-ran successfully at [39728310182](https://github.com/elijahmunzai-rgb/elijah-video-source-acquisition/actions/runs/39728310182), with artifact `REAL-FOOTAGE-6S-FILM-STUDIO-CREATIVE-REVIEW` ID `12403264066`.
- **Motion QA result**: `technical_pass:true`, `faults:[]`, 18 decoded source-based preview frames at 3fps, median RGB-frame difference **14.82**, two original media IDs. Fails closed for missing source provenance, tiny or lower-resolution video, absent audio or frozen footage. Full human viewing/listening remains explicitly required.
- **Creative observation from four extracted review frames**: two discernible angles of the same two office actors, legible sparse typography, but generic stock aesthetic and limited distinctive cinematography. No actual agency staff, genuine branded props, acting direction, natural dialogue or customer outcome. Sound is minimal ambient pad, measured roughly -15.3 LUFS but with limited LRA. This is a draft to compare with earlier static graphics, not a 4/5 creative approval.
- **No private client source files were uploaded into this public repository**. Original stock asset downloads happen on ephemeral runner and are not included in output artifact. GitHub artifact contains derivative MP4, stills, rights ledger and QA reports.
- **Live** `https://video-production.inboundoutbound.io` remains on its existing healthy beta pipeline and does NOT receive this unapproved hook. This quality-test branch has no automatic publication/Hostinger deployment.

## Remaining before claiming completed agency commercial

1. User creative acceptance of this first **3–6 second** proof or detailed direction for improvement. Needs particularly more original concept, VO and dynamic sound.
2. Confirm official transparent IO Agency logo / footage consent if required; don't invent paid customer results or filmed agency employees.
3. Expand from two stock scenes to an original **30-second vertical 9:16 story** with approved rights-cleared media, real narration/mix, shot-to-shot story advancement and human creative QA. Then build separately authored 2m and 10m targets; **do not loop** the 30s reel as a substitute.
4. Evaluate and integrate relevant *licensed, safe, free* resources out of the frozen 318-source catalog. 318 source metadata checks ≠ 318 fully installed engines. Dan's consented US 16GB GPU is LAST resort and was not accessed.
5. Keep final client assets out of public source repository. Any public video release requires explicit approval.

## Reproduce on allowed GitHub CPU runner

Run `.github/workflows/film-real-footage-proof.yml` on branch `film-real-footage-hook-v1-20261022`. It downloads *only* the two exact Free-License 1080p Mixkit video URLs, verifies full-resolution video, runs `render_hook.py`, probes exported MP4, enforces `quality_check.py`, and publishes review artifacts. The current live Hostinger UI is unaffected.

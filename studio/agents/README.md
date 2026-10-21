# Elijah Film Studio — Eight Free CPU Agent Workers

This is a **working deterministic multi-agent workflow**, not a hosted model with independent human-like reasoning. No paid AI API, GPU or language-model weights are required for the default agents.

## Roles
1. Director — allocates unique shots and camera movements at the requested 15/30/60/120/600 second planning horizon.
2. Scriptwriter — prepares beat-level writing prompts; invented dialogue isn't marked approved.
3. Storyboard — exports every shot as a scheduled planning record and a human-readable sheet.
4. Asset Rights — blocks confidential/unlicensed source material and stops auto-publishing.
5. Camera/VFX — camera moves and source tracking requirements, without pretending actual camera calibration.
6. Motion — original six-second graphic video proof rendered with CPU using the existing Python engine.
7. Audio — separate stem/rights/narration plan; no unauthorized cloning.
8. QA/Delivery — checks duration/IDs/rights and leaves final publication blocked.

Run from GitHub **Actions → Free CPU Film Studio - Eight Agent Team → Run workflow**. Provide only PUBLIC demo title/goal, planned film duration, and aspect. Download its artifact for the storyboard, eight JSON handoffs, QA and actual six-second H264 video.

The 120/600-second storyboards are NOT 2-minute/10-minute completed movies. The six-second proof is original title graphics, NOT photoreal actor synthesis.

## Resource architecture
- Hostinger Web/Cloud UI (optional future work): light client-side dashboard for briefs/status/preview links. Don't assume VPS or authorize a purchase.
- GitHub Actions: on-demand disposable free public CPU runner, constrained by GitHub policy and artifact limits. No infinite 24/7 agent.
- Film repository: signed/reviewed code, CPU Blender/Remotion/OpenCV/FFmpeg render modules, public demo only.
- Client jobs: NOT run via the public repo (workflow inputs/artifacts/logs are publicly visible). Use isolated private workflows/workers with approved secure storage before accepting confidential footage. No private credentials in dashboard JavaScript.

## Optional real-language-model brain
The system has **eight rule-driven agents** already; real open-ended writing/reasoning would need (a) a user-provided AI service with permitted access, or (b) a small CPU inference engine and pretrained model weights stored outside Git, such as an openly licensed quantized GGUF model with llama.cpp. This is optional and should be separately audited for license, safety, CPU cost, quality and reproducibility. Do not assume GitHub Models API exists: it was retired July 2026.

## Expansion roadmap
Public demo storyboard and 6s proof (implemented) → shot asset intake and user rights verification → linked CPU 3D/avatar worker → asset overlay/compositing → discrete audio mix → segmented sequence rendering → technical QC, visible creative review → manually approved delivery. Agent roles should report actual work done, not mark unfinished film tasks as complete.

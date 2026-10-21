---
name: original-source-fidelity-and-full-acquisition
description: Download real tracked upstream source, nested submodules, Git LFS and immutable provenance; preserve exact code, never substitute summaries for missing sources.
---
# Original source fidelity and full acquisition

Target exactly 318 distinct upstream repositories listed by `data/skills.json` at `zhuyansen/awesome-claude-video-skills` commit `ffdf99cbc7879f611abba186e933695904cd638f` (2026-10-19 snapshot).

## Source vs adaptation

A source repository is not itself a video-production skill. Do not rename a stub or README as "installed skills". Preserve upstream source trees exactly with file-level SHA-256 hashes, source repository URL, immutable `HEAD` commit and tree SHA. Preserve licenses, assets, examples, tests, any nested submodules, and LFS files (when accessible). Never replace unavailable projects with homemade imitations while describing them as original.

## Acquisition

- For first-party original sources use `python engine/source_import_full_318.py --output verified-video-sources` on a machine with outbound internet, `git`, and `git-lfs` installed. No upstream code is executed during acquisition.
- For environments with limited memory or time, run 10 indexed shards; reassemble all results. Do not certify the 318 total until 318 unique success records and 318 source inventories have been checked.
- Run code only after security and license review; licenses can restrict redistribution and hosted commercial deployment.
- Capture failed repos by exact name and reason. Try authorized official alternate releases, archival source commits, and missing-access remediation. Never make a failed source appear successful.

## Integration and creative production

Identify which upstream repositories contain real SKILL.md, renderers, template code, scripts, dependencies and supplementary resources. Adopt licensed code verbatim *only* when requested and justified, maintaining license notices. Otherwise implement original code and check its functionality against source-level tests. Cinematic filmmaking quality must still be validated by practical camera, lighting, audio, motion continuity, character and scene render tests. Source acquisition is not equivalent to mastering or successfully rendering video.

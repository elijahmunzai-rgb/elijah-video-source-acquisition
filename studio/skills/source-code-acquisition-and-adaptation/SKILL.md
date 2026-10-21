---
name: source-code-acquisition-and-adaptation
description: Read GitHub sources directly; download and validate the original 318 video-skill repositories when code reuse is needed, with license checks, import provenance and code-first adaptation.
---
# Source Code Acquisition and Adaptation
The frozen video-skill collection comprises exactly 318 entries at zhuyansen/awesome-claude-video-skills, October 19 2026 commit ffdf99cbc7879f611abba186e933695904cd638f. Its following day's index contains 323, so never use live count as if it were the original 318.
## Direct inspection first
Read source files using the connected GitHub repository/file connector. A full clone is not needed to understand concepts or write original camera, 3D, VFX, screenplay, audio and editing code. To reuse upstream code or run its tests, obtain the needed files, commit identity, dependencies, licenses and test suite. Do not copy license-restricted code blindly.
## Bulk acquisition when explicitly requested
Run `python engine/source_import_318.py --output ./studio-sources` on an internet-enabled computer/runner. The tool downloads, checksums, audits ZIP integrity, and reports every repository. It does not execute downloaded code or claim installation. If any repository fails, retry alternate authorized sources and keep the failure visible; never change 318 expected to a smaller number. `GITHUB_TOKEN` can improve rate limits for eligible requests. User's other GitHub repositories must not be repurposed as archives.
## Validation for integration
Per project record: repo URL, commit or archive hash, verified file count, original SKILL.md count, license, security triage, required dependencies, actual renderer tested, status, and source-to-adaptation mapping. A working local coded alternative is distinct from an upstream product copied or fully deployed. Require cinematic creative QA in addition to technical render inspection.

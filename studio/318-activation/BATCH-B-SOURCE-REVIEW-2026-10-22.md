# 318-source Batch B: actual inspected upstream dependencies and runtime eligibility
Date: 22 Oct 2026 (Pakistan). **Read-only code/metadata inspection**, followed by a separate GitHub free CPU isolation test for eligible subsets. These projects are part of the frozen all-318 index. No guarantee a README claim is a proven working production feature.

## Five source-level candidates

1. **FavioVazquez/showtime**: original pinned checkout `2efdb115bec3c8024b766dd93044619cd7ee00f7`; upstream GitHub MIT license. Repository has ~1,383 tracked blobs, a stdlib Python launcher, Node/Chromium production features, and its own Python unit tests; full installation typically downloads ~0.5–0.75GB and uses ~1.4–1.8GB disk. The initial zero-cost test **does NOT install a large model, use external voice APIs, download full browser assets, or claim MP4**. It runs source tests `test_figure_examples.py --fast`, `test_figure_computer.py --fast` and the real offline `showtime new diagram` generator. If passing, count only the *generator* as functional; to certify professional 30s video later, use browser/FFmpeg and source footage QA.

2. **digitalsamba/claude-code-video-toolkit**: pinned `da3f474c1230d161be1384ef97aec27f73b11636`, upstream MIT. The package's normal `pyproject.toml` core dependency list includes `elevenlabs`, `boto3` and `requests`, optional Modal/GPU/Whisper etc, so full `uv sync --all-extras` would conflict with free-first simplicity. **Only the reviewed standalone stdlib-based `tools/cutdown.py`, `tools/pacing.py` and `tools/win_encoding.py` modules** are candidates here. Batch B executes the upstream script to make a real 1080x1920 9:16 stock-human video using FFmpeg and confirms actual H264 output; additionally tests audio WPM detection and offline pitch-preserving tempo correction using a generated synthetic tone. No provider calls or actual celebrity/voice cloning. This is the strongest near-term **real production integration candidate**.

3. **cartesiancs/cartcut**: pinned candidate `d9cbf5fe17ebd395275ccbf43be527487db9be68`, upstream MIT. Full Git tree ~2,382 blobs, `package.json` specifies Electron and extensive native/UI/browser/test dependencies (`electron`, `@imgly/background-removal-node`, `@playwright/test`, `webpack`, `vitest`). No always-on Headless Hostinger process. Full `npm install`/Electron build should be isolated in a bounded GUI-capable test job later, not blindly included in batch B.

4. **FireRedTeam/FireRed-OpenStoryline**: pinned candidate `c9e945215586f45c12a61c1951ee9a8e9c43a027`, upstream Apache-2.0. `requirements.txt` includes `langchain_openai`, `openai`, `sentence-transformers`, `torchaudio`, `funasr`, `transnetv2_pytorch`, `librosa`. Significant CPU/disk/model constraints, cloud API risk and GPU-accelerated features. **Full AI inference unapproved for this free-only phase**. Future test only audited deterministic edit modules in a bounded, isolated run, with no provider secrets or private footage. Do not claim operational until a genuine offline output exists.

5. **iart-ai/motion-skills**: pinned candidate `bb5a3ce666110855a3437de2f70e9968c408e005`, upstream MIT. The top-level repository is an **index pointing to 18 separate skill packs** (newer README lists 55 skills). It is not one long-running video app. Choose specific actual child project source/rights/runtime when needed; do not count its linked sub-repos as already installed or add them to the frozen 318 without explicit provenance. Good as production direction references and subject-specific advice, not an independent runtime executable.

## Security, quality and resources

- Git clone URL and SHA exact; no private GitHub secret, no paid provider keys.
- GitHub ephemeral public CPU runner only; **no changes to live Hostinger, no Daniel GPU, no app/billing upgrade**.
- Mixkit public illustrative clip `4610` individually listed under Free License for the DigitalSamba vertical test; **actors are stock, NOT agency employees or endorsers**.
- SHA is not a license grant: upstream notices/full source licensing require review before any redistribution to final client projects.
- Module test SUCCESS is different from `Installed`, `Integrated`, and `Cinema Approved`. The 318 registry will only advance with linked actual CI outputs, and real commercial creative quality still needs human review.
- Batch B workflow: `.github/workflows/film-318-operational-batch-b.yml`. Await actual GitHub run conclusion before reporting passed.

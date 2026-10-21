# Source research and reproducibility
Research checked 2026-10-20.
- The directory `https://github.com/zhuyansen/awesome-claude-video-skills` collects 318 project references at the time of review, states 16 were tested, and describes its *directory text* as CC0. Do not assume its outgoing projects are all CC0 or safe to execute. This plugin is a separate original implementation, **not** the entire 318-repo collection.
- Their short-list: `https://github.com/vincentsch/explainroo` for quick narrated explainers, `https://github.com/feitangyuan/onetake` for continuous narrative, `https://github.com/remotion-dev/skills` for programmatic video. Results are reports from the list maintainer, not independently verified benchmarks here.
- Official Remotion agent guidelines: `https://github.com/remotion-dev/skills`. Use with current docs/version when moving to React-based animation.
- Official FFmpeg documentation: `https://ffmpeg.org/documentation.html` (video encoding, codecs, filtering) and FFprobe `https://ffmpeg.org/ffprobe.html`.
- Avoid direct blind installation of arbitrary third-party skills; read SKILL.md and install script, verify license, dependencies, and filesystem/network behavior before running.
- This plugin bundles original Python rendering and sound synthesizer code. No external video generation APIs, media assets, samples, fonts, or downloaded skills are bundled.

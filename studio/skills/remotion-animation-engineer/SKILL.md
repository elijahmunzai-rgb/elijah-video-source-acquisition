---
name: remotion-animation-engineer
description: Implement advanced React/TypeScript video compositions with Remotion frame-driven motion, sequencing and renders when dependencies are installed.
---


# Remotion / React Animation Engineer
Use when the creative needs complex layered motion, compositing, vector paths, CSS transforms, charts, 3D-like depth or fine timeline control beyond the bundled Python renderer.
- Check local `node`, `npm`, project packages and `npx remotion --version` before relying on Remotion. Local installation from npm requires network and appropriate package licensing. Do not claim available merely because Node exists.
- Use `<Composition>` with `durationInFrames`,`fps`,`width`,`height`; inside compositions use `useCurrentFrame()`, `interpolate()` and `spring()` with deterministic frame-based transforms.
- Encapsulate components by scene, animated text, backgrounds, lower-thirds, chart components, CTA. Set time-based animation relative to each sequence.
- Use safe-area margins, contrast, performant assets and `prefers-reduced-motion`-sensible controls for web previews. Avoid animation via nondeterministic timers, external APIs, unseeded randomness.
- Test frames at segment entry, middle, and exit and run `npx remotion render` only when runtime exists and render is requested.
- Official skill source: https://github.com/remotion-dev/skills ; review official version-specific guidance rather than copying third-party skills indiscriminately.

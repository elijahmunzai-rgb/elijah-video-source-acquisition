# Elijah Film Studio — Production Command Desk (phase-2 beta)

> **Branch:** `studio-operator-phase2-20261022`. This branch is deliberately isolated from the **live, working read-only** `video-production.inboundoutbound.io` staging release and from the repository default `main` branch. New UI is **not live** until separately uploaded and smoke-verified.

## What works

- Public demo brief composer: title, creative goal, planning horizon (15/30/60/120/600s) and aspect.
- Public GitHub Actions job discovery through `/api/jobs`, including actual status, workflow steps and artifact metadata through `/api/jobs/:id`.
- Secure server-controlled optional workflow dispatch through `POST /api/jobs`, targeting a single allowlisted workflow `film-studio-agents.yml` on the **phase-2 beta branch**. No user-supplied repository, branch or workflow name is accepted. Strict public-only input constraints.
- GitHub workflow has 8 **deterministic**, tested specialist roles. Render currently produces an **actual six-second procedural H264 motion graphics MP4**, plus storyboard, planning JSON and QA. The selected 15–600s value is the **planning horizon**, not a promise of a finished film. No independent AI reasoning agents or photoreal actors.
- Signed-in operator preview: `GET /api/jobs/:id/preview` securely retrieves the specific GitHub artifact ZIP, rejects untrusted redirects and large/invalid archives, extracts only `preview-6s.mp4`, serves bounded MP4 with HTTP Range support. The raw GitHub token is never sent to the browser. Users may also open the run's GitHub artifact page to download the full ZIP.
- Manual fallback GitHub Actions link available without any server-side secrets.
- No database, client uploads, paid model usage or Hostinger-side rendering.

## Hostinger deployment package

1. GitHub Actions workflow `.github/workflows/film-hostinger-upload-package.yml` runs tests and creates **`hostinger-staging-upload-ready-zip` artifact**, containing an inner `Elijah-Film-Studio-Hostinger-Staging.zip`.
2. Upload **the inner ZIP**, not its outer GitHub Actions artifact wrapper, to the **existing, separate** Hostinger `video-production.inboundoutbound.io` Web App → Deployments → Redeploy → Upload new files.
3. Preserve **Other**, **Node.js 20.x**, root `./`, build command **None**, output directory blank, package manager **npm**, entry file **`server.mjs`**. Package includes `package.json`, `server.mjs`, `index.html`, `operator.mjs`, `media.mjs`, all at ZIP root.
4. After Hostinger marks new deployment **Completed**, test homepage, `/healthz` (200), `/api/session` (200, dispatch initially locked), `/api/jobs` (200 or a graceful upstream 503). Verify existing IO Agency websites are unchanged and no billing or VPS purchase occurred.
5. **Never** overwrite WordPress production files or use a global process-kill/hosting restart. Do not claim a push to GitHub auto-deploys Hostinger; this is manual ZIP release.

## Explicit credentials setup for optional one-click dashboard launches

By default, the UI is **read-only and locked**, intentionally. To enable *authenticated public demo* dispatch:

- Use Hostinger's **site-specific Environment variables** section (NOT GitHub repo source or chat messages) to set:
  - `STUDIO_ADMIN_PASSWORD`: a strong unique 16+ character administrator password.
  - `GITHUB_STUDIO_TOKEN`: a scoped GitHub fine-grained personal access token for **only** repository `elijahmunzai-rgb/elijah-video-source-acquisition`, with **Actions: Read and write** and **Metadata: Read**. Avoid classic broad-scope tokens; set short expiry and rotate.
- Apply the environment settings/restart **only this web app**. Keep tokens out of GitHub public code, client-side JS, logs and screenshots. Never share the token in ChatGPT.
- Sign in from the dashboard. A secure `HttpOnly; SameSite=Strict; Secure` session cookie is used; POST APIs require matching `Origin` and `X-Studio-Action: 1` header, and authorization is checked server-side.
- Dispatch is restricted to fixed workflow/ref, allowlisted fields, public-demo attestation, **at most 2 launches/hour and 6/day in a single process**. This cap is in memory, resets on server restart and does **not** provide hard spend controls across scaled replicas. GitHub workflow's 15-min timeout and no-publish policy remain.
- If neither secret is set, the homepage/jobs API still work; `/api/session` shows `login_enabled:false` and `dispatch_enabled:false`. Browser cannot dispatch or preview by guessing an API URL.
- The public GitHub repo and any public-demo inputs, workflow logs and artifacts are **public**. Do NOT enter actual client names, confidential briefs, private recordings, proprietary scripts, real customer data or unlicensed assets.
- A GitHub Actions workflow dispatch returns **HTTP 204 with no run ID**. Dashboard returns **202 accepted**, then recent workflow runs reveal actual execution; do not falsely show a fabricated run ID.

## Endpoints

| Route | Access | Function |
|---|---|---|
| `GET /healthz` | Public | Service health only |
| `GET /api/status` | Public | Recent GitHub workflow status (legacy control room) |
| `GET /api/session` | Public | Login/dispatch capability flags; no secret disclosure |
| `POST /api/session` | Origin + password + rate limit | Admin login, 8-hour in-memory session |
| `POST /api/logout` | Origin + action header | Session invalidation |
| `GET /api/jobs` | Public | Actual public workflow_dispatch runs for allowlisted workflow |
| `GET /api/jobs/:id` | Public | Workflow steps and artifact discovery |
| `POST /api/jobs` | Auth + Origin + CSRF header + quota + config | GitHub workflow dispatch |
| `GET /api/jobs/:id/preview` | Auth + config | Bounded ZIP→MP4 streaming; supports Range |

## Test

```bash
cd studio/control-room
npm test
PORT=3000 npm start
```

Do not configure real GitHub credentials in tests. Test suite injects fake credentials/fetch responses. GitHub Actions CI checks normal and Hostinger import-style Node startup, frontend script parsing, and package root structure.

## Later production requirements

To accept private footage, actual creative client briefs, invoicing or publishing: deploy private isolated runners/stores, durable auth and per-job quotas, stronger token rotation, server-side persistence, consent/release review, human approval gates, and background orchestration. **This release is not a finished commercial SaaS, unrestricted AI film director or full feature-film renderer.**

## Token-free public demo requests through GitHub (verified)

For approved public demo content, there is an additional server-independent workflow so a GitHub-authenticated project maintainer or connected GitHub agent can initiate renders **without placing a GitHub token on Hostinger**:

1. On branch `studio-operator-phase2-20261022`, create exactly one new JSON file per commit under `studio/demo-requests/`, for example `2026-10-22-my-demo.json`:
   ```json
   {
     "title": "STUDIO ONLINE",
     "goal": "Demonstrate original CPU film planning and a six-second H264 preview.",
     "duration": "30",
     "aspect": "landscape",
     "public_demo": true
   }
   ```
2. The owner-gated workflow `.github/workflows/film-demo-request-dispatch.yml` validates the newly added public JSON file, enforces the only-approved-actor restriction and uses GitHub Actions' **ephemeral repository-scoped GITHUB_TOKEN** (Actions write; Contents read) to dispatch the fixed `film-studio-agents.yml` workflow on the beta branch. No permanent token is distributed and no credential is used in Hostinger.
3. The render produces eight deterministic handoffs, storyboards, rights/QA checks, and a **real six-second MP4**, with artifacts retained under GitHub Actions retention policy. The dispatched `workflow_dispatch` run appears on the existing Hostinger dashboard's **Production Jobs** list, even though the dashboard's one-click launch form remains locked.

**Verified**: request file `studio/demo-requests/2026-10-22-studio-online.json` triggered dispatcher [run 39719286027](https://github.com/elijahmunzai-rgb/elijah-video-source-acquisition/actions/runs/39719286027) (success), which triggered public-demo render [run 39719295804](https://github.com/elijahmunzai-rgb/elijah-video-source-acquisition/actions/runs/39719295804) (success). The live Hostinger `/api/jobs` returned render run ID 39719295804 as completed/success; `/api/jobs/39719295804` returned actual successful step and downloadable artifact metadata, artifact ID 12399848890. MP4 independently probed as **H.264, 640×360, 6.000 seconds**.

**Security boundaries**: only a GitHub write-authorized owner can create the triggering Git commit; anyone can view public request JSON, logs, and demo artifacts, so never include private client content. The owner/branch/file validation is defense in depth, not a replacement for per-user identity or rate limits in a real paid SaaS. GitHub Actions remains subject to the platform's policies and compute quotas. No auto-publishing. For true one-click web launch, the Hostinger `STUDIO_ADMIN_PASSWORD` and `GITHUB_STUDIO_TOKEN` still need to be configured by the user in Hostinger's site-specific secrets UI.

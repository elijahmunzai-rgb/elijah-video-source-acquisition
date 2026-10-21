# Elijah Film Studio — Hostinger Control Room (staging)

A **zero-additional-cost, read-only Node.js dashboard prototype**, kept on a staging branch, not deployed to live Hostinger.

- Node 20+ standard library only, no npm dependencies, no external CDN or database.
- Fixed public GitHub repo status, recent workflow runs, eight worker roles and explicit demo-only gate.
- Server-side fetching with cache and timeout, strict output sanitization, secure response headers.
- **Cannot trigger a job, publish a film, accept confidential uploads or access private repos.** Those require a later authenticated server-side integration, explicit permissions, and deployment approval.
- Never store GitHub tokens, Hostinger secrets, media consent or client footage in this public repo or frontend.

## Test
\`\`\`
cd studio/control-room
npm test
PORT=3000 npm start
\`\`\`
Open http://localhost:3000. For development only; no Hostinger deployment has happened.

## Proposed release gates
1. Read-only dashboard and unit tests pass.
2. Isolate from production WordPress; deploy as a **separate Hostinger web app** under an approved film-specific domain.
3. Implement a secure backend worker dispatch with GitHub App or properly scoped server-only token, server-side authentication, anti-CSRF, rate limiting and a budget guard. Never put token in browser JS.
4. Keep public GitHub actions on **non-sensitive demos only**. Confidential customer workflows require private isolation.
5. Use persistent storage for final exports; GitHub Actions artifacts expire. Review Hostinger 50GB quota and 3GB plan RAM.
6. Human approval before publishing, no paid services or resource upgrade without authorization.

Existing Business Hostinger: 2 CPU cores, 3072 MB RAM, 50 GB disk; dashboard uses only lightweight server requests, **rendering remains off-host**.

import http from 'node:http';
import {readFile} from 'node:fs/promises';
import {createOperator} from './operator.mjs';

const REPO = 'elijahmunzai-rgb/elijah-video-source-acquisition';
const ACTIONS_URL = 'https://github.com/' + REPO + '/actions';
const API_URL = 'https://api.github.com/repos/' + REPO + '/actions/runs?per_page=12';
const html = await readFile(new URL('./index.html', import.meta.url), 'utf8');

function secure(res, type) {
  res.setHeader('Content-Type', type);
  res.setHeader('X-Content-Type-Options', 'nosniff');
  res.setHeader('Referrer-Policy', 'no-referrer');
  res.setHeader('Cache-Control', 'no-store');
  res.setHeader('X-Frame-Options', 'DENY');
  res.setHeader('Content-Security-Policy',
    "default-src 'none'; script-src 'unsafe-inline'; style-src 'unsafe-inline'; " +
    "connect-src 'self'; img-src 'self'; frame-ancestors 'none'; base-uri 'none'; form-action 'none'");
}
function json(res, code, data) {
  res.statusCode = code;
  secure(res, 'application/json; charset=utf-8');
  res.end(JSON.stringify(data));
}
function sanitizeRun(run) {
  return {
    id: Number(run.id),
    name: String(run.name || '').slice(0, 120),
    status: String(run.status || '').slice(0, 30),
    conclusion: run.conclusion == null ? null : String(run.conclusion).slice(0, 30),
    updated_at: String(run.updated_at || '').slice(0, 40),
    url: /^https:\/\/github\.com\/elijahmunzai-rgb\/elijah-video-source-acquisition\/actions\/runs\/[0-9]+$/.test(run.html_url || '')
      ? run.html_url : null
  };
}
export function createServer({fetcher = fetch, cacheMs = 60_000, operatorEnv = process.env, clock = Date.now} = {}) {
  const operator = createOperator({fetcher, env:operatorEnv, now:clock});
  let cached = null;
  let expires = 0;
  return http.createServer(async (req, res) => {
    const pathname = new URL(req.url || '/', 'http://localhost').pathname;
    if (await operator(req,res)) return;
    if (req.method !== 'GET' && req.method !== 'HEAD') {
      json(res, 405, {error:'Read-only prototype; no job creation, publication or billing'});
      return;
    }
    if (pathname === '/healthz') {
      json(res, 200, {ok:true, dashboard:'staging-read-only', rendering:'external-github-actions'});
      return;
    }
    if (pathname === '/' || pathname === '/index.html') {
      res.statusCode = 200;
      secure(res, 'text/html; charset=utf-8');
      res.end(req.method === 'HEAD' ? '' : html);
      return;
    }
    if (pathname === '/api/status') {
      if (cached && Date.now() < expires) {
        json(res, 200, {...cached, cache:'hit'});
        return;
      }
      try {
        const ctrl = new AbortController();
        const timer = setTimeout(() => ctrl.abort(), 8000);
        let upstream;
        try {
          upstream = await fetcher(API_URL, {
            signal:ctrl.signal,
            headers:{Accept:'application/vnd.github+json', 'User-Agent':'ElijahFilmStudioControlRoom/0.1'}
          });
        } finally {clearTimeout(timer);}
        if (!upstream.ok) throw new Error('upstream not available');
        const raw = await upstream.json();
        if (!Array.isArray(raw.workflow_runs)) throw new Error('invalid GitHub response');
        cached = {
          repository:REPO, repo_url:'https://github.com/' + REPO,
          actions_url:ACTIONS_URL,
          public_demo_only:true, can_dispatch:false, can_publish:false,
          updated_at:new Date().toISOString(),
          runs:raw.workflow_runs.slice(0, 10).map(sanitizeRun)
        };
        expires = Date.now()+cacheMs;
        json(res, 200, {...cached,cache:'miss'});
      } catch {
        json(res, 503, {
          error:'GitHub status temporarily unavailable',
          repository:REPO,
          actions_url:ACTIONS_URL,
          can_dispatch:false,
          can_publish:false
        });
      }
      return;
    }
    json(res,404,{error:'Not found'});
  });
}
// Hostinger imports the configured entry module rather than invoking it as the CLI main.
// Start eagerly in hosting; skip auto-listen inside Node's native test runner.
if (!process.env.NODE_TEST_CONTEXT) {
  const port = Number(process.env.PORT || 3000);
  if (!Number.isInteger(port) || port < 1 || port > 65535) throw new Error('Invalid PORT');
  createServer().listen(port,'0.0.0.0',()=>console.log('Elijah Film Studio read-only dashboard listening on '+port));
}

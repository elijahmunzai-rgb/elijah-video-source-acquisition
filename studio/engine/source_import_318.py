#!/usr/bin/env python3
"""Safely archive all sources from the 318-repository video skill index.

No downloaded source code is executed. Archive bytes and provenance are recorded.
Use in a network-enabled runner. A 318-item inventory does not imply 318 successes.
"""
import argparse
import concurrent.futures
import hashlib
import json
import os
from pathlib import Path
import random
import re
import shutil
import subprocess
import tempfile
import threading
import time
import urllib.error
import urllib.request
import zipfile
from datetime import datetime, timezone

INDEX_REVISION = "ffdf99cbc7879f611abba186e933695904cd638f"  # verified 318 on 2026-10-19
INDEX_URL = f"https://raw.githubusercontent.com/zhuyansen/awesome-claude-video-skills/{INDEX_REVISION}/data/skills.json"
TARGET = 318
USERNAME_RE = re.compile(r"^[a-zA-Z0-9_.-]+/[a-zA-Z0-9_.-]+$")
LOCK = threading.Lock()


def get_bytes(url, timeout=90, tries=5, max_mb=None):
    headers = {"User-Agent": "ElijahVideoStudioSourceAuditor/1.0", "Accept": "application/octet-stream"}
    token = os.getenv("GITHUB_TOKEN")
    if token and (url.startswith("https://api.github.com/") or url.startswith("https://raw.githubusercontent.com/")):
        headers["Authorization"] = f"Bearer {token}"
    for i in range(tries):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=headers), timeout=timeout) as response:
                length = int(response.headers.get("Content-Length", 0))
                if max_mb and length > max_mb * 1024 * 1024:
                    raise ValueError(f"Archive larger than limit: {length} bytes")
                content = response.read((max_mb * 1024 * 1024 + 1) if max_mb else -1)
                if max_mb and len(content) > max_mb * 1024 * 1024:
                    raise ValueError("Downloaded archive exceeded max size")
                return content
        except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError, ConnectionError, OSError) as e:
            code = getattr(e, "code", None)
            if code in (400, 401, 403, 404, 410, 451) and code != 403:
                raise
            if i == tries - 1:
                raise
            delay = min(60, 2 ** i * 3 + random.random() * 2)
            time.sleep(delay)
    raise RuntimeError("Exhausted retries")


def normalized_repos(raw):
    skills = raw.get("skills")
    if not isinstance(skills, list):
        raise ValueError("Manifest must contain a 'skills' list")
    out = []
    seen = set()
    for i, skill in enumerate(skills):
        repo = skill.get("repo_full_name")
        if not isinstance(repo, str) or not USERNAME_RE.fullmatch(repo) or repo in seen:
            raise ValueError(f"Missing, duplicate, or invalid repo at index {i}: {repo!r}")
        seen.add(repo)
        out.append({"repo": repo, "kind": skill.get("kind"), "license_index": skill.get("license"), "source_path": skill.get("path")})
    return out


def load_manifest(manifest_path):
    if manifest_path:
        data = Path(manifest_path).read_bytes()
    else:
        data = get_bytes(INDEX_URL, timeout=30, tries=4)
    raw = json.loads(data)
    repos = normalized_repos(raw)
    if len(repos) != TARGET:
        raise ValueError(f"Refusing partial/mutated list: expected {TARGET}, got {len(repos)}. Use a frozen 318-item snapshot.")
    return raw, repos, hashlib.sha256(data).hexdigest()


def archive_audit(data, max_files=150_000):
    import io
    with zipfile.ZipFile(io.BytesIO(data)) as z:
        entries = z.infolist()
        if len(entries) > max_files:
            raise ValueError(f"Archive file count exceeds limit ({len(entries)})")
        for entry in entries:
            name = entry.filename.replace('\\', '/')
            if name.startswith('/') or '..' in name.split('/'):
                raise ValueError(f"Unsafe ZIP entry path: {name}")
        corrupt = z.testzip()
        if corrupt is not None:
            raise ValueError(f"Corrupt ZIP entry: {corrupt}")
        docs = [x.filename for x in entries if x.filename.lower().endswith(("/skill.md", "/readme.md", "/license", "/license.md", "/license.txt"))]
        scripts = [x.filename for x in entries if x.filename.lower().endswith((".py", ".js", ".ts", ".tsx", ".jsx", ".sh", ".bat", ".ps1"))]
        return {"file_count": len(entries), "skill_md_count": sum(x.lower().endswith('/skill.md') for x in docs), "script_count": len(scripts), "documents_sample": docs[:15]}


def download_one(item, output_dir, retries=5, max_mb=512):
    repo = item['repo']
    owner, name = repo.split('/')
    out = Path(output_dir) / 'archives' / owner / f'{name}.zip'
    out.parent.mkdir(parents=True, exist_ok=True)
    result = {**item, 'status': 'failed', 'source_url': f'https://github.com/{repo}', 'archive': str(out)}
    try:
        if out.is_file():
            payload = out.read_bytes()
            audit = archive_audit(payload)
            result.update(status='verified_existing', sha256=hashlib.sha256(payload).hexdigest(), byte_count=len(payload), audit=audit)
            return result
        # HEAD resolves to the repository default branch on GitHub's archive service.
        urls = [f'https://codeload.github.com/{repo}/zip/HEAD', f'https://github.com/{repo}/archive/HEAD.zip']
        errors = []
        for url in urls:
            try:
                payload = get_bytes(url, timeout=120, tries=retries, max_mb=max_mb)
                audit = archive_audit(payload)
                with tempfile.NamedTemporaryFile(prefix=name + '.', suffix='.part', dir=out.parent, delete=False) as f:
                    f.write(payload)
                    temp = f.name
                os.replace(temp, out)
                result.update(status='verified_downloaded', sha256=hashlib.sha256(payload).hexdigest(), byte_count=len(payload), audit=audit, resolved_download_url=url)
                return result
            except Exception as e:
                errors.append(f'{url}: {type(e).__name__}: {str(e)[:240]}')
        result['error'] = '; '.join(errors)
        return result
    except Exception as e:
        result['error'] = f'{type(e).__name__}: {str(e)[:300]}'
        return result


def main():
    p = argparse.ArgumentParser(description='Download, checksum and audit 318 video-project source archives, without executing them')
    p.add_argument('--manifest', help='Local data/skills.json snapshot. Without this, retrieve latest list')
    p.add_argument('--output', default='elijah-video-sources')
    p.add_argument('--workers', type=int, default=3)
    p.add_argument('--retries', type=int, default=4)
    p.add_argument('--max-repo-mb', type=int, default=512)
    p.add_argument('--dry-run', action='store_true')
    a = p.parse_args()
    raw, repos, msha = load_manifest(a.manifest)
    root = Path(a.output)
    root.mkdir(parents=True, exist_ok=True)
    (root/'manifest.snapshot.json').write_text(json.dumps(raw, ensure_ascii=False, indent=2), encoding='utf-8')
    (root/'repositories.json').write_text(json.dumps(repos, indent=2), encoding='utf-8')
    if a.dry_run:
        print(json.dumps({'count': len(repos), 'expected': TARGET, 'manifest_sha256': msha, 'categories': sorted({x['kind'] for x in repos})}, indent=2))
        return
    results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=max(1, min(a.workers, 8))) as executor:
        futures = [executor.submit(download_one, x, root, a.retries, a.max_repo_mb) for x in repos]
        for future in concurrent.futures.as_completed(futures):
            result = future.result()
            results.append(result)
            with LOCK:
                (root/'download-status.json').write_text(json.dumps(sorted(results, key=lambda x: x['repo']), indent=2), encoding='utf-8')
            print(f"{len(results):>3}/{TARGET} {result['status']:>18} {result['repo']}", flush=True)
    counts = {k: sum(r['status'] == k for r in results) for k in ('verified_downloaded', 'verified_existing', 'failed')}
    report = {'expected': TARGET, 'processed': len(results), 'manifest_sha256': msha, 'generated_utc': datetime.now(timezone.utc).isoformat(), 'counts': counts, 'all_archives_verified': counts['verified_downloaded'] + counts['verified_existing'] == TARGET, 'failures': [r['repo'] for r in results if r['status'] == 'failed']}
    (root/'summary.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
    print(json.dumps(report, indent=2))
    if not report['all_archives_verified']:
        raise SystemExit(2)

if __name__ == '__main__':
    main()

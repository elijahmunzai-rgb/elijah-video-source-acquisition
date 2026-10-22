#!/usr/bin/env python3
"""Opt-in, offline-first ComfyUI operator for a trusted Windows GPU workstation.

Only accepts an explicitly reviewed local workflow whose SHA-256 is pinned in
a local approved-workflows.json file. Never listens on a network port, never
executes shell, never connects to a remote host, never sees GitHub credentials.
This is not a background agent or a remote-access solution on its own.
"""
import argparse
import hashlib
import json
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

LOCAL_COMFY = "http://127.0.0.1:8188"
MAX_WORKFLOW = 2_000_000
MAX_OUTPUT = 1_000_000_000
ALLOWED_MEDIA = {"mp4", "webm", "mov", "png", "jpg", "jpeg", "wav", "flac"}
MAX_POLL_SECONDS = 3600

def workflow_bytes(path):
    raw = Path(path).read_bytes()
    if len(raw) > MAX_WORKFLOW or not raw:
        raise ValueError("Workflow file empty or exceeds 2MB")
    return raw

def validate_workflow(raw):
    parsed = json.loads(raw.decode("utf-8"))
    if not isinstance(parsed, dict) or not 1 <= len(parsed) <= 400:
        raise ValueError("Expected a non-empty ComfyUI API prompt JSON mapping")
    for node_id, node in parsed.items():
        if not str(node_id).isdigit() or not isinstance(node, dict):
            raise ValueError("Invalid ComfyUI node")
        if not isinstance(node.get("class_type"), str) or not isinstance(node.get("inputs"), dict):
            raise ValueError("ComfyUI API JSON requires class_type and inputs on every node")
    return parsed

def approved_workflow(path, policy_path):
    raw = workflow_bytes(path)
    parsed = validate_workflow(raw)
    policy = json.loads(Path(policy_path).read_text(encoding="utf8"))
    allowed = policy.get("approved_sha256", [])
    digest = hashlib.sha256(raw).hexdigest()
    if not isinstance(allowed, list) or digest not in allowed:
        raise PermissionError("Unapproved workflow; review all nodes and pin the SHA-256 locally first: " + digest)
    return parsed, digest

def api_json(method, path, payload=None, timeout=20):
    if not path.startswith("/") or path.startswith("//"):
        raise ValueError("Invalid local API path")
    data = json.dumps(payload).encode() if payload is not None else None
    request = urllib.request.Request(
        LOCAL_COMFY + path, data=data, method=method,
        headers={"Content-Type": "application/json", "Accept": "application/json"},
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        if response.status < 200 or response.status >= 300:
            raise RuntimeError("ComfyUI returned " + str(response.status))
        return json.loads(response.read(10_000_000).decode())

def safe_output_name(name):
    if not isinstance(name, str) or len(name) > 180:
        raise ValueError("Invalid media filename")
    if name.startswith(".") or name != Path(name).name or not re.fullmatch(r"[A-Za-z0-9_. -]+", name):
        raise ValueError("Unsafe output filename")
    if name.rsplit(".", 1)[-1].lower() not in ALLOWED_MEDIA:
        raise ValueError("Output media extension not approved")
    return name

def download_output(item, dest, job_id):
    filename = safe_output_name(item.get("filename"))
    subfolder = item.get("subfolder") or ""
    if not isinstance(subfolder, str) or len(subfolder) > 180 or not re.fullmatch(r"[A-Za-z0-9_/-]*", subfolder) or ".." in subfolder.split("/"):
        raise ValueError("Unsafe output subfolder")
    kind = item.get("type") or "output"
    if kind not in ("output", "temp"):
        raise ValueError("Unsupported ComfyUI output type")
    query = urllib.parse.urlencode({"filename": filename, "subfolder": subfolder, "type": kind})
    request = urllib.request.Request(LOCAL_COMFY + "/view?" + query)
    filename_out = f"{job_id[:12]}_{filename}"
    directory = Path(dest).resolve()
    directory.mkdir(parents=True, exist_ok=True)
    target = (directory / filename_out).resolve()
    if not target.is_relative_to(directory):
        raise ValueError("Output outside approved folder")
    with urllib.request.urlopen(request, timeout=45) as response, target.open("wb") as out:
        size = 0
        while True:
            block = response.read(1024 * 1024)
            if not block:
                break
            size += len(block)
            if size > MAX_OUTPUT:
                out.close()
                target.unlink(missing_ok=True)
                raise ValueError("Output over 1GB safety limit")
            out.write(block)
    return str(target), size

def run(args):
    workflow, digest = approved_workflow(args.workflow, args.approvals)
    if args.dry_run:
        print(json.dumps({"ok": True, "mode": "dry-run", "approved_sha256": digest,
                          "nodes": len(workflow), "external_network": False}, indent=2))
        return
    if args.submit is not True:
        raise ValueError("Use --submit explicitly to send an approved job to local ComfyUI")
    response = api_json("POST", "/prompt", {"prompt": workflow})
    prompt_id = response.get("prompt_id")
    if not isinstance(prompt_id, str) or not re.fullmatch("[A-Za-z0-9-]{6,100}", prompt_id):
        raise RuntimeError("ComfyUI did not return a valid prompt ID")
    print(json.dumps({"submitted": True, "prompt_id": prompt_id, "approved_sha256": digest}))
    if args.no_poll:
        return
    expires = time.monotonic() + args.timeout
    while time.monotonic() < expires:
        history = api_json("GET", "/history/" + prompt_id)
        record = history.get(prompt_id, {})
        if record:
            status = record.get("status", {})
            if status.get("status_str") in ("error", "failed") or status.get("completed") is False:
                raise RuntimeError("ComfyUI workflow failed; inspect local UI logs")
            outputs = record.get("outputs", {})
            files = []
            for result in outputs.values():
                if isinstance(result, dict):
                    for key in ("images", "gifs", "videos", "audio"):
                        value = result.get(key, [])
                        if isinstance(value, list):
                            files.extend(x for x in value if isinstance(x, dict) and "filename" in x)
            done = []
            for item in files[:20]:
                path, size = download_output(item, args.output, prompt_id)
                done.append({"file": path, "bytes": size})
            print(json.dumps({"completed": True, "prompt_id": prompt_id,
                              "files": done, "note": "Review media manually before any publishing"}, indent=2))
            return
        time.sleep(4)
    raise TimeoutError("Local render timed out (job may still be running in ComfyUI)")

def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--workflow", required=True, type=Path, help="Audited ComfyUI API-format JSON")
    ap.add_argument("--approvals", default=Path("approved-workflows.json"), type=Path)
    ap.add_argument("--output", default=Path("render-output"), type=Path)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--submit", action="store_true", help="Explicitly authorize this local render")
    ap.add_argument("--no-poll", action="store_true")
    ap.add_argument("--timeout", type=int, default=1800)
    args = ap.parse_args(argv)
    if args.timeout < 1 or args.timeout > MAX_POLL_SECONDS:
        ap.error("Timeout must be 1..3600 seconds")
    try:
        run(args)
    except (ValueError, PermissionError, FileNotFoundError, urllib.error.URLError,
            TimeoutError, RuntimeError, json.JSONDecodeError) as exc:
        print("Film worker error: " + str(exc), file=sys.stderr)
        return 1
    return 0

if __name__ == "__main__":
    raise SystemExit(main())

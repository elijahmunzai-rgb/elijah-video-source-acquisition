# Elijah Video Studio: 318-repository source importer

Reads the immutable upstream 2026-10-19 video skills snapshot at GitHub commit `ffdf99cbc7879f611abba186e933695904cd638f` (confirmed exactly 318 records). It refuses to silently drop or duplicate repositories, and requires exactly 318 unique entries. Fetches GitHub ZIP source archives for each repo via `codeload.github.com`, retries transient errors, audits ZIP integrity/path safety, records SHA-256 and source provenance, and emits an itemized report. Does **not** execute code, claim dependencies installed, or merge licenses.

**Run on an internet-enabled machine or dedicated GitHub Actions repo:**

```bash
python import_all_318.py --dry-run
python import_all_318.py --output ./elijah-video-sources --workers 3
# Rerun the same command to verify existing archives and retry failures.
```

The index is pinned so later upstream additions (the Oct 20 index already has 323) do not silently replace the original 318. Optionally supply a known 318-item snapshot with `--manifest`. Existing IO Agency / OutboundForge GitHub repositories are intentionally not modified. Output archives must be license- and security-reviewed before any integration or execution. Downloading all repositories is **not necessary** to study their approaches and reimplement equivalent features. Downloading source is useful when you want to run or reuse **their actual code**. Realistic 3D and AI video still require adequate assets and computing resources.

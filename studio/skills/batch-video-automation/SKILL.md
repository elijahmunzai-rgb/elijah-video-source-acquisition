---
name: batch-video-automation
description: Create data-driven variations, personalized videos and reproducible render batches from structured JSON/CSV inputs.
---


# Batch Video Automation
Template + validated input data -> deterministic variants, preserving brand style and timeline. For each record choose explicitly allowlisted text fields and never insert raw input as code, file path or shell argument without validation.
- Use idempotent names, immutable input snapshots, per-render manifest, unique output paths, per-job status, bounded concurrency and resource quotas. Avoid uncontrolled hundreds-of-MP4 memory spikes.
- Store `variant_id | inputs_sha | master_template_sha | output_path | rendered | QA` and surface failed jobs individually.
- Client personalization requires lawful data use, minimum personally identifying details, and opt-in as necessary. Do not create targeted deceptive testimonials or fake endorsements.
- Never configure continuous background work unless a supported scheduler/automation was explicitly requested and created.

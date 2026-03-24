---
name: mux
description: Mux video integration for ABA courses. Use when working with video uploads, playback, asset management, or connecting Mux videos to course lessons. Covers the Mux Python SDK, signed playback tokens, lesson frontmatter fields, and the video player pipeline.
---

# Mux Video Integration

Mux hosts all course video content. Videos use **signed playback** (JWT tokens) — there are no public playback IDs.

## Architecture

```
Mux Dashboard (upload) → asset_id + playback_id
                              ↓
Lesson frontmatter (courses/<slug>/<module>/<lesson>.md)
                              ↓
course_loader.py (parses frontmatter → Lesson dataclass)
                              ↓
lesson.py → mux.py (signs JWT tokens) → <mux-player> element
```

## Environment Variables

Set in `.env` (shared) or `.env.local` (dev override):

| Variable | Purpose |
|---|---|
| `MUX_TOKEN_ID` | API authentication (username) — for asset queries |
| `MUX_TOKEN_SECRET` | API authentication (password) — for asset queries |
| `MUX_SIGNING_KEY_ID` | JWT signing key ID — for playback tokens |
| `MUX_SIGNING_SECRET_KEY` | Base64-encoded RSA private key — for playback tokens |

The first pair is for server-side API calls (listing assets, fetching duration). The second pair is for signing playback tokens that the browser sends to Mux.

## Existing Utilities (`utils/mux.py`)

Three functions — all return `None` gracefully when env vars are missing:

- **`get_mux_tokens(playback_id)`** → `{"playback": token, "thumbnail": token, "storyboard": token}` — signs JWT tokens for the `<mux-player>` element
- **`sign_mux_token(playback_id, audience, expiry, extra_claims)`** → single JWT token (internal, called by `get_mux_tokens`)
- **`fetch_asset_duration(asset_id)`** → duration in **minutes** (rounded, min 1) — calls Mux Assets API

## Lesson Frontmatter Fields

Each lesson `.md` file in `courses/<course-slug>/` uses YAML frontmatter:

```yaml
---
title: "Lesson Title"
duration: 3
playback_id: "abc123..."
asset_id: "xyz789..."
---

Optional markdown content below.
```

| Field | Type | Required | Description |
|---|---|---|---|
| `title` | string | yes | Display title |
| `duration` | int | no | Duration in minutes. Auto-fetched from Mux if `asset_id` is set |
| `playback_id` | string | no | Mux signed playback ID — drives the video player |
| `asset_id` | string | no | Mux asset ID — used for duration fetching |

**Duration resolution order** (in `utils/course_loader.py`):
1. `duration` in frontmatter → use it
2. `asset_id` in frontmatter → call `fetch_asset_duration()`, write result back to frontmatter
3. Fallback → estimate from word count (200 words/min)

## Video Player Rendering (`pages/lesson.py`)

The `_video_player()` function checks `lesson.playback_id`:
- **Missing**: renders a placeholder box
- **Present**: calls `get_mux_tokens()` to sign JWT tokens, renders `<mux-player>` with `playback-id`, `playback-token`, `thumbnail-token`, `storyboard-token`

The `<mux-player>` web component script is loaded via `utils/config.py`:
```python
Script(src="https://cdn.jsdelivr.net/npm/@mux/mux-player", defer=True)
```

## Querying Mux Assets (Ad-hoc Scripts)

Use `uv run python` for all ad-hoc Mux scripts. The `mux_python` SDK is a project dependency.

### List all assets with titles

```python
uv run python -c "
import mux_python, os
from dotenv import load_dotenv
load_dotenv('.env.local', override=True)
load_dotenv('.env')

config = mux_python.Configuration()
config.username = os.getenv('MUX_TOKEN_ID')
config.password = os.getenv('MUX_TOKEN_SECRET')
client = mux_python.ApiClient(config)
assets_api = mux_python.AssetsApi(client)

resp = assets_api.list_assets(limit=100)
for a in resp.data:
    meta = a.meta
    title = meta._title if meta else '(no title)'
    playback = [(p.id, p.policy) for p in (a.playback_ids or [])]
    dur = round(a.duration, 1) if a.duration else '?'
    print(f'{a.id} | {title} | {dur}s | {playback}')
"
```

**Key gotcha**: Asset titles live in `meta._title` (the private attribute), not in `passthrough` or a top-level `title` field. The `meta` object is an `AssetMetadata` — use attribute access, not dict `.get()`.

### Naming convention for uploaded videos

Videos are titled with the pattern: `c<course>-<module>_<lesson>-<slug>`

Example: `c4-3_2-mcp` = course 4, module 3, lesson 2, slug "mcp"

## Workflow: Adding Videos to a Course

1. Upload videos to Mux (dashboard or API), setting the title metadata
2. Run the asset listing script above to get `asset_id` and `playback_id` for each video
3. Add `playback_id` and `asset_id` to each lesson's frontmatter
4. Update `duration` with actual video duration (rounded to nearest minute, min 1)
5. Verify by running `uv run main.py` and navigating to a lesson page

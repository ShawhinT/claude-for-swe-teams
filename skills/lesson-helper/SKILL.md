---
name: lesson-helper
description: Transcribe, write, and edit ABA course lesson files (.md). Use when working with lesson content — transcribing videos, generating or editing lesson copy, updating frontmatter fields, producing course metadata, or any task involving lesson .md files and their associated assets.
---

# Lesson Helper

General-purpose toolkit for ABA course lessons. Handles transcription, content generation, frontmatter management, and course metadata.

## Course Structure

Each course has its own directory under `courses/<course-slug>/` with lesson `.md` files organized by module. Each lesson has YAML frontmatter (title, duration, playback_id, asset_id, transcript). Course metadata lives in `courses/<course-slug>/course.yaml`.

Check `courses/` for available courses and their `course.yaml` for module/lesson structure.

### Video files

Videos for all courses live outside the repo in a local directory, with one subdirectory per course. Set the `COURSE_VIDEOS_DIR` environment variable to point to your videos directory, or default to `./course-videos/`:

```
$COURSE_VIDEOS_DIR/<course-slug>/final/<prefix>-{M}_{L}-{slug}.mp4
```

Each course has a unique short **prefix** for its video filenames. The naming pattern is `{prefix}-{M}_{L}-{slug}.mp4` where `M` = module number, `L` = lesson number, and `slug` = lesson slug.

### Example mapping (claude-code-course, prefix `c4`)

| Video File | Lesson File |
|---|---|
| `c4-1_1-intro.mp4` | `01-introduction/01-intro.md` |
| `c4-1_2-what-is-claude-code.mp4` | `01-introduction/02-what-is-claude-code.md` |
| `c4-2_1-context-management.mp4` | `02-core-features/01-context-management.md` |
| `c4-3_1-skills.mp4` | `03-customization/01-skills.md` |

When working with a course, check `course.yaml` for the module/lesson structure and look in the corresponding video directory for available files. If a course's video prefix is unknown, ask the user.

## Capabilities

### Lesson Copy Generation

When generating or editing lesson body content, read `references/voice-guide.md` for Shaw's voice and style guide. The guide is organized around 3 core principles: reduce reader friction, stay concrete, and end when the content ends. Engage with the principles, not just the specific rules.

### Transcription

Generate timestamped markdown transcripts from course video files using AssemblyAI.

**Run the script:**

```bash
cd .claude/skills/lesson-helper
uv run scripts/transcribe.py <video_path> --title "Lesson Title" --output <output.md>
```

The script:
- Sends the video to AssemblyAI (speech model: `universal-3-pro`)
- Uses AssemblyAI's sentence detection for natural segmentation
- Outputs timestamped markdown with `[M:SS]` markers — one line per sentence

**Output format:**

```markdown
# Lesson Title

[0:00] Hey everyone, I'm Shaw.

[0:02] In this video, I'm going to give a short and practical introduction to Claude Code.

[0:07] Although you'll find countless tutorials for this on YouTube, my goal here is to cover the most important concepts and features you need to start building today.
```

**Output location:** `courses/<course-slug>/transcripts/`

**Known issues:**
- AssemblyAI transcribes "Shaw" as "Shah" — find/replace after transcription
- Technical terms may need correction (e.g., "Claude code" vs "Claude Code", "sub agents" vs "subagents")

**After transcribing**, add a `transcript` field to the lesson's frontmatter:

```yaml
---
title: "Introduction"
duration: 1
playback_id: "abc123..."
asset_id: "xyz789..."
transcript: "c4-1_1-intro.md"
---
```

## Setup

The `.env` file in this skill directory must contain:

```
ASSEMBLYAI_API_KEY=your_key_here
```

Dependencies are managed via `pyproject.toml` in this skill directory. Install with:

```bash
cd .claude/skills/lesson-helper && uv sync
```

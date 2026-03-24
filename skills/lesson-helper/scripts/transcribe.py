"""Transcribe a video file via AssemblyAI and output timestamped markdown."""

import os
import sys
from pathlib import Path

import assemblyai as aai
from dotenv import load_dotenv


def transcribe_video(video_path: str, env_path: str | None = None) -> dict:
    """Transcribe a video file using AssemblyAI.

    Returns dict with 'text' and 'sentences' (list of {start, text}).
    """
    if env_path:
        load_dotenv(env_path)
    else:
        skill_dir = Path(__file__).resolve().parent.parent
        load_dotenv(skill_dir / ".env")

    api_key = os.getenv("ASSEMBLYAI_API_KEY")
    if not api_key:
        raise RuntimeError("ASSEMBLYAI_API_KEY not set")
    aai.settings.api_key = api_key

    config = aai.TranscriptionConfig(
        speech_models=["universal-3-pro", "universal-2"],
        disfluencies=True,
    )

    transcriber = aai.Transcriber()
    transcript = transcriber.transcribe(video_path, config=config)

    if transcript.status == aai.TranscriptStatus.error:
        raise RuntimeError(f"Transcription failed: {transcript.error}")

    sentences = [
        {"start": s.start / 1000, "text": s.text}
        for s in transcript.get_sentences()
    ]

    return {"text": transcript.text, "sentences": sentences}


def format_timestamp(seconds: float) -> str:
    """Format seconds as M:SS."""
    minutes = int(seconds) // 60
    secs = int(seconds) % 60
    return f"{minutes}:{secs:02d}"


def sentences_to_markdown(sentences: list[dict], title: str | None = None) -> str:
    """Convert sentences to timestamped markdown."""
    lines = []
    if title:
        lines.append(f"# {title}")
        lines.append("")

    for sentence in sentences:
        timestamp = format_timestamp(sentence["start"])
        lines.append(f"[{timestamp}] {sentence['text']}")

    return "\n".join(lines)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(
            "Usage: uv run scripts/transcribe.py <video_path> "
            "[--title <title>] [--output <output.md>] [--env-path <path>]"
        )
        sys.exit(1)

    video_path = sys.argv[1]
    title = None
    output_path = None
    env_path = None

    args = sys.argv[2:]
    i = 0
    while i < len(args):
        if args[i] == "--title" and i + 1 < len(args):
            title = args[i + 1]
            i += 2
        elif args[i] == "--output" and i + 1 < len(args):
            output_path = args[i + 1]
            i += 2
        elif args[i] == "--env-path" and i + 1 < len(args):
            env_path = args[i + 1]
            i += 2
        else:
            print(f"Unknown argument: {args[i]}")
            sys.exit(1)

    print(f"Transcribing: {video_path}")
    result = transcribe_video(video_path, env_path)
    print(f"Got {len(result['sentences'])} sentences")

    markdown = sentences_to_markdown(result["sentences"], title)

    if output_path:
        out = Path(output_path)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(markdown)
        print(f"Transcript saved to {out}")
    else:
        print(markdown)

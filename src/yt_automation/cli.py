from __future__ import annotations

import argparse
from pathlib import Path

from rich.console import Console

from .pipeline import list_ideas, run_pipeline
from .remix import remix_and_upload

console = Console()


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="yt-automation",
        description="Local YouTube automation pipeline",
    )
    sub = parser.add_subparsers(dest="command")

    sub.add_parser("ideas", help="Generate idea list")

    run_parser = sub.add_parser("run", help="Generate a full content pack")
    run_parser.add_argument("--idea-index", type=int, default=None, help="Idea index from ideas list")
    run_parser.add_argument("--idea", type=str, default=None, help="Override with your own idea")
    run_parser.add_argument("--out", type=str, default=None, help="Override output base directory")

    remix_parser = sub.add_parser("remix", help="Download (with rights), edit, and optionally upload")
    remix_parser.add_argument("--url", required=True, help="YouTube video URL (you must have rights)")
    remix_parser.add_argument("--title", type=str, default=None, help="Video title")
    remix_parser.add_argument("--description", type=str, default=None, help="Video description")
    remix_parser.add_argument("--tags", type=str, default=None, help="Comma-separated tags")
    remix_parser.add_argument("--category-id", type=str, default=None, help="YouTube category ID")
    remix_parser.add_argument(
        "--privacy",
        type=str,
        default=None,
        choices=["private", "unlisted", "public"],
        help="Privacy status",
    )
    remix_parser.add_argument("--thumbnail", type=str, default=None, help="Thumbnail image path")
    remix_parser.add_argument("--upload", action="store_true", help="Upload to your channel")
    remix_parser.add_argument(
        "--confirm-rights",
        action="store_true",
        help="Confirm you have rights to use the source video",
    )
    remix_parser.add_argument("--out", type=str, default=None, help="Override output base directory")
    remix_parser.add_argument("--keep-download", action="store_true", help="Keep downloaded source file")

    return parser


def main() -> None:
    parser = _build_parser()
    args = parser.parse_args()
    root_dir = Path.cwd()

    if args.command == "ideas":
        ideas = list_ideas(root_dir)
        for idx, idea in enumerate(ideas, start=1):
            console.print(f"{idx}. {idea}")
        return

    if args.command in {"run", None}:
        out_dir = Path(args.out) if args.out else None
        run_pipeline(
            root_dir,
            idea_index=args.idea_index,
            idea_override=args.idea,
            output_dir=out_dir,
        )
        return

    if args.command == "remix":
        tags = [t.strip() for t in args.tags.split(",")] if args.tags else None
        out_dir = Path(args.out) if args.out else None
        thumbnail = Path(args.thumbnail) if args.thumbnail else None
        remix_and_upload(
            root_dir,
            url=args.url,
            title=args.title,
            description=args.description,
            tags=tags,
            category_id=args.category_id,
            privacy_status=args.privacy,
            thumbnail_path=thumbnail,
            confirm_rights=args.confirm_rights,
            do_upload=args.upload,
            output_base=out_dir,
            keep_download=args.keep_download,
        )
        return

    parser.print_help()

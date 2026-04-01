from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from rich.console import Console

from .downloader import download_youtube
from .ffmpeg import render_best_edit
from .utils import load_yaml, make_output_dir, write_json, write_text
from .youtube import upload_video

console = Console()


def _load_defaults(root_dir: Path) -> dict[str, Any]:
    config = load_yaml(root_dir / "config" / "channel.yaml")
    defaults = {
        "title": config.get("channel", {}).get("name", "Untitled Video"),
        "description": "",
        "tags": [config.get("channel", {}).get("niche", "video")],
        "category_id": "27",
        "privacy": "private",
    }
    meta = config.get("metadata", {})
    defaults.update({k: v for k, v in meta.items() if v})
    return defaults


def remix_and_upload(
    root_dir: Path,
    url: str,
    title: str | None,
    description: str | None,
    tags: list[str] | None,
    category_id: str | None,
    privacy_status: str | None,
    thumbnail_path: Path | None,
    confirm_rights: bool,
    do_upload: bool,
    output_base: Path | None,
    keep_download: bool,
) -> Path:
    if not confirm_rights:
        raise ValueError("Confirmation required: pass --confirm-rights to proceed.")

    defaults = _load_defaults(root_dir)
    title = title or defaults["title"]
    description = description or defaults["description"]
    tags = tags or defaults["tags"]
    category_id = category_id or defaults["category_id"]
    privacy_status = privacy_status or defaults["privacy"]

    base_dir = output_base or Path("outputs")
    out_dir = make_output_dir(root_dir / base_dir, "remix")

    console.print("[cyan]Downloading...[/cyan]")
    download_dir = out_dir / "downloads"
    source_path = download_youtube(url, download_dir)

    console.print("[cyan]Rendering edit...[/cyan]")
    edited_path = out_dir / "final.mp4"
    render_best_edit(source_path, edited_path)

    manifest = {
        "source_url": url,
        "source_path": str(source_path),
        "edited_path": str(edited_path),
        "title": title,
        "description": description,
        "tags": tags,
        "category_id": category_id,
        "privacy_status": privacy_status,
    }
    write_json(out_dir / "manifest.json", manifest)
    write_text(out_dir / "title.txt", title)
    write_text(out_dir / "description.txt", description)
    write_text(out_dir / "tags.txt", ", ".join(tags))

    if do_upload:
        console.print("[cyan]Uploading to YouTube...[/cyan]")
        response = upload_video(
            edited_path,
            title=title,
            description=description,
            tags=tags,
            category_id=category_id,
            privacy_status=privacy_status,
            thumbnail_path=thumbnail_path,
        )
        write_json(out_dir / "upload_response.json", response)
        console.print(f"[green]Upload complete:[/green] {response.get('id')}")

    if not keep_download:
        try:
            source_path.unlink()
        except OSError:
            pass

    return out_dir

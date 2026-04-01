from __future__ import annotations

from pathlib import Path

import yt_dlp


def download_youtube(url: str, output_dir: Path) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    outtmpl = str(output_dir / "%(title)s.%(ext)s")

    ydl_opts = {
        "format": "bv*+ba/best",
        "outtmpl": outtmpl,
        "merge_output_format": "mp4",
        "quiet": True,
        "noplaylist": True,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        filename = ydl.prepare_filename(info)
        # If merged, yt-dlp may adjust extension.
        if not filename.lower().endswith(".mp4"):
            filename = str(Path(filename).with_suffix(".mp4"))
    return Path(filename)

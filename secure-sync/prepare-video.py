#!/usr/bin/env python3
"""Generate video thumbnail as the unprivileged desktop user, never as root."""
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

folder = Path.home() / ".config/ii-sddm-theme"
videos = {".mp4", ".mkv", ".mov", ".webm", ".m4v", ".avi"}


def wallpaper():
    settings = (folder / "Settings.qml").read_text(encoding="utf-8")
    colors = (folder / "Colors.qml").read_text(encoding="utf-8")
    match = re.search(r'(?m)^\s*property\s+string\s+background_wallpaperPath:\s*("(?:\\.|[^"\\])*")', settings)
    value = json.loads(match.group(1)) if match else ""
    if not value:
        lines = colors.splitlines()
        if len(lines) > 4 and lines[4].lstrip().startswith("//"):
            value = lines[4].split("//", 1)[1].strip()
    if value:
        path = Path(value).expanduser()
        return path if path.is_absolute() else folder / path
    backgrounds = sorted(folder.glob("background.*"))
    return backgrounds[0] if backgrounds else None


def main():
    if os.geteuid() == 0:
        raise RuntimeError("Run the theme apply wrapper as your normal user.")
    path = wallpaper()
    if path is None:
        raise RuntimeError("No wallpaper detected.")
    if path.suffix.lower() not in videos:
        return
    if not shutil.which("ffmpeg"):
        raise RuntimeError("ffmpeg is required for video wallpaper thumbnails.")
    fd, temp = tempfile.mkstemp(prefix=".sddm-poster-", suffix=".png", dir=folder)
    os.close(fd)
    try:
        subprocess.run(["ffmpeg", "-nostdin", "-loglevel", "error", "-y",
                        "-ss", "1", "-i", str(path), "-frames:v", "1", temp],
                       check=True)
        os.chmod(temp, 0o644)
        os.replace(temp, folder / "placeholder.png")
    finally:
        if os.path.exists(temp):
            os.unlink(temp)


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError, RuntimeError, subprocess.CalledProcessError) as error:
        print(f"ii-sddm-theme thumbnail preparation failed: {error}", file=sys.stderr)
        sys.exit(1)

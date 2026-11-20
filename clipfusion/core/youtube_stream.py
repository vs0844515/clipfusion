"""YouTube Live Stream and Recorded Stream Integration Engine for ClipFusion.
Handles URL validation, stream metadata extraction, DRM/access check, and section capture using yt-dlp.
"""

import os
import re
import sys
import json
import logging
import subprocess
from pathlib import Path
from typing import Dict, Any, Optional, Tuple, Callable

from clipfusion.core.ffmpeg_utils import get_ffmpeg_path

logger = logging.getLogger("clipfusion.youtube")

# YouTube URL matching patterns
YOUTUBE_REGEX = re.compile(
    r"^(https?://)?(www\.)?(youtube\.com/(watch\?v=|live/|shorts/|embed/)|youtu\.be/)([\w-]{11})",
    re.IGNORECASE,
)


def get_ytdlp_path() -> str:
    """Locates the yt-dlp binary with fallback."""
    project_root = Path(__file__).resolve().parent.parent.parent
    local_bin = project_root / "bin" / ("yt-dlp.exe" if sys.platform == "win32" else "yt-dlp")
    if local_bin.is_file():
        return str(local_bin)

    system_bin = shutil_which("yt-dlp")
    if system_bin:
        return system_bin

    known_path = r"C:\Users\vs084\AppData\Local\Programs\clipit-studio\resources\bin\yt-dlp.exe"
    if os.path.isfile(known_path):
        return known_path

    raise FileNotFoundError("yt-dlp binary not found in bin/ or system PATH.")


def shutil_which(cmd: str) -> Optional[str]:
    import shutil
    return shutil.which(cmd)


def validate_youtube_url(url: str) -> Tuple[bool, Optional[str], Optional[str]]:
    """
    Validates YouTube URL format.
    Returns (is_valid, video_id, normalized_url).
    """
    if not url:
        return False, None, None

    url = url.strip()
    match = YOUTUBE_REGEX.search(url)
    if match:
        video_id = match.group(5)
        normalized = f"https://www.youtube.com/watch?v={video_id}"
        return True, video_id, normalized

    return False, None, None


def fetch_stream_info(
    url: str,
    cookies_browser: Optional[str] = None,
    timeout: int = 30,
) -> Dict[str, Any]:
    """
    Extracts stream metadata, status, duration, and availability using yt-dlp.
    Validates access and DRM permissions.
    """
    is_valid, video_id, clean_url = validate_youtube_url(url)
    if not is_valid or not clean_url:
        return {
            "success": False,
            "error_type": "INVALID_URL",
            "message": "Invalid YouTube URL format. Please provide a standard YouTube video, live stream, or recording link.",
        }

    ytdlp_exe = get_ytdlp_path()
    ffmpeg_dir = os.path.dirname(get_ffmpeg_path())

    cmd = [
        ytdlp_exe,
        "--dump-json",
        "--skip-download",
        "--no-playlist",
        "--ffmpeg-location", ffmpeg_dir,
        "--extractor-args", "youtube:player_client=android,web",
    ]

    if cookies_browser and cookies_browser.lower() not in ["none", ""]:
        cmd.extend(["--cookies-from-browser", cookies_browser.lower()])

    cmd.append(clean_url)

    try:
        creationflags = 0
        if sys.platform == "win32" and hasattr(subprocess, "CREATE_NO_WINDOW"):
            creationflags = subprocess.CREATE_NO_WINDOW

        proc = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout,
            creationflags=creationflags,
        )

        stderr_lower = proc.stderr.lower()

        # If DPAPI decryption fails (Chrome 127+ App-Bound encryption on Windows), auto-retry without browser cookies
        if "dpapi" in stderr_lower and cookies_browser:
            logger.info("DPAPI error encountered with browser cookies. Auto-retrying with Android player client...")
            clean_cmd = [arg for arg in cmd if arg != "--cookies-from-browser" and arg != cookies_browser.lower()]
            proc = subprocess.run(
                clean_cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=timeout,
                creationflags=creationflags,
            )
            stderr_lower = proc.stderr.lower()

        # Check for specific restriction errors
        if "sign in to confirm you're not a bot" in stderr_lower or "confirm you're not a bot" in stderr_lower:
            return {
                "success": False,
                "error_type": "BOT_VERIFICATION_REQUIRED",
                "message": (
                    "YouTube requested bot verification for this link. "
                    "You can resolve this easily: select your signed-in browser (Chrome / Edge / Firefox) "
                    "in the 'Browser Session' dropdown below, OR upload a local recording file via the 'Local Video File' tab."
                ),
            }

        if "drm" in stderr_lower:
            return {
                "success": False,
                "error_type": "DRM_RESTRICTED",
                "message": (
                    "This video contains DRM (Digital Rights Management) encryption and cannot be processed. "
                    "ClipFusion strictly complies with digital access controls. "
                    "Please upload a local authorized recording file instead."
                ),
            }

        if "private video" in stderr_lower or "sign in to confirm your age" in stderr_lower or "members-only" in stderr_lower:
            return {
                "success": False,
                "error_type": "ACCESS_RESTRICTED",
                "message": (
                    "This video is private, members-only, or age-restricted and requires account credentials. "
                    "Only eligible public live streams or recordings can be processed. "
                    "Please upload your local recording file instead."
                ),
            }

        if proc.returncode != 0 or not proc.stdout.strip():
            # Extract clean error line
            err_lines = [line.strip() for line in proc.stderr.splitlines() if "ERROR:" in line]
            err_msg = err_lines[0] if err_lines else proc.stderr.strip()[:200]
            return {
                "success": False,
                "error_type": "EXTRACTION_FAILED",
                "message": f"Could not retrieve video information: {err_msg}. Please check your connection, select your browser under 'Browser Session', or use a local video file.",
            }

        # Parse JSON output
        data = json.loads(proc.stdout)

        is_live = data.get("is_live", False)
        was_live = data.get("was_live", False)
        duration = float(data.get("duration") or 0.0)

        # Build clean response
        return {
            "success": True,
            "video_id": video_id,
            "url": clean_url,
            "title": data.get("title", "YouTube Stream"),
            "uploader": data.get("uploader") or data.get("channel") or "Unknown Creator",
            "channel_url": data.get("channel_url", ""),
            "duration": duration,
            "is_live": is_live,
            "was_live": was_live,
            "is_stream": is_live or was_live,
            "thumbnail": data.get("thumbnail", ""),
            "view_count": data.get("view_count", 0),
            "description": (data.get("description") or "")[:300],
            "upload_date": data.get("upload_date", ""),
        }

    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "error_type": "TIMEOUT",
            "message": "Connecting to YouTube timed out. Please verify your connection or try again.",
        }
    except Exception as e:
        return {
            "success": False,
            "error_type": "UNKNOWN_ERROR",
            "message": f"An unexpected error occurred while probing YouTube stream: {str(e)}",
        }


def download_stream_section(
    clean_url: str,
    output_path: str,
    start_time: float = 0.0,
    duration: Optional[float] = None,
    max_resolution: int = 1080,
    cookies_browser: Optional[str] = None,
    progress_callback: Optional[Callable[[int, str], None]] = None,
) -> Tuple[bool, str]:
    """
    Downloads an authorized stream section or recorded video using yt-dlp and local FFmpeg.
    """
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    ytdlp_exe = get_ytdlp_path()
    ffmpeg_dir = os.path.dirname(get_ffmpeg_path())

    if progress_callback:
        progress_callback(10, "Initializing YouTube stream download...")

    # Calculate download section string
    # yt-dlp format: --download-sections "*START_TIME-END_TIME" (in seconds or HH:MM:SS)
    cmd = [
        ytdlp_exe,
        "--no-playlist",
        "--ffmpeg-location", ffmpeg_dir,
        "--extractor-args", "youtube:player_client=android,web",
        "-f", f"bestvideo[height<={max_resolution}][ext=mp4]+bestaudio[ext=m4a]/bestvideo[height<={max_resolution}]+bestaudio/best[height<={max_resolution}]/best",
        "--merge-output-format", "mp4",
        "-o", output_path,
        "--force-overwrites",
    ]

    if cookies_browser and cookies_browser.lower() not in ["none", ""]:
        cmd.extend(["--cookies-from-browser", cookies_browser.lower()])

    if duration is not None and duration > 0:
        end_time = start_time + duration
        s_h, s_m, s_s = int(start_time // 3600), int((start_time % 3600) // 60), int(start_time % 60)
        e_h, e_m, e_s = int(end_time // 3600), int((end_time % 3600) // 60), int(end_time % 60)
        sec_arg = f"*{s_h:02d}:{s_m:02d}:{s_s:02d}-{e_h:02d}:{e_m:02d}:{e_s:02d}"
        cmd.extend(["--download-sections", sec_arg])
        if progress_callback:
            progress_callback(20, f"Capturing time slice: {sec_arg} ({int(duration)}s)...")
    elif start_time > 0:
        s_h, s_m, s_s = int(start_time // 3600), int((start_time % 3600) // 60), int(start_time % 60)
        sec_arg = f"*{s_h:02d}:{s_m:02d}:{s_s:02d}-inf"
        cmd.extend(["--download-sections", sec_arg])
        if progress_callback:
            progress_callback(20, f"Capturing stream from {s_h:02d}:{s_m:02d}:{s_s:02d} onward...")

    cmd.append(clean_url)

    try:
        creationflags = 0
        if sys.platform == "win32" and hasattr(subprocess, "CREATE_NO_WINDOW"):
            creationflags = subprocess.CREATE_NO_WINDOW

        proc = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=600,  # 10 minute max download window
            creationflags=creationflags,
        )

        if "dpapi" in proc.stderr.lower() and cookies_browser:
            clean_cmd = [arg for arg in cmd if arg != "--cookies-from-browser" and arg != cookies_browser.lower()]
            proc = subprocess.run(
                clean_cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=600,
                creationflags=creationflags,
            )

        if progress_callback:
            progress_callback(80, "Verifying downloaded stream file...")

        if os.path.isfile(output_path) and os.path.getsize(output_path) > 1024:
            if progress_callback:
                progress_callback(100, "Stream section successfully downloaded!")
            return True, output_path

        # If extension changed to .mkv or .webm, find it and remux to .mp4
        stem = Path(output_path).stem
        parent = Path(output_path).parent
        for f in parent.glob(f"{stem}.*"):
            if f.is_file() and f.stat().st_size > 1024:
                # Remux to target output_path MP4 using local FFmpeg
                remux_cmd = [
                    get_ffmpeg_path(),
                    "-hide_banner", "-y",
                    "-i", str(f),
                    "-c:v", "copy",
                    "-c:a", "aac",
                    output_path,
                ]
                subprocess.run(remux_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                if os.path.isfile(output_path) and os.path.getsize(output_path) > 1024:
                    return True, output_path
                return True, str(f)

        return False, f"Failed to capture stream: {proc.stderr[:300]}"

    except subprocess.TimeoutExpired:
        return False, "Download timed out. Please choose a shorter section (e.g., 10–15 minutes)."
    except Exception as e:
        return False, f"Download error: {str(e)}"

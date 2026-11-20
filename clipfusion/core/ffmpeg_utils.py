"""FFmpeg utility module for ClipFusion.
Handles FFmpeg binary discovery, probing, audio extraction, trimming, and filter execution.
"""

import os
import sys
import json
import shutil
import subprocess
import logging
from pathlib import Path
from typing import Dict, Any, Optional, Tuple

logger = logging.getLogger("clipfusion.ffmpeg")

# Global cached path
_CACHED_FFMPEG_PATH: Optional[str] = None


def get_ffmpeg_path() -> str:
    """Locates a working FFmpeg binary with multi-level fallback."""
    global _CACHED_FFMPEG_PATH
    if _CACHED_FFMPEG_PATH and os.path.isfile(_CACHED_FFMPEG_PATH):
        # Ensure it is in PATH for external libraries (like Whisper)
        bin_dir = os.path.dirname(_CACHED_FFMPEG_PATH)
        if bin_dir not in os.environ.get("PATH", ""):
            os.environ["PATH"] = bin_dir + os.pathsep + os.environ.get("PATH", "")
        return _CACHED_FFMPEG_PATH

    # Candidate 1: Local project ./bin/ffmpeg.exe
    project_root = Path(__file__).resolve().parent.parent.parent
    local_bin = project_root / "bin" / ("ffmpeg.exe" if sys.platform == "win32" else "ffmpeg")
    if local_bin.is_file() and os.access(str(local_bin), os.X_OK):
        _CACHED_FFMPEG_PATH = str(local_bin)
        bin_dir = str(local_bin.parent)
        if bin_dir not in os.environ.get("PATH", ""):
            os.environ["PATH"] = bin_dir + os.pathsep + os.environ.get("PATH", "")
        return _CACHED_FFMPEG_PATH

    # Candidate 2: System PATH
    system_ffmpeg = shutil.which("ffmpeg")
    if system_ffmpeg:
        _CACHED_FFMPEG_PATH = system_ffmpeg
        return _CACHED_FFMPEG_PATH

    # Candidate 3: Known Windows vendor paths
    if sys.platform == "win32":
        known_paths = [
            r"C:\Users\vs084\AppData\Local\Programs\clipit-studio\resources\bin\ffmpeg.exe",
            os.path.expandvars(r"%LOCALAPPDATA%\Programs\clipit-studio\resources\bin\ffmpeg.exe"),
            r"C:\Program Files\ffmpeg\bin\ffmpeg.exe",
            r"C:\ffmpeg\bin\ffmpeg.exe",
        ]
        for kp in known_paths:
            if os.path.isfile(kp):
                _CACHED_FFMPEG_PATH = kp
                bin_dir = os.path.dirname(kp)
                if bin_dir not in os.environ.get("PATH", ""):
                    os.environ["PATH"] = bin_dir + os.pathsep + os.environ.get("PATH", "")
                return _CACHED_FFMPEG_PATH

    # Candidate 4: imageio-ffmpeg python package
    try:
        import imageio_ffmpeg
        img_ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
        if img_ffmpeg and os.path.isfile(img_ffmpeg):
            _CACHED_FFMPEG_PATH = img_ffmpeg
            bin_dir = os.path.dirname(img_ffmpeg)
            if bin_dir not in os.environ.get("PATH", ""):
                os.environ["PATH"] = bin_dir + os.pathsep + os.environ.get("PATH", "")
            return _CACHED_FFMPEG_PATH
    except ImportError:
        pass

    raise FileNotFoundError(
        "FFmpeg binary not found! Please place ffmpeg.exe inside 'bin/' directory or add it to system PATH."
    )


# Automatically configure PATH on import
try:
    get_ffmpeg_path()
except Exception:
    pass


def run_ffmpeg(args: list[str], timeout: Optional[int] = None) -> Tuple[bool, str]:
    """Runs FFmpeg command and returns (success, output_or_error_string)."""
    ffmpeg_exe = get_ffmpeg_path()
    full_cmd = [ffmpeg_exe, "-hide_banner", "-y"] + args

    try:
        creationflags = 0
        if sys.platform == "win32":
            creationflags = subprocess.CREATE_NO_WINDOW if hasattr(subprocess, "CREATE_NO_WINDOW") else 0x08000000

        process = subprocess.run(
            full_cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout,
            creationflags=creationflags,
        )

        if process.returncode == 0:
            return True, process.stdout + "\n" + process.stderr
        else:
            return False, f"FFmpeg failed with code {process.returncode}:\n{process.stderr}"
    except subprocess.TimeoutExpired:
        return False, f"FFmpeg timed out after {timeout} seconds"
    except Exception as e:
        return False, f"FFmpeg execution error: {str(e)}"


def get_video_info(video_path: str) -> Dict[str, Any]:
    """Retrieves metadata of a video using FFmpeg or OpenCV fallback."""
    if not os.path.isfile(video_path):
        raise FileNotFoundError(f"Video file not found: {video_path}")

    info: Dict[str, Any] = {
        "path": video_path,
        "filename": os.path.basename(video_path),
        "duration": 0.0,
        "width": 0,
        "height": 0,
        "fps": 30.0,
        "frame_count": 0,
        "has_audio": False,
        "aspect_ratio": 16 / 9,
    }

    # Attempt 1: Probe duration and streams via ffmpeg -i
    ffmpeg_exe = get_ffmpeg_path()
    try:
        proc = subprocess.run(
            [ffmpeg_exe, "-hide_banner", "-i", video_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        stderr_text = proc.stderr

        # Check for audio stream
        if "Audio:" in stderr_text:
            info["has_audio"] = True

        # Parse duration line: "Duration: 00:01:23.45, start: 0.000000, bitrate: 1234 kb/s"
        import re
        dur_match = re.search(r"Duration:\s*(\d+):(\d+):(\d+\.\d+)", stderr_text)
        if dur_match:
            hours = int(dur_match.group(1))
            minutes = int(dur_match.group(2))
            seconds = float(dur_match.group(3))
            info["duration"] = hours * 3600 + minutes * 60 + seconds

        # Parse video stream dimensions: e.g. "Stream #0:0... Video: h264 ... 1920x1080 [SAR 1:1 DAR 16:9], 30 fps"
        dim_match = re.search(r",\s*(\d{2,5})x(\d{2,5})", stderr_text)
        if dim_match:
            info["width"] = int(dim_match.group(1))
            info["height"] = int(dim_match.group(2))
            if info["height"] > 0:
                info["aspect_ratio"] = info["width"] / info["height"]

        fps_match = re.search(r"(\d+(?:\.\d+)?)\s*fps", stderr_text)
        if fps_match:
            info["fps"] = float(fps_match.group(1))

    except Exception as e:
        logger.warning(f"FFmpeg probe warning: {e}")

    # Fallback with OpenCV if dimensions or fps are missing
    if info["width"] == 0 or info["duration"] <= 0.0:
        try:
            import cv2
            cap = cv2.VideoCapture(video_path)
            if cap.isOpened():
                info["width"] = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                info["height"] = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                fps = cap.get(cv2.CAP_PROP_FPS)
                if fps and fps > 0:
                    info["fps"] = fps
                total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
                info["frame_count"] = total_frames
                if total_frames > 0 and info["fps"] > 0 and info["duration"] == 0.0:
                    info["duration"] = total_frames / info["fps"]
                if info["height"] > 0:
                    info["aspect_ratio"] = info["width"] / info["height"]
                cap.release()
        except Exception as e:
            logger.warning(f"OpenCV fallback warning: {e}")

    if info["fps"] > 0 and info["duration"] > 0:
        info["frame_count"] = int(info["duration"] * info["fps"])

    return info


def extract_audio(video_path: str, output_wav_path: str, sample_rate: int = 16000) -> bool:
    """Extracts 16kHz mono PCM audio from video for Whisper & analysis."""
    os.makedirs(os.path.dirname(os.path.abspath(output_wav_path)), exist_ok=True)
    args = [
        "-i", video_path,
        "-vn",
        "-acodec", "pcm_s16le",
        "-ac", "1",
        "-ar", str(sample_rate),
        output_wav_path,
    ]
    success, err = run_ffmpeg(args)
    if not success:
        logger.warning(f"Failed to extract audio from {video_path}: {err}")
        return False
    return os.path.isfile(output_wav_path) and os.path.getsize(output_wav_path) > 100


def cut_video(
    input_path: str,
    output_path: str,
    start_time: float,
    duration: float,
    reencode: bool = True,
) -> bool:
    """Cuts a video segment precisely using FFmpeg."""
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    if reencode:
        args = [
            "-ss", f"{start_time:.3f}",
            "-i", input_path,
            "-t", f"{duration:.3f}",
            "-c:v", "libx264",
            "-preset", "fast",
            "-crf", "18",
            "-c:a", "aac",
            "-b:a", "192k",
            "-pix_fmt", "yuv420p",
            output_path,
        ]
    else:
        args = [
            "-ss", f"{start_time:.3f}",
            "-i", input_path,
            "-t", f"{duration:.3f}",
            "-c", "copy",
            output_path,
        ]

    success, err = run_ffmpeg(args)
    if not success:
        logger.error(f"Cut video failed: {err}")
        return False
    return os.path.isfile(output_path)

"""Video Processing and Rendering Engine for ClipFusion.
Executes FFmpeg rendering pipelines: cutting, 9:16 vertical cropping/tracking, subtitle burning, zoom punch, SFX mixing.
"""

import os
import sys
import json
import shutil
import logging
import subprocess
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple, Callable

from clipfusion.core.ffmpeg_utils import get_ffmpeg_path, run_ffmpeg, get_video_info
from clipfusion.core.face_tracker import SmartFaceTracker, FramingMode, SmoothCropTrajectory
from clipfusion.core.subtitles import SubtitleGenerator, SubtitleStyle
from clipfusion.core.effects import EffectsManager, SoundEffectType
from clipfusion.core.clip_extractor import VideoClipCandidate

logger = logging.getLogger("clipfusion.processor")


class ResolutionPreset:
    SD_480P = "480p"
    HD_720P = "720p"
    FHD_1080P = "1080p"
    QHD_2K = "2k"
    UHD_4K = "4k"
    SQUARE = "square"


RESOLUTION_CONFIGS = {
    "480p": {"width": 480, "height": 854, "label": "📱 480x854 (SD Mobile / Data Saver)", "bitrate": "1800k"},
    "720p": {"width": 720, "height": 1280, "label": "📺 720x1280 (HD Vertical 9:16)", "bitrate": "3500k"},
    "1080p": {"width": 1080, "height": 1920, "label": "📱 1080x1920 (Full HD Vertical 9:16)", "bitrate": "6500k"},
    "2k": {"width": 1440, "height": 2560, "label": "📺 1440x2560 (2K QHD Vertical 9:16)", "bitrate": "14000k"},
    "4k": {"width": 2160, "height": 3840, "label": "🌟 2160x3840 (4K Ultra HD Vertical 9:16)", "bitrate": "28000k"},
    "square": {"width": 1080, "height": 1080, "label": "⏹️ 1080x1080 (1:1 Square Feed)", "bitrate": "5500k"},
}


class ExportConfig:
    """Settings for rendering individual or batch clips in 480p, 720p, 1080p, 2K, or 4K."""
    def __init__(
        self,
        framing_mode: str = FramingMode.SMART_TRACK,
        burn_subtitles: bool = True,
        subtitle_style: Optional[SubtitleStyle] = None,
        enable_zoom_effect: bool = True,
        sound_effect: str = SoundEffectType.WHOOSH,
        resolution_preset: str = ResolutionPreset.FHD_1080P,
        output_width: Optional[int] = None,
        output_height: Optional[int] = None,
        fps: int = 30,
        video_bitrate: Optional[str] = None,
        audio_bitrate: str = "192k",
    ):
        self.framing_mode = framing_mode
        self.burn_subtitles = burn_subtitles
        self.subtitle_style = subtitle_style or SubtitleStyle()
        self.enable_zoom_effect = enable_zoom_effect
        self.sound_effect = sound_effect
        self.resolution_preset = resolution_preset
        
        # Resolve width & height from preset if not explicitly overridden
        res_meta = RESOLUTION_CONFIGS.get(resolution_preset, RESOLUTION_CONFIGS["1080p"])
        self.output_width = output_width or res_meta["width"]
        self.output_height = output_height or res_meta["height"]
        
        self.fps = fps
        # Auto-calibrate bitrate across 480p, 720p, 1080p, 2K, 4K
        if video_bitrate:
            self.video_bitrate = video_bitrate
        elif self.output_width >= 2160:
            self.video_bitrate = "28000k"  # Ultra HD 4K
        elif self.output_width >= 1440:
            self.video_bitrate = "14000k"  # 2K QHD
        elif self.output_width >= 1080:
            self.video_bitrate = "6500k"   # Full HD 1080p
        elif self.output_width >= 720:
            self.video_bitrate = "3500k"   # HD 720p
        else:
            self.video_bitrate = "1800k"   # SD 480p Mobile

        self.audio_bitrate = audio_bitrate


class VideoProcessor:
    """Coordinates video transformation and export using FFmpeg."""

    def __init__(self, output_dir: Optional[str] = None, temp_dir: Optional[str] = None):
        project_root = Path(__file__).resolve().parent.parent.parent
        self.output_dir = output_dir or str(project_root / "output")
        self.temp_dir = temp_dir or str(project_root / "temp")
        os.makedirs(self.output_dir, exist_ok=True)
        os.makedirs(self.temp_dir, exist_ok=True)

        self.effects_mgr = EffectsManager()
        self.face_tracker = SmartFaceTracker()

    def generate_clip_thumbnail(
        self,
        video_path: str,
        timestamp: float,
        output_thumb_path: str,
        target_w: int = 360,
        target_h: int = 640,
    ) -> bool:
        """Extracts a vertical 9:16 thumbnail image from video at specified timestamp."""
        os.makedirs(os.path.dirname(os.path.abspath(output_thumb_path)), exist_ok=True)
        # Scale to 9:16 center thumbnail
        args = [
            "-ss", f"{timestamp:.2f}",
            "-i", video_path,
            "-vframes", "1",
            "-vf", f"scale={target_w}:{target_h}:force_original_aspect_ratio=increase,crop={target_w}:{target_h}",
            output_thumb_path,
        ]
        success, _ = run_ffmpeg(args)
        return success and os.path.isfile(output_thumb_path)

    def render_clip(
        self,
        input_video_path: str,
        clip: VideoClipCandidate,
        config: ExportConfig,
        custom_output_path: Optional[str] = None,
        crop_trajectory: Optional[SmoothCropTrajectory] = None,
        progress_callback: Optional[Callable[[int, str], None]] = None,
    ) -> Optional[str]:
        """
        Renders a fully processed vertical 9:16 clip:
        - Precise segment trimming
        - 9:16 Smart Face Track / Blurred Canvas / Center crop
        - Animated Subtitles burned into video
        - Optional Zoom Punch-in
        - Optional Sound Effects mixed into audio
        - Encoded to 1080x1920 H.264 MP4
        """
        if not os.path.isfile(input_video_path):
            raise FileNotFoundError(f"Input video not found: {input_video_path}")

        clip_id_str = f"clip_{clip.clip_id:02d}"
        res_tag = "4k" if config.output_width >= 2160 else ("2k" if config.output_width >= 1440 else "1080p")
        if custom_output_path:
            out_mp4 = custom_output_path
        else:
            safe_name = f"ClipFusion_{clip_id_str}_{res_tag}_{int(clip.start_time)}s_to_{int(clip.end_time)}s.mp4"
            out_mp4 = os.path.join(self.output_dir, safe_name)

        clip_temp_dir = os.path.join(self.temp_dir, clip_id_str)
        os.makedirs(clip_temp_dir, exist_ok=True)

        duration = max(1.0, clip.end_time - clip.start_time)
        logger.info(f"Rendering {clip_id_str} ({clip.start_time:.2f}s - {clip.end_time:.2f}s, dur: {duration:.2f}s)")

        if progress_callback:
            progress_callback(10, f"Initializing export for Clip #{clip.clip_id}...")

        # Step 1: Generate ASS subtitle file if subtitles enabled
        ass_path = None
        if config.burn_subtitles:
            # Flatten words or interpolate from segments/transcript
            all_words = []
            if clip.segments:
                for seg in clip.segments:
                    words = seg.get("words", [])
                    if words:
                        all_words.extend(words)
                    elif seg.get("text"):
                        # Interpolate word timestamps across segment duration
                        seg_text = seg["text"].strip()
                        seg_start = seg.get("start", clip.start_time)
                        seg_end = seg.get("end", clip.end_time)
                        tokens = seg_text.split()
                        if tokens:
                            dt = max(0.1, (seg_end - seg_start) / float(len(tokens)))
                            for idx, token in enumerate(tokens):
                                all_words.append({
                                    "word": token,
                                    "start": seg_start + idx * dt,
                                    "end": seg_start + (idx + 1) * dt,
                                })
            elif clip.transcript_text:
                # Interpolate from clip transcript text
                tokens = clip.transcript_text.split()
                if tokens:
                    dt = max(0.1, duration / float(len(tokens)))
                    for idx, token in enumerate(tokens):
                        all_words.append({
                            "word": token,
                            "start": clip.start_time + idx * dt,
                            "end": clip.start_time + (idx + 1) * dt,
                        })

            if all_words:
                sub_gen = SubtitleGenerator(style=config.subtitle_style)
                ass_path = os.path.join(clip_temp_dir, f"{clip_id_str}_subtitles.ass")
                sub_gen.generate_ass_file(
                    words_list=all_words,
                    output_ass_path=ass_path,
                    video_width=config.output_width,
                    video_height=config.output_height,
                    time_offset=clip.start_time,
                )

        if progress_callback:
            progress_callback(30, "Configuring 9:16 vertical crop & visual framing...")

        # Step 2: Build Video Filter Chain
        vf_filters: List[str] = []
        complex_video_graph = None

        if config.framing_mode == FramingMode.SPLIT_SCREEN:
            # Opus Clip Split Screen (Streamer Facecam Top + Gameplay Bottom)
            is_complex_video = True
            face_box = None
            orig_w = crop_trajectory.orig_w if crop_trajectory else 1920
            orig_h = crop_trajectory.orig_h if crop_trajectory else 1080
            if crop_trajectory and crop_trajectory.keyframes:
                face_box = (crop_trajectory.keyframes[0][1], 0, crop_trajectory.crop_w, crop_trajectory.crop_h)
            complex_video_graph = self.face_tracker.build_split_screen_filter(
                face_box=face_box,
                orig_w=orig_w,
                orig_h=orig_h,
                target_w=config.output_width,
                target_h=config.output_height,
            )
        elif config.framing_mode == FramingMode.BLURRED_CANVAS:
            # Canvas with blurred background
            is_complex_video = True
            complex_video_graph = self.face_tracker.build_blurred_canvas_filter(
                target_w=config.output_width,
                target_h=config.output_height,
            )
        else:
            is_complex_video = False
            if crop_trajectory is not None and config.framing_mode == FramingMode.SMART_TRACK:
                crop_scale = self.face_tracker.build_ffmpeg_crop_filter(
                    crop_trajectory,
                    target_w=config.output_width,
                    target_h=config.output_height,
                )
                vf_filters.append(crop_scale)
            else:
                # Center crop to 9:16
                vf_filters.append(
                    f"crop=ih*9/16:ih:(iw-ih*9/16)/2:0,scale={config.output_width}:{config.output_height}:flags=lanczos"
                )

        # Step 3: Add Zoom Punch effect if enabled
        if config.enable_zoom_effect and duration >= 5.0 and not is_complex_video:
            punch_t = min(3.0, duration * 0.2)
            punch_dur = min(3.5, duration * 0.35)
            zoom_f = self.effects_mgr.build_zoom_filter(
                enable_zoom=True,
                punch_time=punch_t,
                punch_duration=punch_dur,
                zoom_factor=1.15,
                target_w=config.output_width,
                target_h=config.output_height,
            )
            if zoom_f:
                vf_filters.append(zoom_f)

        # Step 4: Burn subtitles
        if ass_path and os.path.isfile(ass_path):
            # Format path for FFmpeg filter (escape colons and backslashes for Windows)
            escaped_ass = ass_path.replace("\\", "/").replace(":", "\\:")
            # Use 'ass' filter if supported, or 'subtitles' filter
            vf_filters.append(f"ass='{escaped_ass}'")

        if progress_callback:
            progress_callback(50, "Preparing audio mixing & sound effects...")

        # Step 5: Sound Effects & Audio Mixing
        sfx_path = self.effects_mgr.get_sound_path(config.sound_effect)
        extra_inputs = []
        filter_complex_parts = []

        if sfx_path and os.path.isfile(sfx_path):
            sfx_in_args, sfx_filter = self.effects_mgr.build_audio_mix_filter(
                sfx_path=sfx_path,
                sfx_start_time=0.2,
                sfx_volume=0.45,
            )
            extra_inputs.extend(sfx_in_args)

        if progress_callback:
            progress_callback(70, f"Encoding 1080x1920 MP4 with FFmpeg...")

        # Step 6: Assemble full FFmpeg command
        cmd_args = [
            "-ss", f"{clip.start_time:.3f}",
            "-t", f"{duration:.3f}",
            "-i", input_video_path,
        ]
        cmd_args.extend(extra_inputs)

        # Filter construction
        if is_complex_video:
            video_base = complex_video_graph
            if ass_path and os.path.isfile(ass_path):
                escaped_ass = ass_path.replace("\\", "/").replace(":", "\\:")
                video_graph = f"{video_base},ass='{escaped_ass}'[vout]"
            else:
                video_graph = f"{video_base}[vout]"

            if extra_inputs and sfx_path:
                delay_ms = 200
                full_complex = (
                    f"{video_graph};"
                    f"[1:a]adelay={delay_ms}|{delay_ms},volume=0.45[sfx_delayed];"
                    f"[0:a][sfx_delayed]amix=inputs=2:duration=first[aout]"
                )
                cmd_args.extend(["-filter_complex", full_complex, "-map", "[vout]", "-map", "[aout]"])
            else:
                cmd_args.extend(["-filter_complex", video_graph, "-map", "[vout]", "-map", "0:a?"])
        else:
            # Standard vf chain
            combined_vf = ",".join(vf_filters) if vf_filters else f"scale={config.output_width}:{config.output_height}"
            if extra_inputs and sfx_path:
                delay_ms = 200
                full_complex = (
                    f"[0:v]{combined_vf}[vout];"
                    f"[1:a]adelay={delay_ms}|{delay_ms},volume=0.45[sfx_delayed];"
                    f"[0:a][sfx_delayed]amix=inputs=2:duration=first[aout]"
                )
                cmd_args.extend(["-filter_complex", full_complex, "-map", "[vout]", "-map", "[aout]"])
            else:
                cmd_args.extend(["-vf", combined_vf, "-map", "0:v", "-map", "0:a?"])

        # Encoding parameters for ultra compatibility: H.264 High Profile, AAC 192k
        cmd_args.extend([
            "-c:v", "libx264",
            "-preset", "fast",
            "-crf", "19",
            "-pix_fmt", "yuv420p",
            "-c:a", "aac",
            "-b:a", config.audio_bitrate,
            "-r", str(config.fps),
            out_mp4,
        ])

        success, msg = run_ffmpeg(cmd_args, timeout=300)

        # If subtitle filter caused an issue (e.g. fontconfig cache on Windows), fallback to render without ASS filter
        if not success and "ass" in msg.lower():
            logger.warning("ASS filter issue detected. Re-attempting export without ASS burning...")
            clean_vf = [f for f in vf_filters if "ass=" not in f]
            cmd_args_fallback = [
                "-ss", f"{clip.start_time:.3f}",
                "-t", f"{duration:.3f}",
                "-i", input_video_path,
                "-vf", ",".join(clean_vf) if clean_vf else f"scale={config.output_width}:{config.output_height}",
                "-c:v", "libx264",
                "-preset", "fast",
                "-crf", "19",
                "-pix_fmt", "yuv420p",
                "-c:a", "aac",
                out_mp4,
            ]
            success, msg = run_ffmpeg(cmd_args_fallback, timeout=300)

        if not success:
            logger.error(f"Render failed: {msg}")
            if progress_callback:
                progress_callback(100, f"Render error: {msg[:100]}...")
            return None

        if progress_callback:
            progress_callback(100, f"Successfully exported {os.path.basename(out_mp4)}!")

        return out_mp4 if os.path.isfile(out_mp4) else None

    def batch_render_clips(
        self,
        input_video_path: str,
        clips: List[VideoClipCandidate],
        config: ExportConfig,
        trajectories: Optional[Dict[int, SmoothCropTrajectory]] = None,
        progress_callback: Optional[Callable[[int, str], None]] = None,
    ) -> List[str]:
        """Renders multiple clips sequentially with total progress reporting."""
        rendered_paths: List[str] = []
        total = len(clips)
        if total == 0:
            return rendered_paths

        for i, clip in enumerate(clips):
            step_base = int((i / float(total)) * 100)
            step_span = int(100 / float(total))

            def sub_callback(pct, message):
                overall = step_base + int((pct / 100.0) * step_span)
                if progress_callback:
                    progress_callback(overall, f"[Clip {i+1}/{total}] {message}")

            traj = trajectories.get(clip.clip_id) if trajectories else None
            out_file = self.render_clip(
                input_video_path=input_video_path,
                clip=clip,
                config=config,
                crop_trajectory=traj,
                progress_callback=sub_callback,
            )
            if out_file:
                rendered_paths.append(out_file)

        if progress_callback:
            progress_callback(100, f"Rendered {len(rendered_paths)}/{total} clips successfully!")

        return rendered_paths

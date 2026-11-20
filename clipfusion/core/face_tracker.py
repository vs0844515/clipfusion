"""Smart Face Tracking and Auto-Reframing Engine for ClipFusion.
Calculates smooth 9:16 camera panning following the active speaker without jitter.
"""

import math
import logging
from typing import Dict, List, Optional, Tuple
import cv2
import numpy as np

from clipfusion.core.visual_analyzer import VisualAnalysisResult

logger = logging.getLogger("clipfusion.tracker")


class FramingMode:
    SMART_TRACK = "smart_track"
    SPLIT_SCREEN = "split_screen"
    CENTER_CROP = "center_crop"
    BLURRED_CANVAS = "blurred_background"


class SmoothCropTrajectory:
    """Represents time-varying crop coordinates for FFmpeg dynamic crop or frame rendering."""

    def __init__(self, target_aspect: float = 9 / 16):
        self.target_aspect = target_aspect  # 9:16 = 0.5625
        self.crop_w = 0
        self.crop_h = 0
        self.orig_w = 0
        self.orig_h = 0
        # List of (timestamp, x_offset, y_offset)
        self.keyframes: List[Tuple[float, int, int]] = []

    def get_crop_at(self, timestamp: float) -> Tuple[int, int, int, int]:
        """Returns (x, y, w, h) crop window at a given timestamp."""
        if not self.keyframes:
            x = max(0, (self.orig_w - self.crop_w) // 2)
            y = max(0, (self.orig_h - self.crop_h) // 2)
            return (x, y, self.crop_w, self.crop_h)

        # Binary search or interpolation between keyframes
        times = [k[0] for k in self.keyframes]
        idx = np.searchsorted(times, timestamp)

        if idx == 0:
            return (self.keyframes[0][1], self.keyframes[0][2], self.crop_w, self.crop_h)
        if idx >= len(self.keyframes):
            return (self.keyframes[-1][1], self.keyframes[-1][2], self.crop_w, self.crop_h)

        t0, x0, y0 = self.keyframes[idx - 1]
        t1, x1, y1 = self.keyframes[idx]

        alpha = (timestamp - t0) / max(0.001, t1 - t0)
        x = int(x0 + alpha * (x1 - x0))
        y = int(y0 + alpha * (y1 - y0))
        return (x, y, self.crop_w, self.crop_h)


class SmartFaceTracker:
    """Computes smooth vertical 9:16 framing trajectory using face and subject coordinates."""

    def __init__(self, smoothing_factor: float = 0.15, deadband_px: int = 25):
        """
        smoothing_factor: EMA weight (0.05 = super smooth/slow, 0.3 = rapid tracking)
        deadband_px: ignore micro-movements smaller than this threshold to avoid camera twitching
        """
        self.alpha = smoothing_factor
        self.deadband = deadband_px

    def compute_trajectory(
        self,
        visual_result: VisualAnalysisResult,
        clip_start: float,
        clip_end: float,
        mode: str = FramingMode.SMART_TRACK,
    ) -> SmoothCropTrajectory:
        """Calculates smooth 9:16 crop window across the clip duration."""
        orig_w = visual_result.width
        orig_h = visual_result.height
        trajectory = SmoothCropTrajectory(target_aspect=9 / 16)
        trajectory.orig_w = orig_w
        trajectory.orig_h = orig_h

        # Calculate 9:16 crop dimensions
        # For a standard 16:9 video (e.g. 1920x1080), height remains 1080, crop_w = 1080 * 9 / 16 = 608
        target_aspect = 9.0 / 16.0
        current_aspect = orig_w / max(1.0, orig_h)

        if current_aspect > target_aspect:
            # Video is wider than 9:16 (standard landscape)
            crop_h = orig_h
            crop_w = int(round(crop_h * target_aspect))
            # Ensure width is even for H.264
            crop_w = crop_w if crop_w % 2 == 0 else crop_w - 1
        else:
            # Video is taller than 9:16
            crop_w = orig_w
            crop_h = int(round(crop_w / target_aspect))
            crop_h = crop_h if crop_h % 2 == 0 else crop_h - 1

        trajectory.crop_w = crop_w
        trajectory.crop_h = crop_h

        max_x = max(0, orig_w - crop_w)
        max_y = max(0, orig_h - crop_h)
        default_x = max_x // 2
        default_y = max_y // 2

        if mode == FramingMode.CENTER_CROP or mode == FramingMode.BLURRED_CANVAS:
            # Fixed center framing
            trajectory.keyframes.append((clip_start, default_x, default_y))
            trajectory.keyframes.append((clip_end, default_x, default_y))
            return trajectory

        # Mode: SMART_TRACK
        # Collect sampled face points in the interval
        interval = visual_result.sample_interval
        s_idx = max(0, int(clip_start / interval))
        e_idx = min(len(visual_result.frames), int(clip_end / interval) + 1)
        sub_frames = visual_result.frames[s_idx:e_idx]

        if not sub_frames:
            trajectory.keyframes.append((clip_start, default_x, default_y))
            trajectory.keyframes.append((clip_end, default_x, default_y))
            return trajectory

        # Initialize current smoothed X center
        first_face = sub_frames[0].primary_face_box
        if first_face is not None:
            init_center_x = first_face[0] + first_face[2] // 2
        else:
            init_center_x = orig_w // 2

        smoothed_x = float(np.clip(init_center_x - crop_w // 2, 0, max_x))

        for frame in sub_frames:
            t = frame.timestamp
            target_cx = None
            if frame.primary_face_box is not None:
                # Primary face center
                face_box = frame.primary_face_box
                target_cx = face_box[0] + face_box[2] // 2
            elif getattr(frame, "subject_center_x", None) is not None:
                # Subject motion center-of-mass
                target_cx = frame.subject_center_x

            if target_cx is not None:
                target_x = float(np.clip(target_cx - crop_w // 2, 0, max_x))
                if abs(target_x - smoothed_x) > self.deadband:
                    smoothed_x = self.alpha * target_x + (1.0 - self.alpha) * smoothed_x
            else:
                smoothed_x = 0.05 * default_x + 0.95 * smoothed_x

            clamp_x = int(round(np.clip(smoothed_x, 0, max_x)))
            # Ensure even offset
            clamp_x = clamp_x if clamp_x % 2 == 0 else clamp_x - 1
            trajectory.keyframes.append((t, clamp_x, default_y))

        return trajectory

    def build_ffmpeg_crop_filter(
        self,
        trajectory: SmoothCropTrajectory,
        target_w: int = 1080,
        target_h: int = 1920,
    ) -> str:
        """Constructs an FFmpeg filter string for cropping and scaling to 1080x1920."""
        # Check if crop position is approximately stationary
        if not trajectory.keyframes:
            return f"crop={trajectory.crop_w}:{trajectory.crop_h},scale={target_w}:{target_h}"

        x_coords = [k[1] for k in trajectory.keyframes]
        x_min, x_max = min(x_coords), max(x_coords)

        # If pan distance is small (< 30px), lock to median for maximum visual clarity & speed
        if (x_max - x_min) < 30 or len(trajectory.keyframes) < 3:
            median_x = int(np.median(x_coords))
            median_x = median_x if median_x % 2 == 0 else median_x - 1
            return (
                f"crop={trajectory.crop_w}:{trajectory.crop_h}:{median_x}:0,"
                f"scale={target_w}:{target_h}:flags=lanczos"
            )

        # Dynamic smooth camera glide using polynomial regression following the subject
        try:
            t0 = trajectory.keyframes[0][0]
            rel_times = np.array([max(0.0, k[0] - t0) for k in trajectory.keyframes], dtype=np.float32)
            xs = np.array(x_coords, dtype=np.float32)
            max_x = max(0, trajectory.orig_w - trajectory.crop_w)

            # Fit 2nd degree polynomial for cinematic smooth camera pan
            deg = 2 if len(rel_times) >= 5 else 1
            coeffs = np.polyfit(rel_times, xs, deg)

            if deg == 2:
                a, b, c = coeffs[0], coeffs[1], coeffs[2]
                poly_expr = f"{a:.5f}*t*t{b:+.4f}*t{c:+.2f}"
            else:
                m, c = coeffs[0], coeffs[1]
                poly_expr = f"{m:.4f}*t{c:+.2f}"

            crop_x_expr = f"min(max(0,{poly_expr}),{max_x})"
            return (
                f"crop={trajectory.crop_w}:{trajectory.crop_h}:'{crop_x_expr}':0,"
                f"scale={target_w}:{target_h}:flags=lanczos"
            )
        except Exception as e:
            logger.warning(f"Failed to generate dynamic crop polynomial ({e}), falling back to median crop.")
            median_x = int(np.median(x_coords))
            median_x = median_x if median_x % 2 == 0 else median_x - 1
            return (
                f"crop={trajectory.crop_w}:{trajectory.crop_h}:{median_x}:0,"
                f"scale={target_w}:{target_h}:flags=lanczos"
            )

    def build_split_screen_filter(
        self,
        face_box: Optional[Tuple[int, int, int, int]] = None,
        orig_w: int = 1280,
        orig_h: int = 720,
        target_w: int = 1080,
        target_h: int = 1920,
    ) -> str:
        """
        Constructs Opus Clip signature Split Screen:
        Top: Speaker / Facecam (height 768px)
        Bottom: Gameplay / Main Action (height 1152px)
        Stacked vertically into 1080x1920.
        """
        top_h = 768
        bot_h = 1152

        # 1. Top facecam crop
        if face_box is not None:
            fx, fy, fw, fh = face_box
            pad = int(max(fw, fh) * 0.45)
            cx, cy = fx + fw // 2, fy + fh // 2
            cw = min(orig_w, fw + pad * 2)
            ch = min(orig_h, int(cw * (top_h / target_w)))
            cx = max(0, min(orig_w - cw, cx - cw // 2))
            cy = max(0, min(orig_h - ch, cy - ch // 2))
            top_filter = f"crop={cw}:{ch}:{cx}:{cy},scale={target_w}:{top_h}:flags=lanczos"
        else:
            cw = int(orig_w * 0.45)
            ch = int(cw * (top_h / target_w))
            top_filter = f"crop={cw}:{ch}:0:0,scale={target_w}:{top_h}:flags=lanczos"

        # 2. Bottom gameplay crop: center 16:9 or 9:16 slice
        bot_cw = int(orig_h * (target_w / bot_h))
        bot_cw = min(orig_w, max(100, bot_cw))
        bot_cx = max(0, (orig_w - bot_cw) // 2)
        bot_filter = f"crop={bot_cw}:{orig_h}:{bot_cx}:0,scale={target_w}:{bot_h}:flags=lanczos"

        return f"[0:v]split=2[in_top][in_bot];[in_top]{top_filter}[top_v];[in_bot]{bot_filter}[bot_v];[top_v][bot_v]vstack"

    def build_blurred_canvas_filter(
        self,
        target_w: int = 1080,
        target_h: int = 1920,
    ) -> str:
        """Constructs FFmpeg filter for blurred canvas 9:16 background with sharp video centered."""
        return (
            f"[0:v]split=2[bg_in][fg_in];"
            f"[bg_in]scale={target_w}:{target_h}:force_original_aspect_ratio=increase,"
            f"crop={target_w}:{target_h},"
            f"boxblur=20:5[bg];"
            f"[fg_in]scale={target_w}:-2:force_original_aspect_ratio=decrease[fg];"
            f"[bg][fg]overlay=(W-w)/2:(H-h)/2"
        )

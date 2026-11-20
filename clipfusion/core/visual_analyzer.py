"""Visual analysis engine for ClipFusion.
Analyzes frame dynamics, motion energy, shot transitions, and face presence using OpenCV.
"""

import os
import cv2
import numpy as np
import logging
from typing import Dict, List, Any, Optional, Tuple

logger = logging.getLogger("clipfusion.visual")


class FrameAnalysis:
    """Analysis data for a single sampled video frame."""
    def __init__(self, timestamp: float, frame_index: int):
        self.timestamp = timestamp
        self.frame_index = frame_index
        self.motion_score = 0.0
        self.is_scene_cut = False
        self.face_count = 0
        self.primary_face_box: Optional[Tuple[int, int, int, int]] = None  # (x, y, w, h)
        self.subject_center_x: Optional[int] = None                        # Center-of-mass of motion/subject
        self.face_score = 0.0


class VisualAnalysisResult:
    """Aggregated visual metrics for the video."""
    def __init__(self, duration: float, fps: float, width: int, height: int):
        self.duration = duration
        self.fps = fps
        self.width = width
        self.height = height
        self.sample_interval = 0.5  # 2 fps sampling rate for fast processing
        self.frames: List[FrameAnalysis] = []
        self.scene_cuts: List[float] = []
        self.avg_motion = 0.0
        self.face_coverage_ratio = 0.0

    def get_motion_at(self, timestamp: float) -> float:
        """Returns visual motion score at a given timestamp."""
        if not self.frames:
            return 0.0
        idx = min(len(self.frames) - 1, max(0, int(timestamp / self.sample_interval)))
        return self.frames[idx].motion_score

    def get_face_at(self, timestamp: float) -> Optional[Tuple[int, int, int, int]]:
        """Returns primary face bbox (x, y, w, h) at a given timestamp."""
        if not self.frames:
            return None
        idx = min(len(self.frames) - 1, max(0, int(timestamp / self.sample_interval)))
        return self.frames[idx].primary_face_box


class VisualAnalyzer:
    """Extracts visual dynamics, shot boundaries, and face tracking data."""

    def __init__(self, sample_interval: float = 0.5):
        self.sample_interval = sample_interval
        self._face_cascade = None
        self._yunet_detector = None
        self._init_face_detectors()

    def _init_face_detectors(self):
        """Initializes available face detectors (Haar, YuNet ONNX, or color/geometry)."""
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

        # 1. Check for YuNet ONNX model if FaceDetectorYN is available
        yunet_path = os.path.join(project_root, "assets", "face_detection_yunet.onnx")
        if hasattr(cv2, "FaceDetectorYN") and os.path.isfile(yunet_path):
            try:
                self._yunet_detector = cv2.FaceDetectorYN.create(
                    model=yunet_path,
                    config="",
                    input_size=(640, 360),
                    score_threshold=0.6,
                    nms_threshold=0.3,
                )
                logger.info("Initialized YuNet neural face detector.")
            except Exception as e:
                logger.warning(f"Could not load YuNet detector: {e}")

        # 2. Check for Haar Cascade if CascadeClassifier is available in this OpenCV build
        if hasattr(cv2, "CascadeClassifier"):
            candidates = [
                os.path.join(project_root, "assets", "haarcascade_frontalface_default.xml"),
                cv2.data.haarcascades + "haarcascade_frontalface_default.xml" if hasattr(cv2, "data") and hasattr(cv2.data, "haarcascades") else "",
            ]
            for c_path in candidates:
                if c_path and os.path.isfile(c_path):
                    try:
                        self._face_cascade = cv2.CascadeClassifier(c_path)
                        logger.info(f"Loaded Haar face cascade detector from {c_path}")
                        break
                    except Exception as e:
                        logger.warning(f"Failed to load cascade from {c_path}: {e}")

    def detect_face_box(
        self,
        small_frame: np.ndarray,
        gray: np.ndarray,
        orig_w: int,
        orig_h: int,
        scale: float,
    ) -> Tuple[Optional[Tuple[int, int, int, int]], float]:
        """
        Detects the primary face bounding box (ox, oy, ow, oh) in original coordinates.
        Uses Haar -> YuNet -> Skin/Geometry multi-tier detection with high reliability.
        """
        inv_scale = 1.0 / max(scale, 1e-6)
        sh, sw = small_frame.shape[:2]

        # Tier 1: Haar cascade (if supported)
        if self._face_cascade is not None:
            try:
                faces = self._face_cascade.detectMultiScale(
                    gray,
                    scaleFactor=1.15,
                    minNeighbors=4,
                    minSize=(25, 25),
                )
                if len(faces) > 0:
                    best = max(faces, key=lambda f: f[2] * f[3])
                    ox = int(best[0] * inv_scale)
                    oy = int(best[1] * inv_scale)
                    ow = int(best[2] * inv_scale)
                    oh = int(best[3] * inv_scale)
                    area_ratio = (ow * oh) / float(orig_w * orig_h)
                    score = min(1.0, area_ratio * 10.0 + 0.3)
                    return (ox, oy, ow, oh), score
            except Exception:
                pass

        # Tier 2: YuNet Neural Face Detector (if available)
        if self._yunet_detector is not None:
            try:
                self._yunet_detector.setInputSize((sw, sh))
                _, faces = self._yunet_detector.detect(small_frame)
                if faces is not None and len(faces) > 0:
                    # Sort by confidence or size
                    best_f = max(faces, key=lambda f: f[2] * f[3])
                    ox = int(best_f[0] * inv_scale)
                    oy = int(best_f[1] * inv_scale)
                    ow = int(best_f[2] * inv_scale)
                    oh = int(best_f[3] * inv_scale)
                    conf = float(best_f[14]) if len(best_f) > 14 else 0.85
                    return (ox, oy, ow, oh), min(1.0, conf)
            except Exception:
                pass

        # Tier 3: Skin-Tone & Facial Ellipse Geometry Detector
        try:
            ycrcb = cv2.cvtColor(small_frame, cv2.COLOR_BGR2YCrCb)
            mask = cv2.inRange(ycrcb, np.array([0, 133, 77]), np.array([255, 173, 127]))
            kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
            mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
            mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
            contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            candidates = []
            min_area = (sw * sh) * 0.008
            max_area = (sw * sh) * 0.6
            for c in contours:
                area = cv2.contourArea(c)
                if min_area <= area <= max_area:
                    x, y, cw, ch = cv2.boundingRect(c)
                    aspect = ch / max(1.0, float(cw))
                    if 0.60 <= aspect <= 2.8:
                        cx = x + cw / 2.0
                        cy = y + ch / 2.0
                        center_dist = abs(cx - sw / 2.0) / (sw / 2.0)
                        upper_bias = 1.0 if cy < sh * 0.75 else 0.5
                        rank_score = (area / max_area) * 2.0 + (1.0 - center_dist) * 1.5 + upper_bias
                        candidates.append((x, y, cw, ch, rank_score, area))

            if candidates:
                best = max(candidates, key=lambda item: item[4])
                bx, by, bw, bh = best[0], best[1], best[2], best[3]
                ox = int(bx * inv_scale)
                oy = int(by * inv_scale)
                ow = int(bw * inv_scale)
                oh = int(bh * inv_scale)
                area_ratio = (ow * oh) / float(orig_w * orig_h)
                score = min(1.0, area_ratio * 8.0 + 0.25)
                return (ox, oy, ow, oh), score
        except Exception:
            pass

        return None, 0.0

    def analyze_video(
        self,
        video_path: str,
        progress_callback=None,
    ) -> VisualAnalysisResult:
        """Processes video frames to extract motion, cuts, and face presence."""
        if not os.path.isfile(video_path):
            raise FileNotFoundError(f"Video file not found: {video_path}")

        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            raise IOError(f"Could not open video file {video_path}")

        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        duration = total_frames / fps if total_frames > 0 and fps > 0 else 0.0

        result = VisualAnalysisResult(duration=duration, fps=fps, width=width, height=height)
        result.sample_interval = self.sample_interval

        # Step size in frames
        frame_step = max(1, int(round(fps * self.sample_interval)))

        prev_gray = None
        prev_hist = None
        current_frame_idx = 0
        analyzed_count = 0
        face_detected_count = 0
        total_motion = 0.0

        while current_frame_idx < total_frames or total_frames == 0:
            cap.set(cv2.CAP_PROP_POS_FRAMES, current_frame_idx)
            ret, frame = cap.read()
            if not ret or frame is None:
                break

            timestamp = current_frame_idx / fps
            frame_data = FrameAnalysis(timestamp=timestamp, frame_index=current_frame_idx)

            # Resize to smaller resolution for high-speed analysis (e.g. 360p)
            h, w = frame.shape[:2]
            scale = 360.0 / max(h, 1)
            small_w = max(1, int(w * scale))
            small_h = 360
            small_frame = cv2.resize(frame, (small_w, small_h), interpolation=cv2.INTER_AREA)
            gray = cv2.cvtColor(small_frame, cv2.COLOR_BGR2GRAY)

            # 1. Motion dynamics calculation
            if prev_gray is not None:
                diff = cv2.absdiff(gray, prev_gray)
                motion_val = float(np.mean(diff)) / 255.0
                frame_data.motion_score = min(1.0, motion_val * 4.0)  # scale to [0, 1]
                total_motion += frame_data.motion_score

                # 2. Subject motion center-of-mass tracking
                _, diff_thresh = cv2.threshold(diff, 20, 255, cv2.THRESH_BINARY)
                M = cv2.moments(diff_thresh)
                if M["m00"] > 80:
                    cx_small = int(M["m10"] / M["m00"])
                    frame_data.subject_center_x = int(cx_small * (1.0 / scale))

                # 3. Scene cut detection using HSV histogram correlation
                hsv = cv2.cvtColor(small_frame, cv2.COLOR_BGR2HSV)
                hist = cv2.calcHist([hsv], [0, 1], None, [16, 16], [0, 180, 0, 256])
                cv2.normalize(hist, hist, 0, 1, cv2.NORM_MINMAX)

                if prev_hist is not None:
                    similarity = cv2.compareHist(hist, prev_hist, cv2.HISTCMP_CORREL)
                    if similarity < 0.35:  # Significant visual shift
                        frame_data.is_scene_cut = True
                        result.scene_cuts.append(round(timestamp, 2))

                prev_hist = hist
            else:
                hsv = cv2.cvtColor(small_frame, cv2.COLOR_BGR2HSV)
                prev_hist = cv2.calcHist([hsv], [0, 1], None, [16, 16], [0, 180, 0, 256])
                cv2.normalize(prev_hist, prev_hist, 0, 1, cv2.NORM_MINMAX)

            prev_gray = gray

            # 3. Multi-tier face detection
            face_box, face_score = self.detect_face_box(
                small_frame=small_frame,
                gray=gray,
                orig_w=width,
                orig_h=height,
                scale=scale,
            )
            if face_box is not None:
                face_detected_count += 1
                frame_data.face_count = 1
                frame_data.primary_face_box = face_box
                frame_data.face_score = face_score

            result.frames.append(frame_data)
            analyzed_count += 1
            current_frame_idx += frame_step

            # Report progress
            if progress_callback and analyzed_count % 15 == 0 and duration > 0:
                pct = min(40 + int((timestamp / duration) * 20), 60)
                progress_callback(pct, f"Analyzing visual dynamics & faces: {int(timestamp)}s / {int(duration)}s")

        cap.release()

        if analyzed_count > 0:
            result.avg_motion = total_motion / analyzed_count
            result.face_coverage_ratio = face_detected_count / analyzed_count

        return result

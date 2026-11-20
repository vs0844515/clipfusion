"""Audio analysis and speech transcription engine for ClipFusion.
Analyzes RMS energy, pitch/cadence dynamics, silence boundaries, and Whisper word-level transcription.
"""

import os
import re
import math
import logging
from typing import Dict, List, Any, Optional, Tuple
import numpy as np

logger = logging.getLogger("clipfusion.audio")

# High-engagement and emotional indicator keywords with weights
ENGAGEMENT_KEYWORDS = {
    # High excitement / shock
    "insane": 3.0, "crazy": 3.0, "unbelievable": 3.5, "omg": 3.5, "what": 2.0,
    "no way": 3.5, "mind-blowing": 4.0, "shocking": 3.5, "wtf": 3.5, "boom": 2.5,
    "impossible": 3.0, "unreal": 3.0, "disaster": 3.0, "genius": 3.0,
    
    # Curiosity hooks & secrets
    "secret": 3.5, "never": 2.5, "always": 2.0, "listen": 2.5, "stop": 3.0,
    "mistake": 3.0, "hack": 3.0, "trick": 2.5, "truth": 3.0, "exposed": 3.5,
    "warning": 3.0, "danger": 3.0, "hidden": 3.0, "revealed": 3.5, "wait": 2.5,
    
    # Entertainment / reaction
    "hilarious": 3.0, "laugh": 2.5, "bro": 2.0, "dude": 1.5, "look": 2.0,
    "watch this": 3.5, "died": 2.5, "crying": 2.5, "failed": 3.0,
    
    # Value / Superlatives
    "ultimate": 2.5, "best": 2.0, "worst": 2.5, "easiest": 2.5, "fastest": 2.5,
    "billionaire": 3.0, "money": 2.5, "rich": 2.5, "game changer": 3.5,
}
VIRAL_KEYWORDS = ENGAGEMENT_KEYWORDS


class AudioSegment:
    """Represents a speech segment with timing and transcript."""
    def __init__(self, start: float, end: float, text: str, words: Optional[List[Dict[str, Any]]] = None):
        self.start = float(start)
        self.end = float(end)
        self.text = text.strip()
        self.words = words or []
        self.duration = max(0.0, self.end - self.start)
        self.excitement_score = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "start": round(self.start, 3),
            "end": round(self.end, 3),
            "duration": round(self.duration, 3),
            "text": self.text,
            "words": self.words,
            "excitement_score": round(self.excitement_score, 3),
        }


class AudioAnalysisResult:
    """Container for audio analysis and transcription metrics."""
    def __init__(self, sample_rate: int, duration: float):
        self.sample_rate = sample_rate
        self.duration = duration
        self.time_step = 0.1  # 100ms per energy slice
        self.energy_profile: np.ndarray = np.array([])
        self.zcr_profile: np.ndarray = np.array([])
        self.silence_intervals: List[Tuple[float, float]] = []
        self.pause_timestamps: List[float] = []
        self.segments: List[AudioSegment] = []
        self.avg_energy = 0.0
        self.max_energy = 1.0


class AudioAnalyzer:
    """Performs RMS loudness, spectral dynamics, and local Whisper transcription."""

    def __init__(self, whisper_model_size: str = "base"):
        self.whisper_model_size = whisper_model_size
        self._whisper_model = None

    def _load_whisper(self):
        """Lazy loads local Whisper model."""
        if self._whisper_model is not None:
            return self._whisper_model

        try:
            import whisper
            import torch
            device = "cuda" if torch.cuda.is_available() else "cpu"
            logger.info(f"Loading local Whisper ({self.whisper_model_size}) on {device}...")
            self._whisper_model = whisper.load_model(self.whisper_model_size, device=device)
            return self._whisper_model
        except Exception as e:
            logger.warning(f"Could not load Whisper model ({e}). Fallback mode will be used.")
            return None

    def analyze_audio_file(
        self,
        wav_path: str,
        progress_callback=None,
    ) -> AudioAnalysisResult:
        """Full audio signal analysis: energy curve, silence points, speech cadence."""
        if not os.path.isfile(wav_path):
            raise FileNotFoundError(f"WAV audio file not found: {wav_path}")

        # 1. Read WAV samples
        samples, sr = self._read_wav(wav_path)
        duration = len(samples) / float(sr) if sr > 0 else 0.0
        result = AudioAnalysisResult(sample_rate=sr, duration=duration)

        if duration <= 0:
            return result

        if progress_callback:
            progress_callback(10, "Computing audio energy & loudness profiles...")

        # 2. Windowed RMS energy and Zero-Crossing Rate
        window_size = int(sr * result.time_step)
        if window_size <= 0:
            window_size = 1600

        num_windows = int(len(samples) // window_size)
        if num_windows == 0:
            return result

        energies = np.zeros(num_windows, dtype=np.float32)
        zcrs = np.zeros(num_windows, dtype=np.float32)

        for i in range(num_windows):
            chunk = samples[i * window_size : (i + 1) * window_size]
            rms = np.sqrt(np.mean(chunk**2)) if len(chunk) > 0 else 0.0
            energies[i] = rms

            # Zero-crossing rate (indicates spectral brightness/laughter/energy)
            if len(chunk) > 1:
                zcr = np.mean(np.abs(np.diff(np.sign(chunk)))) / 2.0
                zcrs[i] = zcr

        # Normalize energy profile between 0 and 1
        max_e = float(np.max(energies)) if len(energies) > 0 else 1.0
        if max_e > 1e-6:
            norm_energies = energies / max_e
        else:
            norm_energies = energies

        result.energy_profile = norm_energies
        result.zcr_profile = zcrs
        result.avg_energy = float(np.mean(norm_energies))
        result.max_energy = max_e

        # 3. Detect pauses / silence timestamps for clean clip cuts
        silence_thresh = max(0.04, float(np.percentile(norm_energies, 20)))
        silence_indices = np.where(norm_energies <= silence_thresh)[0]
        
        pause_times = []
        for idx in silence_indices:
            t = round(idx * result.time_step, 2)
            pause_times.append(t)
        result.pause_timestamps = pause_times

        if progress_callback:
            progress_callback(30, "Extracting speech & generating timestamps...")

        # 4. Transcribe speech using Whisper
        model = self._load_whisper()
        if model is not None:
            try:
                trans_result = model.transcribe(
                    wav_path,
                    word_timestamps=True,
                    verbose=False,
                )
                raw_segments = trans_result.get("segments", [])
                for seg in raw_segments:
                    text = seg.get("text", "").strip()
                    s_start = seg.get("start", 0.0)
                    s_end = seg.get("end", 0.0)
                    words_data = []
                    for w in seg.get("words", []):
                        words_data.append({
                            "word": w.get("word", "").strip(),
                            "start": round(w.get("start", s_start), 3),
                            "end": round(w.get("end", s_end), 3),
                            "prob": round(w.get("probability", 1.0), 2),
                        })

                    segment_obj = AudioSegment(
                        start=s_start,
                        end=s_end,
                        text=text,
                        words=words_data,
                    )
                    # Compute keyword excitement score
                    segment_obj.excitement_score = self._score_text_excitement(text)
                    result.segments.append(segment_obj)
            except Exception as e:
                logger.warning(f"Whisper transcription failed, falling back: {e}")

        # Fallback if no segments found (e.g., quiet audio or Whisper absent)
        if not result.segments and duration > 5.0:
            result.segments = self._generate_fallback_segments(duration, norm_energies, result.time_step)

        if progress_callback:
            progress_callback(40, f"Speech analyzed: {len(result.segments)} segments detected.")

        return result

    def _score_text_excitement(self, text: str) -> float:
        """Scores text based on viral keyword density, exclamation, and emotional terms."""
        if not text:
            return 0.0

        lower = text.lower()
        score = 0.0

        for kw, weight in VIRAL_KEYWORDS.items():
            pattern = r"\b" + re.escape(kw) + r"\b"
            matches = len(re.findall(pattern, lower))
            score += matches * weight

        # Bonus for punctuation excitement: ! and ?
        exclamations = text.count("!")
        questions = text.count("?")
        score += exclamations * 1.5 + questions * 0.8

        # Bonus for ALL CAPS words (indicating shouting or strong emphasis)
        words = text.split()
        caps = sum(1 for w in words if len(w) > 2 and w.isupper())
        score += caps * 1.2

        return min(10.0, score)

    def _generate_fallback_segments(
        self, duration: float, norm_energies: np.ndarray, time_step: float
    ) -> List[AudioSegment]:
        """Generates synthetic segments based on energy peaks when Whisper isn't available."""
        segments = []
        step_sec = 6.0
        cur = 0.0
        while cur < duration:
            seg_end = min(duration, cur + step_sec)
            start_idx = int(cur / time_step)
            end_idx = int(seg_end / time_step)
            chunk_energy = (
                float(np.mean(norm_energies[start_idx:end_idx]))
                if end_idx > start_idx and len(norm_energies) > start_idx
                else 0.5
            )
            seg = AudioSegment(
                start=cur,
                end=seg_end,
                text=f"Engaging highlight moment ({int(cur)}s - {int(seg_end)}s)",
                words=[],
            )
            seg.excitement_score = chunk_energy * 5.0
            segments.append(seg)
            cur = seg_end
        return segments

    def _read_wav(self, wav_path: str) -> Tuple[np.ndarray, int]:
        """Reads a WAV file into float32 numpy array normalized to [-1.0, 1.0]."""
        try:
            from scipy.io import wavfile
            sr, data = wavfile.read(wav_path)
            if data.dtype == np.int16:
                samples = data.astype(np.float32) / 32768.0
            elif data.dtype == np.int32:
                samples = data.astype(np.float32) / 2147483648.0
            elif data.dtype == np.uint8:
                samples = (data.astype(np.float32) - 128.0) / 128.0
            else:
                samples = data.astype(np.float32)

            if len(samples.shape) > 1:
                # Average channels to mono
                samples = np.mean(samples, axis=1)

            return samples, sr
        except Exception as e:
            logger.warning(f"scipy.io.wavfile failed ({e}), falling back to standard wave module")

        import wave
        with wave.open(wav_path, "rb") as wf:
            sr = wf.getframerate()
            n_frames = wf.getnframes()
            raw_bytes = wf.readframes(n_frames)
            data16 = np.frombuffer(raw_bytes, dtype=np.int16)
            samples = data16.astype(np.float32) / 32768.0
            if wf.getnchannels() > 1:
                samples = samples[:: wf.getnchannels()]
            return samples, sr

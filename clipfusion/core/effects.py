"""Effects module for ClipFusion.
Handles zoom punch-in effects and synthesized/custom audio sound effects (whoosh, pop, ding, boom).
"""

import os
import math
import logging
from typing import Dict, List, Optional, Tuple
import numpy as np

logger = logging.getLogger("clipfusion.effects")


class SoundEffectType:
    NONE = "none"
    WHOOSH = "whoosh"
    POP = "pop"
    DING = "ding"
    BOOM = "boom"
    BELL = "bell"


class EffectsManager:
    """Manages visual zoom punch effects and sound effect audio mixing."""

    def __init__(self, sounds_dir: Optional[str] = None):
        self.sounds_dir = sounds_dir or os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
            "assets",
            "sounds",
        )
        os.makedirs(self.sounds_dir, exist_ok=True)
        self._ensure_sound_assets()

    def _ensure_sound_assets(self):
        """Generates high quality procedural sound effects if not already present."""
        effects = {
            "whoosh.wav": self._synthesize_whoosh,
            "pop.wav": self._synthesize_pop,
            "ding.wav": self._synthesize_ding,
            "boom.wav": self._synthesize_boom,
            "bell.wav": self._synthesize_bell,
        }
        for filename, synth_func in effects.items():
            path = os.path.join(self.sounds_dir, filename)
            if not os.path.isfile(path) or os.path.getsize(path) < 100:
                try:
                    samples, sr = synth_func()
                    self._save_wav(path, samples, sr)
                except Exception as e:
                    logger.warning(f"Could not synthesize sound {filename}: {e}")

    def get_sound_path(self, effect_type: str) -> Optional[str]:
        """Returns path to the requested sound effect WAV file."""
        if effect_type == SoundEffectType.NONE or not effect_type:
            return None
        filename = f"{effect_type.lower()}.wav"
        path = os.path.join(self.sounds_dir, filename)
        if os.path.isfile(path):
            return path
        return None

    def build_zoom_filter(
        self,
        enable_zoom: bool,
        punch_time: float = 2.5,
        punch_duration: float = 3.0,
        zoom_factor: float = 1.15,
        target_w: int = 1080,
        target_h: int = 1920,
    ) -> str:
        """
        Builds an FFmpeg zoom punch-in filter string.
        Punches in at punch_time for punch_duration seconds.
        """
        if not enable_zoom:
            return ""

        # Smooth punch expression using scale and crop
        # When between punch_time and punch_time + punch_duration, zoom 1.15x
        z_end = punch_time + punch_duration
        scale_w = int(round(target_w * zoom_factor))
        scale_h = int(round(target_h * zoom_factor))
        # ensure even
        scale_w = scale_w if scale_w % 2 == 0 else scale_w - 1
        scale_h = scale_h if scale_h % 2 == 0 else scale_h - 1
        offset_x = (scale_w - target_w) // 2
        offset_y = (scale_h - target_h) // 2

        # Filter string using FFmpeg conditional eval or zoompan
        # A lightweight, universally supported method:
        filter_str = (
            f"split=2[orig_v][zoom_src];"
            f"[zoom_src]scale={scale_w}:{scale_h}:flags=bilinear,"
            f"crop={target_w}:{target_h}:{offset_x}:{offset_y}[zoomed];"
            f"[orig_v][zoomed]overlay=enable='between(t,{punch_time:.2f},{z_end:.2f})'"
        )
        return filter_str

    def build_audio_mix_filter(
        self,
        sfx_path: Optional[str],
        sfx_start_time: float = 0.2,
        sfx_volume: float = 0.45,
    ) -> Tuple[List[str], str]:
        """
        Returns additional FFmpeg input flags and audio filtergraph for mixing SFX.
        Outputs (['-i', sfx_path], filter_complex_str)
        """
        if not sfx_path or not os.path.isfile(sfx_path):
            return [], ""

        delay_ms = int(round(sfx_start_time * 1000))
        # SFX input will be stream 1 (or next index)
        # We delay SFX and mix with main audio
        input_args = ["-i", sfx_path]
        filter_str = (
            f"[1:a]adelay={delay_ms}|{delay_ms},volume={sfx_volume:.2f}[sfx_delayed];"
            f"[0:a][sfx_delayed]amix=inputs=2:duration=first:dropout_transition=2[aout]"
        )
        return input_args, filter_str

    # --- Procedural Audio Synthesis Functions ---

    def _save_wav(self, path: str, samples: np.ndarray, sr: int):
        """Saves float32 numpy array as 16-bit PCM WAV."""
        from scipy.io import wavfile
        clamped = np.clip(samples, -1.0, 1.0)
        data16 = (clamped * 32767.0).astype(np.int16)
        wavfile.write(path, sr, data16)

    def _synthesize_whoosh(self) -> Tuple[np.ndarray, int]:
        """Synthesizes a clean air whoosh transition sound."""
        sr = 44100
        dur = 0.6
        t = np.linspace(0, dur, int(sr * dur), endpoint=False)
        # Noise shaped with bandpass filter / resonant sweep
        noise = np.random.uniform(-1, 1, len(t))
        # Exponential swell and decay envelope
        env = np.sin(np.pi * (t / dur)) ** 3
        # Modulated frequency whoosh
        carrier = np.sin(2 * np.pi * (200 + 600 * (t / dur)) * t)
        whoosh = (noise * 0.7 + carrier * 0.3) * env
        return whoosh, sr

    def _synthesize_pop(self) -> Tuple[np.ndarray, int]:
        """Synthesizes a snappy TikTok pop / click sound."""
        sr = 44100
        dur = 0.15
        t = np.linspace(0, dur, int(sr * dur), endpoint=False)
        # Rapid downward frequency chirp (800Hz -> 100Hz)
        freq = 800.0 * np.exp(-35.0 * t) + 120.0
        phase = 2 * np.pi * np.cumsum(freq) / sr
        env = np.exp(-28.0 * t)
        pop = np.sin(phase) * env
        return pop, sr

    def _synthesize_ding(self) -> Tuple[np.ndarray, int]:
        """Synthesizes a clean metallic chime / ding."""
        sr = 44100
        dur = 0.9
        t = np.linspace(0, dur, int(sr * dur), endpoint=False)
        # Chime harmonics: 1760Hz, 3520Hz, 5280Hz
        h1 = np.sin(2 * np.pi * 1760 * t) * np.exp(-4.5 * t)
        h2 = 0.5 * np.sin(2 * np.pi * 3520 * t) * np.exp(-7.0 * t)
        h3 = 0.25 * np.sin(2 * np.pi * 5280 * t) * np.exp(-10.0 * t)
        ding = (h1 + h2 + h3) * 0.8
        return ding, sr

    def _synthesize_boom(self) -> Tuple[np.ndarray, int]:
        """Synthesizes a deep cinematic impact boom."""
        sr = 44100
        dur = 1.2
        t = np.linspace(0, dur, int(sr * dur), endpoint=False)
        # Sub-bass downward pitch glide (110Hz -> 35Hz)
        freq = 110.0 * np.exp(-4.0 * t) + 35.0
        phase = 2 * np.pi * np.cumsum(freq) / sr
        env = np.exp(-3.5 * t)
        sub = np.sin(phase) * env
        # Add slight initial transient click
        transient = np.random.uniform(-1, 1, len(t)) * np.exp(-50.0 * t) * 0.4
        boom = sub + transient
        return boom, sr

    def _synthesize_bell(self) -> Tuple[np.ndarray, int]:
        """Synthesizes a bright notification bell."""
        sr = 44100
        dur = 0.8
        t = np.linspace(0, dur, int(sr * dur), endpoint=False)
        f0 = 1046.5  # C6
        f1 = 1318.5  # E6
        b1 = np.sin(2 * np.pi * f0 * t) * np.exp(-5.0 * t)
        b2 = 0.6 * np.sin(2 * np.pi * f1 * t) * np.exp(-6.0 * t)
        bell = (b1 + b2) * 0.75
        return bell, sr

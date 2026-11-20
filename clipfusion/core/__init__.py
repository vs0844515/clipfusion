"""ClipFusion Core Processing Engine."""

from clipfusion.core.ffmpeg_utils import get_ffmpeg_path, get_video_info, extract_audio
from clipfusion.core.audio_analyzer import AudioAnalyzer
from clipfusion.core.visual_analyzer import VisualAnalyzer
from clipfusion.core.face_tracker import SmartFaceTracker, FramingMode
from clipfusion.core.clip_extractor import ClipExtractor, VideoClipCandidate, HighlightCategory
from clipfusion.core.subtitles import SubtitleGenerator, SubtitleStyle, CAPTION_PRESETS_40
from clipfusion.core.effects import EffectsManager, SoundEffectType
from clipfusion.core.metadata_generator import MetadataGenerator
from clipfusion.core.video_processor import VideoProcessor, ExportConfig, ResolutionPreset, RESOLUTION_CONFIGS
from clipfusion.core.youtube_stream import validate_youtube_url, fetch_stream_info, download_stream_section

__all__ = [
    "get_ffmpeg_path",
    "get_video_info",
    "extract_audio",
    "AudioAnalyzer",
    "VisualAnalyzer",
    "SmartFaceTracker",
    "FramingMode",
    "ClipExtractor",
    "VideoClipCandidate",
    "HighlightCategory",
    "SubtitleGenerator",
    "SubtitleStyle",
    "CAPTION_PRESETS_40",
    "EffectsManager",
    "SoundEffectType",
    "MetadataGenerator",
    "VideoProcessor",
    "ExportConfig",
    "ResolutionPreset",
    "RESOLUTION_CONFIGS",
    "validate_youtube_url",
    "fetch_stream_info",
    "download_stream_section",
]

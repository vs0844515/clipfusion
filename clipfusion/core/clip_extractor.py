"""Clip Extractor and Engagement Scoring Engine for ClipFusion.
Analyzes audio dynamics, speech sentiment/hooks, visual pacing, and classifies moments into:
- Funny reactions
- Exciting moments
- Unexpected moments
- Gaming highlights
- Loud reactions
- Interesting conversations
- Emotional moments
"""

import math
import re
import logging
from typing import Dict, List, Any, Optional, Tuple
import numpy as np

from clipfusion.core.audio_analyzer import AudioAnalysisResult, AudioSegment
from clipfusion.core.visual_analyzer import VisualAnalysisResult

logger = logging.getLogger("clipfusion.extractor")


class HighlightCategory:
    FUNNY = "Funny Reaction"
    EXCITING = "Exciting Moment"
    UNEXPECTED = "Unexpected Moment"
    GAMING = "Gaming Highlight"
    LOUD = "Loud Reaction"
    CONVERSATION = "Interesting Conversation"
    EMOTIONAL = "Emotional Moment"


CATEGORY_ICONS = {
    HighlightCategory.FUNNY: "😂",
    HighlightCategory.EXCITING: "⚡",
    HighlightCategory.UNEXPECTED: "😲",
    HighlightCategory.GAMING: "🎮",
    HighlightCategory.LOUD: "📢",
    HighlightCategory.CONVERSATION: "🎙️",
    HighlightCategory.EMOTIONAL: "💖",
}


class VideoClipCandidate:
    """Represents a potential high-engagement short clip with calculated scores and category."""

    def __init__(
        self,
        clip_id: int,
        start_time: float,
        end_time: float,
        engagement_score: float,
        audio_score: float,
        speech_score: float,
        visual_score: float,
        face_score: float,
        transcript_text: str,
        highlight_category: str = HighlightCategory.EXCITING,
        highlight_reason: str = "",
        segments: Optional[List[Dict[str, Any]]] = None,
    ):
        self.clip_id = clip_id
        self.start_time = round(start_time, 2)
        self.end_time = round(end_time, 2)
        self.duration = round(max(1.0, end_time - start_time), 2)
        
        # Audience Engagement & Opus Virality Score (0 to 100)
        self.engagement_score = round(engagement_score, 1)
        self.virality_score = self.engagement_score

        self.audio_score = round(audio_score, 1)
        self.speech_score = round(speech_score, 1)
        self.visual_score = round(visual_score, 1)
        self.face_score = round(face_score, 1)
        self.transcript_text = transcript_text.strip()
        
        # Opus Clip-style 3-Pillar Retention Scores (Out of 10)
        self.hook_score = round(min(9.9, max(7.2, (speech_score * 0.6 + audio_score * 0.4) / 10.0)), 1)
        self.flow_score = round(min(9.9, max(6.8, (visual_score * 0.5 + speech_score * 0.5) / 10.0)), 1)
        self.value_score = round(min(9.9, max(7.0, (face_score * 0.4 + audio_score * 0.6) / 10.0)), 1)

        if self.engagement_score >= 90:
            self.virality_tier = "Very High"
            self.tier_color = "#10b981"  # Emerald Green
        elif self.engagement_score >= 80:
            self.virality_tier = "High"
            self.tier_color = "#6366f1"  # Indigo Purple
        else:
            self.virality_tier = "Good"
            self.tier_color = "#f59e0b"  # Amber Orange

        self.why_it_works = self._generate_why_it_works(highlight_category, self.hook_score, self.flow_score)
        
        self.highlight_category = highlight_category
        self.highlight_icon = CATEGORY_ICONS.get(highlight_category, "🎯")
        self.highlight_reason = highlight_reason or f"{self.highlight_icon} {highlight_category}"
        
        self.segments = segments or []
        self.hook_text = self._extract_hook(transcript_text)
        self.suggested_title = ""
        self.suggested_title_variations: List[str] = []
        self.suggested_description = ""
        self.suggested_hashtags: List[str] = []
        self.suggested_tags_csv = ""

    def _generate_why_it_works(self, category: str, hook: float, flow: float) -> str:
        """Generates an Opus Clip-style AI explanation for why this clip retains viewers."""
        reasons = {
            HighlightCategory.FUNNY: f"Strong comedic timing in first 3s (Hook: {hook}/10) followed by contagious laughter and punchline payoff.",
            HighlightCategory.GAMING: f"High visual motion dynamics and intense competitive climax (Flow: {flow}/10) with peak auditory reaction.",
            HighlightCategory.LOUD: f"Dramatic dynamic contrast with high-decibel vocal bursts (Hook: {hook}/10) that instantly recapture viewer attention.",
            HighlightCategory.UNEXPECTED: f"Abrupt turn of events creating a powerful curiosity gap (Hook: {hook}/10) that maximizes watch time.",
            HighlightCategory.CONVERSATION: f"Thought-provoking question or counter-intuitive insight (Hook: {hook}/10) driving high comments and shares.",
            HighlightCategory.EMOTIONAL: f"Deep empathetic sentiment and genuine vulnerability that creates strong emotional resonance.",
            HighlightCategory.EXCITING: f"Rapid vocal cadence and relentless pacing (Flow: {flow}/10) ideal for short-form retention algorithms.",
        }
        return reasons.get(category, f"High-impact hook ({hook}/10) and smooth pacing ({flow}/10) designed for maximum short-form retention.")

    def _extract_hook(self, text: str) -> str:
        """Extracts the initial punchy sentence or hook for audience retention."""
        if not text:
            return "Epic Highlight Moment"
        parts = text.split(".")
        if len(parts) >= 2 and len(parts[0]) > 10:
            return parts[0].strip() + "."
        words = text.split()
        return " ".join(words[:12]) + ("..." if len(words) > 12 else "")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "clip_id": self.clip_id,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "duration": self.duration,
            "engagement_score": self.engagement_score,
            "virality_score": self.virality_score,
            "audio_score": self.audio_score,
            "speech_score": self.speech_score,
            "visual_score": self.visual_score,
            "face_score": self.face_score,
            "highlight_category": self.highlight_category,
            "highlight_icon": self.highlight_icon,
            "hook_text": self.hook_text,
            "transcript_text": self.transcript_text,
            "highlight_reason": self.highlight_reason,
            "suggested_title": self.suggested_title,
            "suggested_description": self.suggested_description,
            "suggested_hashtags": self.suggested_hashtags,
        }


class ClipExtractor:
    """Extracts, scores, and classifies high-engagement moments using multi-modal AI."""

    def __init__(
        self,
        min_clip_duration: float = 15.0,
        max_clip_duration: float = 60.0,
        target_clip_count: int = 12,
    ):
        self.min_duration = max(10.0, float(min_clip_duration))
        self.max_duration = max(self.min_duration, float(max_clip_duration))
        self.target_clip_count = max(1, int(target_clip_count))

    def extract_clips(
        self,
        audio_result: AudioAnalysisResult,
        visual_result: VisualAnalysisResult,
        progress_callback=None,
    ) -> List[VideoClipCandidate]:
        """Discovers, scores, and ranks candidate engagement clips."""
        duration = max(audio_result.duration, visual_result.duration)
        if duration < self.min_duration:
            logger.warning("Video shorter than minimum clip duration. Creating single clip.")
            full_text = " ".join(s.text for s in audio_result.segments)
            return [
                VideoClipCandidate(
                    clip_id=1,
                    start_time=0.0,
                    end_time=duration,
                    engagement_score=85.0,
                    audio_score=80.0,
                    speech_score=80.0,
                    visual_score=80.0,
                    face_score=80.0,
                    transcript_text=full_text,
                    highlight_category=HighlightCategory.EXCITING,
                    highlight_reason="Full Video Highlight",
                )
            ]

        if progress_callback:
            progress_callback(65, "Scanning audio & visual timeline for high-retention moments...")

        # 1. Gather natural pause cut points (silences + shot cuts + segment edges)
        pause_points = sorted(list(set(audio_result.pause_timestamps + visual_result.scene_cuts)))
        for seg in audio_result.segments:
            pause_points.append(seg.start)
            pause_points.append(seg.end)
        pause_points = sorted(list(set([round(p, 2) for p in pause_points if 0 <= p <= duration])))

        # 2. Generate candidate windows
        candidates_raw: List[Dict[str, Any]] = []

        # Anchor Strategy A: Speech-sentence windows
        if audio_result.segments:
            for i, start_seg in enumerate(audio_result.segments):
                c_start = max(0.0, start_seg.start - 0.2)
                accumulated_text = []
                for j in range(i, len(audio_result.segments)):
                    end_seg = audio_result.segments[j]
                    accumulated_text.append(end_seg.text)
                    curr_len = end_seg.end - c_start
                    if curr_len >= self.min_duration:
                        if curr_len <= self.max_duration:
                            candidates_raw.append({
                                "start": c_start,
                                "end": min(duration, end_seg.end + 0.3),
                                "text": " ".join(accumulated_text),
                            })
                        else:
                            break

        # Anchor Strategy B: Sliding window snapped to natural pauses
        step = max(5.0, (self.max_duration - self.min_duration) / 3.0)
        curr_t = 0.0
        while curr_t + self.min_duration <= duration:
            for target_span in [20.0, 30.0, 45.0, 60.0]:
                if self.min_duration <= target_span <= self.max_duration:
                    ideal_end = min(duration, curr_t + target_span)
                    snapped_start = self._snap_to_pause(curr_t, pause_points, max_delta=3.0)
                    snapped_end = self._snap_to_pause(ideal_end, pause_points, max_delta=3.0)
                    span = snapped_end - snapped_start
                    if self.min_duration <= span <= self.max_duration:
                        sub_text = self._get_text_in_window(audio_result.segments, snapped_start, snapped_end)
                        candidates_raw.append({
                            "start": snapped_start,
                            "end": snapped_end,
                            "text": sub_text,
                        })
            curr_t += step

        if not candidates_raw:
            num_splits = max(1, min(self.target_clip_count, int(duration // 25.0)))
            split_len = duration / num_splits
            for s_idx in range(num_splits):
                candidates_raw.append({
                    "start": s_idx * split_len,
                    "end": min(duration, (s_idx + 1) * split_len),
                    "text": f"Highlight segment #{s_idx+1}",
                })

        if progress_callback:
            progress_callback(75, f"Evaluating engagement & classifying {len(candidates_raw)} candidate moments...")

        # 3. Multi-modal Engagement Scoring & Category Classification
        scored_candidates: List[VideoClipCandidate] = []
        for cand in candidates_raw:
            c_start = cand["start"]
            c_end = cand["end"]
            c_text = cand["text"]

            # Factor A: Audio energy (0-100)
            a_score = self._compute_audio_score(audio_result, c_start, c_end)

            # Factor B: Speech sentiment / hooks (0-100)
            s_score = self._compute_speech_score(audio_result, c_start, c_end, c_text)

            # Factor C: Visual motion (0-100)
            v_score = self._compute_visual_score(visual_result, c_start, c_end)

            # Factor D: Face presence (0-100)
            f_score = self._compute_face_score(visual_result, c_start, c_end)

            # Combined Engagement Score (30% Speech, 30% Audio, 20% Face, 20% Visual)
            raw_engagement = (a_score * 0.30) + (s_score * 0.30) + (f_score * 0.20) + (v_score * 0.20)
            
            # Pacing adjustment: bonus for ideal 20-40s retention window
            dur = c_end - c_start
            if 20.0 <= dur <= 40.0:
                raw_engagement += 3.0

            final_engagement = min(99.0, max(65.0, raw_engagement))

            # Classify into one of 7 moment categories
            category, icon, reason = self._classify_moment(
                text=c_text,
                audio_score=a_score,
                visual_score=v_score,
                face_score=f_score,
                audio_res=audio_result,
                start=c_start,
                end=c_end,
            )

            # Matching subtitle segments
            sub_segments = [
                s.to_dict()
                for s in audio_result.segments
                if s.start >= c_start - 0.5 and s.end <= c_end + 0.5
            ]

            scored_candidates.append(
                VideoClipCandidate(
                    clip_id=0,
                    start_time=c_start,
                    end_time=c_end,
                    engagement_score=final_engagement,
                    audio_score=a_score,
                    speech_score=s_score,
                    visual_score=v_score,
                    face_score=f_score,
                    transcript_text=c_text,
                    highlight_category=category,
                    highlight_reason=reason,
                    segments=sub_segments,
                )
            )

        # 4. Sort by Engagement Score descending
        scored_candidates.sort(key=lambda c: c.engagement_score, reverse=True)

        if progress_callback:
            progress_callback(85, "Applying Non-Maximum Suppression to select distinct highlight moments...")

        # 5. Non-Maximum Suppression (NMS) to eliminate duplicate clips
        selected_clips: List[VideoClipCandidate] = []
        iou_threshold = 0.25

        for candidate in scored_candidates:
            if len(selected_clips) >= self.target_clip_count:
                break

            overlap = False
            for selected in selected_clips:
                inter_start = max(candidate.start_time, selected.start_time)
                inter_end = min(candidate.end_time, selected.end_time)
                intersection = max(0.0, inter_end - inter_start)

                if intersection > 0:
                    union = (candidate.end_time - candidate.start_time) + (selected.end_time - selected.start_time) - intersection
                    iou = intersection / union if union > 0 else 0
                    if iou > iou_threshold:
                        overlap = True
                        break

            if not overlap:
                candidate.clip_id = len(selected_clips) + 1
                selected_clips.append(candidate)

        # Fallback if too few
        if len(selected_clips) < min(5, self.target_clip_count):
            for candidate in scored_candidates:
                if len(selected_clips) >= self.target_clip_count:
                    break
                if candidate not in selected_clips:
                    candidate.clip_id = len(selected_clips) + 1
                    selected_clips.append(candidate)

        selected_clips.sort(key=lambda c: c.engagement_score, reverse=True)
        for i, c in enumerate(selected_clips):
            c.clip_id = i + 1

        if progress_callback:
            progress_callback(90, f"Identified top {len(selected_clips)} high-engagement moments!")

        return selected_clips

    def _classify_moment(
        self,
        text: str,
        audio_score: float,
        visual_score: float,
        face_score: float,
        audio_res: AudioAnalysisResult,
        start: float,
        end: float,
    ) -> Tuple[str, str, str]:
        """Classifies the moment into one of 7 distinct categories."""
        lower = text.lower()

        # 1. Funny Reaction
        funny_keywords = r"\b(haha|lol|lmao|rofl|hilarious|funny|joke|laugh|crying|died|wheeze)\b"
        if re.search(funny_keywords, lower) or "😂" in text:
            return (
                HighlightCategory.FUNNY,
                CATEGORY_ICONS[HighlightCategory.FUNNY],
                "Humor, laughter & comical reaction cue detected",
            )

        # 2. Gaming Highlight
        gaming_keywords = r"\b(clutch|kill|headshot|win|victory|ace|boss|died|gg|play|drop|shot|damage|respawn|gameplay)\b"
        if re.search(gaming_keywords, lower) and visual_score > 70.0:
            return (
                HighlightCategory.GAMING,
                CATEGORY_ICONS[HighlightCategory.GAMING],
                "High-speed action & competitive gaming highlight",
            )

        # 3. Unexpected Moment (surprise plot twists & abrupt shock)
        unexpected_keywords = r"\b(wait|hold on|did you see that|are you kidding|what just happened|plot twist|out of nowhere)\b"
        if re.search(unexpected_keywords, lower):
            return (
                HighlightCategory.UNEXPECTED,
                CATEGORY_ICONS[HighlightCategory.UNEXPECTED],
                "Surprise turn of events & sudden reaction",
            )

        # 4. Loud Reaction
        if audio_score >= 88.0 or text.count("!") >= 3:
            return (
                HighlightCategory.LOUD,
                CATEGORY_ICONS[HighlightCategory.LOUD],
                "High-decibel vocal burst & loud exclamation",
            )

        # 5. Interesting Conversation
        conversation_keywords = r"\b(why|how|what if|secret|truth|think about|explain|because|story|lesson|perspective|advice)\b"
        if re.search(conversation_keywords, lower) or text.count("?") >= 2:
            return (
                HighlightCategory.CONVERSATION,
                CATEGORY_ICONS[HighlightCategory.CONVERSATION],
                "Thought-provoking dialogue & insightful discussion",
            )

        # 6. Emotional Moment
        emotional_keywords = r"\b(feel|heart|cried|love|deep|changed my life|never forget|honestly|grateful|struggle|pain|inspired)\b"
        if re.search(emotional_keywords, lower):
            return (
                HighlightCategory.EMOTIONAL,
                CATEGORY_ICONS[HighlightCategory.EMOTIONAL],
                "Empathic connection & heartfelt narrative moment",
            )

        # 7. Exciting Moment (Default / Energy)
        return (
            HighlightCategory.EXCITING,
            CATEGORY_ICONS[HighlightCategory.EXCITING],
            "High-energy delivery & dynamic audience engagement",
        )

    def _snap_to_pause(self, timestamp: float, pause_points: List[float], max_delta: float = 3.0) -> float:
        if not pause_points:
            return timestamp
        best_p = timestamp
        min_d = max_delta + 1.0
        for p in pause_points:
            d = abs(p - timestamp)
            if d < min_d:
                min_d = d
                best_p = p
        if min_d <= max_delta:
            return best_p
        return timestamp

    def _get_text_in_window(self, segments: List[AudioSegment], start: float, end: float) -> str:
        texts = []
        for s in segments:
            if (s.start >= start and s.start <= end) or (s.end >= start and s.end <= end):
                texts.append(s.text)
        return " ".join(texts)

    def _compute_audio_score(self, audio: AudioAnalysisResult, start: float, end: float) -> float:
        if len(audio.energy_profile) == 0:
            return 70.0
        s_idx = max(0, int(start / audio.time_step))
        e_idx = min(len(audio.energy_profile), int(end / audio.time_step))
        if e_idx <= s_idx:
            return 70.0

        slice_e = audio.energy_profile[s_idx:e_idx]
        mean_e = float(np.mean(slice_e))
        peak_e = float(np.max(slice_e))
        bursts = float(np.sum(slice_e > 0.6)) / float(len(slice_e))

        score = (mean_e * 40.0) + (peak_e * 35.0) + (bursts * 25.0)
        return min(100.0, max(50.0, score * 100.0))

    def _compute_speech_score(
        self, audio: AudioAnalysisResult, start: float, end: float, text: str
    ) -> float:
        base_score = 65.0
        sub_segs = [s for s in audio.segments if s.start >= start and s.end <= end]
        if sub_segs:
            total_excitement = sum(s.excitement_score for s in sub_segs)
            base_score += min(30.0, total_excitement * 4.0)

        word_count = len(text.split())
        words_per_sec = word_count / max(1.0, end - start)
        if 2.0 <= words_per_sec <= 3.8:
            base_score += 5.0

        return min(100.0, max(50.0, base_score))

    def _compute_visual_score(self, visual: VisualAnalysisResult, start: float, end: float) -> float:
        if not visual.frames:
            return 70.0
        s_idx = max(0, int(start / visual.sample_interval))
        e_idx = min(len(visual.frames), int(end / visual.sample_interval))
        if e_idx <= s_idx:
            return 70.0

        slice_frames = visual.frames[s_idx:e_idx]
        motions = [f.motion_score for f in slice_frames]
        cuts = sum(1 for f in slice_frames if f.is_scene_cut)

        avg_m = np.mean(motions) if motions else 0.2
        cut_bonus = min(15.0, cuts * 4.0)
        score = 55.0 + (avg_m * 30.0) + cut_bonus
        return min(100.0, max(50.0, score))

    def _compute_face_score(self, visual: VisualAnalysisResult, start: float, end: float) -> float:
        if not visual.frames:
            return 70.0
        s_idx = max(0, int(start / visual.sample_interval))
        e_idx = min(len(visual.frames), int(end / visual.sample_interval))
        if e_idx <= s_idx:
            return 70.0

        slice_frames = visual.frames[s_idx:e_idx]
        face_frames = sum(1 for f in slice_frames if f.face_count > 0)
        face_ratio = face_frames / max(1, len(slice_frames))

        score = 60.0 + (face_ratio * 38.0)
        return min(100.0, max(50.0, score))

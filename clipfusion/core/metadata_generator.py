"""Metadata Generator for ClipFusion.
Creates high-engagement YouTube Shorts, TikTok, and Instagram Reels titles, descriptions, and hashtags.
Tailored for Funny reactions, Gaming highlights, Loud reactions, Unexpected moments, and Conversations.
"""

import re
import random
import logging
from typing import Dict, List, Any, Optional

logger = logging.getLogger("clipfusion.metadata")

# Category-specific title templates
CATEGORY_TITLE_TEMPLATES = {
    "Funny Reaction": [
        "I CAN'T STOP LAUGHING AT THIS 😂",
        "The funniest reaction on stream 💀",
        "You won't survive this laugh 😭",
        "Bro really thought nobody would notice 🤣",
        "Try not to laugh challenge: IMPOSSIBLE 💀",
    ],
    "Gaming Highlight": [
        "THE MOST INSANE CLUTCH PLAY 🎮",
        "No way he actually pulled this off... 🏆",
        "Peak gaming moment right here 🔥",
        "1 in a Million Gaming Play ⚡",
        "This is why you never give up 🎯",
    ],
    "Unexpected Moment": [
        "NOBODY expected this to happen... 😲",
        "Wait for the plot twist! 👀",
        "What just happened?! 🤯",
        "The timing could not have been better ⚡",
        "Watch until the end... You won't believe it 😱",
    ],
    "Loud Reaction": [
        "HEADPHONES WARNING! ⚠️🎧",
        "The loudest reaction on stream 📢",
        "Bro's microphone could barely handle it 🔊",
        "Absolute peak chaos right here 💥",
        "I felt that reaction in my soul 😱",
    ],
    "Interesting Conversation": [
        "The Truth About {topic} You Need To Hear 🎙️",
        "This completely changed how I think about {topic} 🧠",
        "Only 1% of people understand this about {topic} 💡",
        "The secret perspective nobody talks about 🤫",
        "Deep wisdom in 30 seconds ⚡",
    ],
    "Emotional Moment": [
        "This moment touched everyone's heart 💖",
        "The most genuine moment on stream ✨",
        "A reminder that we all need to hear ❤️",
        "This will make you rethink everything 🥺",
        "Pure, unfiltered emotion right here 🌟",
    ],
    "Exciting Moment": [
        "THIS CHANGED EVERYTHING ⚡",
        "Wait Until You Hear This... 🤯",
        "The Insane Truth About {topic} 🔥",
        "You Won't Believe What Happened! 😱",
        "How To Master {topic} In 30 Seconds 🚀",
    ],
}

# Niche hashtags
NICHE_TAG_MAP = {
    r"\b(money|rich|business|crypto|invest|million|wealth)\b": ["#money", "#business", "#entrepreneur", "#wealth", "#investing"],
    r"\b(tech|ai|code|software|computer|phone|future)\b": ["#tech", "#technology", "#ai", "#artificialintelligence", "#future"],
    r"\b(game|gaming|play|stream|ps5|xbox|pc|clutch|kill)\b": ["#gaming", "#gamer", "#gamersoftiktok", "#gamingclips", "#streamer"],
    r"\b(laugh|funny|comedy|joke|hilarious|prank|lol|lmao)\b": ["#funny", "#comedy", "#hilarious", "#lol", "#meme"],
    r"\b(mindset|success|gym|workout|focus|grind|discipline)\b": ["#motivation", "#discipline", "#success", "#mindset", "#grind"],
    r"\b(story|podcast|interview|talk|episode|chat)\b": ["#podcast", "#podcastclips", "#interview", "#stories", "#storytime"],
    r"\b(live|livestream|twitch|streamer|broadcast)\b": ["#livestream", "#streamer", "#twitch", "#streamhighlights", "#livemoments"],
}


class MetadataGenerator:
    """Generates social media titles, descriptions, and hashtags from transcript and moment category."""

    def __init__(self):
        pass

    def generate_metadata(
        self,
        transcript_text: str,
        highlight_reason: str,
        clip_id: int = 1,
        duration: float = 30.0,
        category: Optional[str] = None,
        creator_handle: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Produces engaging title options, platform descriptions, and hashtags."""
        clean_text = transcript_text.strip()
        topic = self._extract_key_topic(clean_text)

        # 1. Title generation tailored by category (3 variations)
        title_vars = self._create_title_variations(clean_text, topic, clip_id, category)
        primary_title = title_vars[0]

        # 2. Hashtags generation
        hashtags = self._create_hashtags(clean_text, topic, category)
        tags_clean = [t.replace("#", "") for t in hashtags]
        tags_csv = ", ".join(tags_clean)

        # 3. Description generation
        description = self._create_description(
            clean_text=clean_text,
            topic=topic,
            highlight_reason=highlight_reason,
            duration=duration,
            hashtags=hashtags,
            category=category,
            creator_handle=creator_handle,
        )

        return {
            "title": primary_title,
            "title_variations": title_vars,
            "description": description,
            "hashtags": hashtags,
            "hashtags_str": " ".join(hashtags),
            "tags_csv": tags_csv,
            "topic": topic,
        }

    def _create_title_variations(self, text: str, topic: str, clip_id: int, category: Optional[str]) -> List[str]:
        """Generates 3 distinct high-CTR title variations for A/B testing."""
        cat_key = category if category in CATEGORY_TITLE_TEMPLATES else "Exciting Moment"
        templates = CATEGORY_TITLE_TEMPLATES.get(cat_key, CATEGORY_TITLE_TEMPLATES["Exciting Moment"])
        
        # Option 1: Template standard
        t1 = templates[(clip_id - 1) % len(templates)].replace("{topic}", topic)
        
        # Option 2: Question or curiosity hook
        questions = [s.strip() for s in text.split("?") if len(s.strip()) > 10]
        if questions and len(questions[0]) < 65:
            t2 = f"{questions[0].strip()}? 🤯"
        else:
            t2 = templates[(clip_id) % len(templates)].replace("{topic}", topic)

        # Option 3: Action punchline
        words = text.split()
        short_quote = " ".join(words[:6]) if len(words) >= 4 else text[:30]
        t3 = f'"{short_quote.strip()}" 🔥' if short_quote else f"{topic.upper()} GONE WRONG! ⚡"

        # Deduplicate while preserving order
        unique_titles = []
        for t in [t1, t2, t3]:
            if t not in unique_titles:
                unique_titles.append(t)
        while len(unique_titles) < 3:
            unique_titles.append(f"Epic {category or 'Highlight'} #{clip_id} ⚡")

        return unique_titles[:3]

    def _extract_key_topic(self, text: str) -> str:
        """Extracts prominent noun or subject from the text."""
        if not text:
            return "This Moment"

        clean = re.sub(r"[^\w\s]", "", text)
        words = [w.capitalize() for w in clean.split() if len(w) > 3 and w.lower() not in {
            "that", "this", "what", "with", "from", "have", "been", "were", "they", "will",
            "just", "about", "there", "their", "which", "could", "would", "these", "other",
            "like", "yeah", "okay", "gonna", "wanna"
        }]

        if words:
            return words[0]
        return "This"

    def _create_title(self, text: str, topic: str, clip_id: int, category: Optional[str]) -> str:
        """Selects and formats a high-engagement title based on moment category."""
        # 1. Check for punchy question in transcript
        questions = [s.strip() for s in text.split("?") if len(s.strip()) > 10]
        if questions and len(questions[0]) < 55:
            return f"{questions[0].strip()}? 🤯"

        # 2. Select category-specific template
        cat_key = category if category in CATEGORY_TITLE_TEMPLATES else "Exciting Moment"
        templates = CATEGORY_TITLE_TEMPLATES.get(cat_key, CATEGORY_TITLE_TEMPLATES["Exciting Moment"])
        template = templates[(clip_id - 1) % len(templates)]
        title = template.replace("{topic}", topic)
        return title

    def _create_hashtags(self, text: str, topic: str, category: Optional[str]) -> List[str]:
        """Finds matching niche hashtags plus universal short-form tags."""
        universal = ["#shorts", "#trending", "#fyp", "#clipfusion", "#reels"]
        matched_niche = []

        if category == "Gaming Highlight":
            matched_niche.extend(["#gaming", "#gamer", "#gamingclips", "#streamer"])
        elif category == "Funny Reaction":
            matched_niche.extend(["#funny", "#comedy", "#hilarious", "#lol"])
        elif category == "Loud Reaction":
            matched_niche.extend(["#reaction", "#loudreaction", "#streamer", "#twitch"])
        elif category == "Interesting Conversation":
            matched_niche.extend(["#podcast", "#interview", "#deepconversations", "#mindset"])

        lower = text.lower()
        for pattern, tags in NICHE_TAG_MAP.items():
            if re.search(pattern, lower):
                for t in tags:
                    if t not in matched_niche:
                        matched_niche.append(t)

        topic_tag = "#" + re.sub(r"[^\w]", "", topic).lower()
        if len(topic_tag) > 2 and topic_tag not in universal and topic_tag not in matched_niche:
            matched_niche.insert(0, topic_tag)

        all_tags = universal[:3] + matched_niche[:5] + universal[3:]
        return all_tags[:10]

    def _create_description(
        self,
        clean_text: str,
        topic: str,
        highlight_reason: str,
        duration: float,
        hashtags: List[str],
        category: Optional[str],
        creator_handle: Optional[str] = None,
    ) -> str:
        """Creates complete SEO description."""
        hook_preview = clean_text[:160] + ("..." if len(clean_text) > 160 else "")
        cat_str = f" | Category: {category}" if category else ""
        credit_str = f"👤 Creator: {creator_handle}\n" if creator_handle else ""
        desc = (
            f"⚡ {hook_preview}\n\n"
            f"{credit_str}"
            f"🎯 Highlight: {highlight_reason}{cat_str}\n"
            f"⏱️ Duration: {int(duration)}s | 1080x1920 Full HD / 4K Vertical\n\n"
            f"👉 Follow and subscribe for more daily clips!\n"
            f"💬 Drop your thoughts down in the comments below! What did you think of {topic}?\n\n"
            f"{' '.join(hashtags)}\n\n"
            f"— Generated with ClipFusion AI"
        )
        return desc

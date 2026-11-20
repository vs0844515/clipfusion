"""Social Media Accounts & Publishing Hub for ClipFusion.
Manages creator profiles and handles for YouTube Shorts, TikTok, and Instagram Reels.
Persists settings locally in config/social_accounts.json.
"""

import os
import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional

logger = logging.getLogger("clipfusion.social_accounts")

DEFAULT_CONFIG_PATH = Path(__file__).resolve().parent.parent.parent / "config" / "social_accounts.json"


class SocialAccountsManager:
    """Manages creator social account configurations and multi-platform packaging."""

    def __init__(self, config_path: Optional[Path] = None):
        self.config_path = config_path or DEFAULT_CONFIG_PATH
        self.accounts = self.load_accounts()

    def get_default_structure(self) -> Dict[str, Any]:
        return {
            "youtube": {
                "enabled": True,
                "channel_name": "My Channel",
                "handle": "@creator",
                "default_privacy": "Public",
                "category": "Gaming",
                "auto_tags": "shorts, viral, gaming, clipfusion, trending",
            },
            "tiktok": {
                "enabled": True,
                "username": "@creator_shorts",
                "allow_duet": True,
                "allow_stitch": True,
                "allow_comments": True,
            },
            "instagram": {
                "enabled": True,
                "handle": "@creator_reels",
                "share_to_feed": True,
                "audio_attribution": "Original Audio",
            },
        }

    def load_accounts(self) -> Dict[str, Any]:
        """Loads account profiles from JSON or initializes defaults."""
        if self.config_path.is_file():
            try:
                with open(self.config_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    defaults = self.get_default_structure()
                    # Ensure all platforms present
                    for k, v in defaults.items():
                        if k not in data:
                            data[k] = v
                    return data
            except Exception as e:
                logger.error(f"Failed to read social accounts config: {e}")

        defaults = self.get_default_structure()
        self.save_accounts(defaults)
        return defaults

    def save_accounts(self, accounts_data: Dict[str, Any]) -> bool:
        """Saves account profiles to local JSON configuration."""
        try:
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.config_path, "w", encoding="utf-8") as f:
                json.dump(accounts_data, f, indent=4, ensure_ascii=False)
            self.accounts = accounts_data
            return True
        except Exception as e:
            logger.error(f"Failed to write social accounts config: {e}")
            return False

    def build_platform_packages(self, clip, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Generates platform-tailored post content using configured handles."""
        yt = self.accounts.get("youtube", {})
        tt = self.accounts.get("tiktok", {})
        ig = self.accounts.get("instagram", {})

        title = metadata.get("title", "")
        desc = metadata.get("description", "")
        tags = metadata.get("hashtags", [])
        tags_str = " ".join(tags)

        # YouTube Shorts Package (Title <= 100 chars, description with handle and #Shorts)
        yt_handle = yt.get("handle", "").strip()
        yt_credit = f"\n\nCreator: {yt_handle}" if yt_handle and yt_handle != "@creator" else ""
        yt_title = f"{title[:80]} #Shorts"
        yt_desc = f"{desc}{yt_credit}\n\n#Shorts #YouTubeShorts"
        yt_tags_csv = ", ".join([t.replace("#", "") for t in tags] + [x.strip() for x in yt.get("auto_tags", "").split(",") if x.strip()])

        # TikTok Package (Max punchy caption, creator tag, 4-6 tags)
        tt_handle = tt.get("username", "").strip()
        tt_credit = f" via {tt_handle}" if tt_handle and tt_handle != "@creator_shorts" else ""
        top_tags = " ".join(tags[:5] + ["#fyp", "#viral"])
        tt_caption = f"{title}{tt_credit}\n\n{top_tags}"

        # Instagram Reels Package (Engaging caption + CTA + 15 hashtags)
        ig_handle = ig.get("handle", "").strip()
        ig_credit = f"\n\nFollow {ig_handle} for more viral moments!" if ig_handle and ig_handle != "@creator_reels" else ""
        ig_caption = f"{title} 🔥\n\nDrop your thoughts in the comments! 👇{ig_credit}\n\n{tags_str}"

        return {
            "youtube": {
                "title": yt_title,
                "description": yt_desc,
                "tags_csv": yt_tags_csv,
                "privacy": yt.get("default_privacy", "Public"),
                "category": yt.get("category", "Gaming"),
                "channel": yt.get("channel_name", "My Channel"),
            },
            "tiktok": {
                "caption": tt_caption,
                "handle": tt_handle,
                "allow_duet": tt.get("allow_duet", True),
                "allow_stitch": tt.get("allow_stitch", True),
            },
            "instagram": {
                "caption": ig_caption,
                "handle": ig_handle,
                "share_to_feed": ig.get("share_to_feed", True),
            },
        }

"""Animated Subtitle Generator for ClipFusion with 40 Production Caption Designs.
Includes authentic OpusClip presets: Word Cut, Marker Sweep, Negative Keywords, Karaoke,
Handwritten, Mozi, Simple, Soft Build, Typewriter, Glide, Doodle, Editorial, and 28 more!
"""

import os
import re
import math
import logging
from typing import Dict, List, Any, Optional, Tuple

logger = logging.getLogger("clipfusion.subtitles")


# Opus Clip signature auto-emojis for high-impact keywords
OPUS_EMOJI_MAP = {
    "win": "🏆", "winner": "🏆", "victory": "🏆", "clutch": "⚡", "headshot": "🎯",
    "kill": "💀", "dead": "💀", "die": "💀", "died": "💀", "dieded": "💀",
    "money": "💸", "cash": "💰", "rich": "🤑", "dollar": "💵", "crypto": "🪙",
    "fire": "🔥", "hot": "🔥", "insane": "🤯", "crazy": "🤯", "shocked": "😱",
    "omg": "😱", "wait": "👀", "look": "👀", "laugh": "😂", "lol": "🤣",
    "haha": "😂", "love": "❤️", "heart": "💖", "game": "🎮", "play": "🎮",
    "warning": "⚠️", "danger": "⚠️", "secret": "🤫", "stop": "🛑", "police": "🚔",
    "car": "🏎️", "gun": "🔫", "shot": "💥", "boom": "💣", "star": "⭐", "best": "⭐",
    "bhai": "🔥", "bro": "👊", "boss": "👑", "king": "👑", "pro": "⚡", "yes": "✅",
}


# =========================================================================
# 40 AUTHENTIC OPUSCLIP & CREATOR CAPTION DESIGNS
# =========================================================================
CAPTION_PRESETS_40 = {
    # --- 1. VIRAL CREATORS (1-8) ---
    "word_cut": {
        "id": "word_cut",
        "name": "Word Cut",
        "category": "Viral Creators",
        "font_name": "Arial Black",
        "primary_color": "&H00FFFFFF",
        "highlight_color": "&H0000FFFF",
        "outline_color": "&H00000000",
        "outline_width": 4,
        "shadow_depth": 2,
        "border_style": 1,
        "back_color": "&H80000000",
        "bold": True,
        "italic": False,
        "underline": False,
        "words_per_group": 2,
        "preview_text": "To get<br><b>started</b>",
        "desc": "Stacked 2-line rapid rhythm matching Opus Word Cut",
    },
    "marker_sweep": {
        "id": "marker_sweep",
        "name": "Marker Sweep",
        "category": "Viral Creators",
        "font_name": "Trebuchet MS",
        "primary_color": "&H00FFFFFF",
        "highlight_color": "&H00FF66CC",
        "outline_color": "&H002A0845",
        "outline_width": 4,
        "shadow_depth": 2,
        "border_style": 1,
        "back_color": "&H906B21A8",
        "bold": True,
        "italic": False,
        "underline": False,
        "words_per_group": 3,
        "preview_text": "TO GET <span style='background: #8b5cf6; padding: 2px 6px; border-radius: 4px; color: #fff;'>STARTED</span>",
        "desc": "Purple highlighter sweep box behind active punchline",
    },
    "negative_keywords": {
        "id": "negative_keywords",
        "name": "Negative keywords",
        "category": "Viral Creators",
        "font_name": "Arial Black",
        "primary_color": "&H00A0A0A0",
        "highlight_color": "&H004499FF",
        "outline_color": "&H00000000",
        "outline_width": 4,
        "shadow_depth": 2,
        "border_style": 1,
        "back_color": "&H80000000",
        "bold": True,
        "italic": False,
        "underline": False,
        "words_per_group": 3,
        "preview_text": "TO GET <span style='color: #fb923c; font-weight: 900;'>STARTED</span>",
        "desc": "Muted secondary text with vibrant copper-orange highlight",
    },
    "karaoke": {
        "id": "karaoke",
        "name": "Karaoke",
        "category": "Viral Creators",
        "font_name": "Arial Black",
        "primary_color": "&H00FFFFFF",
        "highlight_color": "&H0000E5FF",
        "outline_color": "&H00000000",
        "outline_width": 4,
        "shadow_depth": 3,
        "border_style": 1,
        "back_color": "&H80000000",
        "bold": True,
        "italic": False,
        "underline": False,
        "words_per_group": 3,
        "preview_text": "TO GET <span style='color: #38bdf8; text-shadow: 0 0 10px #38bdf8;'>STARTED</span>",
        "desc": "Classic active karaoke wave with glowing cyan",
    },
    "mozi": {
        "id": "mozi",
        "name": "Mozi",
        "category": "Viral Creators",
        "font_name": "Impact",
        "primary_color": "&H00FFFFFF",
        "highlight_color": "&H0033FF33",
        "outline_color": "&H00000000",
        "outline_width": 5,
        "shadow_depth": 2,
        "border_style": 1,
        "back_color": "&H80000000",
        "bold": True,
        "italic": False,
        "underline": False,
        "words_per_group": 3,
        "preview_text": "TO GET <span style='color: #22c55e;'>STARTED</span>",
        "desc": "Alex Hormozi signature neon green punch words",
    },
    "mrbeast": {
        "id": "mrbeast",
        "name": "MrBeast Alert",
        "category": "Viral Creators",
        "font_name": "Impact",
        "primary_color": "&H0000FFFF",
        "highlight_color": "&H000000FF",
        "outline_color": "&H00000000",
        "outline_width": 6,
        "shadow_depth": 4,
        "border_style": 1,
        "back_color": "&H80000000",
        "bold": True,
        "italic": False,
        "underline": False,
        "words_per_group": 2,
        "preview_text": "<span style='color: #facc15;'>TO GET</span> <span style='color: #ef4444;'>STARTED!</span>",
        "desc": "High-octane yellow & red flash with deep 3D black outline",
    },
    "iman_gadzhi": {
        "id": "iman_gadzhi",
        "name": "Gadzhi Elite",
        "category": "Viral Creators",
        "font_name": "Segoe UI",
        "primary_color": "&H00F0F0F0",
        "highlight_color": "&H00D0C0A0",
        "outline_color": "&H00101010",
        "outline_width": 3,
        "shadow_depth": 1,
        "border_style": 1,
        "back_color": "&H80000000",
        "bold": True,
        "italic": False,
        "underline": False,
        "words_per_group": 3,
        "preview_text": "<span style='letter-spacing: 2px; color: #f1f5f9;'>TO GET STARTED</span>",
        "desc": "Ultra-clean luxury aesthetic with muted champagne gold",
    },
    "ali_abdaal": {
        "id": "ali_abdaal",
        "name": "Abdaal Pastel",
        "category": "Viral Creators",
        "font_name": "Trebuchet MS",
        "primary_color": "&H00FFFFFF",
        "highlight_color": "&H0099FFCC",
        "outline_color": "&H00000000",
        "outline_width": 3,
        "shadow_depth": 1,
        "border_style": 3,
        "back_color": "&H80203020",
        "bold": True,
        "italic": False,
        "underline": False,
        "words_per_group": 3,
        "preview_text": "To get <span style='color: #86efac; background: rgba(134,239,172,0.2); padding: 2px 6px; border-radius: 4px;'>started</span>",
        "desc": "Soft pastel sage green with gentle pill background",
    },

    # --- 2. TYPOGRAPHY & FONT STYLES (9-16) ---
    "handwritten": {
        "id": "handwritten",
        "name": "Handwritten",
        "category": "Typography",
        "font_name": "Segoe Print",
        "primary_color": "&H00FFFFFF",
        "highlight_color": "&H0000FFFF",
        "outline_color": "&H00000000",
        "outline_width": 3,
        "shadow_depth": 2,
        "border_style": 1,
        "back_color": "&H80000000",
        "bold": True,
        "italic": True,
        "underline": False,
        "words_per_group": 3,
        "preview_text": "<i>To get <span style='text-decoration: underline wavy #facc15;'>started</span></i>",
        "desc": "Cursive script font with hand-drawn yellow underline",
    },
    "editorial": {
        "id": "editorial",
        "name": "Editorial",
        "category": "Typography",
        "font_name": "Georgia",
        "primary_color": "&H00F0F0F0",
        "highlight_color": "&H0022C0FF",
        "outline_color": "&H00101010",
        "outline_width": 3,
        "shadow_depth": 2,
        "border_style": 1,
        "back_color": "&H80000000",
        "bold": False,
        "italic": True,
        "underline": False,
        "words_per_group": 3,
        "preview_text": "<span style='font-family: serif; font-style: italic;'>to get <b style='color: #fbbf24;'>started</b></span>",
        "desc": "Sophisticated serif italic typography with gold sheen",
    },
    "typewriter": {
        "id": "typewriter",
        "name": "Typewriter",
        "category": "Typography",
        "font_name": "Courier New",
        "primary_color": "&H00FFFFFF",
        "highlight_color": "&H0000D0FF",
        "outline_color": "&H00000000",
        "outline_width": 3,
        "shadow_depth": 2,
        "border_style": 1,
        "back_color": "&H80000000",
        "bold": True,
        "italic": False,
        "underline": False,
        "words_per_group": 3,
        "preview_text": "<span style='font-family: monospace;'>To get started<b style='color: #f59e0b;'>█</b></span>",
        "desc": "Retro monospace typewriter with animated block cursor",
    },
    "simple": {
        "id": "simple",
        "name": "Simple",
        "category": "Typography",
        "font_name": "Arial Black",
        "primary_color": "&H00FFFFFF",
        "highlight_color": "&H00FFFFFF",
        "outline_color": "&H00000000",
        "outline_width": 5,
        "shadow_depth": 2,
        "border_style": 1,
        "back_color": "&H80000000",
        "bold": True,
        "italic": False,
        "underline": False,
        "words_per_group": 1,
        "preview_text": "<span style='font-weight: 900; letter-spacing: 1px;'>STARTED</span>",
        "desc": "Single word centered high-impact 3D outline",
    },
    "soft_build": {
        "id": "soft_build",
        "name": "Soft Build",
        "category": "Typography",
        "font_name": "Arial",
        "primary_color": "&H00FFFFFF",
        "highlight_color": "&H0033CCFF",
        "outline_color": "&H00000000",
        "outline_width": 3,
        "shadow_depth": 1,
        "border_style": 1,
        "back_color": "&H80000000",
        "bold": True,
        "italic": False,
        "underline": False,
        "words_per_group": 3,
        "preview_text": "<span style='opacity: 0.5;'>To get </span><b>started</b>",
        "desc": "Smooth progressive opacity build for calm delivery",
    },
    "retro_arcade": {
        "id": "retro_arcade",
        "name": "Retro 8-Bit",
        "category": "Typography",
        "font_name": "Lucida Console",
        "primary_color": "&H00FFFF00",
        "highlight_color": "&H0000FFFF",
        "outline_color": "&H00800000",
        "outline_width": 4,
        "shadow_depth": 3,
        "border_style": 1,
        "back_color": "&H80000000",
        "bold": True,
        "italic": False,
        "underline": False,
        "words_per_group": 3,
        "preview_text": "<span style='color: #22d3ee; font-family: monospace; font-weight: 800;'>TO GET <span style='color: #facc15;'>STARTED</span></span>",
        "desc": "Pixel arcade gaming style with cyan & yellow",
    },
    "heavy_metal": {
        "id": "heavy_metal",
        "name": "Heavy Metal",
        "category": "Typography",
        "font_name": "Impact",
        "primary_color": "&H00E0E0E0",
        "highlight_color": "&H000000FF",
        "outline_color": "&H00200000",
        "outline_width": 5,
        "shadow_depth": 4,
        "border_style": 1,
        "back_color": "&H80000000",
        "bold": True,
        "italic": False,
        "underline": False,
        "words_per_group": 2,
        "preview_text": "<span style='font-family: Impact; color: #e2e8f0; text-shadow: 2px 2px #ef4444;'>HEAVY METAL</span>",
        "desc": "Gothic heavy stone texture with red shadow cut",
    },
    "clean_sans": {
        "id": "clean_sans",
        "name": "Clean Sans",
        "category": "Typography",
        "font_name": "Segoe UI",
        "primary_color": "&H00FFFFFF",
        "highlight_color": "&H0038BDF8",
        "outline_color": "&H00000000",
        "outline_width": 3,
        "shadow_depth": 2,
        "border_style": 1,
        "back_color": "&H80000000",
        "bold": True,
        "italic": False,
        "underline": False,
        "words_per_group": 3,
        "preview_text": "<span>To get <b style='color: #38bdf8;'>started</b></span>",
        "desc": "Balanced modern geometric sans-serif for everyday clips",
    },

    # --- 3. BADGES, BOXES & HIGHLIGHTS (17-24) ---
    "glide": {
        "id": "glide",
        "name": "Glide Pill",
        "category": "Badges & Boxes",
        "font_name": "Arial Black",
        "primary_color": "&H00FFFFFF",
        "highlight_color": "&H00FFFFFF",
        "outline_color": "&H00000000",
        "outline_width": 2,
        "shadow_depth": 1,
        "border_style": 3,
        "back_color": "&H002020E0",
        "bold": True,
        "italic": False,
        "underline": False,
        "words_per_group": 3,
        "preview_text": "To get <span style='background: #ef4444; color: #fff; padding: 3px 8px; border-radius: 6px; font-weight: 800;'>started</span>",
        "desc": "Crisp red pill box badge wrapping active key phrase",
    },
    "cyber_cyan_box": {
        "id": "cyber_cyan_box",
        "name": "Cyber Box",
        "category": "Badges & Boxes",
        "font_name": "Trebuchet MS",
        "primary_color": "&H00FFFFFF",
        "highlight_color": "&H00FFFF00",
        "outline_color": "&H00602000",
        "outline_width": 3,
        "shadow_depth": 2,
        "border_style": 1,
        "back_color": "&H80000000",
        "bold": True,
        "italic": False,
        "underline": False,
        "words_per_group": 3,
        "preview_text": "TO GET <span style='border: 1.5px solid #06b6d4; background: rgba(6,182,212,0.15); color: #22d3ee; padding: 2px 8px; border-radius: 6px;'>STARTED</span>",
        "desc": "Electric blue bounding box with cyber cyan glow",
    },
    "emerald_pill": {
        "id": "emerald_pill",
        "name": "Emerald Badge",
        "category": "Badges & Boxes",
        "font_name": "Arial Black",
        "primary_color": "&H00FFFFFF",
        "highlight_color": "&H00000000",
        "outline_color": "&H00000000",
        "outline_width": 2,
        "shadow_depth": 1,
        "border_style": 3,
        "back_color": "&H0040A010",
        "bold": True,
        "italic": False,
        "underline": False,
        "words_per_group": 3,
        "preview_text": "TO GET <span style='background: #10b981; color: #000; padding: 2px 8px; border-radius: 6px; font-weight: 800;'>STARTED</span>",
        "desc": "Neon emerald green solid pill badge with dark lettering",
    },
    "doodle": {
        "id": "doodle",
        "name": "Doodle",
        "category": "Badges & Boxes",
        "font_name": "Comic Sans MS",
        "primary_color": "&H00FFFFFF",
        "highlight_color": "&H0000FFFF",
        "outline_color": "&H00000000",
        "outline_width": 3,
        "shadow_depth": 2,
        "border_style": 1,
        "back_color": "&H80000000",
        "bold": True,
        "italic": False,
        "underline": False,
        "words_per_group": 3,
        "preview_text": "To get <span style='color: #fde047;'>started</span> <span>✨</span>",
        "desc": "Playful casual sketch typography with doodle sparkles",
    },
    "news_anchor": {
        "id": "news_anchor",
        "name": "News Box",
        "category": "Badges & Boxes",
        "font_name": "Arial Black",
        "primary_color": "&H00FFFFFF",
        "highlight_color": "&H0000E5FF",
        "outline_color": "&H00000000",
        "outline_width": 1,
        "shadow_depth": 0,
        "border_style": 3,
        "back_color": "&H00000000",
        "bold": True,
        "italic": False,
        "underline": False,
        "words_per_group": 4,
        "preview_text": "<span style='background: #000000; color: #ffffff; padding: 4px 10px; border-radius: 4px; border-left: 3px solid #ef4444;'>TO GET STARTED</span>",
        "desc": "Solid opaque dark banner with red TV news accent",
    },
    "golden_glow": {
        "id": "golden_glow",
        "name": "24K Gold",
        "category": "Badges & Boxes",
        "font_name": "Impact",
        "primary_color": "&H00FFFFFF",
        "highlight_color": "&H0000C5FF",
        "outline_color": "&H00003060",
        "outline_width": 4,
        "shadow_depth": 3,
        "border_style": 1,
        "back_color": "&H80000000",
        "bold": True,
        "italic": False,
        "underline": False,
        "words_per_group": 3,
        "preview_text": "TO GET <span style='color: #f59e0b; text-shadow: 0 0 12px #f59e0b;'>STARTED 🏆</span>",
        "desc": "Rich metallic gold glow with trophy icon accent",
    },
    "toxic_lime": {
        "id": "toxic_lime",
        "name": "Toxic Lime",
        "category": "Badges & Boxes",
        "font_name": "Impact",
        "primary_color": "&H00FFFFFF",
        "highlight_color": "&H0000FF99",
        "outline_color": "&H00004010",
        "outline_width": 4,
        "shadow_depth": 2,
        "border_style": 1,
        "back_color": "&H80000000",
        "bold": True,
        "italic": False,
        "underline": False,
        "words_per_group": 2,
        "preview_text": "<span style='background: #84cc16; color: #000; padding: 3px 8px; border-radius: 6px; font-weight: 900;'>TO GET STARTED</span>",
        "desc": "Acid slime neon lime pill for intense reactions",
    },
    "sunset_gradient": {
        "id": "sunset_gradient",
        "name": "Sunset Sweep",
        "category": "Badges & Boxes",
        "font_name": "Trebuchet MS",
        "primary_color": "&H00FFFFFF",
        "highlight_color": "&H002080FF",
        "outline_color": "&H00301040",
        "outline_width": 3,
        "shadow_depth": 2,
        "border_style": 1,
        "back_color": "&H80000000",
        "bold": True,
        "italic": False,
        "underline": False,
        "words_per_group": 3,
        "preview_text": "TO GET <span style='background: linear-gradient(90deg, #f97316, #ec4899); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-weight: 800;'>STARTED</span>",
        "desc": "Warm sunset gradient shifting from coral orange to magenta",
    },

    # --- 4. GAMING & HYPE (25-32) ---
    "rage_fire": {
        "id": "rage_fire",
        "name": "Rage Fire",
        "category": "Gaming & Hype",
        "font_name": "Impact",
        "primary_color": "&H0000FFFF",
        "highlight_color": "&H000020FF",
        "outline_color": "&H00000080",
        "outline_width": 5,
        "shadow_depth": 4,
        "border_style": 1,
        "back_color": "&H80000000",
        "bold": True,
        "italic": False,
        "underline": False,
        "words_per_group": 2,
        "preview_text": "<span style='color: #ef4444; text-shadow: 0 0 10px #ef4444;'>RAGE FIRE 🔥</span>",
        "desc": "Intense gamer rage moments with fiery red glow",
    },
    "clutch_lightning": {
        "id": "clutch_lightning",
        "name": "Clutch Lightning",
        "category": "Gaming & Hype",
        "font_name": "Impact",
        "primary_color": "&H00FFFFFF",
        "highlight_color": "&H00FFFF30",
        "outline_color": "&H00401000",
        "outline_width": 4,
        "shadow_depth": 3,
        "border_style": 1,
        "back_color": "&H80000000",
        "bold": True,
        "italic": False,
        "underline": False,
        "words_per_group": 2,
        "preview_text": "<span style='color: #38bdf8; text-shadow: 0 0 12px #38bdf8;'>CLUTCH PLAY ⚡</span>",
        "desc": "Electric blue lightning shock for clutch victory moments",
    },
    "neon_tokyo": {
        "id": "neon_tokyo",
        "name": "Tokyo Cyberpunk",
        "category": "Gaming & Hype",
        "font_name": "Trebuchet MS",
        "primary_color": "&H00FF50B0",
        "highlight_color": "&H00FFFF00",
        "outline_color": "&H00300020",
        "outline_width": 4,
        "shadow_depth": 2,
        "border_style": 1,
        "back_color": "&H80000000",
        "bold": True,
        "italic": False,
        "underline": False,
        "words_per_group": 3,
        "preview_text": "<span style='color: #f43f5e;'>TOKYO</span> <span style='color: #06b6d4;'>NEON 🌸</span>",
        "desc": "Cyberpunk synthwave split with hot magenta & turquoise",
    },
    "matrix_terminal": {
        "id": "matrix_terminal",
        "name": "Matrix Terminal",
        "category": "Gaming & Hype",
        "font_name": "Consolas",
        "primary_color": "&H0020D020",
        "highlight_color": "&H0060FF60",
        "outline_color": "&H00002000",
        "outline_width": 3,
        "shadow_depth": 2,
        "border_style": 1,
        "back_color": "&H80000000",
        "bold": True,
        "italic": False,
        "underline": False,
        "words_per_group": 3,
        "preview_text": "<span style='color: #22c55e; font-family: monospace;'>SYSTEM_BOOT &gt;</span>",
        "desc": "Phosphor green monospace terminal for tech & coding clips",
    },
    "discord_blurple": {
        "id": "discord_blurple",
        "name": "Streamer Blurple",
        "category": "Gaming & Hype",
        "font_name": "Arial Black",
        "primary_color": "&H00FFFFFF",
        "highlight_color": "&H00F06050",
        "outline_color": "&H00301510",
        "outline_width": 3,
        "shadow_depth": 2,
        "border_style": 3,
        "back_color": "&H00F06050",
        "bold": True,
        "italic": False,
        "underline": False,
        "words_per_group": 3,
        "preview_text": "STREAMING <span style='background: #5865f2; color: #fff; padding: 2px 6px; border-radius: 4px;'>LIVE</span>",
        "desc": "Discord stream aesthetics with blurple brand tones",
    },
    "headshot_alert": {
        "id": "headshot_alert",
        "name": "Sniper Crosshair",
        "category": "Gaming & Hype",
        "font_name": "Impact",
        "primary_color": "&H00FFFFFF",
        "highlight_color": "&H000099FF",
        "outline_color": "&H00000080",
        "outline_width": 5,
        "shadow_depth": 3,
        "border_style": 1,
        "back_color": "&H80000000",
        "bold": True,
        "italic": False,
        "underline": False,
        "words_per_group": 2,
        "preview_text": "<span style='color: #f59e0b; font-weight: 900;'>HEADSHOT 🎯</span>",
        "desc": "FPS tactical orange highlight for shooter gameplay clips",
    },
    "galaxy_cosmic": {
        "id": "galaxy_cosmic",
        "name": "Galaxy Cosmic",
        "category": "Gaming & Hype",
        "font_name": "Segoe UI",
        "primary_color": "&H00FFFFFF",
        "highlight_color": "&H00FF80C0",
        "outline_color": "&H00401050",
        "outline_width": 4,
        "shadow_depth": 3,
        "border_style": 1,
        "back_color": "&H80000000",
        "bold": True,
        "italic": False,
        "underline": False,
        "words_per_group": 3,
        "preview_text": "<span style='color: #c084fc; text-shadow: 0 0 10px #c084fc;'>COSMIC GALAXY 🌌</span>",
        "desc": "Deep space starlight violet with nebular glow",
    },
    "stealth_tactical": {
        "id": "stealth_tactical",
        "name": "Stealth Camo",
        "category": "Gaming & Hype",
        "font_name": "Arial Black",
        "primary_color": "&H00D0D0C0",
        "highlight_color": "&H0030E0F0",
        "outline_color": "&H00102010",
        "outline_width": 3,
        "shadow_depth": 2,
        "border_style": 1,
        "back_color": "&H80000000",
        "bold": True,
        "italic": False,
        "underline": False,
        "words_per_group": 3,
        "preview_text": "<span style='background: #334155; color: #fde047; padding: 2px 6px; border-radius: 4px;'>TACTICAL OPS</span>",
        "desc": "Military tactical dark slate with amber hazard alert",
    },

    # --- 5. SOCIAL MEDIA & REELS (33-40) ---
    "tiktok_bounce": {
        "id": "tiktok_bounce",
        "name": "TikTok Pop",
        "category": "Social & Reels",
        "font_name": "Arial Black",
        "primary_color": "&H00FFFFFF",
        "highlight_color": "&H00E5F000",
        "outline_color": "&H00300020",
        "outline_width": 4,
        "shadow_depth": 2,
        "border_style": 1,
        "back_color": "&H80000000",
        "bold": True,
        "italic": False,
        "underline": False,
        "words_per_group": 2,
        "preview_text": "<span style='color: #00f2ea;'>TIK</span><span style='color: #ff004f;'>TOK</span> <span style='color: #fff;'>POP</span>",
        "desc": "Signature TikTok dual-color chromatic pop",
    },
    "reels_sunset": {
        "id": "reels_sunset",
        "name": "Insta Sunset",
        "category": "Social & Reels",
        "font_name": "Trebuchet MS",
        "primary_color": "&H00FFFFFF",
        "highlight_color": "&H007020F0",
        "outline_color": "&H00200030",
        "outline_width": 3,
        "shadow_depth": 2,
        "border_style": 1,
        "back_color": "&H80000000",
        "bold": True,
        "italic": False,
        "underline": False,
        "words_per_group": 3,
        "preview_text": "<span style='background: linear-gradient(135deg, #833ab4, #fd1d1d, #fcb045); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-weight: 900;'>REELS VIRAL</span>",
        "desc": "Instagram Reels gradient with violet-coral punch",
    },
    "podcast_warm": {
        "id": "podcast_warm",
        "name": "Warm Podcast",
        "category": "Social & Reels",
        "font_name": "Georgia",
        "primary_color": "&H00F5F5F0",
        "highlight_color": "&H0000D0FF",
        "outline_color": "&H00000000",
        "outline_width": 3,
        "shadow_depth": 2,
        "border_style": 1,
        "back_color": "&H80000000",
        "bold": True,
        "italic": False,
        "underline": False,
        "words_per_group": 4,
        "preview_text": "<span style='color: #e2e8f0; font-family: Georgia;'>Lex Fridman • 🎙️</span>",
        "desc": "Warm storytelling serif for long-form podcasts",
    },
    "finance_bull": {
        "id": "finance_bull",
        "name": "Bullish Ticker",
        "category": "Social & Reels",
        "font_name": "Impact",
        "primary_color": "&H00FFFFFF",
        "highlight_color": "&H0020E030",
        "outline_color": "&H00003000",
        "outline_width": 4,
        "shadow_depth": 2,
        "border_style": 1,
        "back_color": "&H80000000",
        "bold": True,
        "italic": False,
        "underline": False,
        "words_per_group": 2,
        "preview_text": "<span style='color: #10b981; font-weight: 800;'>+1000% PROFIT 💸</span>",
        "desc": "Financial market ticker green for crypto & money videos",
    },
    "storyteller": {
        "id": "storyteller",
        "name": "Storyteller",
        "category": "Social & Reels",
        "font_name": "Segoe UI",
        "primary_color": "&H00E0E0E0",
        "highlight_color": "&H00FFE090",
        "outline_color": "&H00101010",
        "outline_width": 2,
        "shadow_depth": 1,
        "border_style": 1,
        "back_color": "&H80000000",
        "bold": False,
        "italic": True,
        "underline": False,
        "words_per_group": 4,
        "preview_text": "<span style='color: #f8fafc; font-style: italic; letter-spacing: 1px;'>Once upon a time...</span>",
        "desc": "Cinematic narrative subtitle with soft warm glow",
    },
    "cinema_vintage": {
        "id": "cinema_vintage",
        "name": "Cinema 1970",
        "category": "Social & Reels",
        "font_name": "Courier New",
        "primary_color": "&H00B0FFFF",
        "highlight_color": "&H0020FFFF",
        "outline_color": "&H00000000",
        "outline_width": 3,
        "shadow_depth": 2,
        "border_style": 1,
        "back_color": "&H80000000",
        "bold": True,
        "italic": False,
        "underline": False,
        "words_per_group": 3,
        "preview_text": "<span style='color: #fef08a; letter-spacing: 2px; text-shadow: 2px 2px #000;'>CINEMA 1970</span>",
        "desc": "Vintage 35mm film grain cream subtitles with shadow",
    },
    "speedrun_1word": {
        "id": "speedrun_1word",
        "name": "Speedrun 1-Word",
        "category": "Social & Reels",
        "font_name": "Impact",
        "primary_color": "&H00FFFFFF",
        "highlight_color": "&H0000FFFF",
        "outline_color": "&H00000000",
        "outline_width": 6,
        "shadow_depth": 3,
        "border_style": 1,
        "back_color": "&H80000000",
        "bold": True,
        "italic": False,
        "underline": False,
        "words_per_group": 1,
        "preview_text": "<span style='font-size: 1.2rem; font-weight: 900; color: #facc15;'>BOOM!</span>",
        "desc": "1 word at a time ultra-fast pace for hyper-retention",
    },
    "glass_minimal": {
        "id": "glass_minimal",
        "name": "Glass Minimal",
        "category": "Social & Reels",
        "font_name": "Segoe UI",
        "primary_color": "&H00FFFFFF",
        "highlight_color": "&H0000E0FF",
        "outline_color": "&H00000000",
        "outline_width": 1,
        "shadow_depth": 0,
        "border_style": 3,
        "back_color": "&HC0101015",
        "bold": True,
        "italic": False,
        "underline": False,
        "words_per_group": 3,
        "preview_text": "<span style='background: rgba(255,255,255,0.15); backdrop-filter: blur(8px); padding: 4px 10px; border-radius: 12px; border: 1px solid rgba(255,255,255,0.2); color: #fff;'>Glass Minimal</span>",
        "desc": "Apple glassmorphism translucent pill with crisp white text",
    },
}


class SubtitleStyle:
    """Configuration for animated subtitle styling with 40 creator caption designs."""

    def __init__(
        self,
        font_name: str = "Arial Black",
        font_size: int = 56,
        primary_color: str = "&H00FFFFFF",
        highlight_color: str = "&H0000FFFF",
        outline_color: str = "&H00000000",
        outline_width: int = 4,
        shadow_depth: int = 2,
        words_per_group: int = 3,
        vertical_margin: int = 440,
        auto_emojis: bool = True,
        all_caps: bool = True,
        border_style: int = 1,
        back_color: str = "&H80000000",
        bold: bool = True,
        italic: bool = False,
        underline: bool = False,
        preset_id: str = "word_cut",
    ):
        self.font_name = font_name
        self.font_size = font_size
        self.primary_color = primary_color
        self.highlight_color = highlight_color
        self.outline_color = outline_color
        self.outline_width = outline_width
        self.shadow_depth = shadow_depth
        self.words_per_group = max(1, min(6, words_per_group))
        self.vertical_margin = vertical_margin
        self.auto_emojis = auto_emojis
        self.all_caps = all_caps
        self.border_style = border_style
        self.back_color = back_color
        self.bold = bold
        self.italic = italic
        self.underline = underline
        self.preset_id = preset_id

    @classmethod
    def from_preset(
        cls,
        preset_name: str = "word_cut",
        font_size: int = 56,
        words_per_group: Optional[int] = None,
        vertical_margin: int = 440,
        font_name: Optional[str] = None,
        auto_emojis: bool = True,
        all_caps: Optional[bool] = None,
    ) -> "SubtitleStyle":
        """Factory creating any of the 40 calibrated caption designs."""
        cfg = CAPTION_PRESETS_40.get(preset_name, CAPTION_PRESETS_40.get("word_cut", {})).copy()
        if not cfg:
            cfg = list(CAPTION_PRESETS_40.values())[0]

        eff_words = words_per_group if words_per_group is not None else cfg.get("words_per_group", 3)
        eff_caps = all_caps if all_caps is not None else (not cfg.get("italic", False))

        return cls(
            font_name=font_name or cfg.get("font_name", "Arial Black"),
            font_size=font_size,
            primary_color=cfg.get("primary_color", "&H00FFFFFF"),
            highlight_color=cfg.get("highlight_color", "&H0000FFFF"),
            outline_color=cfg.get("outline_color", "&H00000000"),
            outline_width=cfg.get("outline_width", 4),
            shadow_depth=cfg.get("shadow_depth", 2),
            words_per_group=eff_words,
            vertical_margin=vertical_margin,
            auto_emojis=auto_emojis,
            all_caps=eff_caps,
            border_style=cfg.get("border_style", 1),
            back_color=cfg.get("back_color", "&H80000000"),
            bold=cfg.get("bold", True),
            italic=cfg.get("italic", False),
            underline=cfg.get("underline", False),
            preset_id=preset_name,
        )


class SubtitleGenerator:
    """Generates animated ASS subtitle files with resolution auto-scaling."""

    def __init__(self, style: Optional[SubtitleStyle] = None):
        self.style = style or SubtitleStyle()

    def generate_ass_file(
        self,
        words_list: List[Dict[str, Any]],
        output_ass_path: str,
        video_width: int = 1080,
        video_height: int = 1920,
        time_offset: float = 0.0,
    ) -> bool:
        """
        Generates an ASS subtitle file with karaoke / word-by-word highlight.
        Automatically scales font size and margins for 4K (2160x3840), 2K, or 1080p.
        """
        os.makedirs(os.path.dirname(os.path.abspath(output_ass_path)), exist_ok=True)

        # Scale factor relative to baseline 1080x1920
        res_scale = video_width / 1080.0
        scaled_font_size = max(18, int(round(self.style.font_size * res_scale)))
        scaled_outline = max(1, int(round(self.style.outline_width * res_scale)))
        scaled_shadow = max(0, int(round(self.style.shadow_depth * res_scale)))
        scaled_margin_v = max(40, int(round(self.style.vertical_margin * res_scale)))
        scaled_margin_lr = max(20, int(round(40 * res_scale)))

        clip_words = []
        for w in words_list:
            w_start = max(0.0, w.get("start", 0.0) - time_offset)
            w_end = max(w_start + 0.1, w.get("end", 0.0) - time_offset)
            clean_word = w.get("word", "").strip()
            if clean_word:
                clip_words.append({
                    "word": clean_word,
                    "start": w_start,
                    "end": w_end,
                })

        if not clip_words:
            logger.warning("No words provided for subtitle generation.")
            return False

        groups = self._group_words(clip_words, max_words=self.style.words_per_group)

        bold_val = -1 if self.style.bold else 0
        italic_val = -1 if self.style.italic else 0
        underline_val = -1 if self.style.underline else 0

        header = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {video_width}
PlayResY: {video_height}
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,{self.style.font_name},{scaled_font_size},{self.style.primary_color},{self.style.highlight_color},{self.style.outline_color},{self.style.back_color},{bold_val},{italic_val},{underline_val},0,100,100,1,0,{self.style.border_style},{scaled_outline},{scaled_shadow},2,{scaled_margin_lr},{scaled_margin_lr},{scaled_margin_v},1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""

        events = []
        for grp in groups:
            for i, active_w in enumerate(grp):
                w_start_str = self._format_ass_time(active_w["start"])
                w_end_str = self._format_ass_time(active_w["end"])

                parts = []
                for j, w in enumerate(grp):
                    raw = w["word"].upper() if self.style.all_caps else w["word"]
                    
                    # Auto-inject high-retention emojis on matching words
                    if self.style.auto_emojis and j == i:
                        clean_lower = re.sub(r"[^\w]", "", w["word"].lower())
                        if clean_lower in OPUS_EMOJI_MAP:
                            raw = f"{raw} {OPUS_EMOJI_MAP[clean_lower]}"

                    if j == i:
                        # Highlight active word with preset color
                        parts.append(f"{{\\c{self.style.highlight_color}}}{raw}{{\\r}}")
                    else:
                        parts.append(f"{{\\c{self.style.primary_color}}}{raw}{{\\r}}")

                line_text = " ".join(parts)
                event_line = f"Dialogue: 0,{w_start_str},{w_end_str},Default,,0,0,0,,{line_text}\n"
                events.append(event_line)

        try:
            with open(output_ass_path, "w", encoding="utf-8") as f:
                f.write(header)
                f.writelines(events)
            return True
        except Exception as e:
            logger.error(f"Error writing ASS subtitle file: {e}")
            return False

    def _group_words(self, words: List[Dict[str, Any]], max_words: int = 3) -> List[List[Dict[str, Any]]]:
        """Group words into rhythmic bursts matching short-form creator cadence."""
        if not words:
            return []

        groups = []
        current = []
        for w in words:
            current.append(w)
            # Break group if max words reached or long punctuation pause
            has_break = bool(re.search(r"[.?!,]", w["word"]))
            if len(current) >= max_words or (has_break and len(current) >= 2):
                groups.append(current)
                current = []

        if current:
            groups.append(current)
        return groups

    @staticmethod
    def _format_ass_time(seconds: float) -> str:
        """Format seconds into ASS timestamp H:MM:SS.cs"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        centisecs = int(round((seconds - int(seconds)) * 100))
        return f"{hours}:{minutes:02d}:{secs:02d}.{centisecs:02d}"

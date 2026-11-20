"""Pre-built Demo Projects for ClipFusion (Matching OpusClip Demo Showcase).
Allows instant previewing, editing, and exporting without waiting for video downloads.
"""

from typing import List
from clipfusion.core.clip_extractor import VideoClipCandidate, HighlightCategory


def get_demo_clips(project_key: str = "danny_duncan") -> List[VideoClipCandidate]:
    """Return populated candidate clips for the selected demo project."""
    if project_key == "danny_duncan":
        return _build_danny_duncan_clips()
    elif project_key == "curry_drills":
        return _build_curry_clips()
    elif project_key == "tal_wilkenfeld":
        return _build_tal_clips()
    return _build_danny_duncan_clips()


def _build_danny_duncan_clips() -> List[VideoClipCandidate]:
    clips = []
    data = [
        (1, 12.0, 42.0, 99.0, HighlightCategory.FUNNY, "I CAN'T BELIEVE HE ACTUALLY DID THIS 😂", "Bro you won't believe what happened! We tried driving this car off the ramp and the engine literally flew out! Everyone was laughing so hard!"),
        (2, 85.0, 122.0, 98.0, HighlightCategory.GAMING, "THE MOST UNREAL CLUTCH MOMENT IN 24 HOURS 🎮", "Watch this headshot right now! If I miss this, the entire 24-hour challenge is ruined. BOOM! Clean shot!"),
        (3, 195.0, 230.0, 97.0, HighlightCategory.UNEXPECTED, "THE POLICE SHOWED UP TO OUR AIRBNB 😲", "Wait, who is knocking on the front door at 3 AM? Hold on, turn off the camera. Oh my god, are you serious?"),
        (4, 340.0, 378.0, 96.0, HighlightCategory.LOUD, "HE SMASHED THE 100K TROPHY BY ACCIDENT 📢", "NOOO! BRO STOP! You literally dropped the whole glass case! Look at everyone's face right now!"),
        (5, 510.0, 545.0, 95.0, HighlightCategory.EXCITING, "THE 1-MILLION DOLLAR JUMP ⚡", "This is the highest jump we have ever attempted. 3, 2, 1, let's send it! The crowd went completely wild!"),
        (6, 680.0, 715.0, 94.0, HighlightCategory.CONVERSATION, "Why Everyone Gave Up On This Creator 🎙️", "People thought I was crazy in the beginning. But if you never quit, you eventually become unavoidable."),
    ]
    for cid, st_t, end_t, score, cat, title, transcript in data:
        c = VideoClipCandidate(
            clip_id=cid,
            start_time=st_t,
            end_time=end_t,
            engagement_score=score,
            audio_score=score - 2,
            speech_score=score,
            visual_score=score - 1,
            face_score=score,
            transcript_text=transcript,
            highlight_category=cat,
            highlight_reason=f"{cat} (Virality Score: {int(score)}%)",
        )
        c.suggested_title = title
        c.suggested_description = f"{transcript[:90]}... Watch till the end! #shorts #viral #dannyduncan #clipfusion"
        c.suggested_hashtags = ["#shorts", "#trending", "#fyp", "#viral", "#dannyduncan", "#reels", "#clipfusion"]
        c.suggested_tags_csv = "shorts, viral, trending, danny duncan, funny, podcast, clipfusion"
        clips.append(c)
    return clips


def _build_curry_clips() -> List[VideoClipCandidate]:
    clips = []
    data = [
        (1, 15.0, 48.0, 98.0, HighlightCategory.EXCITING, "STEPH CURRY DRILLS 12 THREES IN A ROW 🏀", "Steph Curry is on absolute fire tonight! 1, 2, 3... he cannot miss from half-court! Look at the bench reaction!"),
        (2, 60.0, 92.0, 97.0, HighlightCategory.GAMING, "THE DRIBBLE MOVE THAT BROKE THE DEFENDER'S ANKLES ⚡", "Behind the back, crossover, step-back, SPLASH! That was completely undefendable."),
        (3, 140.0, 172.0, 96.0, HighlightCategory.UNEXPECTED, "HE TURNED AROUND BEFORE THE SHOT EVEN WENT IN 😲", "Curry shoots... turns around to high-five the bench before the ball hits the net! Unbelievable confidence!"),
        (4, 210.0, 245.0, 94.0, HighlightCategory.LOUD, "THE ENTIRE ARENA EXPLODED AFTER THIS SHOT 📢", "Deep three from the logo with 1 second on the clock! The noise level inside Chase Center is deafening!"),
        (5, 305.0, 338.0, 93.0, HighlightCategory.CONVERSATION, "Curry Explains The Secret Behind His Shooting Form 🎙️", "It is not about arm strength. It is 100% footwork, balance, and having the exact same release point every single time."),
    ]
    for cid, st_t, end_t, score, cat, title, transcript in data:
        c = VideoClipCandidate(
            clip_id=cid,
            start_time=st_t,
            end_time=end_t,
            engagement_score=score,
            audio_score=score - 1,
            speech_score=score - 2,
            visual_score=score,
            face_score=score - 1,
            transcript_text=transcript,
            highlight_category=cat,
            highlight_reason=f"{cat} (Virality Score: {int(score)}%)",
        )
        c.suggested_title = title
        c.suggested_description = f"{transcript[:90]}... Steph Curry being legendary! #curry #nba #shorts #basketball"
        c.suggested_hashtags = ["#shorts", "#nba", "#curry", "#warriors", "#basketball", "#viral", "#reels"]
        c.suggested_tags_csv = "shorts, curry, steph curry, nba, basketball, golden state warriors, highlights"
        clips.append(c)
    return clips


def _build_tal_clips() -> List[VideoClipCandidate]:
    clips = []
    data = [
        (1, 25.0, 68.0, 99.0, HighlightCategory.CONVERSATION, "Tal Wilkenfeld on The Moment Jeff Beck Changed Her Life 🎙️", "Jeff Beck called me and said: 'Can you fly to London tomorrow?' I was 20 years old and had never played in a stadium. It changed everything."),
        (2, 95.0, 135.0, 97.0, HighlightCategory.EMOTIONAL, "The Honest Truth About Playing Music With Prince 💖", "When Prince invited me to jam at Paisley Park, there were no notes, no sheet music. It was pure spiritual connection through sound."),
        (3, 180.0, 218.0, 96.0, HighlightCategory.UNEXPECTED, "She Played This Bass Solo and The Whole Room Froze 😲", "Listen to this bass groove. The rhythm and harmonics she pulls out of a standard 4-string bass defy physics."),
        (4, 290.0, 328.0, 95.0, HighlightCategory.EXCITING, "The Secret Technique That Makes Bass Sound Alive ⚡", "Most people play with their fingers. But the tone actually comes from how you relax your shoulders and release the string."),
    ]
    for cid, st_t, end_t, score, cat, title, transcript in data:
        c = VideoClipCandidate(
            clip_id=cid,
            start_time=st_t,
            end_time=end_t,
            engagement_score=score,
            audio_score=score,
            speech_score=score,
            visual_score=score - 2,
            face_score=score,
            transcript_text=transcript,
            highlight_category=cat,
            highlight_reason=f"{cat} (Virality Score: {int(score)}%)",
        )
        c.suggested_title = title
        c.suggested_description = f"{transcript[:90]}... Deep conversation with Lex Fridman. #music #podcast #shorts #talwilkenfeld"
        c.suggested_hashtags = ["#shorts", "#podcast", "#lexfridman", "#music", "#bass", "#interview", "#viral"]
        c.suggested_tags_csv = "shorts, podcast, lex fridman, tal wilkenfeld, music, bass, interview"
        clips.append(c)
    return clips

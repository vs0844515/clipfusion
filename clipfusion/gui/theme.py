"""Dark Studio styling and theme definitions for ClipFusion."""

DARK_THEME_CSS = """
<style>
/* Main app dark canvas */
.stApp {
    background-color: #0d1117;
    color: #e6edf3;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
}

/* Sidebar styling */
[data-testid="stSidebar"] {
    background-color: #161b22;
    border-right: 1px solid #30363d;
}

[data-testid="stSidebar"] .stMarkdown h1, 
[data-testid="stSidebar"] .stMarkdown h2, 
[data-testid="stSidebar"] .stMarkdown h3 {
    color: #f0f6fc;
}

/* Gradient Header */
.clipfusion-hero {
    background: linear-gradient(135deg, #1e1e38 0%, #0d1117 100%);
    border: 1px solid #383b58;
    border-radius: 14px;
    padding: 24px 28px;
    margin-bottom: 24px;
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.4);
}

.clipfusion-title {
    font-size: 2.3rem;
    font-weight: 800;
    background: linear-gradient(90deg, #a855f7 0%, #6366f1 50%, #06b6d4 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 6px;
    display: flex;
    align-items: center;
    gap: 12px;
}

.clipfusion-subtitle {
    font-size: 1.05rem;
    color: #8b949e;
    margin-bottom: 12px;
}

.badge-row {
    display: flex;
    gap: 8px;
    flex-wrap: wrap;
    margin-top: 10px;
}

.tech-badge {
    background: rgba(99, 102, 241, 0.15);
    border: 1px solid rgba(99, 102, 241, 0.35);
    color: #c7d2fe;
    padding: 4px 10px;
    border-radius: 20px;
    font-size: 0.78rem;
    font-weight: 600;
    letter-spacing: 0.5px;
    display: inline-flex;
    align-items: center;
    gap: 6px;
}

.yt-badge {
    background: rgba(239, 68, 68, 0.15);
    border: 1px solid rgba(239, 68, 68, 0.4);
    color: #fca5a5;
    padding: 4px 10px;
    border-radius: 20px;
    font-size: 0.78rem;
    font-weight: 600;
    display: inline-flex;
    align-items: center;
    gap: 6px;
}

.status-badge-ok {
    background: rgba(16, 185, 129, 0.15);
    border: 1px solid rgba(16, 185, 129, 0.4);
    color: #6ee7b7;
    padding: 4px 10px;
    border-radius: 20px;
    font-size: 0.78rem;
    font-weight: 600;
}

/* Card layout */
.clip-card {
    background: #161b22;
    border: 1px solid #30363d;
    border-radius: 12px;
    padding: 18px;
    margin-bottom: 18px;
    transition: all 0.25s ease;
    box-shadow: 0 4px 12px rgba(0,0,0,0.25);
}

.clip-card:hover {
    border-color: #6366f1;
    transform: translateY(-2px);
    box-shadow: 0 8px 20px rgba(99, 102, 241, 0.2);
}

.clip-header-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 12px;
    flex-wrap: wrap;
    gap: 8px;
}

.engagement-pill {
    background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
    color: #ffffff;
    padding: 4px 12px;
    border-radius: 16px;
    font-weight: 700;
    font-size: 0.85rem;
    box-shadow: 0 2px 8px rgba(99, 102, 241, 0.4);
}

.category-pill {
    background: #21262d;
    color: #c7d2fe;
    padding: 4px 10px;
    border-radius: 16px;
    font-size: 0.8rem;
    font-weight: 600;
    border: 1px solid #383b58;
}

.duration-pill {
    background: #21262d;
    color: #8b949e;
    padding: 4px 10px;
    border-radius: 16px;
    font-size: 0.8rem;
    border: 1px solid #30363d;
}

.hook-text {
    font-size: 0.95rem;
    color: #f0f6fc;
    font-weight: 500;
    line-height: 1.45;
    margin-bottom: 10px;
    background: #0d1117;
    padding: 10px 12px;
    border-radius: 8px;
    border-left: 3px solid #6366f1;
}

.reason-tag {
    font-size: 0.82rem;
    color: #a5b4fc;
    margin-bottom: 14px;
    display: flex;
    align-items: center;
    gap: 6px;
}

/* Metric chip */
.metric-container {
    display: flex;
    gap: 12px;
    margin-bottom: 16px;
}

.metric-box {
    background: #161b22;
    border: 1px solid #30363d;
    border-radius: 10px;
    padding: 12px 16px;
    flex: 1;
    text-align: center;
}

.metric-box .label {
    font-size: 0.75rem;
    color: #8b949e;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

.metric-box .val {
    font-size: 1.35rem;
    font-weight: 700;
    color: #f0f6fc;
    margin-top: 4px;
}

/* Stream info card */
.stream-card {
    background: #161b22;
    border: 1px solid #30363d;
    border-radius: 12px;
    padding: 16px 20px;
    margin-bottom: 16px;
    display: flex;
    gap: 16px;
    align-items: center;
}

.stream-live-pill {
    background: #ef4444;
    color: #fff;
    font-weight: 800;
    font-size: 0.75rem;
    padding: 2px 8px;
    border-radius: 4px;
    letter-spacing: 0.5px;
    animation: pulse 2s infinite;
}

/* Button enhancements */
.stButton>button {
    border-radius: 8px;
    font-weight: 600;
    transition: all 0.2s ease;
}

.stDownloadButton>button {
    border-radius: 8px;
    font-weight: 600;
}

/* Tabs styling */
.stTabs [data-baseweb="tab-list"] {
    gap: 8px;
    background-color: #161b22;
    padding: 6px;
    border-radius: 10px;
    border: 1px solid #30363d;
}

.stTabs [data-baseweb="tab"] {
    border-radius: 6px;
    color: #8b949e;
    padding: 8px 16px;
    font-weight: 600;
}

.stTabs [aria-selected="true"] {
    background-color: #6366f1 !important;
    color: #ffffff !important;
}

/* --- OPUS CLIP SIGNATURE UI ELEMENTS --- */
.opus-score-container {
    display: flex;
    align-items: center;
    gap: 12px;
    margin-bottom: 12px;
}

.opus-score-badge {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    padding: 6px 14px;
    border-radius: 20px;
    font-weight: 800;
    font-size: 1.05rem;
    letter-spacing: 0.5px;
    box-shadow: 0 4px 14px rgba(0, 0, 0, 0.35);
}

.opus-score-vhigh {
    background: linear-gradient(135deg, rgba(16, 185, 129, 0.25) 0%, rgba(5, 150, 105, 0.15) 100%);
    border: 1.5px solid #10b981;
    color: #34d399;
}

.opus-score-high {
    background: linear-gradient(135deg, rgba(99, 102, 241, 0.25) 0%, rgba(139, 92, 246, 0.15) 100%);
    border: 1.5px solid #8b5cf6;
    color: #c084fc;
}

.opus-score-good {
    background: linear-gradient(135deg, rgba(245, 158, 11, 0.25) 0%, rgba(217, 119, 6, 0.15) 100%);
    border: 1.5px solid #f59e0b;
    color: #fbbf24;
}

.opus-pillars-row {
    display: flex;
    gap: 8px;
    margin-bottom: 12px;
    flex-wrap: wrap;
}

.opus-pillar-pill {
    background: #0d1117;
    border: 1px solid #30363d;
    border-radius: 8px;
    padding: 6px 12px;
    font-size: 0.82rem;
    color: #e6edf3;
    display: flex;
    align-items: center;
    gap: 6px;
    flex: 1;
    min-width: 105px;
    justify-content: center;
}

.opus-pillar-pill b {
    color: #f0f6fc;
    font-weight: 700;
}

.opus-insight-box {
    background: linear-gradient(135deg, rgba(99, 102, 241, 0.08) 0%, rgba(14, 165, 233, 0.05) 100%);
    border: 1px solid rgba(99, 102, 241, 0.35);
    border-radius: 10px;
    padding: 10px 14px;
    margin-bottom: 14px;
    font-size: 0.85rem;
    line-height: 1.45;
    color: #cbd5e1;
}

.opus-insight-box b {
    color: #a5b4fc;
}

.opus-card {
    background: #161b22;
    border: 1px solid #30363d;
    border-radius: 14px;
    padding: 20px;
    margin-bottom: 20px;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
    transition: all 0.25s ease;
}

.opus-card:hover {
    border-color: #6366f1;
    box-shadow: 0 8px 24px rgba(99, 102, 241, 0.25);
    transform: translateY(-2px);
}

/* --- 4K RESOLUTION & SOCIAL PLATFORMS --- */
.badge-4k {
    background: linear-gradient(135deg, rgba(245, 158, 11, 0.25) 0%, rgba(217, 119, 6, 0.15) 100%);
    border: 1.5px solid #f59e0b;
    color: #fbbf24;
    padding: 3px 10px;
    border-radius: 6px;
    font-size: 0.8rem;
    font-weight: 800;
    letter-spacing: 0.5px;
    display: inline-flex;
    align-items: center;
    gap: 4px;
}

.platform-badge-yt {
    background: rgba(239, 68, 68, 0.15);
    border: 1.5px solid #ef4444;
    color: #fca5a5;
    padding: 4px 12px;
    border-radius: 20px;
    font-size: 0.82rem;
    font-weight: 700;
    display: inline-flex;
    align-items: center;
    gap: 6px;
}

.platform-badge-tt {
    background: linear-gradient(135deg, rgba(0, 242, 234, 0.15) 0%, rgba(255, 0, 79, 0.15) 100%);
    border: 1.5px solid #00f2ea;
    color: #ffffff;
    padding: 4px 12px;
    border-radius: 20px;
    font-size: 0.82rem;
    font-weight: 700;
    display: inline-flex;
    align-items: center;
    gap: 6px;
}

.platform-badge-ig {
    background: linear-gradient(135deg, rgba(225, 48, 108, 0.2) 0%, rgba(253, 29, 29, 0.15) 100%);
    border: 1.5px solid #e1306c;
    color: #fbcfe8;
    padding: 4px 12px;
    border-radius: 20px;
    font-size: 0.82rem;
    font-weight: 700;
    display: inline-flex;
    align-items: center;
    gap: 6px;
}

.social-card {
    background: #161b22;
    border: 1px solid #30363d;
    border-radius: 12px;
    padding: 16px;
    margin-bottom: 16px;
}

.caption-preview {
    background: #000000;
    border: 1px solid #30363d;
    border-radius: 10px;
    padding: 20px;
    text-align: center;
    margin: 12px 0;
    box-shadow: inset 0 0 20px rgba(0,0,0,0.8);
}

/* --- GOOGLE ONE-TAP SIGN-IN & OPUS NAVBAR --- */
.opus-top-navbar {
    display: flex;
    justify-content: space-between;
    align-items: center;
    background: rgba(22, 27, 34, 0.85);
    backdrop-filter: blur(12px);
    border: 1px solid #30363d;
    border-radius: 12px;
    padding: 10px 20px;
    margin-bottom: 20px;
    flex-wrap: wrap;
    gap: 12px;
}

.opus-nav-links {
    display: flex;
    gap: 16px;
    align-items: center;
    flex-wrap: wrap;
}

.opus-nav-link {
    color: #8b949e;
    font-size: 0.88rem;
    font-weight: 600;
    text-decoration: none;
    transition: color 0.2s ease;
}

.opus-nav-link:hover {
    color: #f0f6fc;
}

.user-profile-badge {
    display: inline-flex;
    align-items: center;
    gap: 10px;
    background: #0d1117;
    border: 1px solid #30363d;
    padding: 5px 12px 5px 8px;
    border-radius: 24px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
}

.user-avatar-circle {
    width: 30px;
    height: 30px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    color: #ffffff;
    font-weight: 800;
    font-size: 0.95rem;
    box-shadow: 0 2px 6px rgba(0, 0, 0, 0.4);
}

.google-auth-box {
    background: #1e1e24;
    border: 1px solid #3d444d;
    border-radius: 12px;
    padding: 16px 18px;
    box-shadow: 0 10px 25px rgba(0,0,0,0.5);
    margin-bottom: 14px;
}

.google-header-row {
    display: flex;
    align-items: center;
    gap: 10px;
    font-size: 0.88rem;
    color: #e6edf3;
    font-weight: 600;
    margin-bottom: 12px;
    padding-bottom: 8px;
    border-bottom: 1px solid #30363d;
}

.google-account-card {
    display: flex;
    align-items: center;
    gap: 12px;
    background: #161b22;
    border: 1px solid #30363d;
    border-radius: 10px;
    padding: 10px 14px;
    margin-bottom: 10px;
    cursor: pointer;
    transition: all 0.2s ease;
}

.google-account-card:hover {
    border-color: #6366f1;
    background: #1c2128;
}

.google-account-card.active {
    border-color: #10b981;
    background: rgba(16, 185, 129, 0.08);
}

/* --- MOBILE BROWSER & GOOGLE PLAY STORE --- */
.mobile-hub-card {
    background: #161b22;
    border: 1px solid #30363d;
    border-radius: 14px;
    padding: 20px;
    margin-bottom: 18px;
    box-shadow: 0 4px 14px rgba(0,0,0,0.3);
}

.mobile-hub-card:hover {
    border-color: #6366f1;
}

.playstore-tag {
    background: linear-gradient(135deg, #01875f 0%, #00a86b 100%);
    color: #ffffff;
    padding: 4px 12px;
    border-radius: 20px;
    font-size: 0.82rem;
    font-weight: 700;
    display: inline-flex;
    align-items: center;
    gap: 6px;
    box-shadow: 0 2px 8px rgba(1, 135, 95, 0.4);
}

/* =========================================================================
   AUTHENTIC OPUSCLIP SIGNATURE UI SUITE (MATCHING USER SCREENSHOTS)
   ========================================================================= */

/* 1. OpusClip Top Header */
.opus-site-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 14px 28px;
    background: #000000;
    border-bottom: 1px solid #1f1f23;
    margin-bottom: 24px;
    position: sticky;
    top: 0;
    z-index: 999;
}

.opus-brand {
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 1.5rem;
    font-weight: 800;
    color: #ffffff;
    letter-spacing: -0.5px;
    text-decoration: none;
}

.opus-brand span {
    color: #ffffff;
}

.opus-nav-menu {
    display: flex;
    gap: 24px;
    align-items: center;
}

.opus-nav-item {
    color: #a1a1aa;
    font-size: 0.90rem;
    font-weight: 500;
    text-decoration: none;
    transition: color 0.15s ease;
    cursor: pointer;
}

.opus-nav-item:hover {
    color: #ffffff;
}

.opus-signup-btn {
    background: #ffffff !important;
    color: #000000 !important;
    font-weight: 700 !important;
    font-size: 0.90rem !important;
    padding: 8px 18px !important;
    border-radius: 24px !important;
    border: none !important;
    cursor: pointer !important;
    transition: transform 0.15s ease, opacity 0.15s ease !important;
    display: inline-block !important;
}

.opus-signup-btn:hover {
    transform: scale(1.03);
    opacity: 0.95;
}

/* 2. OpusClip Landing Hero (Image 2) */
.opus-hero-section {
    text-align: center;
    padding: 40px 10px 30px 10px;
    max-width: 950px;
    margin: 0 auto;
}

.opus-hero-tag {
    color: #a1a1aa;
    font-size: 0.82rem;
    font-weight: 700;
    letter-spacing: 1.5px;
    text-transform: uppercase;
    margin-bottom: 18px;
}

.opus-hero-heading {
    font-size: 3.4rem;
    font-weight: 800;
    color: #ffffff;
    line-height: 1.15;
    margin-bottom: 20px;
    letter-spacing: -1px;
}

.opus-glow-reels {
    position: relative;
    display: inline-block;
    padding: 4px 22px;
    border-radius: 36px;
    background: linear-gradient(135deg, rgba(236, 72, 153, 0.25) 0%, rgba(99, 102, 241, 0.3) 50%, rgba(6, 182, 212, 0.25) 100%);
    backdrop-filter: blur(16px);
    border: 1px solid rgba(255, 255, 255, 0.2);
    box-shadow: 0 0 35px rgba(168, 85, 247, 0.4), inset 0 0 15px rgba(255, 255, 255, 0.15);
    color: #ffffff;
}

.opus-hero-subtitle {
    font-size: 1.15rem;
    color: #a1a1aa;
    max-width: 680px;
    margin: 0 auto 36px auto;
    line-height: 1.5;
}

/* 3. Opus Search Pill Box (Image 2 & 5) */
.opus-pill-search-box {
    background: #121216;
    border: 1.5px solid #27272a;
    border-radius: 40px;
    padding: 8px 12px 8px 24px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    max-width: 720px;
    margin: 0 auto 40px auto;
    box-shadow: 0 12px 40px rgba(0, 0, 0, 0.6);
    transition: border-color 0.2s ease, box-shadow 0.2s ease;
}

.opus-pill-search-box:focus-within {
    border-color: #6366f1;
    box-shadow: 0 12px 40px rgba(99, 102, 241, 0.25);
}

/* 4. Opus Viral Showcase Carousel (Image 5) */
.opus-carousel-grid {
    display: flex;
    gap: 16px;
    justify-content: center;
    flex-wrap: wrap;
    margin-bottom: 28px;
}

.opus-carousel-card {
    position: relative;
    width: 145px;
    height: 195px;
    border-radius: 14px;
    background: #18181b;
    border: 1px solid #27272a;
    overflow: hidden;
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.5);
    transition: transform 0.2s ease, border-color 0.2s ease;
}

.opus-carousel-card:hover {
    transform: translateY(-4px);
    border-color: #6366f1;
}

.opus-carousel-icon {
    position: absolute;
    top: 8px;
    right: 8px;
    width: 24px;
    height: 24px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 0.75rem;
    background: rgba(0, 0, 0, 0.6);
    backdrop-filter: blur(4px);
}

.opus-carousel-badge {
    position: absolute;
    bottom: 8px;
    left: 8px;
    background: rgba(0, 0, 0, 0.75);
    backdrop-filter: blur(6px);
    border: 1px solid rgba(255, 255, 255, 0.15);
    border-radius: 8px;
    padding: 3px 8px;
    font-size: 0.75rem;
    font-weight: 800;
    color: #ffffff;
}

/* 5. Feature Pills Bar (Image 5) */
.opus-feature-bar-row {
    display: flex;
    justify-content: center;
    gap: 12px;
    flex-wrap: wrap;
    margin-bottom: 40px;
}

.opus-feature-pill-btn {
    background: #18181b;
    border: 1px solid #27272a;
    color: #e4e4e7;
    font-size: 0.85rem;
    font-weight: 600;
    padding: 8px 16px;
    border-radius: 20px;
    display: inline-flex;
    align-items: center;
    gap: 8px;
    transition: all 0.15s ease;
}

.opus-feature-pill-btn:hover {
    background: #27272a;
    border-color: #3f3f46;
    color: #ffffff;
}

/* 6. Universal Login Modal Dialog (Image 1) */
.opus-modal-backdrop {
    background: rgba(0, 0, 0, 0.85);
    border: 1px solid #27272a;
    border-radius: 24px;
    padding: 36px 32px;
    max-width: 480px;
    margin: 0 auto 30px auto;
    box-shadow: 0 20px 60px rgba(0, 0, 0, 0.8);
    text-align: center;
}

.opus-modal-title {
    font-size: 1.65rem;
    font-weight: 800;
    color: #ffffff;
    margin-bottom: 8px;
    letter-spacing: -0.5px;
}

.opus-modal-subtitle {
    font-size: 0.95rem;
    color: #a1a1aa;
    margin-bottom: 24px;
}

.opus-auth-btn-google {
    background: #27272a !important;
    border: 1px solid #3f3f46 !important;
    color: #ffffff !important;
    font-size: 0.92rem !important;
    font-weight: 600 !important;
    padding: 12px 20px !important;
    border-radius: 28px !important;
    width: 100% !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    gap: 10px !important;
    margin-bottom: 12px !important;
    cursor: pointer !important;
    transition: background 0.15s ease, border-color 0.15s ease !important;
}

.opus-auth-btn-google:hover {
    background: #323238 !important;
    border-color: #52525b !important;
}

.opus-auth-btn-apple {
    background: #27272a !important;
    border: 1px solid #3f3f46 !important;
    color: #ffffff !important;
    font-size: 0.92rem !important;
    font-weight: 600 !important;
    padding: 12px 20px !important;
    border-radius: 28px !important;
    width: 100% !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    gap: 10px !important;
    margin-bottom: 20px !important;
    cursor: pointer !important;
    transition: background 0.15s ease !important;
}

.opus-auth-btn-apple:hover {
    background: #323238 !important;
}

.opus-divider-text {
    display: flex;
    align-items: center;
    color: #71717a;
    font-size: 0.82rem;
    margin: 20px 0;
}

.opus-divider-text::before,
.opus-divider-text::after {
    content: "";
    flex: 1;
    border-bottom: 1px solid #27272a;
}

.opus-divider-text::before {
    margin-right: 12px;
}

.opus-divider-text::after {
    margin-left: 12px;
}

.opus-email-input {
    background: #18181b !important;
    border: 1.5px solid #27272a !important;
    border-radius: 28px !important;
    padding: 12px 20px !important;
    color: #ffffff !important;
    font-size: 0.92rem !important;
    width: 100% !important;
    margin-bottom: 12px !important;
}

.opus-btn-continue-email {
    background: #ffffff !important;
    color: #000000 !important;
    font-weight: 700 !important;
    font-size: 0.95rem !important;
    padding: 12px 24px !important;
    border-radius: 28px !important;
    border: none !important;
    width: 100% !important;
    cursor: pointer !important;
    margin-bottom: 16px !important;
    transition: opacity 0.15s ease !important;
}

.opus-btn-continue-email:hover {
    opacity: 0.92 !important;
}

.opus-modal-footer {
    font-size: 0.78rem;
    color: #71717a;
    line-height: 1.4;
    margin-top: 16px;
}

.opus-modal-footer a {
    color: #a1a1aa;
    text-decoration: underline;
}

/* 7. Opus Studio Editor (Image 4) */
.opus-editor-shell {
    background: #09090b;
    border: 1px solid #27272a;
    border-radius: 16px;
    padding: 16px;
    margin-bottom: 24px;
}

.opus-transcript-box {
    background: #121216;
    border: 1px solid #27272a;
    border-radius: 12px;
    padding: 16px;
    height: 480px;
    overflow-y: auto;
    font-size: 0.92rem;
    line-height: 1.8;
    color: #d4d4d8;
}

.opus-transcript-word-viral {
    color: #84cc16;
    font-weight: 700;
    background: rgba(132, 204, 22, 0.12);
    padding: 2px 4px;
    border-radius: 4px;
}

.opus-speaker-tag {
    background: rgba(236, 72, 153, 0.2);
    color: #f472b6;
    border-radius: 12px;
    padding: 2px 10px;
    font-size: 0.75rem;
    font-weight: 700;
    display: inline-block;
    margin-bottom: 6px;
}

.opus-timeline-bar {
    background: #18181b;
    border: 1px solid #27272a;
    border-radius: 10px;
    padding: 12px 16px;
    margin-top: 16px;
    display: flex;
    justify-content: space-between;
    align-items: center;
}

/* 8. Vizard Style Vibrant Royal Purple Footer (User Screenshot) */
.vizard-footer-container {
    background: #471d9d;
    background: linear-gradient(135deg, #4b20a3 0%, #3e1687 100%);
    border-radius: 18px;
    padding: 44px 36px 36px 36px;
    margin-top: 50px;
    margin-bottom: 25px;
    position: relative;
    overflow: hidden;
    box-shadow: 0 16px 40px rgba(0, 0, 0, 0.45);
    border: 1px solid rgba(255, 255, 255, 0.08);
}

.vizard-footer-layout {
    display: flex;
    flex-wrap: wrap;
    gap: 32px;
    position: relative;
    z-index: 2;
}

.vizard-footer-brand {
    flex: 0 0 210px;
    display: flex;
    flex-direction: column;
}

.vizard-footer-logo {
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 1.85rem;
    font-weight: 800;
    color: #ffffff;
    letter-spacing: -0.5px;
    line-height: 1;
}

.vizard-footer-sparkle-icon {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    font-size: 1.6rem;
    color: #f472b6;
}

.vizard-footer-socials {
    display: flex;
    gap: 12px;
    align-items: center;
    margin-bottom: 16px;
}

.vizard-footer-social-icon {
    color: #ffffff;
    opacity: 0.88;
    text-decoration: none;
    font-size: 1.05rem;
    transition: transform 0.15s ease, opacity 0.15s ease;
    display: inline-flex;
    align-items: center;
    justify-content: center;
}

.vizard-footer-social-icon:hover {
    opacity: 1;
    transform: translateY(-2px);
    color: #f7a028;
}

.vizard-footer-ph-badge {
    background: #ffffff;
    border-radius: 8px;
    padding: 6px 12px;
    display: inline-flex;
    align-items: center;
    gap: 8px;
    box-shadow: 0 4px 14px rgba(0, 0, 0, 0.2);
    width: fit-content;
}

.vizard-footer-grid {
    flex: 1;
    min-width: 580px;
    display: grid;
    grid-template-columns: repeat(5, minmax(130px, 1fr));
    gap: 24px;
}

.vizard-col-title {
    color: #f7a028;
    font-weight: 800;
    font-size: 0.92rem;
    margin-bottom: 12px;
    letter-spacing: 0.2px;
}

.vizard-col-link {
    color: #ffffff;
    font-size: 0.82rem;
    line-height: 1.45;
    display: block;
    margin-bottom: 7px;
    text-decoration: none;
    opacity: 0.92;
    transition: opacity 0.15s ease, color 0.15s ease;
}

.vizard-col-link:hover {
    opacity: 1;
    color: #fcd34d;
    text-decoration: underline;
}

.vizard-bg-sparkle-1 {
    position: absolute;
    top: -12px;
    left: 42%;
    color: rgba(255, 255, 255, 0.15);
    font-size: 2.5rem;
    user-select: none;
    pointer-events: none;
    z-index: 1;
}

.vizard-bg-sparkle-2 {
    position: absolute;
    bottom: 12px;
    right: 28px;
    color: rgba(255, 255, 255, 0.15);
    font-size: 3.5rem;
    user-select: none;
    pointer-events: none;
    z-index: 1;
}

@media (max-width: 960px) {
    .vizard-footer-grid {
        grid-template-columns: repeat(2, 1fr);
        min-width: 100%;
    }
    .vizard-footer-brand {
        flex: 1 1 100%;
        margin-bottom: 24px;
    }
}

@media (max-width: 600px) {
    .vizard-footer-grid {
        grid-template-columns: 1fr;
    }
    .vizard-footer-container {
        padding: 30px 20px;
    }
}

/* 9. Creator Dashboard Studio Box & Demo Projects */
.opus-creator-card {
    background: #18181b;
    border: 1px solid #27272a;
    border-radius: 16px;
    padding: 20px 24px 18px 24px;
    max-width: 860px;
    margin: 0 auto 28px auto;
    box-shadow: 0 16px 48px rgba(0, 0, 0, 0.6);
}

.opus-card-tabstrip {
    display: flex;
    justify-content: space-between;
    align-items: center;
    border-bottom: 1px solid #27272a;
    padding-bottom: 12px;
    margin-bottom: 18px;
    flex-wrap: wrap;
    gap: 12px;
}

.opus-tab-btn-active {
    background: #27272a;
    border: 1.5px solid #22c55e;
    color: #ffffff;
    font-size: 0.90rem;
    font-weight: 700;
    padding: 6px 16px;
    border-radius: 8px;
    display: inline-flex;
    align-items: center;
    gap: 8px;
}

.opus-tab-btn-inactive {
    color: #a1a1aa;
    font-size: 0.90rem;
    font-weight: 600;
    padding: 6px 14px;
    display: inline-flex;
    align-items: center;
    gap: 8px;
    cursor: pointer;
    transition: color 0.15s ease;
}

.opus-tab-btn-inactive:hover {
    color: #ffffff;
}

.opus-card-input-box {
    background: #121215;
    border: 1.5px solid #27272a;
    border-radius: 12px;
    padding: 6px 8px 6px 16px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 16px;
    box-shadow: inset 0 2px 6px rgba(0, 0, 0, 0.4);
}

.opus-card-input-box:focus-within {
    border-color: #6366f1;
}

.opus-card-shortcuts-row {
    display: flex;
    gap: 20px;
    align-items: center;
    font-size: 0.86rem;
    color: #a1a1aa;
    font-weight: 600;
}

.opus-card-shortcut-item {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    cursor: pointer;
    transition: color 0.15s ease;
}

.opus-card-shortcut-item:hover {
    color: #ffffff;
}

.opus-recipes-wrapper {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 12px;
    margin-bottom: 48px;
}

.opus-recipe-pill {
    position: relative;
    background: #18181b;
    border: 1px solid #27272a;
    border-radius: 24px;
    padding: 6px 14px;
    font-size: 0.84rem;
    color: #d4d4d8;
    font-weight: 600;
    display: inline-flex;
    align-items: center;
    gap: 6px;
    cursor: pointer;
    transition: all 0.15s ease;
}

.opus-recipe-pill:hover {
    background: #27272a;
    border-color: #3f3f46;
    color: #ffffff;
}

.opus-recipe-dot {
    width: 6px;
    height: 6px;
    border-radius: 50%;
    background: #f43f5e;
    display: inline-block;
    vertical-align: top;
    margin-top: -4px;
    margin-left: 2px;
}

.opus-demo-card {
    position: relative;
    border-radius: 14px;
    overflow: hidden;
    height: 220px;
    background: #18181b;
    border: 1px solid #27272a;
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.4);
    display: flex;
    flex-direction: column;
    justify-content: flex-end;
    padding: 16px;
    transition: transform 0.2s ease, border-color 0.2s ease;
}

.opus-demo-card:hover {
    transform: translateY(-4px);
    border-color: #6366f1;
}

.opus-demo-overlay {
    position: absolute;
    inset: 0;
    background: linear-gradient(180deg, rgba(0, 0, 0, 0) 30%, rgba(2, 6, 23, 0.85) 75%, rgba(2, 6, 23, 0.98) 100%);
    z-index: 1;
}

.opus-demo-content {
    position: relative;
    z-index: 2;
    display: flex;
    justify-content: space-between;
    align-items: flex-end;
}

/* 10. Authentic Opus 40-Caption Design Picker Modal (Image 12:57 PM) */
.opus-caption-picker-card {
    background: #18181b;
    border: 1px solid #27272a;
    border-radius: 20px;
    padding: 24px 28px;
    margin-bottom: 24px;
    box-shadow: 0 20px 60px rgba(0, 0, 0, 0.7);
}

.opus-caption-box-preview {
    background: #27272a;
    border: 2px solid #3f3f46;
    border-radius: 16px;
    height: 110px;
    display: flex;
    align-items: center;
    justify-content: center;
    text-align: center;
    padding: 12px;
    transition: all 0.15s ease;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
}

.opus-caption-box-preview:hover {
    border-color: #71717a;
    transform: translateY(-2px);
}

.opus-caption-box-preview.active {
    border: 2.5px solid #ffffff !important;
    box-shadow: 0 0 20px rgba(255, 255, 255, 0.3);
    background: #2e2e34;
}

.opus-caption-box-label {
    text-align: center;
    font-size: 0.82rem;
    font-weight: 600;
    color: #a1a1aa;
    margin-top: 8px;
    margin-bottom: 12px;
}

/* Whop App & Vyro AI Ecosystem Branding */
.whop-badge {
    background: linear-gradient(135deg, rgba(255, 98, 67, 0.18) 0%, rgba(255, 138, 101, 0.12) 100%);
    border: 1px solid #ff6243;
    color: #ff8a65;
    padding: 5px 12px;
    border-radius: 9999px;
    font-size: 0.82rem;
    font-weight: 800;
    display: inline-flex;
    align-items: center;
    gap: 6px;
    box-shadow: 0 0 16px rgba(255, 98, 67, 0.25);
}

.vyro-badge {
    background: linear-gradient(135deg, rgba(168, 85, 247, 0.18) 0%, rgba(56, 189, 248, 0.15) 100%);
    border: 1px solid #a855f7;
    color: #c084fc;
    padding: 5px 12px;
    border-radius: 9999px;
    font-size: 0.82rem;
    font-weight: 800;
    display: inline-flex;
    align-items: center;
    gap: 6px;
    box-shadow: 0 0 16px rgba(168, 85, 247, 0.25);
}

.ecosystem-hero-card {
    background: linear-gradient(180deg, #181822 0%, #0d0e15 100%);
    border: 1.5px solid #2d2f44;
    border-radius: 20px;
    padding: 24px;
    box-shadow: 0 16px 36px rgba(0, 0, 0, 0.6);
    transition: transform 0.2s ease, border-color 0.2s ease;
    height: 100%;
    position: relative;
    overflow: hidden;
}

.ecosystem-hero-card:hover {
    border-color: #6366f1;
    transform: translateY(-3px);
}

.ecosystem-hero-card.whop {
    border-color: rgba(255, 98, 67, 0.5);
}

.ecosystem-hero-card.whop:hover {
    border-color: #ff6243;
    box-shadow: 0 16px 40px rgba(255, 98, 67, 0.2);
}

.ecosystem-hero-card.vyro {
    border-color: rgba(168, 85, 247, 0.5);
}

.ecosystem-hero-card.vyro:hover {
    border-color: #a855f7;
    box-shadow: 0 16px 40px rgba(168, 85, 247, 0.2);
}

.ecosystem-tag-pill {
    background: rgba(255, 255, 255, 0.08);
    border: 1px solid rgba(255, 255, 255, 0.15);
    color: #e2e8f0;
    font-size: 0.76rem;
    font-weight: 600;
    padding: 3px 9px;
    border-radius: 6px;
}

.whop-action-btn {
    background: #ff6243;
    color: #ffffff !important;
    font-weight: 800;
    border-radius: 10px;
    padding: 10px 16px;
    text-align: center;
    text-decoration: none;
    display: inline-block;
    transition: background 0.15s ease;
}

.whop-action-btn:hover {
    background: #ff785e;
}

/* Image 3 Modern Studio Ingestion & Recipe Cards */
.opus-stage3-card {
    background: #141418;
    border: 1.5px solid #27272e;
    border-radius: 20px;
    padding: 22px;
    margin-bottom: 20px;
    box-shadow: 0 14px 34px rgba(0, 0, 0, 0.45);
}

.opus-feature-switch-row {
    background: #191920;
    border: 1px solid #282834;
    border-radius: 12px;
    padding: 12px 18px;
    margin-bottom: 10px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    transition: all 0.15s ease;
}

.opus-feature-switch-row:hover {
    border-color: #3f3f50;
    background: #1d1d26;
}

.opus-free-tag {
    background: rgba(34, 197, 94, 0.15);
    border: 1px solid rgba(34, 197, 94, 0.4);
    color: #4ade80;
    font-size: 0.72rem;
    font-weight: 800;
    padding: 2px 7px;
    border-radius: 9999px;
    display: inline-flex;
    align-items: center;
    gap: 4px;
}
</style>
"""

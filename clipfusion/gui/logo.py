"""
ClipFusion AI - Official Vector Logo & Brand Assets.
Provides ultra-sharp, scalable SVG logo components with vibrant royal purple,
neon cyan, and magenta electric gradients.
"""

# 1. Iconic Fusion Emblem SVG (Scissors + Film Reel + AI Sparkle Infinity Loop)
CLIPFUSION_ICON_SVG = """<svg width="44" height="44" viewBox="0 0 100 100" fill="none" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="cf_grad1" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#ff6243"/>
      <stop offset="50%" stop-color="#ec4899"/>
      <stop offset="100%" stop-color="#8b5cf6"/>
    </linearGradient>
    <linearGradient id="cf_grad2" x1="100%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" stop-color="#38bdf8"/>
      <stop offset="50%" stop-color="#6366f1"/>
      <stop offset="100%" stop-color="#a855f7"/>
    </linearGradient>
    <radialGradient id="cf_glow" cx="50%" cy="50%" r="50%">
      <stop offset="0%" stop-color="#ec4899" stop-opacity="0.8"/>
      <stop offset="100%" stop-color="#8b5cf6" stop-opacity="0"/>
    </radialGradient>
    <filter id="cf_shadow" x="-20%" y="-20%" width="140%" height="140%">
      <feDropShadow dx="0" dy="4" stdDeviation="6" flood-color="#a855f7" flood-opacity="0.5"/>
    </filter>
  </defs>

  <!-- Ambient Backglow -->
  <circle cx="50" cy="50" r="42" fill="url(#cf_glow)" opacity="0.35"/>

  <!-- Outer Rounded Diamond Shield -->
  <rect x="12" y="12" width="76" height="76" rx="22" fill="#0f0f15" stroke="url(#cf_grad1)" stroke-width="2.5" filter="url(#cf_shadow)"/>

  <!-- Left Fusion Wing / Loop -->
  <path d="M30 65C23 58 23 42 32 34C40 26 54 36 60 50L30 65Z" fill="url(#cf_grad1)" opacity="0.9"/>

  <!-- Right Fusion Wing / Loop -->
  <path d="M70 35C77 42 77 58 68 66C60 74 46 64 40 50L70 35Z" fill="url(#cf_grad2)" opacity="0.9"/>

  <!-- Central Play Core -->
  <polygon points="46,38 62,50 46,62" fill="#ffffff" filter="url(#cf_shadow)"/>

  <!-- Futuristic Sparkle Accents -->
  <circle cx="50" cy="22" r="3" fill="#38bdf8"/>
  <circle cx="78" cy="50" r="2.5" fill="#ec4899"/>
  <circle cx="50" cy="78" r="3" fill="#ff6243"/>
  <circle cx="22" cy="50" r="2.5" fill="#a855f7"/>
</svg>"""

# 2. Complete Full Brand Header (Icon + Styled Typography + AI Badge)
CLIPFUSION_LOGO_FULL_HTML = f"""<div style="display: inline-flex; align-items: center; gap: 14px; text-decoration: none; user-select: none;">
    <div style="display: flex; align-items: center; justify-content: center; filter: drop-shadow(0 4px 16px rgba(168, 85, 247, 0.4));">
        {CLIPFUSION_ICON_SVG}
    </div>
    <div style="display: flex; flex-direction: column; justify-content: center; text-align: left;">
        <div style="display: flex; align-items: center; gap: 6px; line-height: 1;">
            <span style="font-size: 1.85rem; font-weight: 900; color: #ffffff; letter-spacing: -0.8px;">
                Clip<span style="background: linear-gradient(135deg, #ff6243 0%, #ec4899 50%, #a855f7 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">Fusion</span>
            </span>
            <span style="background: linear-gradient(135deg, #ec4899, #8b5cf6); color: #ffffff; font-size: 0.65rem; font-weight: 900; padding: 2px 7px; border-radius: 6px; letter-spacing: 0.8px; text-transform: uppercase; box-shadow: 0 2px 8px rgba(236, 72, 153, 0.4);">
                AI
            </span>
        </div>
        <span style="font-size: 0.72rem; color: #94a3b8; font-weight: 600; letter-spacing: 0.4px; margin-top: 4px;">
            VIRAL VIDEO REPURPOSING STUDIO
        </span>
    </div>
</div>"""

# 3. Compact Logo Pill (for Navigation bar or Top corner)
CLIPFUSION_LOGO_PILL_HTML = f"""<div style="display: inline-flex; align-items: center; gap: 10px; background: rgba(18, 18, 24, 0.85); border: 1px solid rgba(168, 85, 247, 0.35); border-radius: 30px; padding: 6px 16px 6px 8px; backdrop-filter: blur(12px); box-shadow: 0 6px 20px rgba(0,0,0,0.4);">
    <div style="display: flex; align-items: center; width: 32px; height: 32px;">
        {CLIPFUSION_ICON_SVG.replace('width="44" height="44"', 'width="32" height="32"')}
    </div>
    <div style="display: flex; align-items: center; gap: 6px;">
        <span style="font-size: 1.15rem; font-weight: 900; color: #ffffff; letter-spacing: -0.4px;">
            Clip<span style="color: #ec4899;">Fusion</span>
        </span>
        <span style="background: #a855f7; color: #fff; font-size: 0.58rem; font-weight: 900; padding: 1px 5px; border-radius: 4px;">AI</span>
    </div>
</div>"""

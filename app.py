"""
ClipFusion AI - Root Entry Point for Streamlit Web Cloud & Browser Hosting.
"""
import sys
from pathlib import Path

# Ensure project root is in sys.path
ROOT_DIR = Path(__file__).resolve().parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

# Run main GUI app
gui_app = ROOT_DIR / "clipfusion" / "gui" / "app.py"
with open(gui_app, "r", encoding="utf-8") as f:
    code = compile(f.read(), str(gui_app), "exec")
    exec(code, globals())

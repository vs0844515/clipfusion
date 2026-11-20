"""User authentication and profile session manager for ClipFusion.
Supports universal login for all creators (Google, Apple, Email),
Google One-Tap account switching, and persistent sessions.
"""

import json
from pathlib import Path
from typing import Dict, Any, Optional

DEFAULT_ACCOUNTS = [
    {
        "id": "vishal_sharma",
        "name": "Vishal Sharma",
        "email": "vs0844515@gmail.com",
        "avatar_letter": "V",
        "avatar_bg": "linear-gradient(135deg, #ec4899 0%, #db2777 100%)",
        "badge_color": "#ec4899",
        "plan": "100% Free Forever (No Subscriptions)",
        "role": "Owner / Main Channel",
        "status": "Active",
        "provider": "google",
    },
    {
        "id": "vexon_gaming",
        "name": "VEXON GAMING",
        "email": "vexongaming370@gmail.com",
        "avatar_letter": "V",
        "avatar_bg": "linear-gradient(135deg, #8b5cf6 0%, #6366f1 100%)",
        "badge_color": "#8b5cf6",
        "plan": "100% Free Forever (No Subscriptions)",
        "role": "Gaming & Live Stream Studio",
        "status": "Active",
        "provider": "google",
    },
]


class AuthManager:
    """Manages active creator credentials, universal login, and persistence."""

    def __init__(self, config_dir: Optional[Path] = None):
        if config_dir is None:
            self.config_dir = Path(__file__).resolve().parent.parent.parent / "config"
        else:
            self.config_dir = Path(config_dir)
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.session_file = self.config_dir / "user_session.json"
        self._ensure_session_file()

    def _ensure_session_file(self):
        if not self.session_file.is_file():
            initial_state = {
                "is_authenticated": False,
                "current_account_id": "vishal_sharma",
                "accounts": DEFAULT_ACCOUNTS,
            }
            try:
                with open(self.session_file, "w", encoding="utf-8") as f:
                    json.dump(initial_state, f, indent=4)
            except Exception:
                pass

    def load_session(self) -> Dict[str, Any]:
        """Load current authentication session from disk."""
        try:
            if self.session_file.is_file():
                with open(self.session_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    return data
        except Exception:
            pass
        return {
            "is_authenticated": False,
            "current_account_id": "vishal_sharma",
            "accounts": DEFAULT_ACCOUNTS,
        }

    def is_logged_in(self) -> bool:
        """Check if any creator is currently logged in."""
        sess = self.load_session()
        return bool(sess.get("is_authenticated", False))

    def get_current_user(self) -> Dict[str, Any]:
        """Get the currently logged-in user profile dictionary."""
        sess = self.load_session()
        cur_id = sess.get("current_account_id", "vishal_sharma")
        accounts = sess.get("accounts", DEFAULT_ACCOUNTS)
        for acc in accounts:
            if acc.get("id") == cur_id or acc.get("email") == cur_id:
                return acc
        return accounts[0] if accounts else DEFAULT_ACCOUNTS[0]

    def get_all_accounts(self) -> list:
        """Get list of all saved creator accounts."""
        sess = self.load_session()
        return sess.get("accounts", DEFAULT_ACCOUNTS)

    def switch_account(self, account_id_or_email: str) -> Dict[str, Any]:
        """Switch active account by ID or email and persist state."""
        sess = self.load_session()
        sess["is_authenticated"] = True
        sess["current_account_id"] = account_id_or_email
        self._save_session(sess)
        return self.get_current_user()

    def sign_in_google(self, email: str = "vs0844515@gmail.com", name: str = "Vishal Sharma") -> Dict[str, Any]:
        """Universal Google Login for any creator."""
        return self._sign_in_or_register(name=name, email=email, provider="google")

    def sign_in_apple(self, email: str = "creator@icloud.com", name: str = "Apple Creator") -> Dict[str, Any]:
        """Universal Apple Login for any creator."""
        return self._sign_in_or_register(name=name, email=email, provider="apple")

    def sign_in_email(self, email: str) -> Dict[str, Any]:
        """Universal Email Login for any creator worldwide."""
        clean_name = email.split("@")[0].replace(".", " ").replace("_", " ").title()
        return self._sign_in_or_register(name=clean_name, email=email, provider="email")

    def _sign_in_or_register(self, name: str, email: str, provider: str = "email") -> Dict[str, Any]:
        """Internal helper to sign in existing or create new creator profile."""
        sess = self.load_session()
        accounts = sess.get("accounts", DEFAULT_ACCOUNTS)
        
        # Check if already in accounts
        existing = next((a for a in accounts if a.get("email", "").lower() == email.lower()), None)
        if existing:
            sess["current_account_id"] = existing["id"]
        else:
            new_id = email.split("@")[0].lower().replace(".", "_").replace("+", "_")
            letter = name[0].upper() if name else "C"
            
            # Palette for new users
            palette = [
                "linear-gradient(135deg, #ec4899 0%, #db2777 100%)",
                "linear-gradient(135deg, #8b5cf6 0%, #6366f1 100%)",
                "linear-gradient(135deg, #06b6d4 0%, #3b82f6 100%)",
                "linear-gradient(135deg, #10b981 0%, #059669 100%)",
                "linear-gradient(135deg, #f59e0b 0%, #d97706 100%)",
            ]
            bg_color = palette[len(accounts) % len(palette)]
            
            new_acc = {
                "id": new_id,
                "name": name,
                "email": email,
                "avatar_letter": letter,
                "avatar_bg": bg_color,
                "badge_color": "#6366f1",
                "plan": "100% Free Forever (No Subscriptions)",
                "role": "Content Creator",
                "status": "Active",
                "provider": provider,
            }
            accounts.append(new_acc)
            sess["accounts"] = accounts
            sess["current_account_id"] = new_id

        sess["is_authenticated"] = True
        self._save_session(sess)
        return self.get_current_user()

    def sign_out(self):
        """Sign out current user and set guest mode."""
        sess = self.load_session()
        sess["is_authenticated"] = False
        self._save_session(sess)

    def _save_session(self, sess: Dict[str, Any]):
        try:
            with open(self.session_file, "w", encoding="utf-8") as f:
                json.dump(sess, f, indent=4)
        except Exception:
            pass

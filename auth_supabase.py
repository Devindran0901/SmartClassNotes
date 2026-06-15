"""
auth_supabase.py — SmartClassNotes v3
Backend powered by Supabase (Postgres + Auth).
"""

import os
import base64
from datetime import datetime
from supabase import create_client, Client
import streamlit as st

_client: Client = None
_admin_client: Client = None

def _get_secret(key_name: str) -> str:
    """Bulletproof secret fetcher to avoid Streamlit rerun race conditions."""
    try:
        if "supabase" in st.secrets and key_name in st.secrets["supabase"]:
            return st.secrets["supabase"][key_name]
    except Exception:
        pass
    # Fallback to environment variables
    env_map = {"url": "SUPABASE_URL", "key": "SUPABASE_KEY", "service_role_key": "SUPABASE_SERVICE_KEY"}
    return os.environ.get(env_map.get(key_name, ""), "")

def _sb() -> Client:
    """Standard client for regular user-authenticated operations."""
    global _client
    if _client is None:
        _client = create_client(_get_secret("url"), _get_secret("key"))
    return _client

def _sb_admin() -> Client:
    """Privileged admin client using service_role key to manage core Auth records and bypass RLS for history/analytics."""
    global _admin_client
    if _admin_client is None:
        secret_key = _get_secret("service_role_key")
        active_key = secret_key if secret_key else _get_secret("key")
        _admin_client = create_client(_get_secret("url"), active_key)
    return _admin_client

# ══════════════════════════════════════════════════════════════════════════════
#  CREATE — Register
# ══════════════════════════════════════════════════════════════════════════════
def register_user(name: str, email: str, password: str) -> dict:
    try:
        sb = _sb()
        auth_res = sb.auth.sign_up({"email": email, "password": password})
        if not auth_res.user:
            return {"success": False, "message": "Registration failed. Email may already be in use."}
        auth_id = auth_res.user.id
        existing = sb.table("users").select("id").eq("auth_id", auth_id).execute()
        if not existing.data:
            sb.table("users").insert({
                "auth_id": auth_id, "name": name, "email": email, "bio": "",
                "course": "", "profile_pic": "", "theme": "dark", "language": "en",
            }).execute()
        return {"success": True, "message": "Account created successfully. You can now sign in."}
    except Exception as e:
        msg = str(e)
        if "23505" in msg or "duplicate" in msg.lower():
            return {"success": False, "message": "Email is already registered."}
        return {"success": False, "message": msg}

# ══════════════════════════════════════════════════════════════════════════════
#  READ — Login
# ══════════════════════════════════════════════════════════════════════════════
def login_user(email: str, password: str) -> dict:
    try:
        sb = _sb()
        auth_res = sb.auth.sign_in_with_password({"email": email, "password": password})
        if not auth_res.user:
            return {"success": False, "message": "Incorrect email or password."}
        auth_id = auth_res.user.id
        prof = sb.table("users").select("*").eq("auth_id", auth_id).execute()
        if not prof.data:
            sb.table("users").insert({
                "auth_id": auth_id, "name": email.split("@")[0], "email": email,
                "bio": "", "course": "", "profile_pic": "", "theme": "dark", "language": "en",
            }).execute()
            prof = sb.table("users").select("*").eq("auth_id", auth_id).execute()
        user = prof.data[0]
        return {
            "success": True,
            "user_id": user["id"], "auth_id": auth_id, "email": user["email"],
            "name": user["name"], "profile_pic": user.get("profile_pic", ""),
            "theme": user.get("theme", "dark"), "language": user.get("language", "en"),
        }
    except Exception as e:
        if "invalid" in str(e).lower(): return {"success": False, "message": "Incorrect email or password."}
        return {"success": False, "message": str(e)}

# ══════════════════════════════════════════════════════════════════════════════
#  READ/UPDATE — Profile Operations
# ══════════════════════════════════════════════════════════════════════════════
def get_profile(user_id) -> dict:
    try:
        res = _sb().table("users").select("*").eq("id", user_id).execute()
        return dict(res.data[0]) if res.data else {}
    except Exception: return {}

def update_profile(user_id, payload: dict) -> dict:
    try:
        allowed = ("name", "email", "bio", "course", "theme", "language")
        update_data = {k: v for k, v in payload.items() if k in allowed}
        if not update_data: return {"success": True, "message": "Nothing to update."}
        update_data["updated_at"] = datetime.utcnow().isoformat()
        _sb().table("users").update(update_data).eq("id", user_id).execute()
        return {"success": True, "message": "Profile updated."}
    except Exception as e: return {"success": False, "message": str(e)}

def update_profile_picture(user_id, image_bytes: bytes, mime_type: str = "image/jpeg") -> dict:
    try:
        if len(image_bytes) > 2 * 1024 * 1024: return {"success": False, "message": "Image must be under 2 MB."}
        encoded = f"data:{mime_type};base64," + base64.b64encode(image_bytes).decode()
        _sb().table("users").update({"profile_pic": encoded, "updated_at": datetime.utcnow().isoformat()}).eq("id", user_id).execute()
        return {"success": True, "message": "Photo updated.", "profile_pic": encoded}
    except Exception as e: return {"success": False, "message": str(e)}

def remove_profile_picture(user_id) -> dict:
    try:
        _sb().table("users").update({"profile_pic": "", "updated_at": datetime.utcnow().isoformat()}).eq("id", user_id).execute()
        return {"success": True, "message": "Photo removed."}
    except Exception as e: return {"success": False, "message": str(e)}

def delete_account(user_id) -> dict:
    try:
        sb, sb_admin = _sb(), _sb_admin()
        prof = sb.table("users").select("auth_id").eq("id", user_id).execute()
        if not prof.data: return {"success": False, "message": "User profile not found."}
        sb.table("users").delete().eq("id", user_id).execute()
        sb_admin.auth.admin.delete_user(prof.data[0]["auth_id"])
        return {"success": True, "message": "Account wiped."}
    except Exception as e: return {"success": False, "message": str(e)}

def logout_user():
    try: _sb().auth.sign_out()
    except Exception: pass

# ══════════════════════════════════════════════════════════════════════════════
#  PASSWORD RESET (OTP FLOW)
# ══════════════════════════════════════════════════════════════════════════════
def request_password_reset(email: str) -> dict:
    try:
        _sb().auth.reset_password_email(email)
        return {"success": True, "message": "Reset code sent to email."}
    except Exception as e:
        return {"success": False, "message": str(e)}

def reset_password(email: str, token: str, new_password: str) -> dict:
    try:
        # Verify the 6-digit OTP code sent to the email
        res = _sb().auth.verify_otp({"email": email, "token": token, "type": "recovery"})
        if res.user:
            # Update password using admin client safely
            _sb_admin().auth.admin.update_user_by_id(res.user.id, {"password": new_password})
            return {"success": True, "message": "Password reset successfully."}
        return {"success": False, "message": "Invalid code or verification failed."}
    except Exception as e:
        return {"success": False, "message": str(e)}

# ══════════════════════════════════════════════════════════════════════════════
#  HISTORY — Create + Read (ADMIN BYPASS)
# ══════════════════════════════════════════════════════════════════════════════
def add_history_entry(user_id, entry_type: str, overall_summary: str, overview: str, keypoints: list, source_meta: dict = None) -> dict:
    try:
        _sb_admin().table("history").insert({
            "user_id": user_id, "type": entry_type, "overall_summary": overall_summary,
            "overview": overview, "keypoints": keypoints or [], "source_meta": source_meta or {},
        }).execute()
        _bump_analytics(user_id, entry_type, success=True)
        return {"success": True}
    except Exception as e:
        _bump_analytics(user_id, entry_type, success=False)
        return {"success": False, "message": str(e)}

def get_history(user_id, limit: int = 100) -> list:
    try:
        res = _sb_admin().table("history").select("*").eq("user_id", user_id).order("created_at", desc=True).limit(limit).execute()
        return res.data or []
    except Exception: return []

def delete_history_entry(entry_id) -> dict:
    try:
        _sb_admin().table("history").delete().eq("id", entry_id).execute()
        return {"success": True}
    except Exception as e: return {"success": False, "message": str(e)}

# ══════════════════════════════════════════════════════════════════════════════
#  ANALYTICS (ADMIN BYPASS)
# ══════════════════════════════════════════════════════════════════════════════
def _bump_analytics(user_id, entry_type: str, success: bool = True, time_saved_minutes: int = 45):
    try:
        sb_admin = _sb_admin()
        res = sb_admin.table("analytics").select("*").eq("user_id", user_id).execute()
        if not res.data:
            sb_admin.table("analytics").insert({"user_id": user_id}).execute()
            res = sb_admin.table("analytics").select("*").eq("user_id", user_id).execute()

        row = res.data[0]
        type_col = {"text": "text_count", "mic": "mic_count", "file": "file_count", "youtube": "youtube_count"}.get(entry_type)

        update_data = {
            "total_summaries": (row.get("total_summaries") or 0) + (1 if success else 0),
            "success_count":   (row.get("success_count") or 0) + (1 if success else 0),
            "fail_count":      (row.get("fail_count") or 0) + (0 if success else 1),
            "total_time_saved_minutes": (row.get("total_time_saved_minutes") or 0) + (time_saved_minutes if success else 0),
            "updated_at": datetime.utcnow().isoformat(),
        }
        if type_col and success:
            update_data[type_col] = (row.get(type_col) or 0) + 1

        sb_admin.table("analytics").update(update_data).eq("user_id", user_id).execute()
    except Exception as e:
        print(f"Analytics bump error: {e}")

def get_analytics(user_id) -> dict:
    try:
        res = _sb_admin().table("analytics").select("*").eq("user_id", user_id).execute()
        if res.data: return res.data[0]
    except Exception: pass
    return {"total_summaries": 0, "total_time_saved_minutes": 0, "success_count": 0, "fail_count": 0, "text_count": 0, "mic_count": 0, "file_count": 0, "youtube_count": 0}
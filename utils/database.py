"""
utils/database.py
Supabase database client – handles auth and predictions persistence.
"""

import os
import streamlit as st

try:
    from supabase import create_client, Client
    SUPABASE_AVAILABLE = True
except ImportError:
    SUPABASE_AVAILABLE = False


def get_supabase_client():
    """Return a Supabase client, reading credentials from st.secrets or env."""
    if not SUPABASE_AVAILABLE:
        return None
    try:
        url = st.secrets.get("SUPABASE_URL", os.getenv("SUPABASE_URL", ""))
        key = st.secrets.get("SUPABASE_ANON_KEY", os.getenv("SUPABASE_ANON_KEY", ""))
        if not url or not key:
            return None
        return create_client(url, key)
    except Exception:
        return None


# ── Users ────────────────────────────────────────────────────────────────────

def create_user(username: str, email: str, password_hash: str) -> dict:
    """Insert a new user; returns {ok, data, error}."""
    client = get_supabase_client()
    if client is None:
        return {"ok": False, "error": "Database not configured. Check SUPABASE_URL & SUPABASE_ANON_KEY."}
    try:
        res = client.table("app_users").insert({
            "username": username,
            "email": email,
            "password_hash": password_hash,
        }).execute()
        if res.data:
            return {"ok": True, "data": res.data[0]}
        return {"ok": False, "error": "Insert returned no data."}
    except Exception as e:
        err = str(e)
        if "duplicate" in err.lower() or "unique" in err.lower():
            if "username" in err.lower():
                return {"ok": False, "error": "Username already taken."}
            return {"ok": False, "error": "Email already registered."}
        return {"ok": False, "error": err}


def get_user_by_email(email: str) -> dict | None:
    """Fetch user row by email; returns dict or None."""
    client = get_supabase_client()
    if client is None:
        return None
    try:
        res = client.table("app_users").select("*").eq("email", email).execute()
        return res.data[0] if res.data else None
    except Exception:
        return None


def get_user_by_username(username: str) -> dict | None:
    client = get_supabase_client()
    if client is None:
        return None
    try:
        res = client.table("app_users").select("*").eq("username", username).execute()
        return res.data[0] if res.data else None
    except Exception:
        return None


# ── Predictions ───────────────────────────────────────────────────────────────

def save_prediction(user_id: str, username: str, inputs: dict, predicted_yield: float) -> dict:
    """Persist a prediction record."""
    client = get_supabase_client()
    if client is None:
        return {"ok": False, "error": "Database not configured."}
    try:
        res = client.table("predictions").insert({
            "user_id": user_id,
            "username": username,
            "region": inputs.get("region"),
            "crop": inputs.get("crop"),
            "rainfall_mm": inputs.get("rainfall_mm"),
            "temperature_c": inputs.get("temperature_c"),
            "humidity_pct": inputs.get("humidity_pct"),
            "soil_ph": inputs.get("soil_ph"),
            "soil_texture": inputs.get("soil_texture"),
            "soil_saturation": inputs.get("soil_saturation"),
            "land_size": inputs.get("land_size"),
            "predicted_yield": predicted_yield,
        }).execute()
        return {"ok": True, "data": res.data[0] if res.data else {}}
    except Exception as e:
        return {"ok": False, "error": str(e)}


def get_recent_predictions(limit: int = 20) -> list:
    """Fetch the most recent predictions across all users."""
    client = get_supabase_client()
    if client is None:
        return []
    try:
        res = (
            client.table("predictions")
            .select("*")
            .order("created_at", desc=True)
            .limit(limit)
            .execute()
        )
        return res.data or []
    except Exception:
        return []


def get_user_predictions(user_id: str, limit: int = 10) -> list:
    """Fetch predictions for a specific user."""
    client = get_supabase_client()
    if client is None:
        return []
    try:
        res = (
            client.table("predictions")
            .select("*")
            .eq("user_id", user_id)
            .order("created_at", desc=True)
            .limit(limit)
            .execute()
        )
        return res.data or []
    except Exception:
        return []

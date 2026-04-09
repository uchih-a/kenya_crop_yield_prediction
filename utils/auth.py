"""
utils/auth.py
Password hashing and session management helpers.
"""

import re
import bcrypt
import streamlit as st


# ── Password helpers ──────────────────────────────────────────────────────────

def hash_password(plain: str) -> str:
    return bcrypt.hashpw(plain.encode(), bcrypt.gensalt()).decode()


def verify_password(plain: str, hashed: str) -> bool:
    try:
        return bcrypt.checkpw(plain.encode(), hashed.encode())
    except Exception:
        return False


# ── Validation ────────────────────────────────────────────────────────────────

def validate_email(email: str) -> bool:
    pattern = r"^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$"
    return bool(re.match(pattern, email))


def validate_password(password: str) -> list[str]:
    """Return list of unmet requirements (empty = valid)."""
    errors = []
    if len(password) < 8:
        errors.append("At least 8 characters")
    if not re.search(r"[A-Z]", password):
        errors.append("At least one uppercase letter")
    if not re.search(r"[0-9]", password):
        errors.append("At least one number")
    return errors


def validate_username(username: str) -> list[str]:
    errors = []
    if len(username) < 3:
        errors.append("At least 3 characters")
    if len(username) > 30:
        errors.append("Maximum 30 characters")
    if not re.match(r"^[a-zA-Z0-9_]+$", username):
        errors.append("Only letters, numbers, and underscores")
    return errors


# ── Session ───────────────────────────────────────────────────────────────────

def init_session():
    defaults = {
        "authenticated": False,
        "user_id": None,
        "username": None,
        "email": None,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


def login_user(user: dict):
    st.session_state.authenticated = True
    st.session_state.user_id = user["id"]
    st.session_state.username = user["username"]
    st.session_state.email = user["email"]


def logout_user():
    for key in ["authenticated", "user_id", "username", "email"]:
        st.session_state[key] = None if key != "authenticated" else False


def is_authenticated() -> bool:
    return bool(st.session_state.get("authenticated", False))

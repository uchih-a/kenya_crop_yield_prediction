"""
pages/auth_page.py
Login and Signup with validation and feedback.
"""

import streamlit as st
from utils.auth import (
    hash_password, verify_password,
    validate_email, validate_password, validate_username,
    login_user,
)
from utils.database import create_user, get_user_by_email, get_user_by_username


def render():
    # ── Hero banner ────────────────────────────────────────────────────────
    st.markdown("""
    <div style='
        background: linear-gradient(135deg,#1B4332 0%,#2D6A4F 55%,#52B788 100%);
        border-radius:18px;padding:2.5rem 2rem;text-align:center;margin-bottom:2rem;
        box-shadow:0 6px 30px rgba(27,67,50,0.25)
    '>
      <div style='font-size:3rem;margin-bottom:0.4rem'>🌾</div>
      <h1 style='
          font-family:"DM Serif Display",Georgia,serif;
          color:#D8F3DC;font-size:2.1rem;margin:0 0 0.3rem
      '>AgriYield Kenya</h1>
      <p style='color:rgba(216,243,220,0.8);margin:0;font-size:0.97rem'>
        Agricultural Productivity & Crop Yield Prediction · LSTM Deep Learning
      </p>
    </div>
    """, unsafe_allow_html=True)

    # ── Centered container ─────────────────────────────────────────────────
    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        tab_login, tab_signup = st.tabs(["Sign In", "Create Account"])

        # ── LOGIN ──────────────────────────────────────────────────────────
        with tab_login:
            st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)

            login_id    = st.text_input("Email or Username", key="login_id",
                                        placeholder="you@example.com or username")
            login_pass  = st.text_input("Password", type="password", key="login_pass",
                                        placeholder="Your password")

            col_btn, col_hint = st.columns([1.5, 1])
            with col_btn:
                login_clicked = st.button("Sign In →", use_container_width=True, key="btn_login")

            st.markdown("<div style='height:0.3rem'></div>", unsafe_allow_html=True)

            if login_clicked:
                if not login_id or not login_pass:
                    st.markdown('<div class="ag-error">⚠️ Please fill in all fields.</div>',
                                unsafe_allow_html=True)
                else:
                    with st.spinner("Authenticating…"):
                        # Try email first, then username
                        user = None
                        if "@" in login_id:
                            user = get_user_by_email(login_id.strip().lower())
                        else:
                            user = get_user_by_username(login_id.strip())

                        if user is None:
                            st.markdown(
                                '<div class="ag-error">❌ Account not found. Check your credentials or sign up.</div>',
                                unsafe_allow_html=True,
                            )
                        elif not verify_password(login_pass, user["password_hash"]):
                            st.markdown(
                                '<div class="ag-error">❌ Incorrect password. Please try again.</div>',
                                unsafe_allow_html=True,
                            )
                        else:
                            login_user(user)
                            st.markdown(
                                f'<div class="ag-success">✅ Welcome back, <strong>{user["username"]}</strong>!</div>',
                                unsafe_allow_html=True,
                            )
                            st.session_state.page = "home"
                            st.rerun()

        # ── SIGNUP ─────────────────────────────────────────────────────────
        with tab_signup:
            st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)

            reg_username = st.text_input("Username", key="reg_user",
                                         placeholder="agronomist_nairobi",
                                         help="3–30 chars, letters/numbers/underscores only")
            reg_email    = st.text_input("Email Address", key="reg_email",
                                         placeholder="you@example.com")
            reg_pass     = st.text_input("Password", type="password", key="reg_pass",
                                         placeholder="Min 8 chars, 1 uppercase, 1 number",
                                         help="Minimum 8 characters with at least one uppercase letter and one number")
            reg_confirm  = st.text_input("Confirm Password", type="password", key="reg_confirm",
                                         placeholder="Repeat password")

            # Live password strength indicator
            if reg_pass:
                errors_pw = validate_password(reg_pass)
                strength  = 3 - len(errors_pw)
                color_map = {0: "#E76F51", 1: "#F4A261", 2: "#52B788", 3: "#2D6A4F"}
                label_map = {0: "Weak", 1: "Fair", 2: "Good", 3: "Strong"}
                bar_w = ["0%", "33%", "66%", "100%"][strength]
                color = color_map[strength]
                st.markdown(f"""
                <div style='margin-top:-0.5rem;margin-bottom:0.5rem'>
                  <div style='height:4px;background:#E0E0E0;border-radius:4px'>
                    <div style='height:4px;width:{bar_w};background:{color};border-radius:4px;transition:width 0.3s'></div>
                  </div>
                  <div style='font-size:0.75rem;color:{color};margin-top:2px'>{label_map[strength]} password</div>
                </div>
                """, unsafe_allow_html=True)

            signup_clicked = st.button("Create Account →", use_container_width=True, key="btn_signup")
            st.markdown("<div style='height:0.3rem'></div>", unsafe_allow_html=True)

            if signup_clicked:
                errors = []

                # Username validation
                u_errors = validate_username(reg_username.strip())
                errors.extend(u_errors)

                # Email validation
                if not reg_email or not validate_email(reg_email.strip()):
                    errors.append("Valid email address required")

                # Password validation
                p_errors = validate_password(reg_pass)
                errors.extend(p_errors)

                # Confirm password
                if reg_pass != reg_confirm:
                    errors.append("Passwords do not match")

                if errors:
                    err_html = "".join(f"<li>{e}</li>" for e in errors)
                    st.markdown(
                        f'<div class="ag-error"><strong>Please fix the following:</strong><ul style="margin:0.3rem 0 0 0">{err_html}</ul></div>',
                        unsafe_allow_html=True,
                    )
                else:
                    with st.spinner("Creating your account…"):
                        hashed = hash_password(reg_pass)
                        result = create_user(
                            username=reg_username.strip(),
                            email=reg_email.strip().lower(),
                            password_hash=hashed,
                        )

                    if result["ok"]:
                        st.markdown(
                            f'<div class="ag-success">🎉 Account created! Welcome, <strong>{reg_username}</strong>. Please sign in.</div>',
                            unsafe_allow_html=True,
                        )
                    else:
                        st.markdown(
                            f'<div class="ag-error">❌ {result["error"]}</div>',
                            unsafe_allow_html=True,
                        )


"""
app.py — Main entry point
Kenya Crop Yield Prediction System
Meru University of Science and Technology
"""

import streamlit as st

# ── Page config (must be first Streamlit call) ─────────────────────────────
st.set_page_config(
    page_title="AgriYield Kenya",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Imports after page config ──────────────────────────────────────────────
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils.auth import init_session, is_authenticated, logout_user
from views import auth_page, home_page, prediction_page, dashboard_page

# ── Global CSS ──────────────────────────────────────────────────────────────
st.markdown("""
<style>
/* ── Fonts ── */
@import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display&family=DM+Sans:wght@300;400;500;600&display=swap');

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
}

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: linear-gradient(160deg, #1B4332 0%, #2D6A4F 60%, #40916C 100%);
    border-right: none;
}
[data-testid="stSidebar"] * {
    color: #D8F3DC !important;
}
[data-testid="stSidebar"] hr {
    border-color: rgba(255,255,255,0.15) !important;
}
[data-testid="stSidebarNav"] { display: none; }

/* ── Metric cards ── */
[data-testid="stMetric"] {
    background: #FFFFFF;
    border: 1px solid #E8F5E9;
    border-radius: 12px;
    padding: 1rem 1.25rem;
    box-shadow: 0 2px 8px rgba(0,0,0,0.06);
}
[data-testid="stMetricLabel"] { color: #52796F !important; font-size: 0.78rem !important; letter-spacing: 0.04em; text-transform: uppercase; }
[data-testid="stMetricValue"] { color: #1B4332 !important; font-size: 1.7rem !important; font-weight: 600 !important; }
[data-testid="stMetricDelta"] { font-size: 0.82rem !important; }

/* ── Buttons ── */
.stButton > button {
    background: linear-gradient(135deg, #2D6A4F, #52B788);
    color: #fff !important;
    border: none;
    border-radius: 8px;
    font-weight: 600;
    letter-spacing: 0.03em;
    transition: transform 0.15s, box-shadow 0.15s;
}
.stButton > button:hover {
    transform: translateY(-1px);
    box-shadow: 0 4px 14px rgba(45,106,79,0.35);
}

/* ── Tabs ── */
.stTabs [role="tab"] {
    color: #52796F;
    font-weight: 500;
    border-radius: 6px 6px 0 0;
}
.stTabs [aria-selected="true"] {
    color: #1B4332 !important;
    border-bottom: 2px solid #52B788 !important;
    background: transparent !important;
}

/* ── Input fields ── */
.stTextInput > div > div > input,
.stSelectbox > div > div > select,
.stNumberInput > div > div > input {
    border-radius: 8px !important;
    border: 1.5px solid #B7E4C7 !important;
}
.stTextInput > div > div > input:focus,
.stSelectbox > div > div > select:focus,
.stNumberInput > div > div > input:focus {
    border-color: #52B788 !important;
    box-shadow: 0 0 0 3px rgba(82,183,136,0.18) !important;
}

/* ── Cards ── */
.ag-card {
    background: #ffffff;
    border-radius: 14px;
    border: 1px solid #E8F5E9;
    padding: 1.5rem 1.75rem;
    box-shadow: 0 2px 12px rgba(27,67,50,0.06);
    margin-bottom: 1rem;
}

/* ── Alert variants ── */
.ag-success { background:#D8F3DC; border-left:4px solid #52B788; padding:0.75rem 1rem; border-radius:6px; color:#1B4332; }
.ag-error   { background:#FFE8E3; border-left:4px solid #E76F51; padding:0.75rem 1rem; border-radius:6px; color:#7F1D1D; }
.ag-info    { background:#E0F2FE; border-left:4px solid #38BDF8; padding:0.75rem 1rem; border-radius:6px; color:#0C4A6E; }
.ag-warn    { background:#FEF9C3; border-left:4px solid #F4A261; padding:0.75rem 1rem; border-radius:6px; color:#713F12; }

/* ── Hide default decoration ── */
#MainMenu, footer { visibility: hidden; }
</style>
""", unsafe_allow_html=True)


# ── Session init ───────────────────────────────────────────────────────────
init_session()


# ── Sidebar navigation ─────────────────────────────────────────────────────
def render_sidebar():
    with st.sidebar:
        st.markdown("""
        <div style='text-align:center;padding:1.2rem 0 0.5rem'>
          <div style='font-size:2.5rem'>🌾</div>
          <div style='font-family:"DM Serif Display",serif;font-size:1.3rem;color:#D8F3DC;font-weight:700;line-height:1.2'>
            AgriYield<br><span style='font-size:0.85rem;opacity:0.8;font-family:sans-serif'>Kenya</span>
          </div>
        </div>
        <hr/>
        """, unsafe_allow_html=True)

        if is_authenticated():
            username = st.session_state.get("username", "User")
            st.markdown(f"""
            <div style='background:rgba(255,255,255,0.12);border-radius:10px;padding:0.6rem 0.9rem;margin-bottom:1rem'>
              <div style='font-size:0.72rem;opacity:0.7;text-transform:uppercase;letter-spacing:0.05em'>Signed in as</div>
              <div style='font-weight:600;font-size:0.95rem'>👤 {username}</div>
            </div>
            """, unsafe_allow_html=True)

            pages = {
                "Home":       "home",
                "Prediction": "prediction",
                "Dashboard":  "dashboard",
            }
            current = st.session_state.get("page", "home")

            for label, key in pages.items():
                active_style = "background:rgba(255,255,255,0.22);font-weight:700;" if current == key else ""
                if st.button(label, key=f"nav_{key}",
                             use_container_width=True,
                             type="secondary"):
                    st.session_state.page = key
                    st.rerun()

            st.markdown("<hr/>", unsafe_allow_html=True)
            if st.button("Sign Out", use_container_width=True):
                logout_user()
                st.session_state.page = "auth"
                st.rerun()
        else:
            st.markdown("""
            <div style='padding:0.5rem 0 1rem;opacity:0.75;font-size:0.88rem;line-height:1.6'>
              Agricultural productivity & crop yield prediction powered by LSTM deep learning.
            </div>
            """, unsafe_allow_html=True)

        st.markdown("""
        <div style='position:fixed;bottom:1rem;left:0;width:260px;text-align:center;font-size:0.7rem;opacity:0.5;color:#D8F3DC'>
          Meru University of Science<br>& Technology · DS 2026
        </div>
        """, unsafe_allow_html=True)


# ── Router ─────────────────────────────────────────────────────────────────
def main():
    render_sidebar()

    if "page" not in st.session_state:
        st.session_state.page = "auth" if not is_authenticated() else "home"

    if not is_authenticated():
        st.session_state.page = "auth"

    page = st.session_state.page

    if page == "auth":
        auth_page.render()
    elif page == "home":
        home_page.render()
    elif page == "prediction":
        prediction_page.render()
    elif page == "dashboard":
        dashboard_page.render()
    else:
        home_page.render()


if __name__ == "__main__":
    main()

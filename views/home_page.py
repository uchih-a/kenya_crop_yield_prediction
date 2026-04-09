"""
pages/home_page.py
Landing page shown after login with project overview.
"""

import streamlit as st
import pandas as pd
import os

DATA_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets", "kenya_crop_yield.csv")


@st.cache_data
def _load_summary():
    df = pd.read_csv(DATA_PATH)
    return {
        "total_records": len(df),
        "regions":       df["Region"].nunique(),
        "crops":         df["Crop"].nunique(),
        "avg_yield":     round(df["Past_Yield_tons_acre"].mean(), 3),
        "max_yield":     round(df["Past_Yield_tons_acre"].max(), 3),
        "years":         df["Month_Year"].str[-4:].nunique(),
    }


def render():
    username = st.session_state.get("username", "Researcher")
    summary  = _load_summary()

    # ── Hero ──────────────────────────────────────────────────────────────
    st.markdown(f"""
    <div style='
        background:linear-gradient(135deg,#1B4332 0%,#2D6A4F 55%,#40916C 100%);
        border-radius:18px;padding:2.8rem 2.5rem;margin-bottom:1.8rem;
        box-shadow:0 6px 30px rgba(27,67,50,0.2);position:relative;overflow:hidden
    '>
      <div style='position:absolute;right:-30px;top:-30px;width:180px;height:180px;
                  background:rgba(255,255,255,0.05);border-radius:50%'></div>
      <div style='position:absolute;right:50px;bottom:-50px;width:130px;height:130px;
                  background:rgba(255,255,255,0.04);border-radius:50%'></div>
      <div style='font-size:0.85rem;color:rgba(216,243,220,0.7);letter-spacing:0.1em;
                  text-transform:uppercase;margin-bottom:0.5rem'>
        Welcome back
      </div>
      <h1 style='font-family:"DM Serif Display",Georgia,serif;color:#D8F3DC;
                 font-size:2rem;margin:0 0 0.4rem'>
        Hello, {username} 👋
      </h1>
      <p style='color:rgba(216,243,220,0.82);margin:0;font-size:0.97rem;max-width:620px;line-height:1.6'>
        Agricultural Productivity &amp; Crop Yield Prediction System · Kenya · 
        Powered by Bidirectional LSTM Deep Learning
      </p>
    </div>
    """, unsafe_allow_html=True)

    # ── KPI Metrics ────────────────────────────────────────────────────────
    c1, c2, c3, c4, c5, c6 = st.columns(6)
    with c1: st.metric("📦 Records",    f"{summary['total_records']:,}")
    with c2: st.metric("🗺️ Regions",    summary["regions"])
    with c3: st.metric("🌱 Crops",      summary["crops"])
    with c4: st.metric("📅 Years",      summary["years"])
    with c5: st.metric("📈 Avg Yield",  f"{summary['avg_yield']} t/ac")
    with c6: st.metric("🏆 Peak Yield", f"{summary['max_yield']} t/ac")

    st.markdown("<div style='height:1.2rem'></div>", unsafe_allow_html=True)

    # ── About + Navigation cards ───────────────────────────────────────────
    col_left, col_right = st.columns([3, 2], gap="large")

    with col_left:
        st.markdown("""
        <div class='ag-card'>
          <h3 style='color:#1B4332;font-family:"DM Serif Display",Georgia,serif;
                     margin:0 0 0.8rem;font-size:1.25rem'>
            About This Project
          </h3>
          <p style='color:#3D5A5E;line-height:1.7;margin-bottom:0.8rem'>
            This system uses <strong>Long Short-Term Memory (LSTM)</strong> neural networks to 
            predict agricultural crop yields across Kenya's seven provinces. It ingests 
            multi-dimensional climate, soil, and historical yield data to generate actionable 
            forecasts for smallholder farmers and agricultural policymakers.
          </p>
          <p style='color:#3D5A5E;line-height:1.7;margin-bottom:0.8rem'>
            The model architecture combines a <strong>Bidirectional LSTM</strong> temporal 
            branch (processing 12-month sliding windows) with a static embedding branch for 
            region, crop type, and soil texture — merged and decoded through dense layers to 
            output yield in <em>tons/acre</em>.
          </p>
          <div style='display:flex;gap:0.75rem;flex-wrap:wrap;margin-top:1rem'>
            <span style='background:#D8F3DC;color:#1B4332;padding:0.3rem 0.8rem;
                         border-radius:20px;font-size:0.8rem;font-weight:600'>LSTM · BiLSTM</span>
            <span style='background:#D8F3DC;color:#1B4332;padding:0.3rem 0.8rem;
                         border-radius:20px;font-size:0.8rem;font-weight:600'>Scikit-learn</span>
            <span style='background:#D8F3DC;color:#1B4332;padding:0.3rem 0.8rem;
                         border-radius:20px;font-size:0.8rem;font-weight:600'>TensorFlow / Keras</span>
            <span style='background:#D8F3DC;color:#1B4332;padding:0.3rem 0.8rem;
                         border-radius:20px;font-size:0.8rem;font-weight:600'>Supabase</span>
            <span style='background:#D8F3DC;color:#1B4332;padding:0.3rem 0.8rem;
                         border-radius:20px;font-size:0.8rem;font-weight:600'>Streamlit</span>
          </div>
        </div>
        """, unsafe_allow_html=True)

        # Research objectives
        st.markdown("""
        <div class='ag-card'>
          <h3 style='color:#1B4332;font-family:"DM Serif Display",Georgia,serif;
                     margin:0 0 0.8rem;font-size:1.25rem'>
            Research Objectives
          </h3>
          <div style='display:grid;gap:0.55rem'>
            <div style='display:flex;align-items:flex-start;gap:0.6rem'>
              <span style='color:#52B788;font-size:1.1rem;margin-top:1px'>①</span>
              <span style='color:#3D5A5E;line-height:1.5'>Develop an LSTM-based deep learning model to predict crop yields from climate and soil inputs.</span>
            </div>
            <div style='display:flex;align-items:flex-start;gap:0.6rem'>
              <span style='color:#52B788;font-size:1.1rem;margin-top:1px'>②</span>
              <span style='color:#3D5A5E;line-height:1.5'>Analyze regional and seasonal yield patterns across Kenya's diverse agroecological zones.</span>
            </div>
            <div style='display:flex;align-items:flex-start;gap:0.6rem'>
              <span style='color:#52B788;font-size:1.1rem;margin-top:1px'>③</span>
              <span style='color:#3D5A5E;line-height:1.5'>Compare deep learning against baseline linear regression on RMSE, MAE, and R² metrics.</span>
            </div>
            <div style='display:flex;align-items:flex-start;gap:0.6rem'>
              <span style='color:#52B788;font-size:1.1rem;margin-top:1px'>④</span>
              <span style='color:#3D5A5E;line-height:1.5'>Deploy an interactive decision-support tool for farmers and agronomists.</span>
            </div>
          </div>
        </div>
        """, unsafe_allow_html=True)

    with col_right:
        # Quick-navigate cards
        pages = [
            ("🔮", "Prediction", "prediction",
             "Enter crop conditions and get instant yield forecasts with confidence intervals."),
            ("📊", "Dashboard", "dashboard",
             "Explore interactive visualisations of rainfall, temperature, and regional yield trends."),
        ]
        for icon, title, page_key, desc in pages:
            st.markdown(f"""
            <div class='ag-card' style='cursor:pointer;transition:transform 0.15s,box-shadow 0.15s'
                 onmouseenter="this.style.transform='translateY(-2px)';this.style.boxShadow='0 6px 20px rgba(27,67,50,0.14)'"
                 onmouseleave="this.style.transform='';this.style.boxShadow=''">
              <div style='font-size:1.8rem;margin-bottom:0.4rem'>{icon}</div>
              <div style='font-size:1.05rem;font-weight:700;color:#1B4332;margin-bottom:0.3rem'>{title}</div>
              <div style='font-size:0.87rem;color:#52796F;line-height:1.5'>{desc}</div>
            </div>
            """, unsafe_allow_html=True)
            if st.button(f"Go to {title} →", key=f"home_nav_{page_key}", use_container_width=True):
                st.session_state.page = page_key
                st.rerun()
            st.markdown("<div style='height:0.2rem'></div>", unsafe_allow_html=True)

        # Model architecture summary
        st.markdown("""
        <div class='ag-card' style='margin-top:0.2rem'>
          <div style='font-size:0.75rem;text-transform:uppercase;letter-spacing:0.08em;
                      color:#52796F;font-weight:600;margin-bottom:0.7rem'>Model Architecture</div>
          <div style='display:grid;gap:0.4rem;font-size:0.85rem;color:#3D5A5E'>
            <div style='display:flex;justify-content:space-between;padding:0.3rem 0;
                        border-bottom:1px solid #E8F5E9'>
              <span>Input window</span><strong style='color:#1B4332'>12 months</strong>
            </div>
            <div style='display:flex;justify-content:space-between;padding:0.3rem 0;
                        border-bottom:1px solid #E8F5E9'>
              <span>Temporal features</span><strong style='color:#1B4332'>14</strong>
            </div>
            <div style='display:flex;justify-content:space-between;padding:0.3rem 0;
                        border-bottom:1px solid #E8F5E9'>
              <span>LSTM units</span><strong style='color:#1B4332'>64 → 32</strong>
            </div>
            <div style='display:flex;justify-content:space-between;padding:0.3rem 0;
                        border-bottom:1px solid #E8F5E9'>
              <span>Architecture</span><strong style='color:#1B4332'>Bi-LSTM + Static</strong>
            </div>
            <div style='display:flex;justify-content:space-between;padding:0.3rem 0'>
              <span>Optimizer</span><strong style='color:#1B4332'>Adam (lr=0.001)</strong>
            </div>
          </div>
        </div>
        """, unsafe_allow_html=True)

    # ── Data overview ──────────────────────────────────────────────────────
    st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)
    with st.expander("📋 Dataset Preview", expanded=False):
        df = pd.read_csv(DATA_PATH)
        st.dataframe(
            df.head(50),
            use_container_width=True,
            hide_index=True,
        )
        st.caption(f"Showing 50 of {len(df):,} records · {df.shape[1]} features")

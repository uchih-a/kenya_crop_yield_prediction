"""
pages/prediction_page.py
Prediction interface with inputs, output, trend chart, and recent predictions toggle.
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
import calendar

from utils.predictor import predict_yield, get_trend_predictions
from utils.database  import save_prediction, get_recent_predictions, get_user_predictions
from utils.theme     import apply_chart_style, GREEN_DARK, GREEN_MID, GREEN_LIGHT, AMBER, ACCENT_RED


REGIONS      = ["Central", "Coastal", "Eastern", "North Eastern", "Nyanza", "Rift Valley", "Western"]
CROPS        = ["Beans", "Coffee", "Maize", "Millet", "Potatoes", "Tea", "Wheat"]
SOIL_TEXTURES = ["Clay", "Clay Loam", "Loam", "Sandy", "Sandy Loam", "Volcanic"]
MONTHS       = list(calendar.month_name)[1:]   # Jan … Dec


def render():
    st.markdown("""
    <div style='margin-bottom:1.5rem'>
      <h1 style='font-family:"DM Serif Display",Georgia,serif;color:#1B4332;
                 font-size:1.8rem;margin:0 0 0.3rem'>🔮 Yield Prediction</h1>
      <p style='color:#52796F;margin:0;font-size:0.93rem'>
        Enter your field conditions below to generate an AI-powered crop yield forecast.
      </p>
    </div>
    """, unsafe_allow_html=True)

    # ── Two-column layout ──────────────────────────────────────────────────
    col_inputs, col_results = st.columns([2, 3], gap="large")

    # ── INPUT FORM ─────────────────────────────────────────────────────────
    with col_inputs:
        st.markdown("""
        <div style='background:#FFFFFF;border:1px solid #E8F5E9;border-radius:14px;
                    padding:1.4rem 1.5rem;box-shadow:0 2px 10px rgba(27,67,50,0.06)'>
          <div style='font-weight:700;color:#1B4332;font-size:0.95rem;
                      text-transform:uppercase;letter-spacing:0.06em;margin-bottom:1rem'>
            Field Parameters
          </div>
        """, unsafe_allow_html=True)

        # ── Location & crop
        region       = st.selectbox("🗺️ Region",       REGIONS,       key="pred_region")
        crop         = st.selectbox("🌱 Crop Type",    CROPS,         key="pred_crop")
        soil_texture = st.selectbox("🪨 Soil Texture", SOIL_TEXTURES, key="pred_soil_tex")
        month        = st.selectbox("📅 Planting Month", MONTHS,      key="pred_month")
        month_num    = MONTHS.index(month) + 1

        st.markdown("<hr style='border-color:#E8F5E9;margin:0.8rem 0'/>", unsafe_allow_html=True)

        # ── Climate inputs
        st.markdown("<div style='font-size:0.8rem;font-weight:600;color:#52796F;text-transform:uppercase;letter-spacing:0.05em;margin-bottom:0.4rem'>Climate</div>", unsafe_allow_html=True)

        rainfall  = st.slider("🌧️ Rainfall (mm)",     0.0, 325.0, 80.0, 0.5, key="pred_rain",
                               help="Monthly rainfall in millimetres")
        temp      = st.slider("🌡️ Temperature (°C)", 8.0, 45.0, 22.0, 0.1, key="pred_temp")
        humidity  = st.slider("💧 Humidity (%)",      10.0, 100.0, 65.0, 0.5, key="pred_hum")

        st.markdown("<hr style='border-color:#E8F5E9;margin:0.8rem 0'/>", unsafe_allow_html=True)

        # ── Soil inputs
        st.markdown("<div style='font-size:0.8rem;font-weight:600;color:#52796F;text-transform:uppercase;letter-spacing:0.05em;margin-bottom:0.4rem'>Soil & Land</div>", unsafe_allow_html=True)

        soil_ph    = st.slider("⚗️ Soil pH",           4.0, 9.0, 6.2, 0.01, key="pred_ph")
        saturation = st.slider("🌊 Soil Saturation (%)", 5.0, 100.0, 49.0, 0.5, key="pred_sat")
        land_size  = st.slider("📐 Land Size (acres)",   0.5, 10.0, 5.0, 0.1, key="pred_land")

        st.markdown("</div>", unsafe_allow_html=True)
        st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)

        predict_btn = st.button("⚡ Generate Prediction", use_container_width=True, key="btn_predict")

    # ── RESULTS ────────────────────────────────────────────────────────────
    with col_results:

        if predict_btn:
            inputs = {
                "region":       region,
                "crop":         crop,
                "soil_texture": soil_texture,
                "rainfall_mm":  rainfall,
                "temperature_c": temp,
                "humidity_pct": humidity,
                "soil_ph":      soil_ph,
                "soil_saturation": saturation,
                "land_size":    land_size,
                "month":        month_num,
            }

            with st.spinner("Running prediction model…"):
                result = predict_yield(inputs)

            pred_yield = result["predicted_yield"]
            ci_low     = result["confidence_low"]
            ci_high    = result["confidence_high"]
            model_name = result["model_name"]

            # Store in session for display persistence
            st.session_state["last_prediction"] = {
                "inputs": inputs, "result": result, "month": month
            }

            # Save to DB
            user_id  = st.session_state.get("user_id")
            username = st.session_state.get("username", "unknown")
            if user_id:
                save_prediction(user_id, username, inputs, pred_yield)

        # ── Show last prediction ───────────────────────────────────────────
        last = st.session_state.get("last_prediction")

        if last is None:
            st.markdown("""
            <div style='background:#F8FAF7;border:2px dashed #B7E4C7;border-radius:14px;
                        padding:3rem 2rem;text-align:center;color:#52796F'>
              <div style='font-size:2.5rem;margin-bottom:0.5rem'>🌾</div>
              <div style='font-size:1rem;font-weight:500'>Fill in the parameters and click <strong>Generate Prediction</strong></div>
              <div style='font-size:0.85rem;margin-top:0.4rem;opacity:0.75'>Your yield forecast will appear here</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            inp  = last["inputs"]
            res  = last["result"]
            pred = res["predicted_yield"]
            cil  = res["confidence_low"]
            cih  = res["confidence_high"]

            # ── Big result card ────────────────────────────────────────────
            total_yield = round(pred * inp["land_size"], 2)

            # Yield rating
            if pred >= 2.0:   rating, badge_color = "Excellent",  "#2D6A4F"
            elif pred >= 1.2: rating, badge_color = "Good",       "#52B788"
            elif pred >= 0.7: rating, badge_color = "Moderate",   "#F4A261"
            else:             rating, badge_color = "Low",        "#E76F51"

            st.markdown(f"""
            <div style='background:linear-gradient(135deg,#1B4332,#2D6A4F);
                        border-radius:16px;padding:1.8rem 2rem;color:white;margin-bottom:1rem;
                        box-shadow:0 6px 24px rgba(27,67,50,0.3)'>
              <div style='display:flex;justify-content:space-between;align-items:flex-start'>
                <div>
                  <div style='font-size:0.78rem;opacity:0.7;text-transform:uppercase;
                              letter-spacing:0.08em;margin-bottom:0.2rem'>
                    Predicted Yield
                  </div>
                  <div style='font-family:"DM Serif Display",Georgia,serif;font-size:3rem;
                              line-height:1;font-weight:400'>
                    {pred} <span style='font-size:1.1rem;opacity:0.8'>tons/acre</span>
                  </div>
                  <div style='font-size:0.83rem;opacity:0.7;margin-top:0.4rem'>
                    95% CI: [{cil} – {cih}] tons/acre
                  </div>
                </div>
                <div style='text-align:right'>
                  <div style='background:{badge_color};border:2px solid rgba(255,255,255,0.3);
                              border-radius:10px;padding:0.4rem 0.9rem;font-weight:700;
                              font-size:0.9rem;margin-bottom:0.5rem'>
                    {rating}
                  </div>
                  <div style='font-size:0.8rem;opacity:0.75'>{inp["crop"]} · {inp["region"]}</div>
                  <div style='font-size:0.8rem;opacity:0.75'>{last["month"]}</div>
                </div>
              </div>
            </div>
            """, unsafe_allow_html=True)

            # ── Secondary metrics ──────────────────────────────────────────
            m1, m2, m3 = st.columns(3)
            with m1: st.metric("🌾 Total Yield",    f"{total_yield} tons",    f"{inp['land_size']} acres")
            with m2: st.metric("📈 Upper Bound",   f"{cih} t/ac")
            with m3: st.metric("📉 Lower Bound",   f"{cil} t/ac")

            st.caption(f"Model: {res['model_name']}")

            # ── Trend chart (monthly projections) ─────────────────────────
            st.markdown("<div style='height:0.6rem'></div>", unsafe_allow_html=True)
            st.markdown("**📈 Monthly Yield Forecast Trend**")

            with st.spinner("Building trend chart…"):
                trend_df = get_trend_predictions(inp, n_months=12)

            fig = go.Figure()

            # Confidence band
            fig.add_trace(go.Scatter(
                x=trend_df["Month_Name"].tolist() + trend_df["Month_Name"].tolist()[::-1],
                y=trend_df["CI_High"].tolist()    + trend_df["CI_Low"].tolist()[::-1],
                fill="toself",
                fillcolor="rgba(82,183,136,0.15)",
                line=dict(color="rgba(0,0,0,0)"),
                hoverinfo="skip",
                name="95% CI",
                showlegend=True,
            ))

            # Prediction line
            fig.add_trace(go.Scatter(
                x=trend_df["Month_Name"],
                y=trend_df["Predicted_Yield"],
                mode="lines+markers",
                line=dict(color=GREEN_MID, width=2.5),
                marker=dict(size=7, color=GREEN_DARK, line=dict(color="white", width=1.5)),
                name="Predicted Yield",
            ))

            # Highlight selected month
            sel_row = trend_df[trend_df["Month_Name"] == last["month"][:3]]
            if not sel_row.empty:
                fig.add_trace(go.Scatter(
                    x=[sel_row.iloc[0]["Month_Name"]],
                    y=[sel_row.iloc[0]["Predicted_Yield"]],
                    mode="markers",
                    marker=dict(size=14, color=AMBER, symbol="star",
                                line=dict(color=GREEN_DARK, width=1.5)),
                    name=f"Selected ({last['month'][:3]})",
                ))

            fig = apply_chart_style(
                fig,
                title=f"{inp['crop']} Yield Forecast — {inp['region']} Region (tons/acre)",
                height=340,
            )
            fig.update_layout(
                xaxis_title="Month",
                yaxis_title="Yield (tons/acre)",
                hovermode="x unified",
            )
            st.plotly_chart(fig, use_container_width=True)

    # ── Recent Predictions Toggle ──────────────────────────────────────────
    st.markdown("<hr style='border-color:#E8F5E9;margin:1.5rem 0 1rem'/>", unsafe_allow_html=True)

    show_recent = st.toggle("📋 Show Recent Predictions", key="toggle_recent")

    if show_recent:
        tab_all, tab_mine = st.tabs(["🌍 All Users", "👤 My Predictions"])

        with tab_all:
            with st.spinner("Loading predictions…"):
                all_preds = get_recent_predictions(limit=25)

            if not all_preds:
                st.markdown('<div class="ag-info">No predictions recorded yet. Be the first to generate one!</div>',
                            unsafe_allow_html=True)
            else:
                df_preds = pd.DataFrame(all_preds)
                display_cols = ["created_at", "username", "region", "crop",
                                "rainfall_mm", "temperature_c", "soil_ph",
                                "predicted_yield"]
                df_display = df_preds[[c for c in display_cols if c in df_preds.columns]].copy()
                df_display.columns = [c.replace("_", " ").title() for c in df_display.columns]
                if "Created At" in df_display.columns:
                    df_display["Created At"] = pd.to_datetime(df_display["Created At"]).dt.strftime("%Y-%m-%d %H:%M")
                st.dataframe(df_display, use_container_width=True, hide_index=True)

        with tab_mine:
            user_id = st.session_state.get("user_id")
            if not user_id:
                st.info("Sign in to view your personal prediction history.")
            else:
                with st.spinner("Loading your predictions…"):
                    my_preds = get_user_predictions(user_id, limit=15)

                if not my_preds:
                    st.markdown('<div class="ag-info">You haven\'t made any predictions yet.</div>',
                                unsafe_allow_html=True)
                else:
                    df_mine = pd.DataFrame(my_preds)
                    display_cols = ["created_at", "region", "crop", "rainfall_mm",
                                    "temperature_c", "soil_ph", "predicted_yield"]
                    df_mine = df_mine[[c for c in display_cols if c in df_mine.columns]].copy()
                    df_mine.columns = [c.replace("_", " ").title() for c in df_mine.columns]
                    if "Created At" in df_mine.columns:
                        df_mine["Created At"] = pd.to_datetime(df_mine["Created At"]).dt.strftime("%Y-%m-%d %H:%M")
                    st.dataframe(df_mine, use_container_width=True, hide_index=True)

                    # Mini personal chart
                    if len(my_preds) > 1:
                        df_chart = pd.DataFrame(my_preds).sort_values("created_at")
                        fig2 = px.bar(
                            df_chart,
                            x=df_chart.index,
                            y="predicted_yield",
                            color="crop",
                            labels={"predicted_yield": "Yield (t/ac)", "x": "Prediction #"},
                            color_discrete_sequence=px.colors.qualitative.Safe,
                        )
                        fig2 = apply_chart_style(fig2, title="Your Prediction History", height=280)
                        st.plotly_chart(fig2, use_container_width=True)

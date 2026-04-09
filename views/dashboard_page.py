"""
pages/dashboard_page.py
Interactive analytics dashboard with:
  1. Rainfall vs Yield (color by temperature)
  2. Average Yield by Region & Crop
  3. Soil pH Distribution & Yield Relationship
Filters: Region, Crop Type
Report generation: PDF download
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import os

from utils.theme  import apply_chart_style, GREEN_DARK, GREEN_MID, GREEN_LIGHT, AMBER, ACCENT_RED
from utils.report import generate_dashboard_report

DATA_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "assets", "kenya_crop_yield.csv"
)

REGIONS = ["All", "Central", "Coastal", "Eastern", "North Eastern", "Nyanza", "Rift Valley", "Western"]
CROPS   = ["All", "Beans", "Coffee", "Maize", "Millet", "Potatoes", "Tea", "Wheat"]


@st.cache_data
def load_data() -> pd.DataFrame:
    df = pd.read_csv(DATA_PATH)
    df["Month_Year"] = pd.to_datetime(df["Month_Year"], format="%m-%Y")
    df["Year"]       = df["Month_Year"].dt.year
    df["Month"]      = df["Month_Year"].dt.month
    return df


# ── Chart 1: Rainfall vs Yield (color by temperature) ─────────────────────

def chart_rainfall_yield(df: pd.DataFrame) -> go.Figure:
    # Sample for performance (max 5 000 points)
    sample = df.sample(min(5000, len(df)), random_state=42)

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=sample["Rainfall_mm"],
        y=sample["Past_Yield_tons_acre"],
        mode="markers",
        marker=dict(
            color=sample["Temperature_C"],
            colorscale="Viridis",
            size=5,
            opacity=0.55,
            colorbar=dict(
                title=dict(text="Temp (°C)", side="right"),
                thickness=14,
                len=0.85,
            ),
            line=dict(width=0),
        ),
        text=sample.apply(
            lambda r: f"{r['Crop']} · {r['Region']}<br>"
                      f"Rainfall: {r['Rainfall_mm']:.1f} mm<br>"
                      f"Yield: {r['Past_Yield_tons_acre']:.3f} t/ac<br>"
                      f"Temp: {r['Temperature_C']:.1f} °C",
            axis=1,
        ),
        hoverinfo="text",
        name="Observations",
    ))

    # Trend line
    z     = np.polyfit(df["Rainfall_mm"], df["Past_Yield_tons_acre"], 1)
    poly  = np.poly1d(z)
    x_lin = np.linspace(df["Rainfall_mm"].min(), df["Rainfall_mm"].max(), 200)

    fig.add_trace(go.Scatter(
        x=x_lin,
        y=poly(x_lin),
        mode="lines",
        line=dict(color=ACCENT_RED, width=2.2, dash="dash"),
        name=f"Trend (slope={z[0]:.4f})",
    ))

    fig = apply_chart_style(fig,
        title="Rainfall vs Yield  (colour = Temperature °C)",
        height=430,
    )
    fig.update_layout(
        xaxis_title="Rainfall (mm)",
        yaxis_title="Yield (tons / acre)",
        hovermode="closest",
    )
    corr = df["Rainfall_mm"].corr(df["Past_Yield_tons_acre"])
    fig.add_annotation(
        text=f"Pearson r = {corr:.3f}",
        xref="paper", yref="paper",
        x=0.98, y=0.04,
        showarrow=False,
        font=dict(size=11, color="#52796F"),
        bgcolor="rgba(255,255,255,0.85)",
        bordercolor="#D4D4D4",
        borderwidth=1,
    )
    return fig


# ── Chart 2: Average yield by region and crop ─────────────────────────────

def chart_region_crop_yield(df: pd.DataFrame) -> go.Figure:
    grp = (
        df.groupby(["Region", "Crop"])["Past_Yield_tons_acre"]
        .mean()
        .reset_index()
        .rename(columns={"Past_Yield_tons_acre": "Avg_Yield"})
    )

    crop_palette = px.colors.qualitative.Safe
    crops        = sorted(grp["Crop"].unique())
    regions      = sorted(grp["Region"].unique())

    fig = go.Figure()
    for i, crop in enumerate(crops):
        sub = grp[grp["Crop"] == crop].set_index("Region").reindex(regions)
        fig.add_trace(go.Bar(
            name=crop,
            x=regions,
            y=sub["Avg_Yield"].values,
            marker_color=crop_palette[i % len(crop_palette)],
            marker_line_width=0,
            text=sub["Avg_Yield"].round(2).astype(str),
            textposition="outside",
            textfont=dict(size=9),
        ))

    fig = apply_chart_style(fig,
        title="Average Yield by Region & Crop (tons / acre)",
        height=430,
    )
    fig.update_layout(
        barmode="group",
        bargap=0.18,
        bargroupgap=0.04,
        xaxis=dict(title="Region", tickangle=-20),
        yaxis=dict(title="Avg Yield (tons/acre)"),
        legend=dict(title="Crop", orientation="h",
                    yanchor="bottom", y=1.01, xanchor="right", x=1),
    )
    return fig


# ── Chart 3: Soil pH distribution + yield relationship ───────────────────

def chart_soil_ph(df: pd.DataFrame) -> go.Figure:
    bins    = np.arange(4.0, 9.25, 0.25)
    labels  = ((bins[:-1] + bins[1:]) / 2).round(2)
    df      = df.copy()
    df["pH_bin"] = pd.cut(df["Soil_pH"], bins=bins, labels=labels)
    ph_df   = df.groupby("pH_bin", observed=True).agg(
        count=("Soil_pH", "count"),
        avg_yield=("Past_Yield_tons_acre", "mean"),
    ).reset_index()
    ph_df["pH_bin"] = ph_df["pH_bin"].astype(float)

    fig = go.Figure()

    # Histogram bars (left y-axis)
    fig.add_trace(go.Bar(
        x=ph_df["pH_bin"],
        y=ph_df["count"],
        name="Frequency",
        marker_color="rgba(82,183,136,0.55)",
        marker_line_color="rgba(45,106,79,0.6)",
        marker_line_width=0.5,
        width=0.22,
        yaxis="y1",
    ))

    # Avg yield line (right y-axis)
    fig.add_trace(go.Scatter(
        x=ph_df["pH_bin"],
        y=ph_df["avg_yield"],
        mode="lines+markers",
        name="Avg Yield",
        line=dict(color=ACCENT_RED, width=2.5),
        marker=dict(size=7, color=ACCENT_RED,
                    line=dict(color="white", width=1.5)),
        yaxis="y2",
    ))

    # Optimal pH band (6.0–7.0)
    fig.add_vrect(
        x0=6.0, x1=7.0,
        fillcolor="rgba(82,183,136,0.08)",
        line_width=0,
        annotation_text="Optimal pH",
        annotation_position="top left",
        annotation_font=dict(size=10, color=GREEN_MID),
    )

    fig = apply_chart_style(fig,
        title="Soil pH Distribution & Yield Relationship",
        height=430,
    )
    fig.update_layout(
        xaxis=dict(title="Soil pH", dtick=0.5),
        yaxis=dict(title="Frequency", titlefont=dict(color="steelblue"),
                   tickfont=dict(color="steelblue")),
        yaxis2=dict(
            title="Avg Yield (tons/acre)",
            titlefont=dict(color=ACCENT_RED),
            tickfont=dict(color=ACCENT_RED),
            overlaying="y",
            side="right",
            showgrid=False,
        ),
        legend=dict(orientation="h", yanchor="bottom", y=1.01,
                    xanchor="right", x=1),
        bargap=0.05,
    )
    return fig


# ── Main render ───────────────────────────────────────────────────────────

def render():
    st.markdown("""
    <div style='margin-bottom:1.5rem'>
      <h1 style='font-family:"DM Serif Display",Georgia,serif;color:#1B4332;
                 font-size:1.8rem;margin:0 0 0.3rem'>📊 Analytics Dashboard</h1>
      <p style='color:#52796F;margin:0;font-size:0.93rem'>
        Interactive visualisations of Kenya's crop yield data. Use the filters to drill down.
      </p>
    </div>
    """, unsafe_allow_html=True)

    df_full = load_data()

    # ── Filter bar ────────────────────────────────────────────────────────
    with st.container():
        st.markdown("""
        <div style='background:#FFFFFF;border:1px solid #E8F5E9;border-radius:12px;
                    padding:1rem 1.5rem;margin-bottom:1.2rem;
                    box-shadow:0 2px 8px rgba(27,67,50,0.05)'>
        """, unsafe_allow_html=True)

        fc1, fc2, fc3, fc4, fc5 = st.columns([1.5, 1.5, 1, 1, 1.5])
        with fc1:
            sel_region = st.selectbox("Region", REGIONS, key="dash_region")
        with fc2:
            sel_crop   = st.selectbox("Crop", CROPS,    key="dash_crop")
        with fc3:
            years      = sorted(df_full["Year"].unique())
            sel_yr_min = st.selectbox("From Year", years, index=0, key="dash_yr_min")
        with fc4:
            sel_yr_max = st.selectbox("To Year", years, index=len(years)-1, key="dash_yr_max")
        with fc5:
            st.markdown("<div style='height:1.5rem'></div>", unsafe_allow_html=True)
            reset_btn = st.button("↺ Reset Filters", key="dash_reset")

        st.markdown("</div>", unsafe_allow_html=True)

    if reset_btn:
        st.session_state.dash_region  = "All"
        st.session_state.dash_crop    = "All"
        st.session_state.dash_yr_min  = years[0]
        st.session_state.dash_yr_max  = years[-1]
        st.rerun()

    # ── Apply filters ─────────────────────────────────────────────────────
    df = df_full.copy()
    if sel_region != "All": df = df[df["Region"] == sel_region]
    if sel_crop   != "All": df = df[df["Crop"]   == sel_crop]
    df = df[(df["Year"] >= sel_yr_min) & (df["Year"] <= sel_yr_max)]

    if df.empty:
        st.markdown('<div class="ag-warn">⚠️ No data matches the selected filters. Try broadening your selection.</div>',
                    unsafe_allow_html=True)
        return

    # ── KPIs ──────────────────────────────────────────────────────────────
    k1, k2, k3, k4, k5 = st.columns(5)
    with k1: st.metric("📦 Records",     f"{len(df):,}")
    with k2: st.metric("📈 Avg Yield",   f"{df['Past_Yield_tons_acre'].mean():.3f} t/ac")
    with k3: st.metric("🏆 Max Yield",   f"{df['Past_Yield_tons_acre'].max():.3f} t/ac")
    with k4: st.metric("🌧️ Avg Rainfall", f"{df['Rainfall_mm'].mean():.1f} mm")
    with k5: st.metric("🌡️ Avg Temp",    f"{df['Temperature_C'].mean():.1f} °C")

    st.markdown("<div style='height:0.8rem'></div>", unsafe_allow_html=True)

    # ── CHART 1: Rainfall vs Yield ────────────────────────────────────────
    st.markdown("""
    <div style='font-size:0.75rem;text-transform:uppercase;letter-spacing:0.08em;
                color:#52796F;font-weight:600;margin-bottom:0.3rem'>
      Chart 1
    </div>
    """, unsafe_allow_html=True)
    st.plotly_chart(chart_rainfall_yield(df), use_container_width=True)

    st.markdown("<hr style='border-color:#E8F5E9;margin:0.5rem 0'/>", unsafe_allow_html=True)

    # ── CHART 2: Region × Crop ─────────────────────────────────────────────
    st.markdown("""
    <div style='font-size:0.75rem;text-transform:uppercase;letter-spacing:0.08em;
                color:#52796F;font-weight:600;margin-bottom:0.3rem;margin-top:0.8rem'>
      Chart 2
    </div>
    """, unsafe_allow_html=True)
    # If a single crop is selected, show region-only bar
    if sel_crop != "All":
        region_df = (
            df.groupby("Region")["Past_Yield_tons_acre"]
            .mean()
            .reset_index()
            .sort_values("Past_Yield_tons_acre", ascending=False)
        )
        fig2 = px.bar(
            region_df, x="Region", y="Past_Yield_tons_acre",
            color="Past_Yield_tons_acre",
            color_continuous_scale=[[0, "#D8F3DC"], [0.5, "#52B788"], [1, "#1B4332"]],
            labels={"Past_Yield_tons_acre": "Avg Yield (t/ac)"},
            text=region_df["Past_Yield_tons_acre"].round(3).astype(str),
        )
        fig2 = apply_chart_style(fig2,
            title=f"Average Yield by Region — {sel_crop}",
            height=380,
        )
        fig2.update_layout(coloraxis_showscale=False,
                           xaxis_title="Region", yaxis_title="Avg Yield (t/ac)")
        st.plotly_chart(fig2, use_container_width=True)
    else:
        st.plotly_chart(chart_region_crop_yield(df), use_container_width=True)

    st.markdown("<hr style='border-color:#E8F5E9;margin:0.5rem 0'/>", unsafe_allow_html=True)

    # ── CHART 3: Soil pH ──────────────────────────────────────────────────
    st.markdown("""
    <div style='font-size:0.75rem;text-transform:uppercase;letter-spacing:0.08em;
                color:#52796F;font-weight:600;margin-bottom:0.3rem;margin-top:0.8rem'>
      Chart 3
    </div>
    """, unsafe_allow_html=True)
    st.plotly_chart(chart_soil_ph(df), use_container_width=True)

    st.markdown("<hr style='border-color:#E8F5E9;margin:1rem 0'/>", unsafe_allow_html=True)

    # ── Bonus: Time series ─────────────────────────────────────────────────
    with st.expander("📈 Monthly Yield Trend Over Time", expanded=False):
        ts_df = (
            df.groupby("Month_Year")["Past_Yield_tons_acre"]
            .mean()
            .reset_index()
            .sort_values("Month_Year")
        )
        fig_ts = go.Figure()
        fig_ts.add_trace(go.Scatter(
            x=ts_df["Month_Year"],
            y=ts_df["Past_Yield_tons_acre"],
            mode="lines",
            line=dict(color=GREEN_MID, width=1.8),
            fill="tozeroy",
            fillcolor="rgba(82,183,136,0.12)",
            name="Avg Yield",
        ))
        fig_ts = apply_chart_style(fig_ts, title="Monthly Average Yield Trend", height=300)
        fig_ts.update_layout(xaxis_title="Month", yaxis_title="Avg Yield (t/ac)")
        st.plotly_chart(fig_ts, use_container_width=True)

    # ── Tabular data expander ─────────────────────────────────────────────
    with st.expander("🗃️ Filtered Data Table", expanded=False):
        st.dataframe(
            df.sort_values("Month_Year", ascending=False).head(500),
            use_container_width=True,
            hide_index=True,
        )
        st.caption(f"Showing up to 500 of {len(df):,} filtered records")

    # ── Generate Report ───────────────────────────────────────────────────
    st.markdown("""
    <div style='background:#FFFFFF;border:1px solid #E8F5E9;border-radius:12px;
                padding:1.2rem 1.5rem;margin-top:0.5rem;
                box-shadow:0 2px 8px rgba(27,67,50,0.05)'>
      <div style='font-weight:700;color:#1B4332;font-size:1rem;margin-bottom:0.4rem'>
        📄 Export Report
      </div>
      <div style='font-size:0.87rem;color:#52796F;margin-bottom:0.8rem'>
        Generate a PDF summary of the current filtered data including statistics, 
        region breakdown, and crop averages.
      </div>
    """, unsafe_allow_html=True)

    gen_col, _ = st.columns([1, 3])
    with gen_col:
        gen_report = st.button("📥 Generate PDF Report", key="btn_report",
                               use_container_width=True)

    if gen_report:
        filters_desc = {
            "Region": sel_region,
            "Crop":   sel_crop,
            "Years":  f"{sel_yr_min} – {sel_yr_max}",
        }
        with st.spinner("Generating report…"):
            pdf_bytes = generate_dashboard_report(df, filters_desc)

        if pdf_bytes:
            from datetime import datetime
            fname = f"agriyield_report_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf"
            st.download_button(
                label="⬇️ Download Report PDF",
                data=pdf_bytes,
                file_name=fname,
                mime="application/pdf",
                key="dl_report",
            )
            st.markdown('<div class="ag-success">✅ Report ready! Click above to download.</div>',
                        unsafe_allow_html=True)
        else:
            st.markdown('<div class="ag-warn">⚠️ PDF generation requires fpdf2. Run: <code>pip install fpdf2</code></div>',
                        unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

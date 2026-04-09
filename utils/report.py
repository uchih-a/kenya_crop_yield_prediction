"""
utils/report.py
PDF report generation using fpdf2.
"""

import io
from datetime import datetime
import pandas as pd

try:
    from fpdf import FPDF
    FPDF_AVAILABLE = True
except ImportError:
    FPDF_AVAILABLE = False


def generate_dashboard_report(df: pd.DataFrame, filters: dict) -> bytes | None:
    """
    Generate a PDF summary report from the dashboard data.
    Returns bytes or None if fpdf2 not available.
    """
    if not FPDF_AVAILABLE:
        return None

    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    # ── Header ────────────────────────────────────────────────────────────────
    pdf.set_fill_color(27, 67, 50)   # GREEN_DARK
    pdf.rect(0, 0, 210, 35, "F")
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Helvetica", "B", 20)
    pdf.set_xy(10, 8)
    pdf.cell(0, 10, "Kenya Crop Yield - Dashboard Report", ln=True)
    pdf.set_font("Helvetica", "", 10)
    pdf.set_xy(10, 22)
    pdf.cell(0, 6, f"Generated: {datetime.now().strftime('%B %d, %Y  %H:%M')}", ln=True)

    pdf.set_text_color(0, 0, 0)
    pdf.ln(15)

    # ── Filters applied ───────────────────────────────────────────────────────
    pdf.set_font("Helvetica", "B", 13)
    pdf.set_text_color(27, 67, 50)
    pdf.cell(0, 8, "Applied Filters", ln=True)
    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Helvetica", "", 11)
    for k, v in filters.items():
        pdf.cell(0, 6, f"  {k}: {v}", ln=True)
    pdf.ln(4)

    # ── Summary statistics ────────────────────────────────────────────────────
    pdf.set_font("Helvetica", "B", 13)
    pdf.set_text_color(27, 67, 50)
    pdf.cell(0, 8, "Summary Statistics", ln=True)
    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Helvetica", "", 11)

    stats = [
        ("Total Records",       f"{len(df):,}"),
        ("Average Yield",       f"{df['Past_Yield_tons_acre'].mean():.3f} tons/acre"),
        ("Max Yield",           f"{df['Past_Yield_tons_acre'].max():.3f} tons/acre"),
        ("Min Yield",           f"{df['Past_Yield_tons_acre'].min():.3f} tons/acre"),
        ("Avg Rainfall",        f"{df['Rainfall_mm'].mean():.1f} mm"),
        ("Avg Temperature",     f"{df['Temperature_C'].mean():.1f} °C"),
        ("Avg Soil pH",         f"{df['Soil_pH'].mean():.2f}"),
        ("Unique Regions",      str(df["Region"].nunique())),
        ("Unique Crops",        str(df["Crop"].nunique())),
    ]

    for label, value in stats:
        pdf.set_font("Helvetica", "B", 11)
        pdf.cell(70, 6, label + ":", ln=False)
        pdf.set_font("Helvetica", "", 11)
        pdf.cell(0, 6, value, ln=True)

    pdf.ln(6)

    # ── Top regions by yield ──────────────────────────────────────────────────
    pdf.set_font("Helvetica", "B", 13)
    pdf.set_text_color(27, 67, 50)
    pdf.cell(0, 8, "Average Yield by Region", ln=True)
    pdf.set_text_color(0, 0, 0)

    region_avg = (
        df.groupby("Region")["Past_Yield_tons_acre"]
        .mean()
        .sort_values(ascending=False)
        .reset_index()
    )

    # Table header
    pdf.set_fill_color(45, 106, 79)
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(90, 7, "Region", border=1, fill=True)
    pdf.cell(60, 7, "Avg Yield (tons/acre)", border=1, fill=True, ln=True)

    pdf.set_text_color(0, 0, 0)
    for _, row in region_avg.iterrows():
        pdf.set_font("Helvetica", "", 10)
        fill = pdf.get_y() % 2 == 0
        pdf.set_fill_color(245, 250, 245)
        pdf.cell(90, 6, str(row["Region"]), border=1, fill=fill)
        pdf.cell(60, 6, f"{row['Past_Yield_tons_acre']:.3f}", border=1, fill=fill, ln=True)

    pdf.ln(6)

    # ── Top crops by yield ────────────────────────────────────────────────────
    pdf.set_font("Helvetica", "B", 13)
    pdf.set_text_color(27, 67, 50)
    pdf.cell(0, 8, "Average Yield by Crop", ln=True)
    pdf.set_text_color(0, 0, 0)

    crop_avg = (
        df.groupby("Crop")["Past_Yield_tons_acre"]
        .mean()
        .sort_values(ascending=False)
        .reset_index()
    )

    pdf.set_fill_color(45, 106, 79)
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(90, 7, "Crop", border=1, fill=True)
    pdf.cell(60, 7, "Avg Yield (tons/acre)", border=1, fill=True, ln=True)

    pdf.set_text_color(0, 0, 0)
    for _, row in crop_avg.iterrows():
        pdf.set_font("Helvetica", "", 10)
        pdf.set_fill_color(245, 250, 245)
        pdf.cell(90, 6, str(row["Crop"]), border=1)
        pdf.cell(60, 6, f"{row['Past_Yield_tons_acre']:.3f}", border=1, ln=True)

    # ── Footer ────────────────────────────────────────────────────────────────
    pdf.ln(10)
    pdf.set_font("Helvetica", "I", 9)
    pdf.set_text_color(120, 120, 120)
    pdf.cell(0, 5, "Agricultural Productivity & Crop Yield Prediction System - Meru University of Science and Technology", ln=True, align="C")

    return pdf.output()

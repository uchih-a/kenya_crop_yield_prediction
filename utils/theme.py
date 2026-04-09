"""
utils/theme.py
Shared Plotly theme and color palette for the application.
"""

import plotly.graph_objects as go
import plotly.express as px

# ── Brand palette ─────────────────────────────────────────────────────────────
GREEN_DARK   = "#1B4332"
GREEN_MID    = "#2D6A4F"
GREEN_LIGHT  = "#52B788"
AMBER        = "#F4A261"
CREAM        = "#FEFAE0"
CHARCOAL     = "#1C1C1C"
LIGHT_BG     = "#F8FAF7"
ACCENT_RED   = "#E76F51"

CROP_COLORS = {
    "Maize":    "#52B788",
    "Beans":    "#F4A261",
    "Tea":      "#2D6A4F",
    "Coffee":   "#6D4C41",
    "Potatoes": "#FFD166",
    "Millet":   "#E76F51",
    "Wheat":    "#B5838D",
}

REGION_COLORS = px.colors.qualitative.Safe

PLOTLY_TEMPLATE = "plotly_white"


def apply_chart_style(fig: go.Figure, title: str = "", height: int = 420) -> go.Figure:
    """Apply consistent brand styling to any Plotly figure."""
    fig.update_layout(
        title=dict(text=title, font=dict(size=15, color=CHARCOAL, family="Georgia, serif"),
                   x=0.03, xanchor="left"),
        height=height,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor=LIGHT_BG,
        font=dict(family="'Segoe UI', sans-serif", size=11, color=CHARCOAL),
        margin=dict(l=20, r=20, t=50, b=20),
        legend=dict(
            bgcolor="rgba(255,255,255,0.85)",
            bordercolor="#D4D4D4",
            borderwidth=1,
        ),
        xaxis=dict(showgrid=False, zeroline=False, showline=True, linecolor="#D4D4D4"),
        yaxis=dict(showgrid=True, gridcolor="#EBEBEB", zeroline=False),
    )
    return fig

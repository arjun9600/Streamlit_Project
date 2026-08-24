"""Shared chart styling helpers — Vivid Neon palette."""
import streamlit as st

# Vivid Neon Variation
NEON_GREEN = "#14e81e"
MINT_CYAN = "#00ea8d"
SKY_BLUE = "#017ed5"
ELECTRIC_PURPLE = "#b53dff"
DEEP_MAGENTA = "#8d00c4"

# Discrete series order (used for multi-category bars/lines/pies)
PALETTE = [NEON_GREEN, MINT_CYAN, SKY_BLUE, ELECTRIC_PURPLE, DEEP_MAGENTA]

# Continuous scale, dark -> bright (used for choropleths / heat-style color axes)
CONTINUOUS = [DEEP_MAGENTA, ELECTRIC_PURPLE, SKY_BLUE, MINT_CYAN, NEON_GREEN]

# Two-tone scale for "good vs bad" (profit vs loss) type charts
DIVERGING = [ELECTRIC_PURPLE, DEEP_MAGENTA, "#3a1466", MINT_CYAN, NEON_GREEN]


def style_fig(fig, height=420):
    """Apply the neon dark theme consistently to any plotly figure."""
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#E9FBEA", size=12),
        colorway=PALETTE,
        legend=dict(bgcolor="rgba(0,0,0,0)", bordercolor="rgba(0,0,0,0)"),
        margin=dict(l=10, r=10, t=50, b=10),
        height=height,
        title_font=dict(color=MINT_CYAN, size=16),
        hoverlabel=dict(bgcolor="#12123a", font_color="#E9FBEA", bordercolor=NEON_GREEN),
    )
    fig.update_xaxes(gridcolor="rgba(0,234,141,0.10)", zerolinecolor="rgba(0,234,141,0.15)")
    fig.update_yaxes(gridcolor="rgba(0,234,141,0.10)", zerolinecolor="rgba(0,234,141,0.15)")
    return fig


def insight_box(title, points):
    """Render a glowing neon 'Business Insights' card under a set of charts.

    points: list[str] — each is one insight bullet (already formatted text).
    """
    items = "".join(f"<li>{p}</li>" for p in points)
    st.markdown(
        f"""
        <div class="insight-box">
            <div class="insight-title">💡 Business Insights</div>
            <div class="insight-subtitle">{title}</div>
            <ul>{items}</ul>
        </div>
        """,
        unsafe_allow_html=True,
    )


def safe_pct_change(new, old):
    """Percent change guarded against divide-by-zero / NaN."""
    if old in (0, None) or pd_isna(old):
        return None
    return (new - old) / abs(old) * 100


def pd_isna(x):
    try:
        import pandas as pd
        return pd.isna(x)
    except Exception:
        return x is None

"""Reusable HTML components: KPI card rows, section wrappers, and
data-driven insight callouts."""
import streamlit as st


def kpi_row(cards: list[dict]):
    """
    cards: list of dicts with keys: label, value, icon (optional), delta (optional str),
    delta_dir ('up'|'down', optional -> 'up' colored as risk/red, 'down' as safe/green)

    Builds every card as a single unbroken HTML line. st.markdown runs its input
    through a CommonMark parser first, and a blank (or whitespace-only) line ends
    a raw <div> HTML block early -- so multi-line "pretty" HTML here would get
    the tail end of each card mis-parsed as literal text instead of rendered.
    """
    parts = ['<div class="kpi-row">']
    for c in cards:
        delta_html = ""
        if c.get("delta"):
            d_class = c.get("delta_dir", "down")
            delta_html = f'<div class="kpi-delta {d_class}">{c["delta"]}</div>'
        parts.append(
            '<div class="kpi-card">'
            f'<div class="kpi-badge">{c.get("icon", "")}</div>'
            f'<div class="kpi-label">{c["label"]}</div>'
            f'<div class="kpi-value">{c["value"]}</div>'
            f'{delta_html}'
            '</div>'
        )
    parts.append("</div>")
    st.markdown("".join(parts), unsafe_allow_html=True)


def section_start(title: str, side: str = None):
    """side='left' gives the card a violet top accent, side='right' a
    rose top accent — used to visually separate paired charts so a
    left/right layout never reads as one flat color block."""
    css_class = "section-card" + (f" side-{side}" if side in ("left", "right") else "")
    st.markdown(f'<div class="{css_class}"><div class="section-title">{title}</div>', unsafe_allow_html=True)


def section_end():
    st.markdown("</div>", unsafe_allow_html=True)


def risk_badge(is_high_risk: bool, mid=False) -> str:
    if mid:
        return '<span class="badge badge-mid">Watch</span>'
    return (
        '<span class="badge badge-high">High risk</span>' if is_high_risk
        else '<span class="badge badge-low">Low risk</span>'
    )


def insight_box(text: str, tone: str = "info"):
    """Renders a small callout under a chart with a plain-English,
    data-driven business insight. tone: 'info' (blue, neutral reading),
    'warn' (rose, flags elevated risk), 'good' (green, favorable signal).
    `text` may contain simple <b> tags for emphasis."""
    icon = {"info": "💡", "warn": "⚠️", "good": "✅"}.get(tone, "💡")
    css = {"info": "insight-info", "warn": "insight-warn", "good": "insight-good"}.get(tone, "insight-info")
    st.markdown(
        f'<div class="insight-box {css}"><span class="insight-icon">{icon}</span><div>{text}</div></div>',
        unsafe_allow_html=True,
    )

"""
Custom "Meridian" theme — production-grade SaaS console look: dark-navy
nav rail with a branded profile footer, a persistent top utility bar
(working search / notifications / avatar / logout), a personalized
welcome banner, icon-badge KPI cards, and data-driven insight callouts
under every chart. Modeled after real B2B admin consoles (Stripe,
Linear, Vercel dashboards), not Streamlit's stock chrome.
"""
import streamlit as st

# ---- Brand / identity (edit these to rebrand) -------------------------
APP_NAME = "Meridian"
APP_TAGLINE = "Risk Console"

# Fallback identity shown before login / if session state is empty.
USER_NAME = "Alex Morgan"
USER_ROLE = "Senior Credit Analyst"
USER_INITIALS = "AM"


def current_user() -> dict:
    """Reads the signed-in user from session state (set by utils.auth),
    falling back to the default demo identity so pages never crash if
    called before login (shouldn't happen once require_login() gates
    every page, but keeps this module self-contained)."""
    return st.session_state.get("user", {
        "name": USER_NAME, "role": USER_ROLE, "initials": USER_INITIALS,
    })


# ---- Palette — "Chill Coding Vibe" --------------------------------------
# Built from the 3-color generated palette (#4c748c slate, #8ce4e4 teal,
# #cdefe3 mint). A deliberately two-toned system: a COOL slate/teal family
# for the left/primary side of the dashboard and charts, and a WARM family
# for the right side — so paired charts never look monotone, while risk
# semantics (green = safe, red/rose = default) stay constant everywhere.
PRIMARY = "#4c748c"       # slate-blue accent (lines, primary bars, active nav)
PRIMARY_SOFT = "#8ce4e4"  # bright teal (secondary series)
PRIMARY_TINT = "#e3f7f4"  # pale mint fill (icon badges) — from #cdefe3
GOLD = "#f59e0b"          # amber accent (kept for warm contrast)
DANGER = "#f43f5e"        # default / high risk (rose-red) — kept semantic
SAFE = "#10b981"          # repaid / low risk (emerald) — kept semantic
PURPLE = "#3d5f73"        # deep slate (pairs with PRIMARY in gradients)
CYAN = "#8ce4e4"          # bright teal

BG = "#cdefe3"            # page background (mint, per request)
CARD_BG = "#ffffff"
CARD_BORDER = "#dcebe8"   # pale teal-gray border
SIDEBAR_BG = "#8ce4e4"    # bright teal (per request)
SIDEBAR_BG_2 = "#7bd8d4"
TEXT_HI = "#0f172a"       # near-black headings
TEXT_LO = "#54707c"       # secondary teal-gray text
GRID = "#eaf5f2"

# Cool spectrum — used for LEFT-column / primary charts.
PALETTE_LEFT = ["#2f4858", "#4c748c", "#5f96ab", "#5aa8a3", "#7cc9c4", "#8ce4e4", "#3f6b7d", "#a9ecdf"]
# Warm spectrum — used for RIGHT-column / secondary charts.
PALETTE_RIGHT = ["#f43f5e", "#f97316", "#f59e0b", "#eab308", "#ec4899", "#fb7185", "#e11d48", "#d946ef"]
# Continuous scales matching each family, for gradient/heat charts that
# aren't risk-semantic (risk keeps its own green->amber->red scale below).
CONTINUOUS_LEFT = ["#e3f7f4", "#8ce4e4", "#4c748c", "#22333c"]
CONTINUOUS_RIGHT = ["#ffedd5", "#fb923c", "#f43f5e", "#881337"]
# Semantic risk gradient (low -> high default risk) — kept identical on
# both sides of the layout because green/amber/red must always mean the
# same thing wherever it appears.
RISK_GRADIENT = ["#10b981", "#f59e0b", "#f43f5e"]

# Default general-purpose categorical palette (used where a chart isn't
# explicitly assigned to a side).
CATEGORICAL_PALETTE = ["#4c748c", "#10b981", "#f97316", "#8ce4e4", "#f43f5e", "#3d5f73", "#eab308", "#5aa8a3"]
RISK_COLOR_MAP = {"Repaid on time": SAFE, "Payment difficulty": DANGER}

PLOTLY_LAYOUT = dict(
    template="plotly_white",
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Inter, sans-serif", color=TEXT_HI, size=12),
    legend=dict(bgcolor="rgba(0,0,0,0)", orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
    margin=dict(t=40, l=10, r=10, b=10),
    xaxis=dict(gridcolor=GRID, zerolinecolor=GRID, linecolor="#d7dce6"),
    yaxis=dict(gridcolor=GRID, zerolinecolor=GRID, linecolor="#d7dce6"),
    colorway=CATEGORICAL_PALETTE,
)

# Gives every chart the small download/zoom/reset icon toolbar seen in
# the reference screenshot (top-right of each chart card).
PLOTLY_CONFIG = {"displayModeBar": True, "displaylogo": False,
                  "modeBarButtonsToRemove": ["lasso2d", "select2d", "autoScale2d"]}


def side_colorway(side: str = "left"):
    """Returns the categorical colorway for a given dashboard side."""
    return PALETTE_LEFT if side == "left" else PALETTE_RIGHT


def side_continuous(side: str = "left", semantic_risk: bool = False):
    """Returns a continuous color scale. Risk-semantic charts always use
    the green->amber->red gradient regardless of side; everything else
    uses the side's own tint family."""
    if semantic_risk:
        return RISK_GRADIENT
    return CONTINUOUS_LEFT if side == "left" else CONTINUOUS_RIGHT


def _raw_html(s: str) -> str:
    """
    Collapse a pretty-indented triple-quoted HTML/CSS template down to
    zero-indent, blank-line-free markup.

    st.markdown(..., unsafe_allow_html=True) runs the text through a
    CommonMark parser first. Any line indented 4+ spaces is read as an
    *indented code block* (not HTML), and even a 0-indent block tag like
    <div> stops being treated as raw HTML at the first blank line. Normal
    "pretty" Python multi-line f-strings trigger both problems. Stripping
    indentation and dropping blank lines keeps the snippet inside one
    contiguous raw-HTML block so it actually renders.
    """
    return "\n".join(line.strip() for line in s.strip("\n").splitlines() if line.strip())


def apply_theme():
    st.markdown(_raw_html(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

    html, body, [class*="css"], .stApp {{
        font-family: 'Inter', sans-serif;
    }}
    .stApp {{
        background: {BG};
    }}
    h1, h2, h3 {{
        font-family: 'Inter', sans-serif !important;
        letter-spacing: -0.01em;
        color: {TEXT_HI} !important;
        font-weight: 800 !important;
    }}
    p, span, label {{
        color: {TEXT_LO};
    }}
    #MainMenu {{visibility: hidden;}}
    footer {{visibility: hidden;}}
    header[data-testid="stHeader"] {{
        background: rgba(245,247,251,0.0);
    }}

    /* ---- Sidebar: light "chill vibe" teal rail with dark readable text ---- */
    section[data-testid="stSidebar"] {{
        background: linear-gradient(180deg, {SIDEBAR_BG} 0%, {SIDEBAR_BG_2} 100%);
        border-right: 1px solid rgba(15,23,42,0.08);
    }}
    section[data-testid="stSidebar"] * {{
        color: #123b42 !important;
    }}
    section[data-testid="stSidebar"] h2, section[data-testid="stSidebar"] h3 {{
        color: {TEXT_HI} !important;
    }}
    section[data-testid="stSidebar"] hr {{
        border-color: rgba(15,23,42,0.14);
    }}
    div[data-testid="stSidebarNav"] a {{
        border-radius: 10px;
        margin: 1px 8px;
        padding: 0.4rem 0.7rem !important;
        color: #123b42 !important;
        font-weight: 600;
    }}
    div[data-testid="stSidebarNav"] a:hover {{
        background: rgba(15,23,42,0.08);
    }}
    div[data-testid="stSidebarNav"] li:has(a[aria-current="page"]) a {{
        background: {PRIMARY};
        color: #ffffff !important;
        font-weight: 700;
        box-shadow: inset 3px 0 0 {PURPLE};
    }}
    section[data-testid="stSidebar"] div[data-baseweb="select"] > div {{
        background: #ffffff;
        border-color: rgba(15,23,42,0.16);
        border-radius: 8px;
        color: {TEXT_HI} !important;
    }}
    section[data-testid="stSidebar"] div[data-baseweb="tag"] {{
        background: {PRIMARY} !important;
    }}
    section[data-testid="stSidebar"] div[data-baseweb="tag"] * {{
        color: #ffffff !important;
    }}
    section[data-testid="stSidebar"] .stSlider [data-baseweb="slider"] {{
        color: {PRIMARY};
    }}
    section[data-testid="stSidebar"] .stButton button {{
        width: 100%;
        background: rgba(244,63,94,0.14);
        border: 1px solid rgba(244,63,94,0.4);
        color: #9f1239 !important;
        border-radius: 8px;
        font-weight: 600;
        padding: 0.35rem 0.6rem;
    }}
    section[data-testid="stSidebar"] .stButton button:hover {{
        background: rgba(244,63,94,0.28);
        border-color: {DANGER};
        color: #7f1233 !important;
    }}
    .brand-block {{
        display: flex;
        align-items: center;
        gap: 10px;
        padding: 0.2rem 0 1rem 0;
    }}
    .brand-mark {{
        width: 32px;
        height: 32px;
        border-radius: 9px;
        background: linear-gradient(135deg, {PRIMARY}, {PURPLE});
        display: flex;
        align-items: center;
        justify-content: center;
        color: #ffffff !important;
        font-weight: 800;
        font-size: 0.95rem;
        flex-shrink: 0;
    }}
    .brand-name {{
        color: {TEXT_HI} !important;
        font-weight: 800;
        font-size: 1.05rem;
        line-height: 1.1;
    }}
    .brand-tag {{
        color: #2f5a63 !important;
        font-size: 0.72rem;
        letter-spacing: 0.03em;
    }}
    .sidebar-profile {{
        display: flex;
        align-items: center;
        gap: 10px;
        padding: 0.8rem 0.2rem 0.6rem 0.2rem;
        margin-top: 0.6rem;
        border-top: 1px solid rgba(15,23,42,0.14);
    }}
    .sidebar-avatar {{
        width: 32px;
        height: 32px;
        border-radius: 50%;
        background: linear-gradient(135deg, {PRIMARY}, {PURPLE});
        border: 1px solid rgba(15,23,42,0.14);
        display: flex;
        align-items: center;
        justify-content: center;
        color: #ffffff !important;
        font-weight: 700;
        font-size: 0.72rem;
        flex-shrink: 0;
    }}
    .sidebar-profile-name {{
        color: #123b42 !important;
        font-size: 0.82rem;
        font-weight: 700;
        line-height: 1.2;
        margin: 0;
    }}
    .sidebar-profile-role {{
        color: #2f5a63 !important;
        font-size: 0.72rem;
        line-height: 1.2;
        margin: 0;
    }}

    /* ---- Top utility bar ---- */
    .topbar-right {{
        display: flex;
        align-items: center;
        justify-content: flex-end;
        gap: 12px;
        height: 100%;
    }}
    .topbar-icon-btn {{
        position: relative;
        width: 36px;
        height: 36px;
        border-radius: 10px;
        background: {CARD_BG};
        border: 1px solid {CARD_BORDER};
        display: flex;
        align-items: center;
        justify-content: center;
        color: {TEXT_LO} !important;
        font-size: 1.05rem;
    }}
    .topbar-icon-dot {{
        position: absolute;
        top: 7px;
        right: 7px;
        width: 7px;
        height: 7px;
        border-radius: 50%;
        background: {DANGER};
        border: 1.5px solid {CARD_BG};
    }}
    .topbar-avatar {{
        display: flex;
        align-items: center;
        gap: 8px;
    }}
    .topbar-avatar-circle {{
        width: 34px;
        height: 34px;
        border-radius: 50%;
        background: linear-gradient(135deg, {PRIMARY}, {PURPLE});
        display: flex;
        align-items: center;
        justify-content: center;
        color: #ffffff !important;
        font-weight: 700;
        font-size: 0.78rem;
        flex-shrink: 0;
    }}
    .topbar-avatar-text p {{
        margin: 0;
        line-height: 1.2;
    }}
    .topbar-avatar-name {{
        font-size: 0.83rem;
        font-weight: 700;
        color: {TEXT_HI} !important;
        white-space: nowrap;
    }}
    .topbar-avatar-role {{
        font-size: 0.72rem;
        color: {TEXT_LO} !important;
        white-space: nowrap;
    }}
    div[data-testid="stTextInput"] input {{
        border-radius: 10px !important;
        border: 1px solid {CARD_BORDER} !important;
        background: {CARD_BG} !important;
        font-size: 0.85rem !important;
        padding: 0.55rem 0.9rem !important;
    }}
    div[data-testid="stTextInput"] input:focus {{
        border-color: {PRIMARY} !important;
        box-shadow: 0 0 0 3px rgba(99,102,241,0.15) !important;
    }}
    .topbar-logout-wrap button {{
        background: {CARD_BG} !important;
        border: 1px solid {CARD_BORDER} !important;
        color: {DANGER} !important;
        font-weight: 700 !important;
        border-radius: 10px !important;
        padding: 0.5rem 0.9rem !important;
    }}
    .topbar-logout-wrap button:hover {{
        background: #fff1f2 !important;
        border-color: {DANGER} !important;
    }}
    .search-result-card {{
        background: {CARD_BG};
        border: 1px solid {CARD_BORDER};
        border-left: 4px solid {PRIMARY};
        border-radius: 12px;
        padding: 0.9rem 1.1rem;
        margin-bottom: 1rem;
        box-shadow: 0 1px 2px rgba(15,23,42,0.04), 0 8px 20px rgba(15,23,42,0.045);
    }}

    /* ---- Welcome banner ---- */
    .welcome-banner {{
        background: linear-gradient(120deg, #2c4652 0%, #16262c 100%);
        border-radius: 16px;
        padding: 1.4rem 1.7rem;
        margin-bottom: 1.3rem;
        display: flex;
        align-items: center;
        justify-content: space-between;
        flex-wrap: wrap;
        gap: 0.8rem;
    }}
    .welcome-banner h2 {{
        margin: 0;
        color: #ffffff !important;
        font-size: 1.35rem;
        font-weight: 800 !important;
        text-shadow: 0 1px 3px rgba(0,0,0,0.35);
    }}
    .welcome-banner p {{
        margin: 0.3rem 0 0 0;
        color: #d7f5f0 !important;
        font-size: 0.92rem;
        text-shadow: 0 1px 2px rgba(0,0,0,0.25);
    }}
    .welcome-pill {{
        background: rgba(255,255,255,0.18);
        border: 1px solid rgba(255,255,255,0.32);
        border-radius: 999px;
        padding: 0.4rem 0.9rem;
        color: #ffffff !important;
        font-size: 0.8rem;
        font-weight: 700;
        white-space: nowrap;
    }}

    /* ---- Page header ---- */
    .page-header {{ margin-bottom: 1.4rem; }}
    .page-header h1 {{
        margin: 0;
        font-size: 1.9rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }}
    .page-header p {{
        margin: 0.3rem 0 0 0;
        color: {TEXT_LO};
        font-size: 1rem;
    }}

    /* ---- KPI cards ---- */
    .kpi-row {{ display: flex; gap: 14px; flex-wrap: wrap; margin-bottom: 1.3rem; }}
    .kpi-card {{
        flex: 1 1 175px;
        background: {CARD_BG};
        border: 1px solid {CARD_BORDER};
        border-radius: 14px;
        padding: 1.05rem 1.25rem;
        box-shadow: 0 1px 2px rgba(15,23,42,0.04), 0 8px 20px rgba(15,23,42,0.045);
        transition: transform 0.15s ease, box-shadow 0.15s ease;
    }}
    .kpi-card:hover {{
        transform: translateY(-2px);
        box-shadow: 0 4px 10px rgba(15,23,42,0.07), 0 14px 28px rgba(15,23,42,0.08);
    }}
    .kpi-label {{
        font-size: 0.75rem;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        color: {TEXT_LO};
        font-weight: 700;
        margin-bottom: 0.4rem;
    }}
    .kpi-value {{
        font-size: 1.6rem;
        font-weight: 800;
        color: {TEXT_HI};
        line-height: 1.1;
    }}
    .kpi-delta {{
        font-size: 0.8rem;
        margin-top: 0.35rem;
        font-weight: 700;
    }}
    .kpi-delta.up {{ color: {DANGER}; }}
    .kpi-delta.down {{ color: {SAFE}; }}
    .kpi-icon {{ font-size: 1.3rem; opacity: 0.95; }}
    .kpi-badge {{
        width: 34px;
        height: 34px;
        border-radius: 9px;
        background: {PRIMARY_TINT};
        display: flex;
        align-items: center;
        justify-content: center;
        margin-bottom: 0.6rem;
        font-size: 1.05rem;
    }}

    /* ---- Chart / section cards, with optional left/right accent ---- */
    .section-card {{
        background: {CARD_BG};
        border: 1px solid {CARD_BORDER};
        border-top: 3px solid transparent;
        border-radius: 16px;
        padding: 1.2rem 1.4rem 0.6rem 1.4rem;
        margin-bottom: 1.2rem;
        box-shadow: 0 1px 2px rgba(15,23,42,0.04), 0 10px 24px rgba(15,23,42,0.05);
    }}
    .section-card.side-left {{ border-top-color: {PRIMARY}; }}
    .section-card.side-right {{ border-top-color: {DANGER}; }}
    .section-title {{
        font-size: 1.05rem;
        font-weight: 800;
        color: {TEXT_HI};
        margin-bottom: 0.6rem;
    }}

    /* ---- Insight callouts (business insights under charts) ---- */
    .insight-box {{
        display: flex;
        gap: 0.6rem;
        align-items: flex-start;
        border-radius: 10px;
        padding: 0.65rem 0.9rem;
        margin: 0.4rem 0 0.9rem 0;
        font-size: 0.85rem;
        line-height: 1.45;
    }}
    .insight-box .insight-icon {{ font-size: 1rem; flex-shrink: 0; margin-top: 0.05rem; }}
    .insight-box b {{ color: inherit; }}
    .insight-info {{ background: {PRIMARY_TINT}; border: 1px solid #b9e4de; color: #1d4a52; }}
    .insight-warn {{ background: #fff1f2; border: 1px solid #fecdd3; color: #9f1239; }}
    .insight-good {{ background: #ecfdf5; border: 1px solid #a7f3d0; color: #065f46; }}

    /* ---- Risk badges ---- */
    .badge {{
        display: inline-block;
        padding: 0.2rem 0.7rem;
        border-radius: 999px;
        font-size: 0.78rem;
        font-weight: 700;
    }}
    .badge-high {{ background: #ffe4e6; color: #9f1239; border: 1px solid #fecdd3; }}
    .badge-low {{ background: #d1fae5; color: #047857; border: 1px solid #a7f3d0; }}
    .badge-mid {{ background: #fef3c7; color: #92400e; border: 1px solid #fde68a; }}

    /* ---- Login screen ---- */
    .login-wrap {{
        max-width: 420px;
        margin: 4vh auto 0 auto;
        background: {CARD_BG};
        border: 1px solid {CARD_BORDER};
        border-radius: 20px;
        padding: 2.2rem 2.2rem 1.6rem 2.2rem;
        box-shadow: 0 1px 2px rgba(15,23,42,0.04), 0 20px 45px rgba(15,23,42,0.09);
    }}
    .login-logo {{
        width: 46px;
        height: 46px;
        border-radius: 13px;
        background: linear-gradient(135deg, {PRIMARY}, {PURPLE});
        display: flex;
        align-items: center;
        justify-content: center;
        color: #fff !important;
        font-weight: 800;
        font-size: 1.3rem;
        margin-bottom: 0.9rem;
    }}
    .login-title {{
        font-size: 1.4rem;
        font-weight: 800;
        color: {TEXT_HI} !important;
        margin-bottom: 0.15rem;
    }}
    .login-sub {{
        font-size: 0.88rem;
        color: {TEXT_LO} !important;
        margin-bottom: 1.3rem;
    }}
    .login-hint {{
        background: {PRIMARY_TINT};
        border: 1px solid #b9e4de;
        color: #1d4a52 !important;
        border-radius: 10px;
        padding: 0.6rem 0.8rem;
        font-size: 0.78rem;
        margin-top: 0.9rem;
    }}
    .login-wrap div[data-testid="stTextInput"] input {{
        border-radius: 10px !important;
    }}
    .login-wrap .stButton button {{
        width: 100%;
        background: linear-gradient(120deg, {PRIMARY}, {PURPLE}) !important;
        color: #fff !important;
        border: none !important;
        border-radius: 10px !important;
        font-weight: 700 !important;
        padding: 0.6rem 0 !important;
        margin-top: 0.4rem;
    }}

    /* ---- Misc ---- */
    button[data-baseweb="tab"] {{
        font-weight: 600;
        color: {TEXT_LO} !important;
    }}
    div[data-testid="stDataFrame"] {{
        border-radius: 12px;
        overflow: hidden;
        border: 1px solid {CARD_BORDER};
    }}
    hr {{ border-color: {CARD_BORDER}; }}
    div[data-testid="stMetricValue"] {{ color: {TEXT_HI}; }}
    .stTabs [data-baseweb="tab-list"] {{
        gap: 4px;
    }}
    </style>
    """), unsafe_allow_html=True)


def style_fig(fig, height=None, side: str = None, semantic_risk: bool = False):
    """Applies the base Plotly layout. Pass side='left'/'right' to swap
    in that column's colorway (cool vs warm) for charts using categorical
    color; risk-semantic charts should leave side=None and set their own
    green->amber->red colors explicitly."""
    layout = dict(PLOTLY_LAYOUT)
    if side:
        layout = dict(layout, colorway=side_colorway(side))
    fig.update_layout(**layout)
    if height:
        fig.update_layout(height=height)
    return fig


def sidebar_brand():
    """Logo mark + product name pinned at the top of the sidebar."""
    st.sidebar.markdown(_raw_html(f"""
    <div class="brand-block">
    <div class="brand-mark">{APP_NAME[0]}</div>
    <div><div class="brand-name">{APP_NAME}</div><div class="brand-tag">{APP_TAGLINE}</div></div>
    </div>
    """), unsafe_allow_html=True)


def sidebar_profile():
    """Signed-in-user card + logout button pinned at the bottom of the sidebar."""
    u = current_user()
    st.sidebar.markdown(_raw_html(f"""
    <div class="sidebar-profile">
    <div class="sidebar-avatar">{u['initials']}</div>
    <div><p class="sidebar-profile-name">{u['name']}</p><p class="sidebar-profile-role">{u['role']}</p></div>
    </div>
    """), unsafe_allow_html=True)
    if st.sidebar.button("🚪 Log out", key="sidebar_logout_btn", use_container_width=True):
        from utils.auth import logout
        logout()


def topbar(df=None, id_col: str = "SK_ID_CURR", search_placeholder: str = "Search applicants, loan IDs..."):
    """Persistent top utility bar: a REAL working search box (filters the
    portfolio by applicant ID when a df is supplied), a notification bell,
    the user chip, and a real logout button."""
    u = current_user()
    col_search, col_right = st.columns([2.2, 1.6])

    with col_search:
        query = st.text_input(
            "Search", placeholder=search_placeholder, label_visibility="collapsed",
            key="global_search_query",
        )

    with col_right:
        c_bell, c_avatar, c_logout = st.columns([0.7, 2.3, 1.1])
        with c_bell:
            st.markdown('<div class="topbar-icon-btn">&#128276;<div class="topbar-icon-dot"></div></div>',
                        unsafe_allow_html=True)
        with c_avatar:
            st.markdown(_raw_html(f"""
            <div class="topbar-avatar">
            <div class="topbar-avatar-circle">{u['initials']}</div>
            <div class="topbar-avatar-text"><p class="topbar-avatar-name">{u['name']}</p><p class="topbar-avatar-role">{u['role']}</p></div>
            </div>
            """), unsafe_allow_html=True)
        with c_logout:
            st.markdown('<div class="topbar-logout-wrap">', unsafe_allow_html=True)
            if st.button("Log out", key="topbar_logout_btn"):
                from utils.auth import logout
                logout()
            st.markdown('</div>', unsafe_allow_html=True)

    if query and df is not None:
        _render_search_results(df, query, id_col)


def _render_search_results(df, query: str, id_col: str):
    """Matches the search box against applicant ID (exact or partial) and,
    if nothing numeric matches, against a couple of common category
    columns — then renders up to 5 hits as compact result cards."""
    import pandas as pd

    q = query.strip()
    matches = pd.DataFrame()

    digits = "".join(ch for ch in q if ch.isdigit())
    if digits:
        matches = df[df[id_col].astype(str).str.contains(digits, na=False)]

    if matches.empty:
        for col in ["NAME_INCOME_TYPE", "NAME_EDUCATION_TYPE", "NAME_FAMILY_STATUS",
                     "NAME_HOUSING_TYPE", "OCCUPATION_TYPE", "RISK_LABEL"]:
            if col in df.columns:
                hit = df[df[col].astype(str).str.contains(q, case=False, na=False)]
                if not hit.empty:
                    matches = hit
                    break

    if matches.empty:
        st.warning(f"No applicants matched “{query}”. Try an applicant ID (e.g. {int(df[id_col].iloc[0])}) or a term like “Working”, “Higher education”, “Married”.")
        return

    st.caption(f"🔎 {len(matches):,} result(s) for “{query}” — showing top 5")
    for _, r in matches.head(5).iterrows():
        risk = r.get("RISK_LABEL", "—")
        badge_class = "badge-high" if risk == "Payment difficulty" else "badge-low"
        badge_text = "High risk" if risk == "Payment difficulty" else "Low risk"
        st.markdown(_raw_html(f"""
        <div class="search-result-card">
        <b>Applicant #{int(r[id_col])}</b> &nbsp;
        <span class="badge {badge_class}">{badge_text}</span>
        &nbsp;·&nbsp; {r.get('GENDER_LABEL','—')}, {r.get('AGE_YEARS', float('nan')):.0f} yrs
        &nbsp;·&nbsp; {r.get('NAME_INCOME_TYPE','—')}
        &nbsp;·&nbsp; Loan ${r.get('AMT_CREDIT', float('nan')):,.0f}
        &nbsp;·&nbsp; Income ${r.get('AMT_INCOME_TOTAL', float('nan')):,.0f}
        </div>
        """), unsafe_allow_html=True)


def welcome_banner(greeting: str, message: str, pill_text: str = None):
    """Personalized greeting banner shown at the top of the home page."""
    pill_html = f'<div class="welcome-pill">{pill_text}</div>' if pill_text else ""
    st.markdown(_raw_html(f"""
    <div class="welcome-banner">
    <div><h2>{greeting}</h2><p>{message}</p></div>
    {pill_html}
    </div>
    """), unsafe_allow_html=True)


def page_header(title: str, subtitle: str, icon: str = ""):
    st.markdown(_raw_html(f"""
    <div class="page-header">
    <h1>{icon} {title}</h1>
    <p>{subtitle}</p>
    </div>
    """), unsafe_allow_html=True)

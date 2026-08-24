"""
Lightweight session-based authentication for the Meridian console.

Not production auth (passwords live in this file for demo purposes) —
it's meant to demonstrate a real login -> session -> logout flow around
the dashboard: every page calls require_login() before rendering, which
shows a styled login card and st.stop()s the script until the person
signs in. utils.theme reads st.session_state["user"] to personalize the
sidebar / topbar, and the logout buttons there call logout() below.
"""
import streamlit as st
from utils.theme import apply_theme, _raw_html, APP_NAME, APP_TAGLINE

# Demo directory. Swap this for a real identity provider / DB lookup
# before shipping — this dict is only for illustrating the auth flow.
USERS = {
    "alex.morgan": {"password": "meridian2026", "name": "Alex Morgan",
                     "role": "Senior Credit Analyst", "initials": "AM"},
    "admin": {"password": "admin123", "name": "Portfolio Admin",
              "role": "Risk Administrator", "initials": "PA"},
}


def is_authenticated() -> bool:
    return bool(st.session_state.get("authenticated"))


def require_login():
    """Call at the top of every page (after apply_theme()/set_page_config).
    Renders the login screen and halts the script if no one's signed in."""
    if is_authenticated():
        return
    _render_login_screen()
    st.stop()


def logout():
    st.session_state.pop("authenticated", None)
    st.session_state.pop("user", None)
    st.rerun()


def _render_login_screen():
    apply_theme()
    st.markdown(_raw_html(f"""
    <div class="login-wrap">
    <div class="login-logo">{APP_NAME[0]}</div>
    <div class="login-title">Sign in to {APP_NAME}</div>
    <div class="login-sub">{APP_TAGLINE} — loan portfolio & default-risk analytics</div>
    </div>
    """), unsafe_allow_html=True)

    _, mid, _ = st.columns([1, 1.05, 1])
    with mid:
        with st.form("login_form", clear_on_submit=False):
            username = st.text_input("Username", placeholder="e.g. alex.morgan")
            password = st.text_input("Password", type="password", placeholder="••••••••••")
            submitted = st.form_submit_button("Sign in")

        if submitted:
            record = USERS.get(username.strip().lower())
            if record and password == record["password"]:
                st.session_state["authenticated"] = True
                st.session_state["user"] = {
                    "name": record["name"], "role": record["role"], "initials": record["initials"],
                }
                st.rerun()
            else:
                st.error("Invalid username or password. Try the demo credentials below.")

        st.markdown(_raw_html("""
        <div class="login-hint">
        🔑 <b>Demo credentials</b><br>
        alex.morgan / meridian2026 &nbsp;·&nbsp; admin / admin123
        </div>
        """), unsafe_allow_html=True)

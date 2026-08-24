import streamlit as st

# Demo credentials — swap this for a real user store / auth provider in production.
USERS = {
    "admin": "admin123",
    "guest": "guest123",
}


def _login_styles():
    st.markdown("""
        <style>
        .login-hero {
            max-width: 420px;
            margin: 6vh auto 0 auto;
            padding: 2.5rem 2.25rem;
            border-radius: 18px;
            background: linear-gradient(160deg, rgba(141,0,196,0.35) 0%, rgba(6,7,13,0.9) 100%);
            border: 1px solid #b53dff;
            box-shadow: 0 12px 45px rgba(181, 61, 255, 0.45);
            backdrop-filter: blur(10px);
        }
        .login-title {
            font-size: 1.6rem;
            font-weight: 800;
            color: #14e81e;
            text-align: center;
            margin-bottom: 0.2rem;
            text-shadow: 0 0 16px rgba(20,232,30,0.6);
        }
        .login-subtitle {
            font-size: 0.9rem;
            color: #017ed5;
            text-align: center;
            margin-bottom: 1.6rem;
        }
        .login-hint {
            font-size: 0.78rem;
            color: #00ea8d;
            text-align: center;
            margin-top: 0.9rem;
        }
        </style>
    """, unsafe_allow_html=True)


def _login_form():
    _login_styles()
    st.markdown('<div class="login-hero">', unsafe_allow_html=True)
    st.markdown('<div class="login-title">🔐 Superstore Command Center</div>', unsafe_allow_html=True)
    st.markdown('<div class="login-subtitle">Sign in to access your analytics suite</div>', unsafe_allow_html=True)

    with st.form("login_form", clear_on_submit=False):
        username = st.text_input("Username", placeholder="Enter username")
        password = st.text_input("Password", type="password", placeholder="Enter password")
        submitted = st.form_submit_button("Sign In", use_container_width=True)

    if submitted:
        if USERS.get(username) == password:
            st.session_state["authenticated"] = True
            st.session_state["username"] = username
            st.rerun()
        else:
            st.error("Invalid username or password. Please try again.")

    st.markdown(
        '<div class="login-hint">Demo credentials &mdash; admin / admin123 &nbsp;·&nbsp; guest / guest123</div>',
        unsafe_allow_html=True,
    )
    st.markdown('</div>', unsafe_allow_html=True)


def require_login():
    """Call at the top of every page. Blocks the page behind a login screen
    until the user authenticates, using st.session_state to persist the
    session across pages and reruns."""
    if "authenticated" not in st.session_state:
        st.session_state["authenticated"] = False

    if not st.session_state["authenticated"]:
        _login_form()
        st.stop()


def render_logout():
    """Sidebar widget showing who's signed in plus a working logout button."""
    with st.sidebar:
        st.markdown("---")
        st.markdown(f"👤 **Signed in as:** `{st.session_state.get('username', 'user')}`")
        if st.button("🚪 Logout", use_container_width=True, key="logout_btn"):
            st.session_state["authenticated"] = False
            st.session_state.pop("username", None)
            st.rerun()

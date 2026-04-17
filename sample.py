# app.py — HCCCI Student Analytics (entry)
from __future__ import annotations
import streamlit as st

# ── Page config MUST be the first Streamlit call
st.set_page_config(
    page_title="HCCCI Student Analytics",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Import after page_config
from auth import (
    verify_login, ensure_default_admin, get_current_user, set_current_user, sign_out,
)
from db import students_collection

# ── Cross-version rerun helper (Streamlit >=1.30 uses st.rerun)
def _rerun():
    r = getattr(st, "rerun", None)
    if callable(r):
        r()
    else:
        e = getattr(st, "experimental_rerun", None)
        if callable(e):
            e()

# ---------- CSS ----------
st.markdown(
    """
    <style>
      .main { padding-top: 1rem; }
      .login-card {
        background: #0f131a; border:1px solid rgba(255,255,255,.08);
        border-radius:16px; padding:1.2rem; box-shadow:0 6px 18px rgba(0,0,0,.35);
      }
      .muted { color: rgba(255,255,255,.65); font-size:.92rem; }

      section[data-testid="stSidebar"] {
        background:#161a22; border-right:1px solid rgba(255,255,255,.08);
      }

      section[data-testid="stSidebar"] > div {
        height:100%;
        display:flex;
        flex-direction:column;
      }

      section[data-testid="stSidebar"] [data-testid="stSidebarNav"] {
        flex:1 1 auto;
        padding-top:.25rem;
      }

      section[data-testid="stSidebar"] [data-testid="stSidebarNav"] a {
        display:block;
        padding:.55rem .65rem;
        margin:.15rem .5rem;
        border-radius:.6rem;
        font-weight:600;
        text-decoration:none !important;
        color: rgba(255,255,255,.92);
      }

      section[data-testid="stSidebar"] [data-testid="stSidebarNav"] a:hover {
        background: rgba(255,255,255,.07);
      }

      section[data-testid="stSidebar"] [data-testid="stSidebarNav"] a[aria-current="page"] {
        background: linear-gradient(135deg,#2d6cdf 0%,#6b8ff5 100%);
        color:#fff !important;
      }

      .sb-footer {
        border-top:1px solid rgba(255,255,255,.08);
        padding:.85rem .8rem 1rem .8rem;
      }

      .sb-user {
        display:flex;
        align-items:center;
        gap:.6rem;
        margin-bottom:.55rem;
      }

      .sb-user .badge {
        font-weight:700;
        font-size:.75rem;
        padding:.10rem .4rem;
        background:#243042;
        color:#dfe7ff;
        border-radius:.35rem;
      }

      .sb-user .email {
        color:#cfd6e6;
        font-size:.87rem;
      }

      .danger-btn > button {
        width:100%;
        background: linear-gradient(135deg,#e74a54 0%,#d12f53 100%) !important;
        color:#fff !important;
        font-weight:700 !important;
        border-radius:.6rem !important;
      }

      .hide-nav section[data-testid="stSidebar"] [data-testid="stSidebarNav"] {
        display:none;
      }
    </style>
    """,
    unsafe_allow_html=True,
)


def render_sidebar_footer(user: dict) -> None:
    if not user:
        return

    with st.sidebar:
        st.markdown('<div class="sb-footer">', unsafe_allow_html=True)

        st.markdown(
            f"""
            <div class="sb-user">
                <div class="badge">{(user.get("role") or "").upper()}</div>
                <div class="email">{user.get("email","")}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        if st.button("Log out", use_container_width=True):
            sign_out()
            _rerun()

        st.markdown("</div>", unsafe_allow_html=True)


def render_login():
    st.markdown("<div class='hide-nav'></div>", unsafe_allow_html=True)

    st.title("🎓 HCCCI Student Analytics")
    st.caption("Please sign in to continue.")

    col1, col2 = st.columns([1, 1], gap="large")

    with col1:
        st.markdown('<div class="login-card">', unsafe_allow_html=True)

        email = st.text_input("Email", placeholder="you@su.edu")
        pw = st.text_input("Password", type="password")

        c1, c2 = st.columns(2)

        with c1:
            if st.button("Login", type="primary", use_container_width=True):
                u = verify_login(email, pw)
                if not u:
                    st.error("Invalid credentials.")
                else:
                    set_current_user(u)
                    _rerun()

        with c2:
            if st.button("Create default admin", use_container_width=True):
                ensure_default_admin(
                    "admin@gmail.com",
                    password="Admin@1234",
                    reset_password=True
                )
                st.success("Created/updated: admin@gmail.com / Admin@1234")

        st.markdown("</div>", unsafe_allow_html=True)


def main():
    user = get_current_user()

    if not user:
        render_login()
        st.stop()

    st.title("🎓 HCCCI Student Analytics")

    st.caption(
        f"Logged in as {user.get('email','')} | role: {user.get('role','')}"
    )

    render_sidebar_footer(user)

    st.info(
        "Use the sidebar to open Registrar, Faculty, or Student dashboards."
    )


if __name__ == "__main__":
    main()
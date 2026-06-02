from __future__ import annotations

import streamlit as st

from hu01_temporizador_rotacion_roles.ui import render as render_hu01
from hu02_revision_codigo.ui import render as render_hu02
from shared.supabase_client import should_use_supabase


st.set_page_config(
    page_title="ELEKTRON XP · Pair Programming",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)


def _inject_global_styles() -> None:
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=Syne:wght@400;600;700;800&family=DM+Sans:wght@300;400;500&display=swap');

        :root {
            --neon: #6EE7B7;
            --neon-blue: #38bdf8;
            --neon-purple: #a78bfa;
            --neon-amber: #fbbf24;
            --neon-red: #f87171;
            --bg: #050a14;
            --bg2: #0d1526;
            --bg3: #111c35;
            --border: rgba(110,231,183,0.12);
            --border-dim: rgba(255,255,255,0.06);
            --text: #e2e8f0;
            --text-dim: #64748b;
            --text-bright: #f8fafc;
            --glass: rgba(13, 21, 38, 0.85);
        }

        html, body, [class*="css"] {
            font-family: 'DM Sans', sans-serif !important;
        }

        .main .block-container {
            padding-top: 1.5rem;
            padding-bottom: 4rem;
            max-width: 1280px;
        }

        /* ── SIDEBAR ── */
        [data-testid="stSidebar"] {
            background: var(--bg) !important;
            border-right: 1px solid var(--border) !important;
        }
        [data-testid="stSidebar"]::before {
            content: '';
            position: absolute;
            top: 0; left: 0; right: 0;
            height: 200px;
            background: radial-gradient(ellipse at top left, rgba(110,231,183,0.08) 0%, transparent 70%);
            pointer-events: none;
        }
        [data-testid="stSidebar"] * {
            color: var(--text) !important;
        }
        [data-testid="stSidebar"] .stRadio label {
            background: rgba(255,255,255,0.03) !important;
            border: 1px solid var(--border-dim) !important;
            border-radius: 10px !important;
            padding: 0.6rem 0.9rem !important;
            margin-bottom: 0.4rem !important;
            transition: all 0.2s ease !important;
            cursor: pointer !important;
        }
        [data-testid="stSidebar"] .stRadio label:hover {
            border-color: var(--border) !important;
            background: rgba(110,231,183,0.06) !important;
        }

        /* ── HERO BANNER ── */
        .xp-hero {
            position: relative;
            overflow: hidden;
            background: linear-gradient(135deg, #050f1e 0%, #091529 40%, #06111f 100%);
            border: 1px solid var(--border);
            border-radius: 20px;
            padding: 2.4rem 2.6rem;
            margin-bottom: 1.5rem;
            box-shadow: 0 0 60px rgba(110,231,183,0.06), inset 0 1px 0 rgba(255,255,255,0.06);
        }
        .xp-hero::before {
            content: '';
            position: absolute;
            top: -60px; left: -40px;
            width: 340px; height: 340px;
            background: radial-gradient(circle, rgba(110,231,183,0.10) 0%, transparent 65%);
            pointer-events: none;
        }
        .xp-hero::after {
            content: '';
            position: absolute;
            bottom: -80px; right: -40px;
            width: 300px; height: 300px;
            background: radial-gradient(circle, rgba(56,189,248,0.08) 0%, transparent 65%);
            pointer-events: none;
        }
        .xp-hero-badge {
            display: inline-flex;
            align-items: center;
            gap: 0.4rem;
            background: rgba(110,231,183,0.1);
            border: 1px solid rgba(110,231,183,0.25);
            border-radius: 999px;
            padding: 0.25rem 0.75rem;
            font-size: 0.75rem;
            font-family: 'Space Mono', monospace;
            color: var(--neon);
            letter-spacing: 0.08em;
            text-transform: uppercase;
            margin-bottom: 1rem;
        }
        .xp-hero h1 {
            font-family: 'Syne', sans-serif !important;
            font-size: 2.6rem;
            font-weight: 800;
            line-height: 1.05;
            letter-spacing: -0.04em;
            color: var(--text-bright);
            margin: 0 0 0.8rem 0;
        }
        .xp-hero h1 span {
            color: var(--neon);
        }
        .xp-hero p {
            color: var(--text-dim);
            font-size: 1rem;
            max-width: 680px;
            line-height: 1.65;
            margin: 0;
        }
        .xp-hero-grid {
            position: absolute;
            top: 0; left: 0; right: 0; bottom: 0;
            background-image: 
                linear-gradient(rgba(110,231,183,0.03) 1px, transparent 1px),
                linear-gradient(90deg, rgba(110,231,183,0.03) 1px, transparent 1px);
            background-size: 40px 40px;
            pointer-events: none;
        }

        /* ── CARDS ── */
        .xp-card {
            background: var(--bg2);
            border: 1px solid var(--border-dim);
            border-radius: 16px;
            padding: 1.25rem 1.4rem;
            margin-bottom: 1rem;
            position: relative;
            overflow: hidden;
        }
        .xp-card::before {
            content: '';
            position: absolute;
            top: 0; left: 0; right: 0;
            height: 1px;
            background: linear-gradient(90deg, transparent, rgba(110,231,183,0.15), transparent);
        }
        .xp-card h3 {
            font-family: 'Syne', sans-serif !important;
            font-size: 1.05rem;
            font-weight: 700;
            color: var(--text-bright) !important;
            margin: 0 0 0.5rem 0 !important;
        }
        .xp-card h4 {
            font-family: 'Syne', sans-serif !important;
            font-size: 0.95rem;
            font-weight: 700;
            color: var(--text-bright) !important;
            margin: 0 0 0.5rem 0 !important;
        }

        /* ── MUTED TEXT ── */
        .xp-muted {
            color: var(--text-dim) !important;
            font-size: 0.88rem;
            line-height: 1.6;
        }

        /* ── PILLS / BADGES ── */
        .xp-pill {
            display: inline-flex;
            align-items: center;
            gap: 0.3rem;
            padding: 0.28rem 0.7rem;
            border-radius: 999px;
            background: rgba(110,231,183,0.08);
            border: 1px solid rgba(110,231,183,0.2);
            color: var(--neon);
            font-weight: 600;
            font-size: 0.78rem;
            font-family: 'Space Mono', monospace;
            margin: 0.15rem 0.15rem 0.15rem 0;
            letter-spacing: 0.02em;
        }
        .xp-pill-success {
            background: rgba(110,231,183,0.1);
            border-color: rgba(110,231,183,0.3);
            color: #6ee7b7;
        }
        .xp-pill-warning {
            background: rgba(251,191,36,0.1);
            border-color: rgba(251,191,36,0.3);
            color: #fbbf24;
        }
        .xp-pill-danger {
            background: rgba(248,113,113,0.1);
            border-color: rgba(248,113,113,0.3);
            color: #f87171;
        }
        .xp-pill-purple {
            background: rgba(167,139,250,0.1);
            border-color: rgba(167,139,250,0.3);
            color: #a78bfa;
        }

        /* ── TIMER ── */
        .xp-timer {
            text-align: center;
            padding: 2rem 1.5rem;
            border-radius: 20px;
            background: linear-gradient(135deg, rgba(110,231,183,0.05) 0%, rgba(56,189,248,0.05) 100%);
            border: 1px solid rgba(110,231,183,0.12);
            position: relative;
            overflow: hidden;
        }
        .xp-timer::before {
            content: '';
            position: absolute;
            inset: 0;
            background: radial-gradient(circle at 50% 0%, rgba(110,231,183,0.08) 0%, transparent 60%);
        }
        .xp-timer-number {
            font-family: 'Space Mono', monospace;
            font-size: 5rem;
            font-weight: 700;
            color: var(--neon);
            line-height: 1;
            text-shadow: 0 0 40px rgba(110,231,183,0.4);
            position: relative;
            z-index: 1;
        }
        .xp-timer-label {
            font-family: 'DM Sans', sans-serif;
            color: var(--text-dim);
            font-size: 0.82rem;
            font-weight: 500;
            margin-top: 0.6rem;
            text-transform: uppercase;
            letter-spacing: 0.1em;
            position: relative;
            z-index: 1;
        }

        /* ── ALERT ── */
        .xp-alert-finished {
            background: linear-gradient(135deg, rgba(248,113,113,0.08) 0%, rgba(251,191,36,0.06) 100%);
            border: 1px solid rgba(248,113,113,0.25);
            border-radius: 14px;
            padding: 1rem 1.2rem;
            color: #f87171;
            font-weight: 600;
            font-size: 0.92rem;
            margin-bottom: 1rem;
            line-height: 1.6;
        }

        /* ── REVIEW CARDS ── */
        .xp-review-card {
            background: var(--bg2);
            border: 1px solid var(--border-dim);
            border-radius: 14px;
            padding: 1.1rem 1.2rem;
            margin-bottom: 0.8rem;
            transition: border-color 0.2s ease;
            position: relative;
            overflow: hidden;
        }
        .xp-review-card:hover {
            border-color: var(--border);
        }
        .xp-review-card::before {
            content: '';
            position: absolute;
            left: 0; top: 0; bottom: 0;
            width: 3px;
            background: var(--neon);
            border-radius: 3px 0 0 3px;
            opacity: 0.5;
        }

        /* ── HEADINGS IN MAIN ── */
        h2 {
            font-family: 'Syne', sans-serif !important;
            font-weight: 800 !important;
            letter-spacing: -0.03em !important;
            color: var(--text-bright) !important;
        }
        h3 {
            font-family: 'Syne', sans-serif !important;
            font-weight: 700 !important;
        }

        /* ── SIDEBAR LOGO / BRAND ── */
        .xp-sidebar-brand {
            display: flex;
            align-items: center;
            gap: 0.6rem;
            margin-bottom: 1.5rem;
            padding-bottom: 1.2rem;
            border-bottom: 1px solid var(--border-dim);
        }
        .xp-sidebar-brand .icon {
            font-size: 1.6rem;
            line-height: 1;
        }
        .xp-sidebar-brand .name {
            font-family: 'Syne', sans-serif;
            font-size: 1rem;
            font-weight: 800;
            color: var(--text-bright) !important;
            letter-spacing: -0.02em;
        }
        .xp-sidebar-brand .sub {
            font-family: 'Space Mono', monospace;
            font-size: 0.65rem;
            color: var(--neon) !important;
            letter-spacing: 0.1em;
            text-transform: uppercase;
        }

        /* ── STORAGE STATUS ── */
        .xp-storage-badge {
            display: flex;
            align-items: center;
            gap: 0.5rem;
            background: rgba(110,231,183,0.06);
            border: 1px solid rgba(110,231,183,0.15);
            border-radius: 10px;
            padding: 0.5rem 0.75rem;
            font-size: 0.82rem;
            color: var(--neon) !important;
            margin-bottom: 1rem;
        }
        .xp-dot {
            width: 7px; height: 7px;
            border-radius: 50%;
            background: var(--neon);
            box-shadow: 0 0 8px var(--neon);
            flex-shrink: 0;
        }

        /* ── FOOTER ── */
        .xp-footer {
            text-align: center;
            font-size: 0.78rem;
            color: var(--text-dim);
            font-family: 'Space Mono', monospace;
            letter-spacing: 0.04em;
            padding-top: 1rem;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


_inject_global_styles()

# ── HERO ──────────────────────────────────────────────────────────────
st.markdown(
    """
    <div class="xp-hero">
        <div class="xp-hero-grid"></div>
        <div class="xp-hero-badge">⚡ v2.0 · XP Methodology</div>
        <h1>ELEKTRON <span>XP</span><br>Pair Programming</h1>
        <p>
            App académica para practicar Extreme Programming: rotación de roles Piloto/Copiloto
            y registro de revisiones de código. Lógica separada por HU, tests automatizados y
            almacenamiento local o Supabase.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

# ── SIDEBAR ────────────────────────────────────────────────────────────
modo = "Supabase" if should_use_supabase() else "Memoria local"

st.sidebar.markdown(
    """
    <div class="xp-sidebar-brand">
        <span class="icon">⚡</span>
        <div>
            <div class="name">ELEKTRON XP</div>
            <div class="sub">Pair Programming</div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.sidebar.markdown(
    f"""
    <div class="xp-storage-badge">
        <div class="xp-dot"></div>
        {modo}
    </div>
    """,
    unsafe_allow_html=True,
)

st.sidebar.caption(
    "Configura `.env` con `USE_SUPABASE=true`, `SUPABASE_URL` y `SUPABASE_KEY` para persistencia en la nube."
)

st.sidebar.markdown("---")
st.sidebar.markdown("**🗂️ Historias de usuario**")

hu = st.sidebar.radio(
    "",
    [
        "HU1 · Temporizador de Rotación",
        "HU2 · Revisión de Código",
    ],
    label_visibility="collapsed",
)

st.sidebar.markdown("---")
st.sidebar.markdown("**🧪 Tests**")
st.sidebar.code("pytest -v", language="bash")
st.sidebar.caption("Ejecuta las suites de test para cada historia de usuario.")

if hu.startswith("HU1"):
    render_hu01()
else:
    render_hu02()

st.divider()
st.markdown(
    '<div class="xp-footer">ELEKTRON XP · Python · Streamlit · Supabase · pytest</div>',
    unsafe_allow_html=True,
)

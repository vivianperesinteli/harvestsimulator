"""Autenticação simples baseada em arquivo — sem dependências externas."""

import hashlib
import hmac
import json
import os
import secrets
from pathlib import Path
from datetime import datetime

import streamlit as st

_DATA_DIR   = Path(__file__).parent.parent / "data"
_USERS_FILE = _DATA_DIR / "users.json"

_DEMO = {
    "demo": {
        "name": "Produtor Demo",
        "email": "demo@simulador.com",
        "password_hash": "sha256:" + hashlib.sha256("demo123".encode()).hexdigest(),
        "created_at": "2024-01-01T00:00:00",
    }
}


def _ensure() -> None:
    _DATA_DIR.mkdir(parents=True, exist_ok=True)
    if not _USERS_FILE.exists():
        _USERS_FILE.write_text(
            json.dumps(_DEMO, indent=2, ensure_ascii=False), encoding="utf-8"
        )


def _load() -> dict:
    _ensure()
    try:
        return json.loads(_USERS_FILE.read_text(encoding="utf-8"))
    except Exception:
        return {}


def _save(users: dict) -> None:
    _ensure()
    _USERS_FILE.write_text(json.dumps(users, indent=2, ensure_ascii=False), encoding="utf-8")


def _hash(password: str) -> str:
    """Gera hash seguro com PBKDF2-SHA256 + salt aleatório."""
    salt = secrets.token_hex(16)
    dk = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), 260_000)
    return f"pbkdf2:{salt}:{dk.hex()}"


def _verify(password: str, stored: str) -> bool:
    """Verifica senha contra hash armazenado (suporta pbkdf2, sha256: prefixado e sha256 puro legado)."""
    if stored.startswith("pbkdf2:"):
        _, salt, dk_hex = stored.split(":", 2)
        dk = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), 260_000)
        return hmac.compare_digest(dk.hex(), dk_hex)
    if stored.startswith("sha256:"):
        legacy = hashlib.sha256(password.encode()).hexdigest()
        return hmac.compare_digest(legacy, stored[7:])
    # Hash SHA-256 puro sem prefixo — formato anterior ao refactor
    if len(stored) == 64 and all(c in "0123456789abcdef" for c in stored):
        legacy = hashlib.sha256(password.encode()).hexdigest()
        return hmac.compare_digest(legacy, stored)
    return False


# ── Public API ────────────────────────────────────────────────────────────────

def is_authenticated() -> bool:
    return bool(st.session_state.get("auth"))


def login(username: str, password: str) -> bool:
    users = _load()
    user  = users.get(username.strip().lower())
    if user and _verify(password, user["password_hash"]):
        st.session_state.auth = {
            "username": username.strip().lower(),
            "name":     user["name"],
            "email":    user["email"],
        }
        return True
    return False


def register(username: str, name: str, email: str, password: str) -> tuple[bool, str]:
    users = _load()
    ukey  = username.strip().lower()
    if not ukey:
        return False, "Invalid username."
    if ukey in users:
        return False, "Username already exists."
    if any(u["email"].lower() == email.strip().lower() for u in users.values()):
        return False, "Email already registered."
    users[ukey] = {
        "name":          name.strip(),
        "email":         email.strip().lower(),
        "password_hash": _hash(password),
        "created_at":    datetime.now().isoformat(),
    }
    _save(users)
    return True, "Account created successfully!"


def logout() -> None:
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.rerun()


# ── Auth page render ──────────────────────────────────────────────────────────

def render_auth() -> None:
    """Landing page de login — design premium tela cheia."""

    st.markdown("""
    <style>
    /* ══════════════════════════════════════════════════
       AUTH PAGE — estilos injetados apenas nesta tela
    ══════════════════════════════════════════════════ */
    section[data-testid="stSidebar"] { display: none !important; }

    /* Esconde header/toolbar/decoration do Streamlit */
    #MainMenu, header, footer,
    [data-testid="stHeader"],
    [data-testid="stDecoration"],
    [data-testid="stDeployButton"],
    [data-testid="stToolbar"],
    [data-testid="stStatusWidget"] {
      display: none !important;
      height: 0 !important;
      overflow: hidden !important;
    }

    /* Fundo verde escuro em toda a página */
    html, body {
      background: #040d07 !important;
      min-height: 100vh;
    }
    .stApp,
    [data-testid="stAppViewContainer"] {
      background:
        repeating-linear-gradient(
          -58deg,
          transparent 0px, transparent 38px,
          rgba(118,196,66,0.022) 38px, rgba(118,196,66,0.022) 39px
        ),
        radial-gradient(ellipse 80% 60% at 25% 40%, rgba(29,92,56,0.45) 0%, transparent 65%),
        radial-gradient(ellipse 50% 70% at 85% 80%, rgba(13,43,24,0.6) 0%, transparent 60%),
        linear-gradient(155deg, #030c06 0%, #0a2016 38%, #0d2b18 65%, #091a0f 100%) !important;
      min-height: 100vh;
    }
    [data-testid="stMain"],
    [data-testid="stMain"] > div,
    .main,
    .main .block-container {
      background: transparent !important;
    }

    /* Container sem padding excessivo */
    .main .block-container {
      padding-top: 0 !important;
      padding-bottom: 0 !important;
      padding-left: 0 !important;
      padding-right: 0 !important;
      max-width: 100% !important;
      min-height: 100vh !important;
    }

    /* Row de colunas centralizada verticalmente */
    [data-testid="stHorizontalBlock"] {
      min-height: 100vh !important;
      align-items: center !important;
      padding: 48px 72px !important;
      gap: 56px !important;
    }

    /* Card branco — coluna do formulário */
    [data-testid="stHorizontalBlock"] > [data-testid="stColumn"]:last-child {
      background: #ffffff !important;
      border-radius: 24px !important;
      padding: 40px 32px !important;
      box-shadow:
        0 40px 100px rgba(0,0,0,0.55),
        0 12px 32px rgba(0,0,0,0.35),
        0 0 0 1px rgba(255,255,255,0.07) !important;
    }

    /* Texto escuro dentro do card */
    [data-testid="stHorizontalBlock"] > [data-testid="stColumn"]:last-child label,
    [data-testid="stHorizontalBlock"] > [data-testid="stColumn"]:last-child p,
    [data-testid="stHorizontalBlock"] > [data-testid="stColumn"]:last-child span,
    [data-testid="stHorizontalBlock"] > [data-testid="stColumn"]:last-child small,
    [data-testid="stHorizontalBlock"] > [data-testid="stColumn"]:last-child div {
      color: #1a1a2e !important;
    }

    /* Tabs dentro do card */
    [data-testid="stHorizontalBlock"] > [data-testid="stColumn"]:last-child [data-baseweb="tab"],
    [data-testid="stHorizontalBlock"] > [data-testid="stColumn"]:last-child [role="tab"] {
      color: #1a1a2e !important;
    }
    [data-testid="stHorizontalBlock"] > [data-testid="stColumn"]:last-child [aria-selected="true"],
    [data-testid="stHorizontalBlock"] > [data-testid="stColumn"]:last-child [aria-selected="true"] p {
      color: #1a5c38 !important;
    }

    /* Inputs dentro do card */
    [data-testid="stHorizontalBlock"] > [data-testid="stColumn"]:last-child input {
      background: #f8faf9 !important;
      border: 1.5px solid #d4e6d9 !important;
      color: #1a1a2e !important;
      border-radius: 10px !important;
    }
    [data-testid="stHorizontalBlock"] > [data-testid="stColumn"]:last-child input:focus {
      border-color: #1a5c38 !important;
      box-shadow: 0 0 0 3px rgba(26,92,56,0.12) !important;
    }

    /* Alerts dentro do card */
    [data-testid="stHorizontalBlock"] > [data-testid="stColumn"]:last-child [data-testid="stAlert"] {
      border-radius: 10px !important;
    }

    /* ── Logo mark da auth page ── */
    .auth-brand-wrap {
      display: flex;
      flex-direction: column;
      align-items: center;
      margin-bottom: 28px;
    }
    .auth-logo-mark {
      width: 64px; height: 64px;
      background: linear-gradient(145deg, #1a5c38 0%, #0d2b18 100%);
      border-radius: 18px;
      display: flex;
      align-items: center;
      justify-content: center;
      box-shadow: 0 8px 24px rgba(13,43,24,0.4), 0 2px 6px rgba(0,0,0,0.2);
      margin-bottom: 16px;
      position: relative;
      overflow: hidden;
    }
    .auth-logo-mark::before {
      content: '';
      position: absolute;
      inset: 0;
      background: linear-gradient(145deg, rgba(118,196,66,0.15) 0%, transparent 60%);
    }
    .auth-brand-name {
      font-size: 1.35rem;
      font-weight: 800;
      color: #0d2b18 !important;
      letter-spacing: -0.02em;
      line-height: 1;
      margin-bottom: 4px;
    }
    .auth-brand-sub {
      font-size: 0.75rem;
      color: #6b8f76 !important;
      font-weight: 500;
      letter-spacing: 0.06em;
      text-transform: uppercase;
    }
    .auth-divider {
      height: 1px;
      background: linear-gradient(90deg, transparent, #e0ead4, transparent);
      margin: 20px 0;
    }

    /* ── Hero da auth page ── */
    .auth-hero {
      padding: 24px 0;
    }
    .auth-hero-badge {
      display: inline-flex;
      align-items: center;
      gap: 6px;
      background: rgba(118,196,66,0.15);
      color: #76c442 !important;
      border: 1px solid rgba(118,196,66,0.3);
      padding: 5px 14px;
      border-radius: 30px;
      font-size: 0.72rem;
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: 0.1em;
      margin-bottom: 32px;
    }
    .auth-hero-badge::before {
      content: '';
      width: 6px; height: 6px;
      background: #76c442;
      border-radius: 50%;
      display: inline-block;
    }
    .auth-hero-title {
      font-size: 3rem;
      font-weight: 900;
      color: #ffffff !important;
      line-height: 1.08;
      letter-spacing: -0.035em;
      margin-bottom: 20px;
    }
    .auth-hero-title span {
      color: #76c442 !important;
    }
    .auth-hero-desc {
      font-size: 1rem;
      color: rgba(255,255,255,0.72) !important;
      line-height: 1.7;
      max-width: 420px;
      margin-bottom: 40px;
    }
    .auth-benefit-list {
      display: flex;
      flex-direction: column;
      gap: 16px;
      margin-bottom: 44px;
    }
    .auth-benefit-item {
      display: flex;
      align-items: center;
      gap: 14px;
    }
    .auth-benefit-icon {
      width: 36px; height: 36px;
      background: rgba(118,196,66,0.12);
      border: 1px solid rgba(118,196,66,0.2);
      border-radius: 10px;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 0.95rem;
      flex-shrink: 0;
    }
    .auth-benefit-content strong {
      display: block;
      font-size: 0.9rem;
      font-weight: 700;
      color: #ffffff !important;
      margin-bottom: 2px;
    }
    .auth-benefit-content span {
      font-size: 0.8rem;
      color: rgba(255,255,255,0.6) !important;
      line-height: 1.4;
    }
    .auth-stats-row {
      display: flex;
      gap: 0;
      border-top: 1px solid rgba(255,255,255,0.08);
      padding-top: 32px;
    }
    .auth-stat {
      flex: 1;
      padding-right: 24px;
      border-right: 1px solid rgba(255,255,255,0.08);
      margin-right: 24px;
    }
    .auth-stat:last-child {
      border-right: none;
      margin-right: 0;
    }
    .auth-stat-val {
      font-size: 1.6rem;
      font-weight: 900;
      color: #76c442 !important;
      line-height: 1;
      margin-bottom: 4px;
    }
    .auth-stat-label {
      font-size: 0.72rem;
      color: rgba(255,255,255,0.5) !important;
      text-transform: uppercase;
      letter-spacing: 0.08em;
    }

    /* ── Separador do olhinho (auth page) — remove border-left do BaseUI ── */
    [data-baseweb="base-input"] div,
    [data-baseweb="base-input"] > div,
    [data-baseweb="base-input"] > div > div,
    [data-baseweb="base-input"] > div:last-child {
      border: none !important;
      border-left: none !important;
      border-right: none !important;
      box-shadow: none !important;
      background: transparent !important;
    }

    /* ── Esconde "Press Enter to apply" ── */
    [data-testid="InputInstructions"] {
      display: none !important;
    }

    /* Demo access info */
    .auth-demo-box {
      margin-top: 16px;
      padding: 12px 16px;
      background: #f0f7f3;
      border: 1px solid #c8e0d0;
      border-radius: 10px;
      font-size: 0.75rem;
      color: #2d6b47 !important;
    }
    .auth-demo-box strong { color: #1a5c38 !important; }
    .auth-demo-box code {
      background: rgba(26,92,56,0.1) !important;
      color: #1a5c38 !important;
      padding: 1px 6px;
      border-radius: 4px;
      font-size: 0.72rem;
    }
    </style>
    """, unsafe_allow_html=True)

    col_hero, col_form = st.columns([6, 4], gap="large")

    # ── Coluna esquerda: hero ─────────────────────────────────────────────
    with col_hero:
        st.markdown("""
        <div class="auth-hero">
            <div class="auth-hero-badge">Soy · Mato Grosso</div>
            <div class="auth-hero-title">
                Simulate your harvest<br>
                <span>before deciding.</span>
            </div>
            <div class="auth-hero-desc">
                Enter your field conditions and management decisions.
                In seconds, receive recommendations based on climate and
                agronomic scenario analysis to maximize your productivity.
            </div>
            <div class="auth-benefit-list">
                <div class="auth-benefit-item">
                    <div class="auth-benefit-icon">📅</div>
                    <div class="auth-benefit-content">
                        <strong>Ideal planting window</strong>
                        <span>Discover which period delivers the most bags per hectare in your context.</span>
                    </div>
                </div>
                <div class="auth-benefit-item">
                    <div class="auth-benefit-icon">🌧️</div>
                    <div class="auth-benefit-content">
                        <strong>Climate risk analysis</strong>
                        <span>El Niño, La Niña or neutral — drought probabilities during the crop's critical period.</span>
                    </div>
                </div>
                <div class="auth-benefit-item">
                    <div class="auth-benefit-icon">📊</div>
                    <div class="auth-benefit-content">
                        <strong>Complete downloadable report</strong>
                        <span>PDF with recommendations, application guidelines and scenario summary.</span>
                    </div>
                </div>
            </div>
            <div class="auth-stats-row">
                <div class="auth-stat">
                    <div class="auth-stat-val">27</div>
                    <div class="auth-stat-label">Combinations evaluated</div>
                </div>
                <div class="auth-stat">
                    <div class="auth-stat-val">3</div>
                    <div class="auth-stat-label">Climate scenarios</div>
                </div>
                <div class="auth-stat">
                    <div class="auth-stat-val">1,000</div>
                    <div class="auth-stat-label">Monte Carlo simulations</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # ── Coluna direita: card de formulário ───────────────────────────────
    with col_form:
        # Logo mark
        st.markdown("""
        <div class="auth-brand-wrap">
            <div class="auth-logo-mark">
                <svg width="36" height="36" viewBox="0 0 36 36" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <!-- Haste central -->
                    <line x1="18" y1="31" x2="18" y2="11" stroke="white" stroke-width="2.2" stroke-linecap="round"/>
                    <!-- Espiga topo -->
                    <ellipse cx="18" cy="9" rx="4" ry="6.5" fill="rgba(255,255,255,0.95)"/>
                    <!-- Folha esquerda -->
                    <path d="M18 22 C14 20 10 16 11 11 C14 13 17 17 18 22Z" fill="rgba(255,255,255,0.75)"/>
                    <!-- Folha direita -->
                    <path d="M18 22 C22 20 26 16 25 11 C22 13 19 17 18 22Z" fill="rgba(255,255,255,0.75)"/>
                    <!-- Folha esq baixo -->
                    <path d="M18 27 C14 25 11 21 13 17 C15 19 17 23 18 27Z" fill="rgba(255,255,255,0.55)"/>
                    <!-- Folha dir baixo -->
                    <path d="M18 27 C22 25 25 21 23 17 C21 19 19 23 18 27Z" fill="rgba(255,255,255,0.55)"/>
                </svg>
            </div>
            <div class="auth-brand-name">Harvest Simulator</div>
            <div class="auth-brand-sub">Soy · Mato Grosso</div>
        </div>
        <div class="auth-divider"></div>
        """, unsafe_allow_html=True)

        tab_login, tab_reg = st.tabs(["Sign in", "Create account"])

        with tab_login:
            with st.form("form_login", clear_on_submit=False):
                username = st.text_input("Username", placeholder="your.username")
                password = st.text_input("Password", type="password", placeholder="••••••")
                entered  = st.form_submit_button("Sign in", type="primary", use_container_width=True)
            if entered:
                if not username or not password:
                    st.error("Please enter username and password.")
                elif login(username, password):
                    st.rerun()
                else:
                    st.error("Incorrect username or password.")

        with tab_reg:
            with st.form("form_register", clear_on_submit=True):
                r_name = st.text_input("Full name", placeholder="Ex: John Smith")
                r_email = st.text_input("Email", placeholder="john@farm.com")
                r_user  = st.text_input("Username", placeholder="john.smith")
                r_pwd   = st.text_input("Password", type="password", placeholder="min. 6 characters")
                r_pwd2  = st.text_input("Confirm password", type="password")
                submitted = st.form_submit_button("Create account", type="primary", use_container_width=True)
            if submitted:
                if not all([r_name, r_email, r_user, r_pwd]):
                    st.error("Please fill in all fields.")
                elif r_pwd != r_pwd2:
                    st.error("Passwords do not match.")
                elif len(r_pwd) < 6:
                    st.error("Password must be at least 6 characters.")
                else:
                    ok, msg = register(r_user, r_name, r_email, r_pwd)
                    if ok:
                        st.success(msg + " Now sign in.")
                    else:
                        st.error(msg)

        st.markdown("""
        <div class="auth-demo-box">
            <strong>Demo access</strong><br>
            Username: <code>demo</code> &nbsp;·&nbsp; Password: <code>demo123</code>
        </div>
        """, unsafe_allow_html=True)

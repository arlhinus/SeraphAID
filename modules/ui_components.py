"""
modules/ui_components.py — Componentes UI compartidos entre páginas.
Sprint 8-FE: topbar unificado, paleta azul marino, sidebar eliminado.
"""
import streamlit as st

# ── Paleta ────────────────────────────────────────────────────────────────────
COLOR = {
    "bg":        "#0F172A",
    "bg2":       "#111827",
    "card":      "#1E293B",
    "border":    "#334155",
    "accent":    "#2563EB",
    "accent_lt": "#3B82F6",
    "text":      "#F8FAFC",
    "text2":     "#CBD5E1",
    "muted":     "#64748B",
    "green":     "#10B981",
    "yellow":    "#F59E0B",
    "red":       "#EF4444",
}

_CSS = f"""
<style>
/* ── Layout ── */
[data-testid="stAppViewContainer"],
[data-testid="stMain"]               {{ background-color: {COLOR['bg']}; }}
.block-container                     {{ padding-top: 0 !important;
                                        padding-left: 1.5rem !important;
                                        padding-right: 1.5rem !important;
                                        max-width: 920px; }}

/* ── Sidebar oculto ── */
section[data-testid="stSidebar"]     {{ display: none !important; }}
[data-testid="collapsedControl"]     {{ display: none !important; }}
button[data-testid="baseButton-header"] {{ display: none !important; }}

/* ── Tipografía ── */
h1, h2, h3, h4                       {{ color: {COLOR['text']}; }}
p, li                                {{ color: {COLOR['text2']}; }}
label                                {{ color: {COLOR['text2']} !important; }}
[data-testid="stCaption"]            {{ color: {COLOR['muted']} !important; }}

/* ── Formulario y cards ── */
[data-testid="stForm"]               {{ background: {COLOR['card']};
                                        border: 1px solid {COLOR['border']};
                                        border-radius: 12px; padding: 1.4rem; }}
[data-testid="stExpander"]           {{ background: {COLOR['card']} !important;
                                        border: 1px solid {COLOR['border']} !important;
                                        border-radius: 10px !important; }}
[data-testid="stContainer"]          {{ border-color: {COLOR['border']} !important; }}

/* ── Métricas ── */
div[data-testid="stMetric"]          {{ background: {COLOR['card']};
                                        border: 1px solid {COLOR['border']};
                                        border-radius: 10px; padding: .7rem 1rem; }}
div[data-testid="stMetricValue"]     {{ color: {COLOR['text']} !important; }}
div[data-testid="stMetricLabel"]     {{ color: {COLOR['text2']} !important; }}

/* ── Botones ── */
.stButton > button                   {{ background-color: {COLOR['accent']};
                                        color: white; border: none; border-radius: 8px;
                                        font-weight: 600; padding: .5rem 1.5rem; }}
.stButton > button:hover             {{ background-color: {COLOR['accent_lt']}; }}

/* ── Inputs ── */
[data-testid="stTextInput"] input,
[data-baseweb="input"] input         {{ background: {COLOR['card']} !important;
                                        border-color: {COLOR['border']} !important;
                                        color: {COLOR['text']} !important; }}
[data-baseweb="select"]              {{ background: {COLOR['card']} !important; }}

/* ── Topbar nav activo ── */
.seraph-nav-active                   {{ background: {COLOR['accent']};
                                        color: {COLOR['text']} !important;
                                        padding: .28rem .9rem; border-radius: 20px;
                                        font-size: .88rem; font-weight: 600;
                                        white-space: nowrap; display: inline-block; }}
/* ── page_link inactivo ── */
a[data-testid="stPageLink-NavLink"] {{ color: {COLOR['text2']} !important;
                                       font-size: .88rem; text-decoration: none !important; }}
a[data-testid="stPageLink-NavLink"]:hover {{ color: {COLOR['text']} !important; }}
</style>
"""


def render_topbar(active_page: str) -> None:
    """
    Inyecta CSS global y renderiza el topbar con logo + navegación.
    active_page: 'examenes' | 'medicamentos'
    Debe llamarse justo después de set_page_config().
    """
    st.markdown(_CSS, unsafe_allow_html=True)

    # ── Brand ──────────────────────────────────────────────────────────────────
    st.markdown(f"""
<div style="background:{COLOR['bg2']};border-bottom:1px solid {COLOR['border']};
            padding:.7rem 0 .5rem;margin-bottom:.8rem;">
  <div style="max-width:920px;margin:0 auto;padding:0 .5rem;
              display:flex;align-items:center;justify-content:space-between;">
    <div>
      <span style="font-size:1.15rem;font-weight:700;color:{COLOR['text']};
                   letter-spacing:-.02em;">🩺 SeraphAID</span>
      <span style="font-size:.78rem;color:{COLOR['muted']};margin-left:.8rem;">
        Información orientativa · No reemplaza atención médica</span>
    </div>
  </div>
</div>""", unsafe_allow_html=True)

    # ── Nav tabs ───────────────────────────────────────────────────────────────
    _c1, _c2, _c3, _c4 = st.columns([1, 1, 6, 1])
    with _c1:
        if active_page == "examenes":
            st.markdown('<span class="seraph-nav-active">🩺 Exámenes</span>',
                        unsafe_allow_html=True)
        else:
            st.page_link("app.py", label="🩺 Exámenes")
    with _c2:
        if active_page == "medicamentos":
            st.markdown('<span class="seraph-nav-active">💊 Medicamentos</span>',
                        unsafe_allow_html=True)
        else:
            st.page_link("pages/02_medicamentos.py", label="💊 Medicamentos")

    st.divider()

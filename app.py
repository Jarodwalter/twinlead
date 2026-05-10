import streamlit as st
import anthropic
import pandas as pd
import time

# ─── PAGE CONFIG ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Twinlead",
    page_icon="🎯",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# ─── CUSTOM CSS ────────────────────────────────────────────────────────────────
st.html("""
<link href="https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600;700&display=swap" rel="stylesheet">
<style>

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif !important;
    background-color: #0D0D0D !important;
    color: #F0F0F0 !important;
}
.stApp { background-color: #0D0D0D; }

#MainMenu, footer, header, .stDeployButton { visibility: hidden; }
[data-testid="stToolbar"] { display: none; }

.block-container {
    max-width: 680px !important;
    padding: 3rem 2rem !important;
}

h1 {
    font-size: 1.6rem !important;
    font-weight: 700 !important;
    letter-spacing: -0.5px !important;
    color: #FFFFFF !important;
    margin-bottom: 0 !important;
}

h2, h3 {
    font-size: 0.85rem !important;
    font-weight: 600 !important;
    color: #888888 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.1em !important;
    margin-top: 2rem !important;
    margin-bottom: 0.5rem !important;
}

.stCaption p, [data-testid="stCaptionContainer"] p {
    color: #555555 !important;
    font-size: 0.82rem !important;
}

hr { border-color: #1C1C1C !important; margin: 1.5rem 0 !important; }

input[type="text"], input[type="number"], textarea {
    background-color: #141414 !important;
    border: 1px solid #242424 !important;
    border-radius: 8px !important;
    color: #F0F0F0 !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.9rem !important;
}
input:focus, textarea:focus {
    border-color: #4F6EF7 !important;
    box-shadow: 0 0 0 3px rgba(79,110,247,0.12) !important;
}
label, [data-testid="stWidgetLabel"] p {
    color: #888888 !important;
    font-size: 0.82rem !important;
    font-weight: 500 !important;
}

.stButton > button[kind="primary"] {
    background: #4F6EF7 !important;
    color: #FFFFFF !important;
    border: none !important;
    border-radius: 8px !important;
    font-family: 'DM Sans', sans-serif !important;
    font-weight: 600 !important;
    font-size: 0.92rem !important;
    padding: 0.65rem 1.5rem !important;
    letter-spacing: 0.01em !important;
    transition: all 0.2s ease !important;
}
.stButton > button[kind="primary"]:hover {
    background: #3D5AE0 !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 4px 24px rgba(79,110,247,0.3) !important;
}

.stButton > button[kind="secondary"] {
    background: transparent !important;
    color: #555555 !important;
    border: 1px solid #242424 !important;
    border-radius: 8px !important;
    font-family: 'DM Sans', sans-serif !important;
    font-weight: 500 !important;
    font-size: 0.85rem !important;
    transition: all 0.2s ease !important;
}
.stButton > button[kind="secondary"]:hover {
    color: #AAAAAA !important;
    border-color: #3A3A3A !important;
}

[data-testid="stLinkButton"] a {
    background: #4F6EF7 !important;
    color: #FFFFFF !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    font-family: 'DM Sans', sans-serif !important;
    text-decoration: none !important;
}
[data-testid="stLinkButton"] a:hover { background: #3D5AE0 !important; }

.stProgress > div > div > div {
    background: linear-gradient(90deg, #4F6EF7, #818CF8) !important;
    border-radius: 4px !important;
}
.stProgress > div > div {
    background: #1A1A1A !important;
    border-radius: 4px !important;
}

[data-testid="stDataFrame"] {
    border: 1px solid #1C1C1C !important;
    border-radius: 10px !important;
    overflow: hidden !important;
}

[data-testid="stAlert"] {
    background: #141414 !important;
    border: 1px solid #242424 !important;
    border-radius: 8px !important;
    color: #888888 !important;
    font-size: 0.85rem !important;
}

[data-testid="stDownloadButton"] button {
    background: transparent !important;
    border: 1px solid #242424 !important;
    color: #888888 !important;
    border-radius: 8px !important;
    font-family: 'DM Sans', sans-serif !important;
    font-weight: 500 !important;
    transition: all 0.2s ease !important;
}
[data-testid="stDownloadButton"] button:hover {
    border-color: #4F6EF7 !important;
    color: #4F6EF7 !important;
}

</style>
""")


# ─── SESSION STATE ──────────────────────────────────────────────────────────────
if "screen" not in st.session_state:
    st.session_state.screen = 1
if "free_run_used" not in st.session_state:
    st.session_state.free_run_used = False
if "leads" not in st.session_state:
    st.session_state.leads = []
if "icp" not in st.session_state:
    st.session_state.icp = {}


# ─── SCREEN 1 : CONFIG ─────────────────────────────────────────────────────────
def screen_config():
    st.title("🎯 Twinlead")
    st.caption("Trouve les clones de tes meilleurs clients. Automatiquement.")
    st.divider()

    st.subheader("Ton ICP")
    sector = st.text_input("Secteur cible", placeholder="ex: Import/Export, Manufacturing, Logistique")
    col1, col2 = st.columns(2)
    with col1:
        revenue_min = st.number_input("CA min (M€)", min_value=0, value=1)
    with col2:
        revenue_max = st.number_input("CA max (M€)", min_value=0, value=15)
    geography = st.text_input("Zone géographique", placeholder="ex: France, Île-de-France, DACH")

    st.divider()

    st.subheader("Entreprises référentes")
    st.caption("2 à 3 clients que tu sais être de bons clients")
    ref1 = st.text_input("Référente 1 *", placeholder="Nom de l'entreprise")
    ref2 = st.text_input("Référente 2 *", placeholder="Nom de l'entreprise")
    ref3 = st.text_input("Référente 3 (optionnel)", placeholder="Nom de l'entreprise")

    st.divider()

    st.subheader("Critères de qualification")
    criteria = st.text_area(
        "Ce qui fait un bon lead pour toi",
        placeholder="ex: activité internationale hors zone euro, import de matières premières...",
        height=80
    )

    st.write("")

    if st.session_state.free_run_used:
        st.warning("Tu as utilisé ton run gratuit.")
        # 💳 STRIPE LINK ICI
        st.link_button("Passer en Starter — 29€/mois →", "STRIPE_LINK", use_container_width=True)
    else:
        st.caption("✅ 1 run gratuit — aucune carte requise")
        if st.button("Lancer la recherche →", type="primary", use_container_width=True):
            if not sector or not ref1:
                st.error("Remplis au minimum le secteur et une entreprise référente.")
            else:
                refs = [r for r in [ref1, ref2, ref3] if r.strip()]
                st.session_state.icp = {
                    "sector": sector,
                    "revenue_min": revenue_min,
                    "revenue_max": revenue_max,
                    "geography": geography,
                    "references": refs,
                    "criteria": criteria
                }
                st.session_state.screen = 2
                st.rerun()


# ─── SCREEN 2 : PROCESSING ─────────────────────────────────────────────────────
def screen_processing():
    st.title("🎯 Twinlead")
    st.divider()

    refs = st.session_state.icp["references"]
    st.subheader("Analyse en cours")
    st.caption(f"{len(refs)} référente(s) · Génération des leads clones...")
    st.write("")

    progress = st.progress(0)
    status = st.empty()

    steps = [
        (0.25, "Analyse des patterns sectoriels..."),
        (0.55, "Identification des signaux de qualification..."),
        (0.80, "Génération des leads clones..."),
        (1.00, "Scoring et justification..."),
    ]

    for val, label in steps:
        status.caption(f"⏳ {label}")
        progress.progress(val)
        time.sleep(1.2)

    # ── APPEL CLAUDE API (décommenter quand la logique agent est prête) ──
    # client = anthropic.Anthropic(api_key=st.secrets["ANTHROPIC_API_KEY"])
    # response = client.messages.create(model="claude-sonnet-4-20250514", max_tokens=1000, messages=[...])

    icp = st.session_state.icp
    mock_leads = [
        {"Entreprise": "ACME Import SAS", "Secteur": icp["sector"], "CA estimé": f"{icp['revenue_min']+2}M€", "Score": "94/100", "Justification": "Export UK + USA actif, hors zone euro"},
        {"Entreprise": "GlobalTrade France", "Secteur": icp["sector"], "CA estimé": f"{icp['revenue_min']+5}M€", "Score": "88/100", "Justification": "Facturation multi-devises, partenaires Asie"},
        {"Entreprise": "NégoTech Lyon", "Secteur": icp["sector"], "CA estimé": f"{icp['revenue_min']+3}M€", "Score": "81/100", "Justification": "Import matières premières, flux USD/GBP"},
    ]

    st.session_state.leads = mock_leads
    st.session_state.free_run_used = True
    status.caption("✅ Analyse terminée")
    time.sleep(0.6)
    st.session_state.screen = 3
    st.rerun()


# ─── SCREEN 3 : RÉSULTATS ──────────────────────────────────────────────────────
def screen_results():
    st.title("🎯 Twinlead")
    st.divider()

    leads = st.session_state.leads
    icp = st.session_state.icp
    st.subheader(f"✅ {len(leads)} leads qualifiés")
    st.caption(f"Secteur : {icp.get('sector')} · Référentes : {', '.join(icp.get('references', []))}")

    df = pd.DataFrame(leads)
    st.dataframe(df, use_container_width=True, hide_index=True)

    st.write("")

    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button("📥 Exporter en CSV", csv, "twinlead_leads.csv", "text/csv", use_container_width=True)

    st.divider()

    # 💳 STRIPE LINK ICI
    st.info("Run gratuit utilisé. Passe en Starter pour 10 runs/mois.")
    st.link_button("Démarrer Starter — 29€/mois →", "STRIPE_LINK", use_container_width=True)

    st.write("")
    if st.button("← Nouvelle recherche", use_container_width=True):
        st.session_state.screen = 1
        st.session_state.leads = []
        st.rerun()


# ─── ROUTER ────────────────────────────────────────────────────────────────────
if st.session_state.screen == 1:
    screen_config()
elif st.session_state.screen == 2:
    screen_processing()
elif st.session_state.screen == 3:
    screen_results()

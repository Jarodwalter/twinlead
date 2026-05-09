import streamlit as st
import anthropic
import pandas as pd
import time

# ─── CONFIG ────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Twinlead",
    page_icon="🎯",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Hide Streamlit default menu for cleaner look
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .stDeployButton {display:none;}
    </style>
""", unsafe_allow_html=True)

# ─── SESSION STATE INIT ─────────────────────────────────────────────────────────
if "screen" not in st.session_state:
    st.session_state.screen = 1
if "free_run_used" not in st.session_state:
    st.session_state.free_run_used = False
if "leads" not in st.session_state:
    st.session_state.leads = []
if "icp" not in st.session_state:
    st.session_state.icp = {}


# ─── SCREEN 1 : CONFIGURATION ICP ──────────────────────────────────────────────
def screen_config():
    st.title("🎯 Twinlead")
    st.caption("Trouve les clones de tes meilleurs clients. Automatiquement.")
    st.divider()

    # ICP
    st.subheader("Ton ICP")
    sector = st.text_input("Secteur cible", placeholder="ex: Import/Export, Manufacturing, Logistique")
    col1, col2 = st.columns(2)
    with col1:
        revenue_min = st.number_input("CA min (M€)", min_value=0, value=1)
    with col2:
        revenue_max = st.number_input("CA max (M€)", min_value=0, value=15)
    geography = st.text_input("Zone géographique", placeholder="ex: France, Île-de-France, DACH")

    st.divider()

    # Entreprises référentes
    st.subheader("Tes entreprises référentes")
    st.caption("2 à 3 clients que tu sais être de bons clients")
    ref1 = st.text_input("Référente 1 *", placeholder="Nom de l'entreprise")
    ref2 = st.text_input("Référente 2 *", placeholder="Nom de l'entreprise")
    ref3 = st.text_input("Référente 3 (optionnel)", placeholder="Nom de l'entreprise")

    st.divider()

    # Critères spécifiques
    st.subheader("Critères de qualification")
    criteria = st.text_area(
        "Ce qui fait un bon lead pour toi",
        placeholder="ex: activité internationale hors zone euro, import de matières premières, filiales à l'étranger...",
        height=80
    )

    st.write("")

    # ── CTA ──
    if st.session_state.free_run_used:
        # 💳 STRIPE LINK ICI — Remplace "STRIPE_LINK" par ton vrai lien Stripe
        st.warning("Tu as utilisé ton run gratuit.")
        st.link_button("🚀 Passer en Starter — 29€/mois", "STRIPE_LINK", use_container_width=True)
    else:
        st.caption("✅ 1 run gratuit — aucune carte requise")
        launch = st.button("Lancer la recherche →", type="primary", use_container_width=True)
        if launch:
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


# ─── SCREEN 2 : TRAITEMENT ─────────────────────────────────────────────────────
def screen_processing():
    st.title("🎯 Twinlead")
    st.divider()

    icp = st.session_state.icp
    refs = icp["references"]
    st.subheader(f"Analyse de {len(refs)} référente(s)...")
    st.caption("Identification des patterns et génération des leads clones")
    st.write("")

    progress = st.progress(0)
    status = st.empty()

    steps = [
        (0.25, "Analyse des patterns sectoriels de tes référentes..."),
        (0.55, "Identification des signaux de qualification..."),
        (0.80, "Génération des leads clones..."),
        (1.00, "Scoring et justification..."),
    ]

    for val, label in steps:
        status.caption(f"⏳ {label}")
        progress.progress(val)
        time.sleep(1.2)

    # ── APPEL CLAUDE API ──
    # Remplace ce bloc mock par l'appel réel une fois la logique agent prête
    # client = anthropic.Anthropic(api_key=st.secrets["ANTHROPIC_API_KEY"])
    # response = client.messages.create(...)

    # Mock leads (à remplacer par la sortie de l'agent)
    mock_leads = [
        {"Entreprise": "ACME Import SAS", "Secteur": icp["sector"], "CA estimé": f"{icp['revenue_min']+2}M€", "Score": "94/100", "Justification": "Export UK + USA actif, taille ICP, hors zone euro"},
        {"Entreprise": "GlobalTrade France", "Secteur": icp["sector"], "CA estimé": f"{icp['revenue_min']+5}M€", "Score": "88/100", "Justification": "Facturation multi-devises, partenaires Asie"},
        {"Entreprise": "NégoTech Lyon", "Secteur": icp["sector"], "CA estimé": f"{icp['revenue_min']+3}M€", "Score": "81/100", "Justification": "Import matières premières, flux USD/GBP"},
    ]

    st.session_state.leads = mock_leads
    st.session_state.free_run_used = True
    status.caption("✅ Analyse terminée")
    time.sleep(0.8)
    st.session_state.screen = 3
    st.rerun()


# ─── SCREEN 3 : RÉSULTATS ──────────────────────────────────────────────────────
def screen_results():
    st.title("🎯 Twinlead")
    st.divider()

    leads = st.session_state.leads
    st.subheader(f"✅ {len(leads)} leads qualifiés trouvés")
    st.caption(f"Secteur : {st.session_state.icp.get('sector')} · Référentes : {', '.join(st.session_state.icp.get('references', []))}")

    df = pd.DataFrame(leads)
    st.dataframe(df, use_container_width=True, hide_index=True)

    st.write("")

    # Export CSV
    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button("📥 Exporter en CSV", csv, "twinlead_leads.csv", "text/csv", use_container_width=True)

    st.divider()

    # ── UPGRADE CTA — 💳 STRIPE LINK ICI ──
    # Remplace "STRIPE_LINK" par ton vrai lien Stripe Payment Link
    st.info("💡 Run gratuit utilisé. Passe en Starter pour 10 runs/mois — 29€.")
    st.link_button("🚀 Démarrer Starter — 29€/mois", "STRIPE_LINK", use_container_width=True)

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

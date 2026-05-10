import anthropic
import json
import streamlit as st

# ─── CLIENT ────────────────────────────────────────────────────────────────────
client = anthropic.Anthropic(api_key=st.secrets["ANTHROPIC_API_KEY"])

# URL MCP Pappers — contient ta clé API Pappers
PAPPERS_MCP_URL = st.secrets["PAPPERS_MCP_URL"]


# ─── PROMPT AGENT ──────────────────────────────────────────────────────────────
def build_prompt(icp: dict, references: list) -> str:
    refs_text = "\n".join([f"- {r}" for r in references])
    return f"""Tu es un expert en prospection B2B. Ta mission : trouver 40 entreprises françaises qui ressemblent aux entreprises référentes ci-dessous.

## ICP cible
- Secteur : {icp['sector']}
- CA : entre {icp['revenue_min']}M€ et {icp['revenue_max']}M€
- Zone géographique : {icp['geography']}
- Critères de qualification : {icp['criteria']}

## Entreprises référentes (tes meilleurs clients)
{refs_text}

## Ta méthode en 4 étapes

### Étape 1 — Analyse des référentes
Pour chaque entreprise référente, utilise Pappers pour analyser :
- Son secteur d'activité exact (code NAF)
- Son objet social
- Sa taille et son CA
Identifie les patterns communs : mots-clés produits, codes NAF, signaux d'activité internationale.

### Étape 2 — Recherche en 3 vagues progressives
**Vague 1** : Recherche avec mots-clés précis des référentes + signaux forts (import, export, international, devises)
**Vague 2** : Recherche avec mots-clés sectoriels + signaux secondaires (négoce, distribution internationale)
**Vague 3** : Recherche élargie par code NAF similaire pour compléter le quota

### Étape 3 — Validation rigoureuse
Pour chaque entreprise trouvée, vérifie via Pappers :
- Statut actif (pas radiée)
- CA dans la fourchette {icp['revenue_min']}M€ - {icp['revenue_max']}M€
- Effectif entre 5 et 200 salariés
- Pas déjà dans la liste (pas de doublon)

### Étape 4 — Scoring et justification
Attribue un score de 0 à 100 à chaque lead selon sa similarité avec les référentes et ses signaux de qualification.

## Format de sortie OBLIGATOIRE
Retourne UNIQUEMENT ce JSON, sans texte autour, sans markdown :
{{
  "leads": [
    {{
      "Entreprise": "Nom de l'entreprise",
      "SIREN": "123456789",
      "NAF": "4669B - Libellé NAF",
      "CA estimé": "5M€",
      "Effectif": "12",
      "Score": "87/100",
      "Justification": "Phrase factuelle courte expliquant pourquoi c'est un bon lead"
    }}
  ]
}}

Génère exactement 40 leads triés par score décroissant. Si tu n'en trouves pas 40, retourne ce que tu as trouvé."""


# ─── ORCHESTRATEUR PRINCIPAL ────────────────────────────────────────────────────
def run_agent(icp: dict, references: list, status_callback=None, progress_callback=None) -> list:
    """
    Lance l'agent Twinlead via Claude API + MCP Pappers.

    Args:
        icp: dict avec sector, revenue_min, revenue_max, geography, criteria
        references: liste de noms d'entreprises référentes
        status_callback: fonction(str) pour mettre à jour le texte de statut
        progress_callback: fonction(float) pour mettre à jour la barre (0 à 1)

    Returns:
        Liste de leads qualifiés (dicts)
    """

    if status_callback:
        status_callback("Connexion à Pappers et analyse des référentes...")
    if progress_callback:
        progress_callback(0.1)

    prompt = build_prompt(icp, references)

    if status_callback:
        status_callback("Recherche en cours — vague 1 (leads qualifiés)...")
    if progress_callback:
        progress_callback(0.3)

    # ── Appel Claude API avec MCP Pappers attaché ──
    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=8000,
        mcp_servers=[
            {
                "type": "url",
                "url": PAPPERS_MCP_URL,
                "name": "pappers"
            }
        ],
        messages=[
            {"role": "user", "content": prompt}
        ]
    )

    if status_callback:
        status_callback("Scoring et justification des leads...")
    if progress_callback:
        progress_callback(0.85)

    # ── Extraction du JSON depuis la réponse ──
    leads = []
    for block in response.content:
        if block.type == "text":
            text = block.text.strip()
            # Nettoyage si Claude ajoute des backticks
            text = text.replace("```json", "").replace("```", "").strip()
            try:
                data = json.loads(text)
                leads = data.get("leads", [])
                break
            except json.JSONDecodeError:
                # Tentative d'extraction si du texte parasite entoure le JSON
                import re
                match = re.search(r'\{.*\}', text, re.DOTALL)
                if match:
                    try:
                        data = json.loads(match.group())
                        leads = data.get("leads", [])
                        break
                    except Exception:
                        pass

    if progress_callback:
        progress_callback(1.0)

    return leads

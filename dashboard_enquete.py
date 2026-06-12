import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="Dashboard – Auto-Évaluation", page_icon="📋", layout="wide")

st.markdown("""
<style>
.main{background:#f5f7fa}
.block-container{padding-top:1.5rem}
.metric-card{background:white;border-radius:12px;padding:18px 22px;
             box-shadow:0 2px 8px rgba(0,0,0,.08);text-align:center}
.metric-card h2{font-size:2.2rem;margin:0}
.metric-card p{margin:0;color:#6b7280;font-size:.9rem}
.stitle{font-size:1.1rem;font-weight:700;color:#1e3a5f;
        border-left:4px solid #1a56db;padding-left:10px;margin:18px 0 10px}
</style>
""", unsafe_allow_html=True)

# ── Chargement ────────────────────────────────────────────────────────────────
# Placez le fichier Excel dans le même dossier que ce script
EXCEL_FILE = "C:/Users/GOUAH/Downloads/ENQUETE_AUTO_EVALUATION_-_all_versions_-_labels_-_2026-06-12-08-58-08.xlsx"

@st.cache_data
def load_data(path):
    return pd.read_excel(path)

df = load_data(EXCEL_FILE)

# ── Mapping colonnes par INDEX (évite tout problème d'apostrophe/encodage) ────
cols = df.columns.tolist()

# Index → colonne
C = {
    "anciennete":   cols[0],   # Ancienneté dans la banque
    "info_date":    cols[1],   # Informé de la date limite
    "communication":cols[2],   # Qualité de la communication
    "delai":        cols[3],   # Délai suffisant
    "comprehension":cols[4],   # Compréhension de la fiche
    "credible":     cols[5],   # Processus crédible
    "difficultes":  cols[6],   # Difficultés au remplissage
    "assistance":   cols[14],  # Assistance
    "charge":       cols[15],  # Charge de travail
    "periode":      cols[16],  # Situation agence/direction
    "crit_com":     cols[36],  # Critères commerciaux réalistes
    "obj_com":      cols[37],  # Objectifs commerciaux réalistes
    "obj_tech":     cols[38],  # Objectifs techniques
    "crit_tech":    cols[39],  # Critères techniques réalistes
    "hesitation":   cols[40],  # Hésitation dépôt
}

CAUSES_RETARD = {
    "Charge de travail":    cols[18],
    "Oubli":                cols[26],
    "Manque de suivi":      cols[20],
    "Difficulté à remplir": cols[21],
    "Manque de motivation": cols[22],
    "Objectifs difficiles": cols[23],
    "Temps insuffisant":    cols[24],
    "Autre":                cols[25],
}

DIFF_REMPLISSAGE = {
    "Compréhension des critères": cols[8],
    "Mesurer les objectifs":      cols[9],
    "Manque d'explication":       cols[10],
    "Difficultés techniques":     cols[11],
    "Évaluer ses performances":   cols[12],
    "Autre":                      cols[13],
}

INDICATEURS = {
    "Comptes ouverts":         cols[29],
    "Mobilisation ressources": cols[30],
    "Production crédits":      cols[31],
    "Taux d'atteinte":         cols[34],
}

FINALITE = {
    "Instructions hiérarchiques": cols[42],
    "Être payé à temps":          cols[43],
    "Obtenir une augmentation":   cols[44],
    "Obtenir une promotion":      cols[45],
    "Suivre mes performances":    cols[46],
    "Éviter les sanctions":       cols[47],
}

COLORS   = px.colors.qualitative.Bold
ORDER_ANC = ["Moins de 1 an", "1 à 3 ans", "3 à 6 ans", "6 à 10 ans", "Plus de 10 ans"]

# ── Sidebar filtre ────────────────────────────────────────────────────────────
st.sidebar.title("🔍 Filtres")
anc_opts = sorted(df[C["anciennete"]].dropna().unique().tolist())
sel_anc  = st.sidebar.multiselect("Ancienneté", anc_opts, default=anc_opts)
dff = df[df[C["anciennete"]].isin(sel_anc)] if sel_anc else df.copy()
st.sidebar.info(f"**{len(dff)}** répondants sur **{len(df)}**")

# ── Helpers ───────────────────────────────────────────────────────────────────
def pct(series, val):
    return round(series.value_counts(normalize=True).get(val, 0) * 100, 1)

def bar_h(series, title, h=360):
    vc = series.value_counts().reset_index()
    vc.columns = ["Réponse", "N"]
    fig = px.bar(vc, y="Réponse", x="N", orientation="h", color="Réponse",
                 color_discrete_sequence=COLORS, height=h, text="N", title=title)
    fig.update_traces(textposition="outside")
    fig.update_layout(showlegend=False, plot_bgcolor="white", paper_bgcolor="white",
                      yaxis_title="", xaxis_title="Répondants", margin=dict(t=45,b=20))
    return fig

def bar_v(series, title, h=340, order=None):
    vc = series.value_counts()
    if order:
        vc = vc.reindex([o for o in order if o in vc.index])
    vc = vc.dropna().reset_index()
    vc.columns = ["Réponse", "N"]
    fig = px.bar(vc, x="Réponse", y="N", color="Réponse",
                 color_discrete_sequence=COLORS, height=h, text="N", title=title)
    fig.update_traces(textposition="outside")
    fig.update_layout(showlegend=False, plot_bgcolor="white", paper_bgcolor="white",
                      xaxis_title="", yaxis_title="Répondants", margin=dict(t=45,b=20))
    return fig

def donut(series, title, h=320):
    vc = series.value_counts().reset_index()
    vc.columns = ["Réponse", "N"]
    fig = px.pie(vc, names="Réponse", values="N", hole=0.38, title=title,
                 color_discrete_sequence=COLORS, height=h)
    fig.update_traces(textposition="inside", textinfo="percent+label")
    fig.update_layout(paper_bgcolor="white", margin=dict(t=45,b=10))
    return fig

def multi_bar(col_dict, title, h=380):
    counts = {lbl: int(dff[col].sum(skipna=True))
              for lbl, col in col_dict.items() if col in dff.columns}
    ser = pd.Series(counts).sort_values()
    fig = px.bar(x=ser.values, y=ser.index, orientation="h", color=ser.index,
                 color_discrete_sequence=COLORS, height=h, text=ser.values, title=title)
    fig.update_traces(textposition="outside")
    fig.update_layout(showlegend=False, plot_bgcolor="white", paper_bgcolor="white",
                      yaxis_title="", xaxis_title="Répondants", margin=dict(t=45,b=20))
    return fig

# ── KPIs ──────────────────────────────────────────────────────────────────────
st.markdown("## 📋 Dashboard – Enquête Auto-Évaluation du Personnel")
st.markdown(f"Analyse de **{len(dff)} répondants** sélectionnés.")
st.divider()

kpis = [
    (pct(dff[C["info_date"]],   "Oui"), "Informés de la date limite",      "#1a56db"),
    (pct(dff[C["delai"]],       "Oui"), "Délai jugé suffisant",             "#0ea5e9"),
    (pct(dff[C["credible"]],    "Oui"), "Processus jugé crédible",          "#10b981"),
    (pct(dff[C["difficultes"]], "Oui"), "Rencontrent des difficultés",      "#f59e0b"),
    (pct(dff[C["hesitation"]],  "Oui"), "Hésitent à déposer la fiche",      "#ef4444"),
]
for col, (val, label, color) in zip(st.columns(5), kpis):
    col.markdown(f'<div class="metric-card"><h2 style="color:{color}">{val}%</h2>'
                 f'<p>{label}</p></div>', unsafe_allow_html=True)

st.markdown("")

# ── Onglets ───────────────────────────────────────────────────────────────────
t1, t2, t3, t4, t5 = st.tabs([
    "👥 Profil", "📬 Communication", "⏰ Retards & Difficultés",
    "🎯 Critères & Objectifs", "💡 Perception & Finalité"
])

# ── TAB 1 ─────────────────────────────────────────────────────────────────────
with t1:
    st.markdown('<div class="stitle">Répartition par ancienneté</div>', unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        st.plotly_chart(bar_v(dff[C["anciennete"]], "Ancienneté dans la banque",
                              order=ORDER_ANC), use_container_width=True)
    with c2:
        st.plotly_chart(donut(dff[C["anciennete"]], "Part par tranche d'ancienneté"),
                        use_container_width=True)
    st.markdown('<div class="stitle">Contexte opérationnel pendant la période d\'évaluation</div>',
                unsafe_allow_html=True)
    st.plotly_chart(bar_h(dff[C["periode"]],
        "Situation de l'agence/direction pendant la période d'évaluation"),
        use_container_width=True)

# ── TAB 2 ─────────────────────────────────────────────────────────────────────
with t2:
    st.markdown('<div class="stitle">Information & Communication</div>', unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        st.plotly_chart(donut(dff[C["info_date"]], "Informé de la date limite ?"),
                        use_container_width=True)
    with c2:
        st.plotly_chart(bar_v(dff[C["communication"]], "Qualité de la communication"),
                        use_container_width=True)
    st.markdown('<div class="stitle">Perception du processus</div>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    with c1:
        st.plotly_chart(donut(dff[C["delai"]], "Délai suffisant ?", h=300),
                        use_container_width=True)
    with c2:
        st.plotly_chart(donut(dff[C["credible"]], "Processus crédible ?", h=300),
                        use_container_width=True)
    with c3:
        st.plotly_chart(bar_v(dff[C["comprehension"]], "Compréhension de la fiche", h=300),
                        use_container_width=True)
    st.markdown('<div class="stitle">Assistance & Charge de travail</div>', unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        ast_data = dff[C["assistance"]].dropna()
        if len(ast_data):
            st.plotly_chart(donut(ast_data, "Bénéficié d'une assistance ?", h=300),
                            use_container_width=True)
    with c2:
        st.plotly_chart(bar_h(dff[C["charge"]],
            "Influence de la charge sur le dépôt tardif", h=300),
            use_container_width=True)

# ── TAB 3 ─────────────────────────────────────────────────────────────────────
with t3:
    st.markdown('<div class="stitle">Causes des retards (choix multiples)</div>',
                unsafe_allow_html=True)
    st.plotly_chart(multi_bar(CAUSES_RETARD, "Principales causes des retards"),
                    use_container_width=True)
    st.markdown('<div class="stitle">Difficultés lors du remplissage</div>',
                unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        st.plotly_chart(donut(dff[C["difficultes"]], "Des difficultés au remplissage ?"),
                        use_container_width=True)
    with c2:
        st.plotly_chart(multi_bar(DIFF_REMPLISSAGE, "Nature des difficultés (choix multiples)"),
                        use_container_width=True)
    st.markdown('<div class="stitle">Analyse croisée : ancienneté × difficultés</div>',
                unsafe_allow_html=True)
    cross = dff.groupby(C["anciennete"])[C["difficultes"]].value_counts(normalize=True).unstack().fillna(0)
    cross = cross.reindex([o for o in ORDER_ANC if o in cross.index])
    if "Oui" in cross.columns:
        fig = px.bar(cross.reset_index(), x=C["anciennete"], y="Oui",
                     title="Taux de difficultés au remplissage par ancienneté",
                     color_discrete_sequence=["#f59e0b"], height=360, text_auto=".0%")
        fig.update_layout(plot_bgcolor="white", paper_bgcolor="white",
                          xaxis_title="", yaxis_title="Part (%)", margin=dict(t=45,b=20))
        st.plotly_chart(fig, use_container_width=True)
    st.markdown('<div class="stitle">Hésitation à déposer la fiche</div>',
                unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        st.plotly_chart(donut(dff[C["hesitation"]],
            "Hésitation si performances < objectifs ?"), use_container_width=True)
    with c2:
        cross2 = dff.groupby(C["anciennete"])[C["hesitation"]].value_counts().unstack().fillna(0)
        cross2 = cross2.reindex([o for o in ORDER_ANC if o in cross2.index])
        fig = px.bar(cross2.reset_index(), x=C["anciennete"],
                     y=[c for c in ["Oui", "Non"] if c in cross2.columns],
                     barmode="group", title="Hésitation par ancienneté",
                     color_discrete_sequence=["#ef4444", "#10b981"], height=360,
                     labels={"value": "Nombre", C["anciennete"]: ""})
        fig.update_layout(plot_bgcolor="white", paper_bgcolor="white", margin=dict(t=45,b=20))
        st.plotly_chart(fig, use_container_width=True)

# ── TAB 4 ─────────────────────────────────────────────────────────────────────
with t4:
    st.markdown('<div class="stitle">Réalisme des objectifs et critères</div>',
                unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        st.plotly_chart(donut(dff[C["crit_com"]], "Critères commerciaux réalistes ?"),
                        use_container_width=True)
    with c2:
        st.plotly_chart(bar_v(dff[C["obj_com"]], "Réalisme des objectifs commerciaux"),
                        use_container_width=True)
    c1, c2 = st.columns(2)
    with c1:
        st.plotly_chart(donut(dff[C["crit_tech"]], "Critères techniques réalistes ?"),
                        use_container_width=True)
    with c2:
        st.plotly_chart(bar_v(dff[C["obj_tech"]], "Objectifs techniques vs travail quotidien"),
                        use_container_width=True)
    st.markdown('<div class="stitle">Indicateurs commerciaux pertinents</div>',
                unsafe_allow_html=True)
    st.plotly_chart(multi_bar(INDICATEURS, "Indicateurs jugés pertinents (choix multiples)"),
                    use_container_width=True)

# ── TAB 5 ─────────────────────────────────────────────────────────────────────
with t5:
    st.markdown('<div class="stitle">Finalité perçue du processus d\'auto-évaluation</div>',
                unsafe_allow_html=True)
    st.plotly_chart(multi_bar(FINALITE,
        "À quoi répond le processus d'auto-évaluation ? (choix multiples)", h=420),
        use_container_width=True)

    st.markdown('<div class="stitle">Radar de satisfaction – indicateurs clés</div>',
                unsafe_allow_html=True)
    scores = {
        "Communication claire":     pct(dff[C["info_date"]],   "Oui"),
        "Délai suffisant":          pct(dff[C["delai"]],        "Oui"),
        "Processus crédible":       pct(dff[C["credible"]],     "Oui"),
        "Pas de difficultés":       100 - pct(dff[C["difficultes"]], "Oui"),
        "Pas d'hésitation":         100 - pct(dff[C["hesitation"]],  "Oui"),
        "Critères comm. réalistes": pct(dff[C["crit_com"]],    "Oui"),
        "Critères tech. réalistes": pct(dff[C["crit_tech"]],   "Oui"),
    }
    cats = list(scores.keys()) + [list(scores.keys())[0]]
    vals = list(scores.values()) + [list(scores.values())[0]]
    fig = go.Figure(go.Scatterpolar(r=vals, theta=cats, fill="toself",
                                    line_color="#1a56db",
                                    fillcolor="rgba(26,86,219,0.18)"))
    fig.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0,100])),
                      title="Radar de satisfaction (%)", showlegend=False,
                      paper_bgcolor="white", height=500, margin=dict(t=60,b=40))
    st.plotly_chart(fig, use_container_width=True)

    st.markdown('<div class="stitle">Tableau récapitulatif</div>', unsafe_allow_html=True)
    recap = pd.DataFrame({"Indicateur": list(scores.keys()),
                          "Score (%)":  list(scores.values())})
    recap["Niveau"] = recap["Score (%)"].apply(
        lambda x: "🟢 Bon" if x >= 75 else ("🟡 Moyen" if x >= 50 else "🔴 Faible"))
    st.dataframe(recap.sort_values("Score (%)", ascending=False).reset_index(drop=True),
                 use_container_width=True, hide_index=True)

st.divider()
st.caption("Dashboard · Enquête Auto-Évaluation du Personnel · 2026")

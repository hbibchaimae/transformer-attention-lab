"""Transformer Attention Lab : démo Streamlit pour une présentation de Master."""
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st

from attention_core import MAX_TOKENS, analyze

st.set_page_config(
    page_title="Attention Lab · Transformers",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
  :root { --ink: #1f3739; --accent: #24615c; --terracotta: #b56c52; }
  .stApp { background: #fbfaf7; color: #1f3739; }
  [data-testid="stSidebar"] { background: #eff1ed; }
  h1, h2, h3 { color: #1f3739 !important; font-family: Georgia, 'Times New Roman', serif; }
  .eyebrow { color: #ad6b51; letter-spacing: .12em; text-transform: uppercase;
              font-size: .77rem; font-weight: 800; margin-bottom: .6rem; }
  .small-note { font-size: .86rem; color: #58706e; line-height: 1.55; }
  .formula { background: #eaf0ed; padding: 14px 16px; border-left: 3px solid #356d67;
             border-radius: 5px; font-size: 1.02rem; }
  [data-testid="stMetric"] { background: #ffffff; border: 1px solid #e4e8e4;
                                padding: 12px 14px; border-radius: 8px; }
  button[kind="primary"] { background-color: #24615c; }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="eyebrow">Deep Learning · Démonstration pédagogique</div>', unsafe_allow_html=True)
st.title("Attention Lab — Interactive Demo")
st.write("Explorez le mécanisme de **Self-Attention** qui se trouve au cœur des Transformers.")
st.info("**Important :** cette application effectue de vrais calculs de matrices, mais ses embeddings et poids sont **synthétiques**. Ce n'est ni GPT ni un Transformer pré-entraîné ; elle sert à visualiser le fonctionnement mathématique.")

with st.sidebar:
    st.header("Paramètres")
    text = st.text_area("Votre phrase", value="Le chat mange une souris", height=92,
                        help=f"Maximum {MAX_TOKENS} tokens pour garder un graphique lisible.")
    mode = st.radio("Type d'attention", ["Encoder · bidirectionnelle", "Decoder · causale"],
                    help="Le masque causal empêche l'accès aux positions futures.")
    heads = st.select_slider("Nombre de têtes", options=[1, 2, 4], value=2)
    seed = st.number_input("Graine des projections", min_value=1, max_value=99999, value=2026, step=1)
    st.divider()
    st.caption("Une même phrase avec la même graine produit la même matrice. Changez un paramètre pour étudier la différence.")

try:
    result = analyze(text, causal=mode.startswith("Decoder"), heads=heads, seed=int(seed))
except (ValueError, TypeError) as error:
    st.error(str(error))
    st.stop()

cols = st.columns(4)
cols[0].metric("Tokens", len(result.tokens))
cols[1].metric("Dimension d_model", result.X.shape[1])
cols[2].metric("Têtes", heads)
cols[3].metric("Attention", "Causale" if result.causal else "Complète")

main_tab, math_tab, cicd_tab = st.tabs(["01 — Explorer l'attention", "02 — Comprendre les calculs", "03 — CI/CD du projet"])

with main_tab:
    st.subheader("La matrice d'attention")
    head_id = st.selectbox("Tête à afficher", range(heads), format_func=lambda x: f"Head {x+1}")
    matrix = result.weights[head_id]
    fig, ax = plt.subplots(figsize=(8, max(3.6, len(result.tokens) * .52 + 1)))
    cmap = plt.get_cmap("YlGn")
    image = ax.imshow(matrix, vmin=0, vmax=1, cmap=cmap, interpolation="nearest")
    ax.set_xticks(range(len(result.tokens)), result.tokens, rotation=35, ha="right")
    ax.set_yticks(range(len(result.tokens)), result.tokens)
    ax.set_xlabel("Key · mot consulté")
    ax.set_ylabel("Query · mot qui regarde")
    for i in range(len(result.tokens)):
        for j in range(len(result.tokens)):
            value = matrix[i, j]
            ax.text(j, i, f"{value:.2f}", ha="center", va="center", fontsize=8,
                    color="white" if value > .48 else "#1f3739")
    ax.set_title("Chaque ligne = distribution d'attention d'un token", pad=14, color="#1f3739")
    fig.colorbar(image, ax=ax, shrink=.72, label="Poids d'attention")
    fig.tight_layout()
    st.pyplot(fig, use_container_width=True)
    plt.close(fig)
    st.caption("Chaque ligne totalise 1. Dans le mode Decoder, les cellules au-dessus de la diagonale sont à zéro.")
    st.subheader("Que regarde un token ?")
    focus_index = st.selectbox("Sélectionnez le token Query", range(len(result.tokens)),
                               format_func=lambda ix: f"{ix+1}. {result.tokens[ix]}")
    frame = pd.DataFrame({"Token Key": result.tokens, "Poids": matrix[focus_index]})
    st.bar_chart(frame.set_index("Token Key"), color="#347770", horizontal=True)
    st.dataframe(frame.style.format({"Poids": "{:.3f}"}), hide_index=True, use_container_width=True)

with math_tab:
    st.subheader("Que signifient Q, K et V ?")
    st.markdown("**Query (Q)** : ce que le token cherche.  **Key (K)** : ce qui permet de comparer les tokens.  **Value (V)** : l'information à combiner.")
    st.latex(r"Attention(Q,K,V)=softmax\left(\frac{QK^T}{\sqrt{d_k}}\right)V")
    st.write("Les embeddings sont transformés par des matrices apprises (ici, des matrices fictives fixes).")
    st.latex(r"Q=XW_Q\qquad K=XW_K\qquad V=XW_V")
    if st.checkbox("Voir les embeddings synthétiques"):
        st.dataframe(pd.DataFrame(result.X, index=result.tokens).round(3), use_container_width=True)
    selected_head = st.selectbox("Tête pour les scores", range(heads), format_func=lambda x: f"Head {x+1}", key="mat_head")
    st.write("**1 — Scores normalisés avant Softmax**")
    scores = result.scores[selected_head]
    scores_display = np.where(np.isneginf(scores), np.nan, scores)
    st.dataframe(pd.DataFrame(scores_display, index=result.tokens, columns=result.tokens).round(3), use_container_width=True)
    st.write("**2 — Softmax : chaque ligne devient une distribution de poids**")
    st.dataframe(pd.DataFrame(result.weights[selected_head], index=result.tokens, columns=result.tokens).round(3), use_container_width=True)
    st.write("**3 — Combinaison pondérée des Values**")
    st.caption("La sortie finale combine les têtes par concaténation, suivie d'une projection W_O.")
    st.dataframe(pd.DataFrame(result.output, index=result.tokens).round(3), use_container_width=True)
    with st.expander("Encoder vs Decoder : à quoi sert le masque ?"):
        st.write("Dans l'Encoder, un token peut regarder les tokens situés avant et après lui. Dans un Decoder autorégressif, un token ne peut pas regarder les positions futures. Le masque remplace les scores des positions interdites par -∞ avant Softmax.")

with cicd_tab:
    st.subheader("Du code local à une application publique")
    st.markdown("""
    **Git** enregistre les versions du projet. **GitHub** héberge le dépôt de code.

    **GitHub Actions** exécute automatiquement des instructions définies dans un fichier YAML.

    **CI — Continuous Integration** : à chaque push, installer les dépendances et lancer les tests.

    **CD — Continuous Deployment** : après la réussite des tests sur main, GitHub Actions met à jour la branche production, utilisée par Streamlit Community Cloud.
    """)
    st.code("Local → GitHub (main) → GitHub Actions → pytest → production → Streamlit Cloud", language="text")
    st.write("Le fichier de configuration est :")
    st.code(".github/workflows/ci-cd.yml", language="text")
    st.success("Le déploiement est automatisé : seules les modifications validées par les tests sont transférées vers la branche production.")

st.divider()
st.caption("Attention Lab · Projet de démonstration Master IA · Les résultats ne représentent pas des connaissances linguistiques apprises.")

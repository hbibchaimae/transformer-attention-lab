# Transformer Attention Lab

Application pédagogique de visualisation de la **Self-Attention** des Transformers, développée avec Python et Streamlit. Les embeddings et les projections sont **synthétiques et reproductibles** : il ne s'agit ni de GPT ni d'un modèle entraîné sur des données linguistiques.

## Démonstration en ligne

- **Version de développement (`main`) :** https://transformer-attention-lab.streamlit.app/
- **Version validée (`production`) :** https://transformer-attention-release.streamlit.app/
- **Dépôt GitHub :** https://github.com/hbibchaimae/transformer-attention-lab
- **Preuve du workflow :** https://github.com/hbibchaimae/transformer-attention-lab/actions/runs/40193976522

## Fonctionnalités

- Saisie d'une phrase et découpage pédagogique en tokens (maximum 12).
- Visualisation des poids de Self-Attention dans une matrice et un graphique.
- Comparaison entre attention bidirectionnelle (Encoder) et causale (Decoder).
- Exploration de 1, 2 ou 4 têtes d'attention.
- Inspection des scores, du Softmax et des représentations de sortie.
- Présentation interactive du pipeline de CI/CD.

## Architecture du projet

| Fichier | Rôle |
|---|---|
| `app.py` | Interface Streamlit |
| `attention_core.py` | Calculs NumPy : embeddings, Q/K/V, Softmax, masque causal, multi-têtes |
| `tests/test_attention_core.py` | 10 tests automatisés avec pytest |
| `.github/workflows/ci-cd.yml` | Workflow GitHub Actions : CI puis promotion vers `production` |
| `requirements.txt` | Dépendances d'exécution |
| `requirements-dev.txt` | Dépendances de développement et de test |
| `.streamlit/config.toml` | Thème de l'interface |
| `Dockerfile` | Configuration Docker disponible à titre optionnel ; non utilisée pour le déploiement Streamlit Cloud actuel |

## Installation locale (Windows, PowerShell)

Depuis le dossier du projet :

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe -m streamlit run app.py
```

Ouvrir ensuite `http://localhost:8501`. Un script `DEMARRER_WINDOWS.bat` est également fourni.

## Workflow CI/CD

**Déclencheurs :** `push` sur `main`, `pull_request` vers `main`, et lancement manuel.

**CI (`tests`) :** récupération du code, installation de Python 3.11 et des dépendances, exécution de `pytest -q`, vérification de la syntaxe avec `compileall`.

**CD (`deploy`) :** le job `deploy` dépend de `tests` via `needs: tests`. Il ne s'exécute que sur `main` hors pull request. Si la CI réussit, GitHub Actions publie le commit validé vers la branche `production` avec `git push origin HEAD:refs/heads/production`.

**Livraison :** Streamlit Community Cloud surveille le dépôt et met à jour l'application liée à la branche `production`. L'application liée à `main` reste une version de développement et peut s'actualiser sans attendre la CI : **la validation préalable concerne la version `production`**.

```text
VS Code -> GitHub/main -> GitHub Actions/CI -> tests OK
                                                 |
                                                 v
                                      GitHub Actions/CD
                                                 |
                                                 v
                                       branche production
                                                 |
                                                 v
                                     Streamlit Community Cloud
```

### Preuve de fonctionnement

Le 25 octobre 2026, l'exécution n°4 (`Update app and CI/CD information`, commit `002cc95`) s'est terminée avec succès : job `CI - Tests Python` réussi, puis job `CD - Promouvoir vers production` réussi. La modification du titre **Attention Lab — Interactive Demo** est ensuite apparue dans l'application publique liée à `production`.

## Sécurité et limites

- Aucun mot de passe, jeton ou clé secrète n'est nécessaire pour la version Streamlit Community Cloud actuelle.
- Ne jamais publier de secrets dans le dépôt public.
- Le workflow utilise un `GITHUB_TOKEN` avec `contents: read` globalement et `contents: write` uniquement pour le job CD.
- Le transfert vers `production` est un push Git ; pour un projet sensible, il conviendrait d'ajouter protection de branche, validations manuelles, revues et contrôles de sécurité.
- Le tokenizer de démonstration ne reproduit pas un tokenizer BPE ; les embeddings sont synthétiques. Les poids affichés ne sont pas des explications linguistiques apprises par un grand modèle.

## Références

- GitHub Actions : https://docs.github.com/en/actions
- Syntaxe des workflows : https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-syntax
- Streamlit Community Cloud : https://docs.streamlit.io/deploy/streamlit-community-cloud
- Article Transformer original : https://arxiv.org/abs/1706.03762

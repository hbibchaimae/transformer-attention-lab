# Transformer Attention Lab — Streamlit, GitHub Actions et Render

## Objectif du projet

Application pédagogique Python pour illustrer le calcul de Self-Attention à l'aide de représentations synthétiques. Ce n'est pas un vrai Transformer entraîné.

Démonstration du pipeline : **VS Code → GitHub → GitHub Actions (CI : tests) → Render (CD : lancement du déploiement)**.

## 1. Lancement local (Windows)

Extraire le dossier dans VS Code, puis double-cliquer sur `DEMARRER_WINDOWS.bat`.

Ou lancer dans PowerShell, depuis le dossier du projet :

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe -m streamlit run app.py
```

Ouvrir `http://localhost:8501`.

## 2. GitHub : envoyer les fichiers

Créer un dépôt GitHub vide, puis dans le dossier du projet :

```bash
git init
git add .
git commit -m "Initialiser Transformer Attention Lab"
git branch -M main
git remote add origin https://github.com/VOTRE-PSEUDO/transformer-attention-lab.git
git push -u origin main
```

Adapter `VOTRE-PSEUDO`. Dans l'onglet `Actions` du dépôt, vérifier que les tests du job CI passent. Le job CD ne déclenche le déploiement que si le hook Render est configuré.

## 3. Render : déployer une application Streamlit gratuitement

1. Aller sur `https://dashboard.render.com/` et créer un compte (GitHub peut être utilisé pour se connecter).
2. Dans **New → Web Service**, choisir **Connect a repository** et sélectionner `transformer-attention-lab`.
3. Choisir le runtime **Docker** (Render peut le détecter via le `Dockerfile`). La commande de démarrage est déjà définie dans ce fichier. Ne pas choisir Static Site.
4. Choisir l'offre **Free** si elle est proposée. Attention : instance limitée, mise en veille après inactivité.
5. Pour la démonstration de **CD pilotée par GitHub Actions**, régler **Auto-Deploy : Off** dans les paramètres du service, pour éviter que Render ne déploie sur chaque push avant la fin des tests.
6. Lancer le premier déploiement depuis le dashboard pour créer et tester le service.
7. Ouvrir **Settings → Deploy Hook**, copier son URL secrète.
8. Dans le dépôt GitHub, aller dans **Settings → Secrets and variables → Actions → New repository secret**.
9. Créer le secret nommé **`RENDER_DEPLOY_HOOK_URL`** et coller l'URL complète. Ne jamais l'afficher dans un fichier public.
10. Faire un `git push` sur `main` ou choisir **Actions → Transformer Lab - CI/CD Render → Run workflow**.
11. Les tests CI doivent réussir avant que GitHub Actions appelle le Deploy Hook.
12. Vérifier ensuite dans **Render → Events / Deploys** que le déploiement **a fini avec succès**. Un résultat vert dans GitHub Actions signifie uniquement que la requête de déploiement a été acceptée.

Votre application sera disponible via une URL `*.onrender.com`.

### Précision sur CI et CD

- **CI** : `actions/checkout`, installation Python, `pytest`, vérification de syntaxe.
- **CD** : déclenchement par GitHub Actions du Deploy Hook Render après succès de la CI. Ce choix prouve l'utilisation explicite de GitHub Actions pour la CD.
- L'option Render **After CI Checks Pass** est une **autre solution** valable pour attendre la CI, mais pour la démonstration demandée on choisit **Auto-Deploy : Off** et on déclenche le hook via GitHub Actions.

### Sécurité

Ne jamais mettre le Deploy Hook en clair dans le code, les captures d'écran ou le dépôt public. Si le lien fuit, le régénérer depuis Render.

### Limites

Render Free peut mettre l'application en veille après 15 minutes d'inactivité ; le redémarrage peut prendre environ une minute. Les ressources sont limitées. Ne pas utiliser comme service de production critique.

## 4. Fichiers importants

| Fichier | Utilité |
|---|---|
| `app.py` | Interface Streamlit |
| `attention_core.py` | Calculs NumPy |
| `tests/test_attention_core.py` | Tests automatisés |
| `.github/workflows/ci-cd.yml` | Workflow CI/CD GitHub Actions avec Render |
| `Dockerfile` | Installation et commande de lancement du serveur |
| `requirements.txt` | Dépendances d'exécution |
| `requirements-dev.txt` | Dépendances des tests |
| `DEMARRER_WINDOWS.bat` | Démarrage simplifié |

### Références officielles

- https://docs.github.com/en/actions
- https://render.com/docs/free
- https://render.com/docs/deploy-hooks
- https://render.com/docs/deploys
- https://docs.streamlit.io/

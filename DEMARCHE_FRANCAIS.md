# Fiche de démonstration : GitHub Actions avec Render

**Git** suit les modifications locales ; **GitHub** héberge le dépôt.

**GitHub Actions** automatise des tâches décrites dans un fichier YAML.

**CI (Continuous Integration)** : installation des dépendances et exécution des tests pour vérifier les modifications.

**CD (Continuous Deployment)** : déclenchement de la publication d'une version après réussite des tests. Dans ce projet, GitHub Actions appelle un **Deploy Hook** de Render.

**Deploy Hook** : URL secrète créée par Render. Une requête HTTP envoyée à cette URL lance un déploiement. Elle est stockée dans **GitHub Secrets**.

**Runner** : machine utilisée temporairement par GitHub Actions pour exécuter les jobs.

**Pourquoi désactiver Auto-Deploy sur Render ?** Pour garantir que le déploiement n'est déclenché que par GitHub Actions après réussite du job CI. Sinon, Render pourrait aussi lancer automatiquement un déploiement dès le push.

**Script oral** : « J'ai développé une application Streamlit illustrant la Self-Attention. J'ai séparé les calculs mathématiques des composants d'interface afin d'écrire des tests. GitHub Actions lance ces tests après chaque push. Si les tests réussissent sur main, le workflow utilise un Deploy Hook privé pour déclencher le déploiement sur Render. Les logs GitHub prouvent le succès des vérifications, puis le dashboard Render confirme la mise en ligne effective. »

**Limite** : cette démonstration utilise des vecteurs synthétiques ; elle ne prétend pas entraîner un grand modèle de langage.

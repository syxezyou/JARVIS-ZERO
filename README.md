<div align="center">
<img src="https://raw.githubusercontent.com/syxezyou/syxezyou/main/assets/syx-galaxy.svg" width="100%" alt="SYX Galaxy"/>

# J.A.R.V.I.S. ZERO — v0.1

**Prototype de recherche et mémoire persistante — SYX**

![Python](https://img.shields.io/badge/Python-3.11%2B-000000?style=for-the-badge&logo=python&logoColor=c084fc)
![FastAPI](https://img.shields.io/badge/FastAPI-000000?style=for-the-badge&logo=fastapi&logoColor=c084fc)
![Status](https://img.shields.io/badge/Statut-Experimental-9333EA?style=for-the-badge)
</div>

## Architecture

- `app.py` : API FastAPI, authentification et mémoire SQLite.
- `core.py` : réseau neuronal NumPy de classement des extraits.
- `search.py` : client SearXNG.
- `static/index.html` : interface web.
- `start.sh` : lancement Uvicorn.
- `.env.example` : exemple de variables, sans secret réel.

## API

| Route | Rôle | Authentification |
| --- | --- | --- |
| GET / | Interface web | Non |
| GET /api/health | État du service | Non |
| POST /api/ask | Question, recherche et extraits sourcés | Bearer token |
| POST /api/feedback | Enregistrer une correction et entraîner le classeur | Bearer token |

Les requêtes POST acceptent du JSON : `question` pour ask, `question` et `correction` pour feedback. Les données sont stockées localement. Ne jamais publier le token ni les données personnelles.


## Important
Ce projet ne dépend d'aucun modèle préentraîné, d'Ollama ou d'API LLM. Son **réseau neuronal entraîné depuis des poids aléatoires** sert à classer les résultats de recherche, **pas** à générer du langage. Les réponses sont des extraits de résultats SearXNG attribués à leurs URL. C'est une première fondation technique, pas une IA conversationnelle équivalente à ChatGPT. Le classement n'a pas encore été entraîné sur un corpus pertinent ; sa qualité initiale est limitée.

## Configuration serveur
- Egg Python 3.11+ sur Pterodactyl, environ 4 Go RAM, port alloué.
- Python, pip et accès Internet sortant depuis le conteneur.
- Une instance SearXNG accessible avec le format JSON activé. Certaines instances publiques refusent les requêtes JSON ou limitent les appels. Pour une installation fiable, héberger SearXNG séparément et configurer `SEARXNG_URL`.
- Pas de GPU nécessaire pour cette version.

## Installation
1. Décompresser l'archive dans `/home/container`.
2. Installer les paquets : `python -m pip install -r requirements.txt` (si egg incompatible, utiliser un egg Python permettant pip).
3. Dans les variables d'environnement Pterodactyl, définir `JARVIS_TOKEN` (secret long et aléatoire), `SEARXNG_URL` (adresse de ton instance) et `SERVER_PORT` (port attribué par Pterodactyl). Le fichier `.env.example` est un exemple : **le programme ne charge pas automatiquement `.env`**.
4. Startup command : `bash start.sh`.
5. Ouvrir `http://IP_DU_SERVEUR:PORT` ; utiliser HTTPS via un reverse proxy avant toute exposition publique. Entrer le token dans l'interface.
6. Tester `GET /api/health`, puis une question.

## Données persistantes
Le dossier `data/` contient `jarvis.sqlite3` et `weights.npz`. Le conserver lors des redéploiements et faire des sauvegardes régulières. Ne pas publier ces fichiers : ils contiennent des échanges et corrections.

## Sécurité / limites
- Protéger l'interface par HTTPS et un token fort. L'interface web est publique sans token mais toutes les opérations de discussion et de correction nécessitent le token.
- Le moteur de recherche interroge uniquement l'API SearXNG configurée ; il ne télécharge pas directement les pages des résultats.
- Les extraits de moteurs peuvent être inexacts, incomplets, biaisés ou obsolètes. Le système **ne vérifie pas encore indépendamment** les affirmations.
- Les corrections utilisateur sont des exemples positifs pour le réseau de classement, mais leur validité n'est pas vérifiée et le réseau n'est pas un modèle de langage.
- Les recherches sont faites **avant chaque réponse** à `/api/ask`. En cas de panne de recherche, le système refuse de répondre sur le fond.
- Le projet est un prototype pédagogique. Prévoir limitation de débit, authentification plus robuste, validation des sources et corpus d'entraînement avant production.

## Suite proposée
1. Collecter un corpus légal de textes et entraîner un tokenizer et un petit modèle de langage causal depuis zéro.
2. Évaluer le modèle sur un jeu de test séparé.
3. Ajouter une étape de vérification croisée et une collecte de données contrôlée, avec consentement et validation.
4. Versionner les modèles et permettre un retour arrière.

## Licence et support

Aucune nouvelle licence attribuée. Les dépendances conservent leurs licences respectives. Les tests d’intégration et la disponibilité de SearXNG restent à vérifier.

---

**Développé par SYX — [@syxezyou](https://github.com/syxezyou)**

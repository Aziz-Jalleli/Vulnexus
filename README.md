# Vulnexus

Plateforme qui analyse les dépendances d'un projet Java ou JavaScript et indique quelles vulnérabilités corriger en premier.

## 1. Vision produit

**Problème.** Une application dépend de dizaines de bibliothèques tierces. Un scanner classique liste des CVE sans priorité, et ne montre ni les dépendances transitives vulnérables ni les bibliothèques abandonnées.

**Solution.** Le développeur téléverse un `pom.xml`, un `package-lock.json` ou un SBOM CycloneDX. La plateforme :

- extrait les dépendances directes et transitives ;
- détecte les vulnérabilités connues (OSV) ;
- prédit le risque de maintenance de chaque bibliothèque (classifieur ML : faible, moyen, élevé) ;
- calcule un score de risque de 0 à 100 par vulnérabilité ;
- produit un rapport avec l'ordre de correction et la version à viser.

**Utilisateurs.** Développeurs Java / JavaScript, responsables techniques et DevSecOps.

**Périmètre du MVP.** Entrées Maven, npm et CycloneDX ; un seul flux d'analyse, de bout en bout. Pas de plateforme SCA complète.

## 2. Architecture initiale

| Bloc | Technologie | Rôle |
|---|---|---|
| Front | Angular | Téléversement, tableau de bord, rapport, graphe de dépendances |
| Back principal | Spring Boot (Java) | Passerelle, analyse du dépôt (orchestration), graphe, intégration OSV, remédiation |
| Service IA | Python, FastAPI | Classifieur de risque de maintenance, score contextuel, explications NLP |
| Base de données | PostgreSQL 16 + pgvector | Projets, scans, dépendances, rapports et embeddings des avis |
| Déploiement | Docker Compose (développement), Kubernetes avec Minikube (cible) | |

Les services communiquent par appels REST synchrones, orchestrés par le service d'analyse du dépôt. Le scan s'exécute en tâche d'arrière-plan et le front interroge son état.

**Rôle de la base vectorielle.** Les descriptions des avis sont transformées en embeddings, stockés dans pgvector. Elles servent à retrouver des avis proches pour ancrer les explications en langage clair, et à la recherche sémantique. C'est un support de la partie NLP ; le composant ML principal est le classifieur de risque de maintenance. Choix argumenté : [docs/choix_base_vectorielle.md](docs/choix_base_vectorielle.md).

## 3. Matrice des responsabilités

R = responsable, C = contribue.

| Domaine | Lead Front | Lead Back | Lead IA | Lead DevOps |
|---|---|---|---|---|
| Interface Angular, tableau de bord | R | C | | |
| Services Spring Boot, passerelle | C | R | | |
| Intégration OSV, deps.dev, extraction des dépendances | | R | C | |
| Jeu de données et classifieur de risque de maintenance | | | R | |
| Service FastAPI, embeddings, base vectorielle | | C | R | C |
| Docker, intégration continue, Kubernetes (Minikube) | | C | | R |
| Tests d'intégration | C | C | C | R |
| Rapport et présentation | C | C | C | C |

| Rôle | Responsable |
|---|---|
| Lead Front | Wissal Mzoughi |
| Lead Back | Imen Elhaj |
| Lead IA | Mohammed Aziz Jallali |
| Lead DevOps | Ahmed Ben Said |

## 4. Démarrage rapide (base vectorielle locale)

Prérequis : Docker et Docker Compose.

**Linux / macOS**

```bash
cp .env.example .env
docker compose up -d          # PostgreSQL 16 + pgvector, schéma créé automatiquement
./scripts/smoke_test.sh       # vérifie l'extension, la distance cosinus et la table
```

**Windows (PowerShell)**

```powershell
Copy-Item .env.example .env
docker compose up -d
bash scripts/smoke_test.sh    # nécessite Git Bash ou WSL
```

Le fichier `.env` n'est jamais versionné : chaque développeur le crée à partir de `.env.example`.

Vérifier l'état : `docker compose ps` (le service `db` doit être `healthy`).
Arrêt : `docker compose down` (ajouter `-v` pour supprimer aussi les données).

> Les scripts de `db/init/` ne s'exécutent qu'à la création du volume. Après les avoir modifiés, il faut repartir de zéro avec `docker compose down -v`.

## 5. Structure du dépôt

```
data/raw/
  advisories/{maven,npm}/   307 avis de sécurité au format OSV
  samples/                  pom.xml, package.json, package-lock.json, sbom.cdx.json
  README.md                 sources, sélection, limites
db/init/001_init.sql        extension pgvector, table advisories, index
docs/choix_base_vectorielle.md
scripts/fetch_advisories.py reconstruit le corpus
scripts/smoke_test.sh       test de la base locale
docker-compose.yml

# à venir
services/                   analyse-depot, graphe-dependances, veille-vulnerabilites,
                            remediation (Spring Boot), risque-ia (FastAPI)
gateway/                    passerelle API
frontend/                   application Angular
k8s/                        manifestes Kubernetes (Minikube)
jenkins/                    pipeline CI/CD
```

## 6. Conventions de contribution

- Personne ne pousse directement sur `main` : tout passe par une pull request relue par au moins un coéquipier.
- Branches : `feature/<sujet>`, `fix/<sujet>`, `devops/<sujet>`.
- Messages de commit : `feat:`, `fix:`, `docs:`, `chore:` suivis d'une courte description.
- Aucun secret dans le dépôt : mots de passe et jetons vont dans `.env` (local) ou dans les Secrets Kubernetes.
- Pas d'archives (`.zip`) ni de gros fichiers binaires dans le dépôt.

## 7. DevOps (en cours)

Chaîne cible : GitHub → Jenkins (build, tests, image Docker, scan Trivy, push) → déploiement sur Kubernetes (Minikube), avec supervision Prometheus et Grafana.

La documentation d'exploitation (lancer la pile, redémarrer, lire les journaux) sera dans `docs/devops.md`.
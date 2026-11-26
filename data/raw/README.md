# Jeu de données brut (`data/raw/`)

Corpus de départ pour l'ingestion. Aucune donnée n'a été modifiée : les fichiers sont des copies telles quelles.

## `advisories/` : avis de sécurité (JSON, format OSV)

| | Maven | npm |
|---|---|---|
| CRITICAL | 40 | 40 |
| HIGH | 40 | 40 |
| MODERATE | 40 | 40 |
| LOW | 40 | 27 |
| **Total** | **160** | **147** |

**307 avis** au total, soit environ 1,3 Mo.

- **Source :** [GitHub Advisory Database](https://github.com/github/advisory-database), dépôt public publié au format OSV. Licence : CC BY 4.0.
- **Sélection :** avis « reviewed », Maven et npm, avec une description non vide et non retirés. Jusqu'à 40 avis par couple (écosystème, sévérité), classés par identifiant. L'avis Log4Shell (`GHSA-jfh8-c2jp-5v3q`) est inclus.
- **Période couverte :** décembre 2021 et année 2022 (limite connue : le corpus ne couvre pas les années récentes).
- **Reproduire :** `python3 scripts/fetch_advisories.py` (clone puis sélectionne les mêmes fichiers).

Champs utilisés par le projet : `id`, `summary`, `details`, `affected[].package`, `affected[].ranges` (versions corrigées), `database_specific.severity`, `published`.

## `samples/` : exemples d'entrées pour le scanner

| Fichier | Origine |
|---|---|
| `package.json` | Écrit à la main : axios 0.21.1, express 4.17.1, lodash 4.17.20 (anciennes versions volontairement) |
| `package-lock.json` | Généré par `npm install --package-lock-only` à partir de `package.json` (53 paquets, directs et transitifs) |
| `sbom.cdx.json` | Généré avec `@cyclonedx/cyclonedx-npm` : SBOM CycloneDX 1.5, 52 composants |
| `pom.xml` | Écrit à la main : Spring Boot 2.5.0, jackson-databind 2.9.8, log4j-core 2.14.1 (anciennes versions volontairement) |

Ces fichiers servent d'exemples de test pour l'extraction des dépendances. Ils ne sont pas à réutiliser dans un vrai projet.

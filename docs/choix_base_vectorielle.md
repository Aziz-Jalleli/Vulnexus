# Choix de la base vectorielle

**Décision : pgvector (extension de PostgreSQL 16).**

## 1. Besoin

Nous stockons des **embeddings de descriptions de vulnérabilités** (avis OSV / GitHub Advisory) pour deux usages :

1. retrouver les avis les plus proches d'une vulnérabilité détectée, afin d'ancrer l'explication en langage clair générée par le service IA (principe RAG) ;
2. permettre une recherche sémantique dans le tableau de bord.

Cette brique est un **support** de la partie NLP. Le composant ML principal du projet reste le classifieur de risque de maintenance, qui n'utilise pas de vecteurs.

**Volume prévu :** quelques milliers à quelques dizaines de milliers de vecteurs (avis Maven et npm). Le corpus de départ en contient 307 (`data/raw/advisories/`).

## 2. Critères

| Critère | Pourquoi il compte ici |
|---|---|
| Filtrage de métadonnées | Chaque requête filtre par écosystème (Maven ou npm), et souvent par sévérité |
| Latence | La recherche s'exécute pendant un scan ; elle ne doit pas ralentir le rapport |
| Simplicité d'orchestration locale | Docker Compose en développement, Minikube ensuite, équipe de 4 sur 7 semaines |

## 3. Comparaison

| Critère | pgvector | Qdrant | Milvus |
|---|---|---|---|
| **Filtrage de métadonnées** | Clause SQL `WHERE` sur des colonnes indexées (B-tree). Pour les index HNSW, le filtre est appliqué après le parcours de l'index : une requête très sélective peut renvoyer moins de résultats que demandé (les *iterative scans* de pgvector 0.8 atténuent ce point) | Filtrage sur *payload* conçu pour la recherche vectorielle, avec un index HNSW tenant compte des filtres | Filtrage sur champs scalaires, expressions riches |
| **Latence** | Suffisante à notre échelle (quelques dizaines de milliers de vecteurs) ; à mesurer (section 5) | Conçu pour la latence faible ; suffisant à notre échelle | Conçu pour de très grands volumes ; surdimensionné ici |
| **Orchestration locale** | **1 conteneur**, déjà nécessaire : PostgreSQL est dans la pile | 1 conteneur supplémentaire, API REST/gRPC dédiée | Mode *standalone* : plusieurs composants (Milvus, etcd, stockage objet), nettement plus lourd |
| **Cohérence avec le reste** | Jointures SQL directes entre avis, scans, dépendances et rapports ; une seule sauvegarde, une seule connexion | Second magasin de données à synchroniser avec PostgreSQL | Idem Qdrant, avec plus de composants |
| **Pods supplémentaires dans Minikube** | 0 (la base existante suffit) | +1 | +3 environ |

## 4. Justification

1. **Une seule base.** PostgreSQL est déjà prévu pour les projets, les scans et les rapports. Ajouter pgvector évite un composant, un déploiement Kubernetes et une synchronisation de données.
2. **Filtrage simple.** Les filtres dont nous avons besoin (écosystème, sévérité, date) sont des colonnes SQL ordinaires, et nous pouvons joindre les résultats aux tables de scan.
3. **Orchestration minimale.** Le fichier `docker-compose.yml` lance une seule image officielle (`pgvector/pgvector:pg16`), et le schéma est créé automatiquement par `db/init/001_init.sql`.
4. **Échelle adaptée.** Nous ne visons pas des millions de vecteurs : les avantages de Qdrant et de Milvus en volume ne nous servent pas ici.

## 5. Limites et plan de validation

- **Les performances ne sont pas encore mesurées.** Aucune valeur de latence n'est annoncée dans ce document. Un test de charge est prévu : 100 requêtes (avec et sans filtre sur l'écosystème et la sévérité) sur le corpus complet, en relevant la latence médiane et le 95e centile, ainsi que le rappel face à une recherche exacte.
- **Risque du filtrage avec HNSW** (section 3) : le test vérifie que les requêtes filtrées renvoient bien le nombre de résultats attendu.
- **Modèle d'embedding** : `sentence-transformers/all-MiniLM-L6-v2` (384 dimensions) est le choix de départ. Si le modèle change, la dimension de la colonne `embedding` change aussi.

## 6. Condition de bascule

Nous passerons à **Qdrant** si le test de validation montre l'un de ces deux cas : le rappel des requêtes filtrées est insuffisant avec pgvector, ou la latence dépasse l'objectif fixé par l'équipe. Le reste de l'architecture n'en serait pas affecté : seul l'accès aux vecteurs est isolé dans le service IA.

#!/usr/bin/env bash
# Vérifie que la base vectorielle tourne et que pgvector répond.
set -euo pipefail
cd "$(dirname "$0")/.."
set -a; source .env; set +a

docker compose exec -T db psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -tA -c \
  "SELECT 'extension: ' || extversion FROM pg_extension WHERE extname='vector';"
docker compose exec -T db psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -tA -c \
  "SELECT 'distance cosinus: ' || ('[1,0,0]'::vector <=> '[0,1,0]'::vector);"
docker compose exec -T db psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -tA -c \
  "SELECT 'table advisories: ' || count(*) || ' lignes' FROM advisories;"
echo "OK"

-- Extension vectorielle
CREATE EXTENSION IF NOT EXISTS vector;

-- Avis de sécurité (format OSV) + leur embedding.
-- Dimension 384 = modèle sentence-transformers/all-MiniLM-L6-v2 (à confirmer en S2).
CREATE TABLE IF NOT EXISTS advisories (
    id          TEXT PRIMARY KEY,          -- ex. GHSA-jfh8-c2jp-5v3q
    ecosystem   TEXT NOT NULL,             -- 'Maven' | 'npm'
    package     TEXT,
    severity    TEXT,                      -- CRITICAL | HIGH | MODERATE | LOW
    summary     TEXT,
    details     TEXT NOT NULL,
    published   TIMESTAMPTZ,
    embedding   vector(384)
);

-- Filtrage sur les métadonnées
CREATE INDEX IF NOT EXISTS idx_advisories_eco_sev ON advisories (ecosystem, severity);

-- Recherche par similarité cosinus (HNSW)
CREATE INDEX IF NOT EXISTS idx_advisories_embedding
    ON advisories USING hnsw (embedding vector_cosine_ops);

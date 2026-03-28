-- Ejecutar una vez en la base (psql o cliente SQL). docker compose: ver ../docker-compose.yml
-- La aplicación también llama a CREATE EXTENSION IF NOT EXISTS vector al primer ingest.

CREATE EXTENSION IF NOT EXISTS vector;

-- La tabla `rag_chunks` la crea el servidor si no existe (dimensión según RAG_EMBEDDING_DIM).

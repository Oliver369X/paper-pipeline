# Construir desde la raíz del monorepo (donde están perplexity-webui-scraper y paper-pipeline):
#   docker build -f paper-pipeline/Dockerfile -t paper-pipeline .
#
# Las credenciales NO van en la imagen: pásalas al ejecutar:
#   docker run --rm -e PERPLEXITY_SESSION_TOKEN -v "%CD%\\mission.md:/app/mission.md" paper-pipeline paper-pipeline mission.md
# o usa docker-compose con env_file: .env (local, no versionado).

FROM python:3.11-slim

WORKDIR /workspace

COPY perplexity-webui-scraper /deps/perplexity-webui-scraper
RUN pip install --no-cache-dir /deps/perplexity-webui-scraper

COPY paper-pipeline /app/paper-pipeline
RUN pip install --no-cache-dir "/app/paper-pipeline[dev]"

WORKDIR /app/paper-pipeline

# Por defecto: tests rápidos sin red ni navegador
CMD ["pytest", "tests", "-q", "-m", "not integration and not e2e"]

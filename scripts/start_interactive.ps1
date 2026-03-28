# Levanta la interfaz visual en el navegador e imprime como usar cada pieza.
# Uso: cd paper-pipeline  ->  .\scripts\start_interactive.ps1

$ErrorActionPreference = "Stop"
$PaperRoot = Split-Path $PSScriptRoot -Parent
$VisualHtml = Join-Path $PaperRoot "visual-flow\index.html"

Write-Host ""
Write-Host "=== Paper pipeline - interaccion manual ===" -ForegroundColor Cyan
Write-Host ""

if (-not (Test-Path $VisualHtml)) {
    Write-Host "No encuentro: $VisualHtml" -ForegroundColor Red
    exit 1
}

Write-Host "[1] Abriendo interfaz visual (3 pestanas)..." -ForegroundColor Green
Start-Process $VisualHtml

Write-Host "[2] Servidor HTTP opcional (otra terminal):" -ForegroundColor Yellow
Write-Host ('    cd "' + $PaperRoot + '\visual-flow"')
Write-Host "    python -m http.server 8765"
Write-Host "    Navegador: puerto 8765"
Write-Host ""

Write-Host "[3] CLI pipeline (venv activado en paper-pipeline):" -ForegroundColor Yellow
Write-Host ('    cd "' + $PaperRoot + '"')
Write-Host "    .\.venv\Scripts\Activate.ps1"
Write-Host "    paper-pipeline mission.md --dry-run"
Write-Host "    paper-pipeline mission.md"
Write-Host ""

Write-Host "[4] Meta-agente (una pasada):" -ForegroundColor Yellow
Write-Host "    paper-meta-loop --output-dir outputs"
Write-Host ""

Write-Host "[5] Watcher (al guardar cursor_turn.md):" -ForegroundColor Yellow
Write-Host "    paper-meta-watch --output-dir outputs"
Write-Host ""

Write-Host "[6] Demo automatica con navegador visible:" -ForegroundColor Yellow
Write-Host "    paper-record-visual --headed"
Write-Host ""
Write-Host "[7] Cursor CLI headless (CURSOR_API_KEY en .env):" -ForegroundColor Yellow
Write-Host "    paper-cursor-agent --mission mission.md --output-dir outputs --dry-run"
Write-Host ""
Write-Host "[8] Bucle reactivo real (Perplexity o Notion o Cursor segun directivas en .md):" -ForegroundColor Yellow
Write-Host "    paper-loop mission.md --output-dir outputs"
Write-Host "    paper-loop mission.md --max-cycles 3 --dry-run"
Write-Host ""

Write-Host "Listo. Cada bloque es independiente." -ForegroundColor Cyan
Write-Host ""

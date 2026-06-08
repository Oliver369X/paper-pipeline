# Export Mermaid sources under docs/assets/*.mmd to docs/assets/generated/*.png
# Requires: npm install -g @mermaid-js/mermaid-cli  (mmdc on PATH)

$ErrorActionPreference = "Stop"
$RepoRoot = Split-Path -Parent $PSScriptRoot
$Assets = Join-Path $RepoRoot "docs\assets"
$OutDir = Join-Path $Assets "generated"
New-Item -ItemType Directory -Force -Path $OutDir | Out-Null

$mmdc = Get-Command mmdc -ErrorAction SilentlyContinue
if (-not $mmdc) {
    Write-Error "mmdc not found. Install: npm install -g @mermaid-js/mermaid-cli"
}

Get-ChildItem -Path $Assets -Filter "*.mmd" | ForEach-Object {
    $in = $_.FullName
    $base = $_.BaseName
    $png = Join-Path $OutDir "$base.png"
    & mmdc -i $in -o $png -b transparent
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
    Write-Host "Wrote $png"
}
Write-Host "Done. Add docs/assets/generated/*.png to .gitignore if you do not commit binaries."

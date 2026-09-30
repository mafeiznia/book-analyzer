# build_release.ps1
# Rebuild BookAnalyzer.exe and clean user-specific data for distribution.

$ErrorActionPreference = "Stop"

Write-Host "Cleaning previous build..." -ForegroundColor Cyan

# Stop any running exe
Get-Process BookAnalyzer -ErrorAction SilentlyContinue | Stop-Process -Force
Start-Sleep -Seconds 2

# Remove old build artifacts
Remove-Item -Recurse -Force dist -ErrorAction SilentlyContinue
Remove-Item -Recurse -Force build -ErrorAction SilentlyContinue
Remove-Item -Force BookAnalyzer.spec -ErrorAction SilentlyContinue

Write-Host "Building with flet pack..." -ForegroundColor Cyan

flet pack app.py `
  --name BookAnalyzer `
  --onedir `
  --icon assets\icon.ico `
  --add-data "assets;assets" `
  --add-data "core\prompts;core\prompts" `
  --hidden-import certifi `
  --hidden-import openai `
  --hidden-import google.generativeai `
  --hidden-import weasyprint `
  --hidden-import ddgs `
  --hidden-import pyperclip `
  --hidden-import markdown `
  --hidden-import lxml `
  --hidden-import bs4 `
  --hidden-import pydantic `
  --hidden-import httpx `
  --hidden-import dotenv `
  --product-name "Book Analyzer" `
  --file-description "Smart Book Analyzer for Translators" `
  --product-version "1.1.0" `
  --file-version "1.1.0.0" `
  --company-name "Mahmoud Aharpour Feiznia" `
  --copyright "Copyright (c) 2026 Mahmoud Aharpour Feiznia"

Write-Host "Cleaning user-specific data from dist..." -ForegroundColor Cyan

# Remove any user data that might have been created
Remove-Item -Force "dist\BookAnalyzer\data\projects.db" -ErrorAction SilentlyContinue
Remove-Item -Force "dist\BookAnalyzer\data\settings.json" -ErrorAction SilentlyContinue
Remove-Item -Force "dist\BookAnalyzer\.env" -ErrorAction SilentlyContinue
Remove-Item -Recurse -Force "dist\BookAnalyzer\output\*" -ErrorAction SilentlyContinue

# Ensure .gitkeep markers so folders stay
New-Item -ItemType File -Path "dist\BookAnalyzer\data\.gitkeep" -Force | Out-Null
New-Item -ItemType File -Path "dist\BookAnalyzer\output\.gitkeep" -Force | Out-Null

Write-Host ""
Write-Host "Build complete and clean!" -ForegroundColor Green
Write-Host "Dist folder: dist\BookAnalyzer\" -ForegroundColor Green
Write-Host "Ready to distribute or package with Inno Setup." -ForegroundColor Green
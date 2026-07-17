<#
.SYNOPSIS
  Launch Claude Code with permission prompts disabled and run /create-statics.

.DESCRIPTION
  The "fully hands-off" entry point for static image ad creatives. Starts an
  INTERACTIVE Claude Code session in --dangerously-skip-permissions (bypass) mode.
  The browser intake form and the copy-approval loop still render normally.

.PARAMETER Format
  Optional static format slug from formats/REGISTRY.md (e.g. static-ad).

.PARAMETER App
  Optional app slug.

.EXAMPLE
  .\create-statics.ps1
  .\create-statics.ps1 static-ad mode-earn
#>
param(
  [string]$Format = "",
  [string]$App = ""
)

Set-Location -LiteralPath $PSScriptRoot

if (-not (Get-Command claude -ErrorAction SilentlyContinue)) {
  Write-Error "The 'claude' CLI was not found on PATH. Install Claude Code or open the project in the desktop/IDE app and type: /create-statics $Format $App"
  exit 1
}

$cmdArgs = "/create-statics $Format $App".TrimEnd()
claude --dangerously-skip-permissions $cmdArgs

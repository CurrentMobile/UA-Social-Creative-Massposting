<#
.SYNOPSIS
  Launch Claude Code in this project with permission prompts disabled and run /create-ugc-video.

.DESCRIPTION
  This is the "fully hands-off" entry point. It starts an INTERACTIVE Claude Code session in
  --dangerously-skip-permissions (bypass) mode so that, after you approve the script, no tool call
  ever prompts for permission. The one-time question form and the script-approval loop still render
  normally -- they are agent prompts, not permission prompts.

  You do not need this launcher to use the command: in any Claude session you can just type
  /create-ugc-video <persona>. The launcher only adds the prompt-free (bypass) session.

.PARAMETER Persona
  Persona slug -- must already exist under assets/_shared/personas/<slug>/ (e.g. retiree-female-poc).

.PARAMETER App
  App slug. Defaults to mode-earn.

.EXAMPLE
  .\create-ugc-video.ps1 retiree-female-poc
  .\create-ugc-video.ps1 student-jake mode-earn
#>
param(
  [Parameter(Mandatory = $true)][string]$Persona,
  [string]$App = "mode-earn"
)

# Always run from the project root so .claude/, .venv/, tools/, and workflows/ resolve.
Set-Location -LiteralPath $PSScriptRoot

if (-not (Get-Command claude -ErrorAction SilentlyContinue)) {
  Write-Error "The 'claude' CLI was not found on PATH. Install Claude Code or open the project in the desktop/IDE app and type: /create-ugc-video $Persona $App"
  exit 1
}

# Seed the slash command as the first prompt; the session stays interactive for the form + approval.
claude --dangerously-skip-permissions "/create-ugc-video $Persona $App"

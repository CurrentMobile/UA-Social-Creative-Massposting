<#
.SYNOPSIS
  Launch Claude Code with permission prompts disabled and run /create-videos.

.DESCRIPTION
  The "fully hands-off" entry point for ANY video format. Starts an INTERACTIVE Claude
  Code session in --dangerously-skip-permissions (bypass) mode so that, after you
  submit the one-shot intake form and approve the script, no tool call ever prompts
  for permission. The browser intake form and the script-approval loop still render
  normally -- they are agent interactions, not permission prompts.

  You do not need this launcher: in any Claude session just type /create-videos
  [format] [persona] [app]. The launcher only adds the prompt-free (bypass) session.

.PARAMETER Format
  Optional format slug from formats/REGISTRY.md (e.g. ugc-single, ranking, lofi-text).
  Omit to pick from the form's format gallery.

.PARAMETER Persona
  Optional persona slug under assets/_shared/personas/<slug>/.

.PARAMETER App
  Optional app slug. Defaults to picking in the form.

.EXAMPLE
  .\create-videos.ps1
  .\create-videos.ps1 ugc-single retiree-female-poc mode-earn
  .\create-videos.ps1 ranking
#>
param(
  [string]$Format = "",
  [string]$Persona = "",
  [string]$App = ""
)

Set-Location -LiteralPath $PSScriptRoot

if (-not (Get-Command claude -ErrorAction SilentlyContinue)) {
  Write-Error "The 'claude' CLI was not found on PATH. Install Claude Code or open the project in the desktop/IDE app and type: /create-videos $Format $Persona $App"
  exit 1
}

$cmdArgs = "/create-videos $Format $Persona $App".TrimEnd()
claude --dangerously-skip-permissions $cmdArgs

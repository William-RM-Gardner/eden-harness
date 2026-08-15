# EDEN — overnight grid runner
#
# Runs every grid cell sequentially, committing and pushing after each one so
# that completed episodes survive a power loss. Native command failures do not
# stop the loop, so a rate-limited family is skipped rather than fatal.
#
# Launch:  .\run-all.ps1

$ErrorActionPreference = 'Continue'
Set-Location -Path $PSScriptRoot

function Invoke-GitSync([string]$msg) {
    # A stale index.lock (VS Code's git integration, Dropbox sync, an
    # interrupted command) would silently break every commit for the rest of
    # the night. Clear it first — nothing else should be using this repo.
    if (Test-Path .git\index.lock) {
        Remove-Item .git\index.lock -Force -ErrorAction SilentlyContinue
    }
    git add -A
    git commit -m $msg
    git push
}

$cells = @(
  @{m='deepseek'; arm='partner';    seed=1},
  @{m='deepseek'; arm='no-partner'; seed=1},
  @{m='deepseek'; arm='partner';    seed=2},
  @{m='deepseek'; arm='no-partner'; seed=2},
  @{m='deepseek'; arm='partner';    seed=3},
  @{m='deepseek'; arm='no-partner'; seed=3},
  @{m='openai';   arm='partner';    seed=1},
  @{m='openai';   arm='no-partner'; seed=1},
  @{m='openai';   arm='partner';    seed=2},
  @{m='openai';   arm='no-partner'; seed=2},
  @{m='openai';   arm='partner';    seed=3},
  @{m='openai';   arm='no-partner'; seed=3}
)

$i = 0
foreach ($c in $cells) {
    $i++
    $label = "$($c.m) $($c.arm) seed $($c.seed)"
    Write-Host ""
    Write-Host "=== [$i/$($cells.Count)] $label ===" -ForegroundColor Cyan
    Write-Host ""

    py run.py --model $($c.m) --arm $($c.arm) --seed $($c.seed) 2>&1 |
        Tee-Object -Append -FilePath "run-all-output.txt"

    Invoke-GitSync "episode: $label"
}

Write-Host ""
Write-Host "ALL CELLS ATTEMPTED" -ForegroundColor Green

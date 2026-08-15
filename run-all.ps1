# EDEN - overnight grid runner
#
# Runs every grid cell sequentially, committing and pushing after each one so
# that completed episodes survive a power loss. Native command failures do not
# stop the loop, so a rate-limited family is skipped rather than fatal.
#
# ASCII only, by design: Windows PowerShell 5.1 reads .ps1 as ANSI unless the
# file carries a BOM, so any non-ASCII character here would be mis-decoded.
#
# Launch:  .\run-all.ps1

$ErrorActionPreference = 'Continue'
Set-Location -Path $PSScriptRoot

# Tee-Object pipes stdout, so Python stops seeing a console and falls back to
# the Windows locale codec (cp1252), which cannot encode the arrows, check
# marks and middots the harness prints. UTF-8 mode forces the issue.
$env:PYTHONUTF8 = '1'
$env:PYTHONIOENCODING = 'utf-8'

# And this makes PowerShell decode the child process output as UTF-8, so the
# transcript file is readable instead of mojibake.
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

# Use the venv Python by full path so the script works no matter which shell
# launches it, activated or not. Bare 'py' is the system Python, which has no
# openai package - that is exactly how the first launch of the night failed.
$python = "C:\Users\willi\eden-venv\Scripts\python.exe"
if (-not (Test-Path $python)) {
    Write-Host "venv python not found at $python - aborting before any API call." -ForegroundColor Red
    exit 1
}

function Invoke-GitSync([string]$msg) {
    # A stale index.lock (VS Code git integration, Dropbox sync, an interrupted
    # command) would silently break every commit for the rest of the night.
    # Clear it first - nothing else should be using this repo.
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

$before = @(Get-ChildItem results\*.jsonl -ErrorAction SilentlyContinue).Count

$i = 0
foreach ($c in $cells) {
    $i++
    $label = "$($c.m) $($c.arm) seed $($c.seed)"
    Write-Host ""
    Write-Host "=== [$i/$($cells.Count)] $label ===" -ForegroundColor Cyan
    Write-Host ""

    & $python run.py --model $($c.m) --arm $($c.arm) --seed $($c.seed) 2>&1 |
        Tee-Object -Append -FilePath "run-all-output.txt"

    Invoke-GitSync "episode: $label"
}

$after = @(Get-ChildItem results\*.jsonl -ErrorAction SilentlyContinue).Count
$new = $after - $before
Write-Host ""
Write-Host "ALL CELLS ATTEMPTED. New episode logs written: $new" -ForegroundColor Green

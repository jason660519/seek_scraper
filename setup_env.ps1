[CmdletBinding()]
param(
    [switch]$Force,
    [switch]$SkipTests
)

$ErrorActionPreference = "Stop"

Write-Host "=== SEEK Job Crawler :: Environment Setup ===" -ForegroundColor Cyan

function Test-Command {
    param([Parameter(Mandatory = $true)][string]$Name)
    return Get-Command $Name -ErrorAction SilentlyContinue
}

function Invoke-Step {
    param(
        [Parameter(Mandatory = $true)][string]$Message,
        [Parameter(Mandatory = $true)][ScriptBlock]$Action
    )

    Write-Host "→ $Message" -ForegroundColor Yellow
    & $Action
    Write-Host "  Done." -ForegroundColor Green
}

$repoRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
Push-Location $repoRoot

try {
    Invoke-Step -Message "Ensuring uv is available" -Action {
        if (-not (Test-Command -Name "uv")) {
            Write-Host "  Installing uv..." -ForegroundColor Cyan
            $installScript = Invoke-RestMethod https://astral.sh/uv/install.ps1
            Invoke-Expression $installScript
        }
        uv --version | Write-Host
    }

    $venvPath = Join-Path $repoRoot ".venv"

    if ($Force -and (Test-Path $venvPath)) {
        Invoke-Step -Message "Removing existing virtual environment" -Action {
            Remove-Item -Path $venvPath -Recurse -Force
        }
    }

    Invoke-Step -Message "Creating or updating virtual environment" -Action {
        if (-not (Test-Path $venvPath)) {
            uv venv --python 3.12
        }
    }

    Invoke-Step -Message "Synchronising Python dependencies (uv.lock)" -Action {
        uv sync --frozen
    }

    Invoke-Step -Message "Ensuring .env is present" -Action {
        $envFile = Join-Path $repoRoot ".env"
        $envExample = Join-Path $repoRoot ".env.example"

        if (-not (Test-Path $envFile) -and (Test-Path $envExample)) {
            Copy-Item -Path $envExample -Destination $envFile
            Write-Host "  Created .env from template. Please review the values." -ForegroundColor DarkCyan
        } else {
            Write-Host "  .env already exists. Skipping." -ForegroundColor DarkCyan
        }
    }

    Invoke-Step -Message "Creating data directories" -Action {
        $paths = @(
            "data",
            "data/raw",
            "data/processed",
            "data/logs",
            "data/cache"
        )

        foreach ($path in $paths) {
            New-Item -ItemType Directory -Force -Path $path | Out-Null
        }
    }

    if (-not $SkipTests) {
        Invoke-Step -Message "Running unit tests" -Action {
            uv run pytest
        }
    } else {
        Write-Host "Skipping unit tests (per user request)." -ForegroundColor DarkYellow
    }
}
finally {
    Pop-Location
}

Write-Host "Environment setup completed successfully." -ForegroundColor Cyan

param(
    [switch]$RecreateVenv
)

$ErrorActionPreference = 'Stop'

if (-not (Get-Command py -ErrorAction SilentlyContinue)) {
    throw 'Python Launcher (py) was not found. Install Python 3.13 from python.org, then run this script again.'
}

if ($RecreateVenv -and (Test-Path '.\venv')) {
    Remove-Item -LiteralPath '.\venv' -Recurse -Force
}

if (-not (Test-Path '.\venv\Scripts\python.exe')) {
    py -3.13 -m venv .venv
}

& .\.venv\Scripts\python.exe -m pip install --upgrade pip
& .\.venv\Scripts\python.exe -m pip install -r requirements.txt
& .\.venv\Scripts\python.exe manage.py check
& .\.venv\Scripts\python.exe manage.py migrate

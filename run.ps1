$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $root

if (Get-Command py -ErrorAction SilentlyContinue) {
  py -3 app.py
}
elseif (Get-Command python -ErrorAction SilentlyContinue) {
  python app.py
}
elseif (Get-Command python3 -ErrorAction SilentlyContinue) {
  python3 app.py
}
else {
  Write-Host "Python is required to run this app. Install from https://www.python.org/downloads/windows/ then run this script again."
  exit 1
}



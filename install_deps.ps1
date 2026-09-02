# Install dependencies into the workspace virtual environment.
# Usage: run this from PowerShell while in the workspace folder.

$scriptRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$activate = Join-Path $scriptRoot 'Scripts\Activate.ps1'

if (Test-Path $activate) {
    Write-Host "Activating venv..."
    & $activate
} else {
    Write-Host "No venv activation script found at $activate" -ForegroundColor Yellow
    Write-Host "Please activate your virtualenv manually before running this script." -ForegroundColor Yellow
}

Write-Host "Upgrading pip, setuptools, wheel..."
python -m pip install --upgrade pip setuptools wheel

Write-Host "Installing requirements from requirements.txt..."
pip install -r (Join-Path $scriptRoot 'requirements.txt')

Write-Host "Done. Verify by running: python -c \"import onnx, onnxruntime; print(onnx.__version__, onnxruntime.__version__)\""

@echo off
REM Install dependencies into the workspace virtual environment (Windows CMD)
SET SCRIPT_DIR=%~dp0
IF EXIST "%SCRIPT_DIR%Scripts\activate.bat" (
  CALL "%SCRIPT_DIR%Scripts\activate.bat"
) ELSE (
  ECHO No venv activation script found. Activate your venv manually.
)

python -m pip install --upgrade pip setuptools wheel
pip install -r "%SCRIPT_DIR%requirements.txt"

ECHO Done. Verify with:
ECHO python -c "import onnx, onnxruntime; print(onnx.__version__, onnxruntime.__version__)"

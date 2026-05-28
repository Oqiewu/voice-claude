@echo off
setlocal
cd /d "%~dp0"

echo === voice-claude: setup + build ===
echo.

if not exist .venv (
    echo [1/3] Creating virtual environment...
    python -m venv .venv
) else (
    echo [1/3] Virtual environment exists, skipping.
)

call .venv\Scripts\activate.bat

echo [2/3] Installing project + dependencies...
pip install --upgrade pip -q
pip install -e . -q
pip install pyinstaller -q

echo [3/3] Building .exe...
pyinstaller --noconfirm --onedir --console --name voice-claude ^
    --collect-all faster_whisper ^
    --collect-all ctranslate2 ^
    --hidden-import sounddevice ^
    src\voice_claude\__main__.py

echo.
if exist dist\voice-claude\voice-claude.exe (
    echo SUCCESS: dist\voice-claude\voice-claude.exe
) else (
    echo FAILED: see errors above.
)
pause

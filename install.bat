@echo off
setlocal enabledelayedexpansion
title voice-claude installer

echo ================================
echo   voice-claude installer
echo ================================
echo.

:: ── Config ───────────────────────────────────────────────────────────────────
set REPO=Oqiewu/voice-claude
set BRANCH=master
set INSTALL_DIR=%LOCALAPPDATA%\voice-claude

:: ── 1. Check Python ──────────────────────────────────────────────────────────
echo [1/5] Checking Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo     Not found. Installing Python 3.12 via winget...
    winget install -e --id Python.Python.3.12 --silent ^
        --accept-package-agreements --accept-source-agreements
    if errorlevel 1 (
        echo.
        echo ERROR: Could not install Python automatically.
        echo Please install Python 3.11+ from https://python.org and re-run.
        pause & exit /b 1
    )
    :: Pick up newly installed python from PATH
    for /f "delims=" %%i in ('where python 2^>nul') do set PYTHON=%%i & goto :python_ok
    echo ERROR: Python installed but not found in PATH. Restart terminal and re-run.
    pause & exit /b 1
) else (
    for /f "delims=" %%i in ('where python') do set PYTHON=%%i & goto :python_ok
)
:python_ok
echo     OK: %PYTHON%

:: ── 2. Download source ───────────────────────────────────────────────────────
echo [2/5] Downloading voice-claude...
set TMP_ZIP=%TEMP%\voice-claude.zip
set TMP_DIR=%TEMP%\voice-claude-src

powershell -NoProfile -Command "[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; Invoke-WebRequest -Uri 'https://github.com/%REPO%/archive/refs/heads/%BRANCH%.zip' -OutFile '%TMP_ZIP%' -UseBasicParsing"
if errorlevel 1 (
    echo ERROR: Download failed. Check internet connection.
    pause & exit /b 1
)

if exist "%TMP_DIR%" rd /s /q "%TMP_DIR%"
powershell -NoProfile -Command "Expand-Archive -Path '%TMP_ZIP%' -DestinationPath '%TMP_DIR%' -Force"
del "%TMP_ZIP%"

:: GitHub zips extract to <repo>-<branch>\ subfolder
set SRC=%TMP_DIR%\voice-claude-%BRANCH%
if not exist "%SRC%\entry.py" (
    echo ERROR: Source not extracted correctly. Expected: %SRC%
    pause & exit /b 1
)

:: ── 3. Virtual environment ───────────────────────────────────────────────────
echo [3/5] Setting up virtual environment...
set VENV=%INSTALL_DIR%\.venv
if not exist "%INSTALL_DIR%" md "%INSTALL_DIR%"
if not exist "%VENV%" "%PYTHON%" -m venv "%VENV%"
set VPYTHON=%VENV%\Scripts\python.exe

:: ── 4. Install deps + build exe ──────────────────────────────────────────────
echo [4/5] Installing dependencies...
set PIP="%VPYTHON%" -m pip install --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org
%PIP% --upgrade pip -q
%PIP% faster-whisper sounddevice numpy pynput pystray Pillow certifi -q
%PIP% pyinstaller -q
%PIP% "%SRC%" -q

echo [5/5] Building voice-claude.exe...
"%VPYTHON%" -m PyInstaller --noconfirm --onedir --noconsole ^
    --name voice-claude ^
    --distpath "%INSTALL_DIR%" ^
    --workpath "%TEMP%\voice-claude-build" ^
    --collect-all faster_whisper ^
    --collect-all ctranslate2 ^
    --collect-all certifi ^
    --hidden-import sounddevice ^
    --hidden-import pystray ^
    --hidden-import PIL ^
    "%SRC%\entry.py"

rd /s /q "%TMP_DIR%" 2>nul

set EXE=%INSTALL_DIR%\voice-claude\voice-claude.exe
if not exist "%EXE%" (
    echo.
    echo ERROR: Build failed. See errors above.
    pause & exit /b 1
)

:: ── Desktop shortcut ─────────────────────────────────────────────────────────
set SHORTCUT=%USERPROFILE%\Desktop\voice-claude.lnk
powershell -NoProfile -Command "$ws = New-Object -ComObject WScript.Shell; $s = $ws.CreateShortcut('%SHORTCUT%'); $s.TargetPath = '%EXE%'; $s.WorkingDirectory = '%INSTALL_DIR%\voice-claude'; $s.Save()"

echo.
echo ================================
echo   Done!
echo   Installed to: %INSTALL_DIR%\voice-claude\
echo   Shortcut created on Desktop.
echo   First launch downloads Whisper (~150 MB).
echo ================================
pause

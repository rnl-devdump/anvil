@echo off
setlocal
echo ========================================================
echo Setting up Python Environment and Dependencies
echo ========================================================

REM Check if Python is installed
python --version >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Python is not installed or not added to PATH.
    echo Please install Python and ensure it is in your system PATH.
    pause
    exit /b 1
)

echo [INFO] Python found. Creating virtual environment '.venv'...
python -m venv .venv
IF %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Failed to create virtual environment.
    pause
    exit /b 1
)

echo [INFO] Activating virtual environment...
call .venv\Scripts\activate.bat

echo [INFO] Upgrading pip...
python -m pip install --upgrade pip

echo.
set /p INSTALL_PIP="Do you want to automatically install dependencies from requirements.txt? (Y/N): "
if /i "%INSTALL_PIP%"=="Y" (
    echo [INFO] Installing dependencies from requirements.txt...
    IF EXIST "requirements.txt" (
        pip install -r requirements.txt
        IF %ERRORLEVEL% NEQ 0 (
            echo [ERROR] Failed to install some dependencies.
        )
    ) ELSE (
        echo [WARNING] requirements.txt not found in the current directory.
    )
) else (
    echo [INFO] Skipping pip install. You can install them manually later by running:
    echo     pip install -r requirements.txt
)

echo.
echo ========================================================
echo Note: This project requires Ollama to run local models.
echo ========================================================
set /p INSTALL_OLLAMA="Do you want to download and install the Ollama application manually now? (Y/N): "
if /i "%INSTALL_OLLAMA%"=="Y" (
    echo [INFO] Opening the Ollama download page in your default web browser...
    start https://ollama.com/download
    echo Please download and run the Windows installer from the website.
)

echo.
echo ========================================================
echo [SUCCESS] Setup complete! You can now run the application.
echo To activate the environment manually in the future, run:
echo     .venv\Scripts\activate
echo ========================================================
pause

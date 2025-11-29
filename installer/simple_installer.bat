@echo off
REM MandirSync Simple Installer
REM This is a basic installer that sets up MandirSync

setlocal enabledelayedexpansion

echo ========================================
echo   MandirSync v1.0 - Simple Installer
echo ========================================
echo.

REM Check for admin privileges
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo ERROR: This installer requires Administrator privileges.
    echo Please right-click and select "Run as Administrator"
    pause
    exit /b 1
)

REM Set installation directory
set "INSTALL_DIR=%USERPROFILE%\MandirSync"
set "BACKEND_DIR=%INSTALL_DIR%\backend"
set "FRONTEND_DIR=%INSTALL_DIR%\frontend"

echo Installation directory: %INSTALL_DIR%
echo.

REM Create installation directory
if not exist "%INSTALL_DIR%" (
    echo Creating installation directory...
    mkdir "%INSTALL_DIR%"
)

REM Check Python
echo Checking Python...
python --version >nul 2>&1
if %errorLevel% neq 0 (
    echo [ERROR] Python 3.11+ is required but not found!
    echo Please install Python from https://www.python.org/downloads/
    echo Make sure to check "Add Python to PATH" during installation.
    pause
    exit /b 1
)
python --version
echo [OK] Python found
echo.

REM Check Node.js
echo Checking Node.js...
node --version >nul 2>&1
if %errorLevel% neq 0 (
    echo [ERROR] Node.js 18+ is required but not found!
    echo Please install Node.js from https://nodejs.org/
    pause
    exit /b 1
)
node --version
echo [OK] Node.js found
echo.

REM Check PostgreSQL
echo Checking PostgreSQL...
psql --version >nul 2>&1
if %errorLevel% neq 0 (
    echo [ERROR] PostgreSQL 14+ is required but not found!
    echo Please install PostgreSQL from https://www.postgresql.org/download/windows/
    pause
    exit /b 1
)
psql --version
echo [OK] PostgreSQL found
echo.

REM Copy source files (if they exist in parent directory)
echo Copying source files...
if exist "..\backend" (
    echo Copying backend...
    xcopy /E /I /Y "..\backend\*" "%BACKEND_DIR%\" >nul
    echo [OK] Backend copied
) else (
    echo [WARNING] Backend source not found. Please copy manually.
)

if exist "..\frontend" (
    echo Copying frontend...
    xcopy /E /I /Y "..\frontend\*" "%FRONTEND_DIR%\" >nul
    echo [OK] Frontend copied
) else (
    echo [WARNING] Frontend source not found. Please copy manually.
)

REM Setup Backend
if exist "%BACKEND_DIR%" (
    echo.
    echo Setting up backend...
    cd /d "%BACKEND_DIR%"
    
    REM Create virtual environment
    if not exist "venv" (
        echo Creating virtual environment...
        python -m venv venv
        echo [OK] Virtual environment created
    )
    
    REM Install dependencies
    echo Installing Python dependencies...
    call venv\Scripts\activate.bat
    pip install -r requirements.txt --quiet
    echo [OK] Python dependencies installed
    
    REM Create .env file if it doesn't exist
    if not exist ".env" (
        echo Creating .env file...
        echo Enter PostgreSQL password for 'postgres' user:
        set /p POSTGRES_PASSWORD="Password: "
        
        (
            echo DATABASE_URL=postgresql://postgres:!POSTGRES_PASSWORD!@localhost:5432/temple_db
            echo SECRET_KEY=mandirsync-secret-key-change-in-production
            echo JWT_SECRET_KEY=mandirsync-jwt-secret-key-change-in-production
            echo DEBUG=True
            echo HOST=0.0.0.0
            echo PORT=8000
            echo ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
        ) > .env
        echo [OK] .env file created
    )
)

REM Setup Frontend
if exist "%FRONTEND_DIR%" (
    echo.
    echo Setting up frontend...
    cd /d "%FRONTEND_DIR%"
    
    REM Install dependencies
    if not exist "node_modules" (
        echo Installing Node.js dependencies...
        call npm install --silent
        echo [OK] Node.js dependencies installed
    ) else (
        echo [OK] Frontend dependencies already installed
    )
)

REM Setup Database
echo.
echo Setting up database...
echo Enter PostgreSQL password for 'postgres' user:
set /p POSTGRES_PASSWORD="Password: "

set PGPASSWORD=%POSTGRES_PASSWORD%
psql -U postgres -c "SELECT 1 FROM pg_database WHERE datname='temple_db'" | findstr /C:"1" >nul
if %errorLevel% neq 0 (
    echo Creating database...
    psql -U postgres -c "CREATE DATABASE temple_db;"
    echo [OK] Database created
) else (
    echo [OK] Database already exists
)

REM Create desktop shortcut
echo.
echo Creating desktop shortcut...
set "SHORTCUT=%USERPROFILE%\Desktop\MandirSync.lnk"
set "TARGET=%INSTALL_DIR%\launcher.bat"

powershell -Command "$WshShell = New-Object -ComObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%SHORTCUT%'); $Shortcut.TargetPath = '%TARGET%'; $Shortcut.WorkingDirectory = '%INSTALL_DIR%'; $Shortcut.Description = 'MandirSync - Temple Management System'; $Shortcut.Save()"

if exist "%SHORTCUT%" (
    echo [OK] Desktop shortcut created
) else (
    echo [WARNING] Could not create desktop shortcut
)

REM Create launcher batch file
echo.
echo Creating launcher...
(
    echo @echo off
    echo cd /d "%INSTALL_DIR%"
    echo.
    echo echo Starting MandirSync...
    echo echo.
    echo.
    echo REM Start Backend
    echo start "MandirSync Backend" cmd /k "cd /d %BACKEND_DIR% && venv\Scripts\activate && python -m uvicorn app.main:app --host 0.0.0.0 --port 8000"
    echo timeout /t 3 /nobreak ^>nul
    echo.
    echo REM Start Frontend
    echo start "MandirSync Frontend" cmd /k "cd /d %FRONTEND_DIR% && npm start"
    echo timeout /t 5 /nobreak ^>nul
    echo.
    echo REM Open browser
    echo start http://localhost:3000
    echo.
    echo echo.
    echo echo MandirSync is starting...
    echo echo Backend: http://localhost:8000
    echo echo Frontend: http://localhost:3000
    echo echo.
    echo echo Close this window to stop the servers.
    echo pause
) > "%INSTALL_DIR%\launcher.bat"

echo [OK] Launcher created
echo.

echo ========================================
echo   Installation Complete!
echo ========================================
echo.
echo MandirSync has been installed to:
echo %INSTALL_DIR%
echo.
echo A desktop shortcut has been created.
echo.
echo Double-click the desktop shortcut to start MandirSync.
echo.
pause


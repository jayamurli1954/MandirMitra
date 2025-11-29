# MandirSync Installer Builder
# This script creates a standalone executable installer

param(
    [string]$OutputPath = "MandirSync-Setup.exe",
    [switch]$IncludeData = $false
)

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  MandirSync Installer Builder" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if PyInstaller is installed
Write-Host "Checking PyInstaller..." -ForegroundColor Yellow
try {
    $pyInstallerVersion = python -m PyInstaller --version 2>&1
    Write-Host "✅ PyInstaller found: $pyInstallerVersion" -ForegroundColor Green
}
catch {
    Write-Host "❌ PyInstaller not found. Installing..." -ForegroundColor Red
    pip install pyinstaller
}

# Create build directory
$BuildDir = "build"
$DistDir = "dist"
if (Test-Path $BuildDir) { Remove-Item -Recurse -Force $BuildDir }
if (Test-Path $DistDir) { Remove-Item -Recurse -Force $DistDir }

Write-Host ""
Write-Host "Building installer..." -ForegroundColor Yellow

# Build the launcher executable
python -m PyInstaller `
    --name "MandirSync-Launcher" `
    --onefile `
    --windowed `
    --icon "icon.ico" `
    --add-data "launcher.py;." `
    --hidden-import "subprocess" `
    --hidden-import "json" `
    --hidden-import "webbrowser" `
    --hidden-import "pathlib" `
    --hidden-import "typing" `
    launcher.py

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Build failed!" -ForegroundColor Red
    exit 1
}

Write-Host "✅ Launcher executable created!" -ForegroundColor Green

# Create installer package structure
Write-Host ""
Write-Host "Creating installer package..." -ForegroundColor Yellow

$InstallerDir = "installer_package"
if (Test-Path $InstallerDir) { Remove-Item -Recurse -Force $InstallerDir }
New-Item -ItemType Directory -Path $InstallerDir | Out-Null

# Copy launcher
Copy-Item "$DistDir\MandirSync-Launcher.exe" "$InstallerDir\MandirSync-Launcher.exe"

# Copy installation guide
Copy-Item "INSTALLATION_GUIDE.md" "$InstallerDir\INSTALLATION_GUIDE.md"

# Create setup script
$SetupScript = @"
@echo off
echo ========================================
echo   MandirSync v1.0 - Setup
echo ========================================
echo.
echo This will install MandirSync on your system.
echo.
pause

REM Create installation directory
set INSTALL_DIR=%USERPROFILE%\MandirSync
if not exist "%INSTALL_DIR%" mkdir "%INSTALL_DIR%"

REM Copy files
echo Copying files...
xcopy /E /I /Y "%~dp0\*" "%INSTALL_DIR%"

REM Create desktop shortcut
echo Creating desktop shortcut...
powershell -Command "$WshShell = New-Object -ComObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%USERPROFILE%\Desktop\MandirSync.lnk'); $Shortcut.TargetPath = '%INSTALL_DIR%\MandirSync-Launcher.exe'; $Shortcut.WorkingDirectory = '%INSTALL_DIR%'; $Shortcut.Description = 'MandirSync - Temple Management System'; $Shortcut.Save()"

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
"@

$SetupScript | Out-File -FilePath "$InstallerDir\setup.bat" -Encoding ASCII

# Create README
$Readme = @"
MandirSync v1.0 - Installation Package

INSTALLATION INSTRUCTIONS:
==========================

1. Run setup.bat as Administrator
2. Follow the on-screen instructions
3. Double-click the desktop shortcut to start

For detailed instructions, see INSTALLATION_GUIDE.md

SYSTEM REQUIREMENTS:
====================

- Windows 10 (64-bit) or later
- Python 3.11+ (will be checked during installation)
- Node.js 18+ (will be checked during installation)
- PostgreSQL 14+ (will be checked during installation)
- 5 GB free disk space
- Internet connection (for initial setup)

SUPPORT:
========

See INSTALLATION_GUIDE.md for troubleshooting and support information.

Version: 1.0
Date: 28th November 2025
"@

$Readme | Out-File -FilePath "$InstallerDir\README.txt" -Encoding ASCII

Write-Host "✅ Installer package created!" -ForegroundColor Green
Write-Host ""
Write-Host "Package location: $InstallerDir" -ForegroundColor Cyan
Write-Host ""
Write-Host "To create a single executable installer, use:" -ForegroundColor Yellow
Write-Host "  - Inno Setup (recommended)" -ForegroundColor Yellow
Write-Host "  - NSIS" -ForegroundColor Yellow
Write-Host "  - Or package the installer_package folder as ZIP" -ForegroundColor Yellow
Write-Host ""


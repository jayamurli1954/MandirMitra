# MandirSync Installer

This directory contains files for creating a one-click installer for MandirSync.

## Files

- **launcher.py** - Main launcher script that checks dependencies and starts the application
- **installer.iss** - Inno Setup script for creating Windows installer
- **build_installer.ps1** - PowerShell script to build the installer package
- **INSTALLATION_GUIDE.md** - Complete installation guide for end users
- **README.md** - This file

## Building the Installer

### Option 1: Using Inno Setup (Recommended)

1. **Install Inno Setup**
   - Download from: https://jrsoftware.org/isdl.php
   - Install Inno Setup Compiler

2. **Build the Launcher Executable**
   ```powershell
   cd installer
   pip install pyinstaller
   python -m PyInstaller --onefile --windowed --name MandirSync-Launcher launcher.py
   ```

3. **Create Installer**
   - Open `installer.iss` in Inno Setup Compiler
   - Click "Build" → "Compile"
   - The installer will be created in `dist/MandirSync-Setup.exe`

### Option 2: Using PowerShell Script

```powershell
cd installer
.\build_installer.ps1
```

This will:
- Check for PyInstaller
- Build the launcher executable
- Create an installer package structure
- You can then package it as ZIP or use Inno Setup/NSIS

### Option 3: Manual Package

1. Build launcher:
   ```powershell
   pip install pyinstaller
   python -m PyInstaller --onefile --windowed --name MandirSync-Launcher launcher.py
   ```

2. Create package:
   - Copy `dist/MandirSync-Launcher.exe` to a folder
   - Copy `INSTALLATION_GUIDE.md`
   - Create `README.txt` with instructions
   - Zip the folder

## Installer Features

The installer will:

1. ✅ Check for required dependencies (Python, Node.js, PostgreSQL)
2. ✅ Guide user to install missing dependencies
3. ✅ Setup database automatically
4. ✅ Install all Python and Node.js dependencies
5. ✅ Create desktop shortcut
6. ✅ Launch application automatically
7. ✅ Open dashboard in browser

## Distribution

### Without Data (Fresh Installation)

The installer does NOT include:
- Database data
- User data
- Configuration files

All data will be created fresh on first run.

### Including Source Code

If you want to include backend/frontend source in the installer:

1. Uncomment the Source lines in `installer.iss`:
   ```
   Source: "..\backend\*"; DestDir: "{app}\backend"; ...
   Source: "..\frontend\*"; DestDir: "{app}\frontend"; ...
   ```

2. Update `launcher.py` to use relative paths instead of `INSTALL_DIR`

## Testing

1. Test on a clean Windows machine (VM recommended)
2. Verify all dependencies are checked correctly
3. Test first-time installation flow
4. Test application launch
5. Test desktop shortcut creation

## Notes

- The installer requires Administrator privileges
- Internet connection required for dependency downloads
- First-time setup may take 5-10 minutes
- All dependencies must be installed before application can run

---

**Version:** 1.0  
**Date:** 28th November 2025


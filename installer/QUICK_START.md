# MandirSync - Quick Start Guide for Installer

## Creating the One-Click Installer

### Method 1: Simple Batch Installer (Easiest)

1. **Copy Files to Installer Directory**
   ```powershell
   # The installer expects backend and frontend in parent directory
   # Structure should be:
   # MandirSync/
   #   ├── backend/
   #   ├── frontend/
   #   └── installer/
   #       ├── simple_installer.bat
   #       └── launcher.py
   ```

2. **Run the Installer**
   - Right-click `simple_installer.bat`
   - Select "Run as Administrator"
   - Follow the prompts

3. **Distribute**
   - Package the `installer` folder as ZIP
   - Users extract and run `simple_installer.bat`

### Method 2: PyInstaller + Inno Setup (Professional)

1. **Build Launcher Executable**
   ```powershell
   cd installer
   pip install pyinstaller
   python -m PyInstaller --onefile --windowed --name MandirSync-Launcher launcher.py
   ```

2. **Create Installer with Inno Setup**
   - Install Inno Setup from https://jrsoftware.org/isdl.php
   - Open `installer.iss` in Inno Setup Compiler
   - Build → Compile
   - Output: `dist/MandirSync-Setup.exe`

3. **Distribute**
   - Share `MandirSync-Setup.exe` with users
   - They double-click to install

## What the Installer Does

### First-Time Installation

1. ✅ Checks for Python 3.11+
2. ✅ Checks for Node.js 18+
3. ✅ Checks for PostgreSQL 14+
4. ✅ Prompts user to install missing dependencies
5. ✅ Creates installation directory (`%USERPROFILE%\MandirSync`)
6. ✅ Copies backend and frontend files
7. ✅ Creates Python virtual environment
8. ✅ Installs Python dependencies
9. ✅ Installs Node.js dependencies
10. ✅ Creates database (`temple_db`)
11. ✅ Creates `.env` file with database configuration
12. ✅ Creates desktop shortcut
13. ✅ Launches application

### Subsequent Launches

1. ✅ Starts backend server (port 8000)
2. ✅ Starts frontend server (port 3000)
3. ✅ Opens browser to dashboard

## Important Notes

### No Data Included

The installer does **NOT** include:
- ❌ Database data
- ❌ User accounts
- ❌ Configuration files (except defaults)
- ❌ Uploaded files

All data is created fresh on first run.

### Dependencies Required

Users must have:
- Python 3.11+ (with PATH configured)
- Node.js 18+ (with PATH configured)
- PostgreSQL 14+ (with service running)

The installer will check and guide users to install these.

### Installation Location

Default: `C:\Users\<Username>\MandirSync`

Can be changed during installation (Inno Setup method).

## Testing the Installer

### Test Checklist

1. ✅ Test on clean Windows machine (VM recommended)
2. ✅ Test with all dependencies missing
3. ✅ Test with all dependencies present
4. ✅ Test first-time installation
5. ✅ Test application launch
6. ✅ Test desktop shortcut
7. ✅ Test database creation
8. ✅ Test with existing installation (upgrade scenario)

### Test Scenarios

**Scenario 1: Fresh Windows Machine**
- No Python, Node.js, or PostgreSQL
- Installer should detect and prompt

**Scenario 2: Partial Dependencies**
- Has Python, missing Node.js and PostgreSQL
- Installer should detect missing ones

**Scenario 3: All Dependencies Present**
- Everything installed
- Installer should proceed directly

**Scenario 4: Re-installation**
- Installation already exists
- Should handle gracefully (ask to overwrite or update)

## Distribution

### Option 1: ZIP Package

1. Create folder structure:
   ```
   MandirSync-Installer/
   ├── installer/
   │   ├── simple_installer.bat
   │   ├── launcher.py
   │   └── INSTALLATION_GUIDE.md
   ├── backend/ (source files)
   └── frontend/ (source files)
   ```

2. Zip the folder
3. Share with users
4. Users extract and run `installer/simple_installer.bat`

### Option 2: Single EXE

1. Build with Inno Setup (see Method 2 above)
2. Share `MandirSync-Setup.exe`
3. Users double-click to install

### Option 3: Portable Version

1. Pre-install everything
2. Package as portable folder
3. Users just run launcher (no installation needed)

## Troubleshooting

### Installer Issues

**Problem: "Access Denied"**
- Solution: Run as Administrator

**Problem: "Python not found"**
- Solution: Install Python and add to PATH

**Problem: "Database creation fails"**
- Solution: Check PostgreSQL password and service status

**Problem: "npm install fails"**
- Solution: Check internet connection, try `npm cache clean --force`

### Runtime Issues

**Problem: "Port already in use"**
- Solution: Close other applications using ports 8000/3000

**Problem: "Backend won't start"**
- Solution: Check database connection in `.env` file

**Problem: "Frontend won't start"**
- Solution: Check if backend is running, verify `node_modules` exists

---

**Version:** 1.0  
**Date:** 28th November 2025


# MandirSync Installer - Summary

## Overview

This installer package provides a **one-click installation** solution for MandirSync v1.0 on Windows systems. The installer automatically:

- ✅ Checks for required dependencies
- ✅ Guides users to install missing dependencies
- ✅ Sets up the database
- ✅ Installs all Python and Node.js packages
- ✅ Creates desktop shortcut
- ✅ Launches the application

## Files Created

### Core Files

1. **launcher.py** - Main Python launcher script
   - Checks dependencies (Python, Node.js, PostgreSQL)
   - Sets up database
   - Installs dependencies
   - Starts backend and frontend servers
   - Opens browser to dashboard

2. **simple_installer.bat** - Simple batch file installer
   - Windows batch script for basic installation
   - No compilation needed
   - Easy to modify

3. **installer.iss** - Inno Setup script
   - Professional Windows installer
   - Creates single EXE file
   - Includes uninstaller

4. **build_installer.ps1** - PowerShell build script
   - Automates installer creation
   - Builds launcher executable
   - Creates installer package

### Documentation

5. **INSTALLATION_GUIDE.md** - Complete user guide
   - Step-by-step installation instructions
   - Troubleshooting guide
   - System requirements
   - FAQ

6. **QUICK_START.md** - Developer guide
   - How to build the installer
   - Testing procedures
   - Distribution methods

7. **README.md** - Installer documentation
   - Overview of installer system
   - Building instructions

## Installation Methods

### Method 1: Simple Batch Installer (Recommended for Quick Setup)

**Pros:**
- ✅ No compilation needed
- ✅ Easy to modify
- ✅ Works immediately
- ✅ No special tools required

**Cons:**
- ❌ Less professional appearance
- ❌ Requires source files to be present

**Usage:**
1. Copy `simple_installer.bat` and source files
2. Run as Administrator
3. Follow prompts

### Method 2: Python Launcher + Inno Setup (Professional)

**Pros:**
- ✅ Professional installer (single EXE)
- ✅ Includes uninstaller
- ✅ Better user experience
- ✅ Can include source files

**Cons:**
- ❌ Requires Inno Setup
- ❌ Requires PyInstaller
- ❌ More complex build process

**Usage:**
1. Build launcher: `pyinstaller --onefile launcher.py`
2. Compile installer: Open `installer.iss` in Inno Setup
3. Distribute `MandirSync-Setup.exe`

## Key Features

### Dependency Checking

The installer checks for:
- **Python 3.11+** - Required for backend
- **Node.js 18+** - Required for frontend
- **PostgreSQL 14+** - Required for database

If any are missing, user is prompted to install.

### Automatic Setup

1. **Database Setup**
   - Prompts for PostgreSQL password
   - Creates `temple_db` database
   - Stores credentials securely

2. **Backend Setup**
   - Creates Python virtual environment
   - Installs all dependencies from `requirements.txt`
   - Creates `.env` configuration file

3. **Frontend Setup**
   - Installs all Node.js dependencies
   - Configures proxy settings

4. **Desktop Shortcut**
   - Creates shortcut on desktop
   - Points to launcher executable
   - Easy access for users

### First-Time vs Subsequent Runs

**First Time:**
- Full installation process
- Dependency checking
- Database creation
- Package installation
- Configuration setup

**Subsequent Runs:**
- Quick launch
- Starts servers
- Opens browser
- No setup needed

## Installation Location

**Default:** `C:\Users\<Username>\MandirSync`

**Structure:**
```
MandirSync/
├── backend/
│   ├── venv/
│   ├── app/
│   ├── .env
│   └── requirements.txt
├── frontend/
│   ├── node_modules/
│   ├── src/
│   └── package.json
├── config.json
└── launcher.py (or .exe)
```

## No Data Included

The installer is **completely fresh** - no data included:
- ❌ No database data
- ❌ No user accounts
- ❌ No configuration (except defaults)
- ❌ No uploaded files

All data is created on first run.

## System Requirements

### Minimum
- Windows 10 (64-bit)
- 4 GB RAM
- 5 GB free disk space
- Internet connection (for initial setup)

### Required Software (Installed Separately)
- Python 3.11+
- Node.js 18+
- PostgreSQL 14+

## Distribution

### Option 1: ZIP Package
- Package installer folder + source files
- Users extract and run installer
- Simple and straightforward

### Option 2: Single EXE
- Build with Inno Setup
- Single executable file
- Professional appearance
- Includes uninstaller

### Option 3: Portable Version
- Pre-install everything
- Package as portable folder
- No installation needed
- Just run launcher

## Testing Checklist

Before distributing:

- [ ] Test on clean Windows machine
- [ ] Test with all dependencies missing
- [ ] Test with all dependencies present
- [ ] Test first-time installation
- [ ] Test application launch
- [ ] Test desktop shortcut
- [ ] Test database creation
- [ ] Test with existing installation
- [ ] Test uninstallation (if applicable)
- [ ] Verify no data is included

## Support

For installation issues:
1. Check `INSTALLATION_GUIDE.md`
2. Review error messages
3. Verify all dependencies installed
4. Check system requirements
5. Contact support if needed

## Next Steps

1. **Build the installer** using your preferred method
2. **Test thoroughly** on clean system
3. **Package for distribution**
4. **Share with users**
5. **Provide support** as needed

---

**Version:** 1.0  
**Date:** 28th November 2025  
**Status:** Ready for Use

---

**The installer is ready! Choose your preferred method and start distributing MandirSync!** 🚀


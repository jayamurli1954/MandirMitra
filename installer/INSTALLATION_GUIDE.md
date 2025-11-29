# MandirSync v1.0 - Installation Guide

**Version:** 1.0 (Standalone)  
**Date:** 28th November 2025

---

## Quick Installation (One-Click)

### For End Users

1. **Download the Installer**
   - Download `MandirSync-Setup.exe` from the release package
   - Save it to your desired location (e.g., Desktop or Downloads folder)

2. **Run the Installer**
   - Double-click `MandirSync-Setup.exe`
   - If Windows shows a security warning, click "More info" → "Run anyway"
   - Follow the installation wizard

3. **First-Time Setup**
   - The installer will check for required dependencies
   - If any are missing, you'll be prompted to install them:
     - **Python 3.11+** - Download from https://www.python.org/downloads/
     - **Node.js 18+** - Download from https://nodejs.org/
     - **PostgreSQL 14+** - Download from https://www.postgresql.org/download/windows/
   - After installing dependencies, the installer will continue automatically

4. **Database Setup**
   - You'll be asked to enter your PostgreSQL password
   - This is the password you set when installing PostgreSQL
   - The installer will create the database automatically

5. **Complete Installation**
   - The installer will:
     - Install all Python dependencies
     - Install all Node.js dependencies
     - Create the database
     - Create a desktop shortcut
   - This may take 5-10 minutes depending on your internet speed

6. **Launch Application**
   - After installation, the application will launch automatically
   - A desktop shortcut will be created for future use
   - The dashboard will open in your default browser

---

## Manual Installation (Advanced)

If you prefer to install manually or the installer doesn't work:

### Prerequisites

Install these software in order:

1. **Python 3.11+**
   - Download: https://www.python.org/downloads/
   - During installation, check "Add Python to PATH"
   - Verify: Open Command Prompt, type `python --version`

2. **Node.js 18+**
   - Download: https://nodejs.org/
   - Install the LTS version
   - Verify: Open Command Prompt, type `node --version`

3. **PostgreSQL 14+**
   - Download: https://www.postgresql.org/download/windows/
   - During installation:
     - Remember the password you set for 'postgres' user
     - Note the port (default: 5432)
   - Verify: Open Command Prompt, type `psql --version`

### Installation Steps

1. **Extract Files**
   ```powershell
   # Extract MandirSync to a folder (e.g., C:\MandirSync)
   # The folder structure should be:
   # MandirSync/
   #   ├── backend/
   #   ├── frontend/
   #   └── installer/
   ```

2. **Setup Database**
   ```powershell
   # Open Command Prompt as Administrator
   psql -U postgres
   
   # Enter your PostgreSQL password
   # Then run:
   CREATE DATABASE temple_db;
   \q
   ```

3. **Setup Backend**
   ```powershell
   cd C:\MandirSync\backend
   
   # Create virtual environment
   python -m venv venv
   
   # Activate virtual environment
   venv\Scripts\activate
   
   # Install dependencies
   pip install -r requirements.txt
   
   # Create .env file
   copy .env.example .env
   notepad .env
   ```
   
   **Update .env file:**
   ```
   DATABASE_URL=postgresql://postgres:YOUR_PASSWORD@localhost:5432/temple_db
   SECRET_KEY=your-secret-key-here
   JWT_SECRET_KEY=your-jwt-secret-key-here
   ```

4. **Setup Frontend**
   ```powershell
   cd C:\MandirSync\frontend
   
   # Install dependencies
   npm install
   ```

5. **Run Application**
   ```powershell
   # Terminal 1 - Start Backend
   cd C:\MandirSync\backend
   venv\Scripts\activate
   python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
   
   # Terminal 2 - Start Frontend
   cd C:\MandirSync\frontend
   npm start
   ```

6. **Access Application**
   - Open browser: http://localhost:3000
   - Default login credentials will be provided separately

---

## System Requirements

### Minimum Requirements
- **OS**: Windows 10 (64-bit) or later
- **CPU**: 2 cores (2.0 GHz)
- **RAM**: 4 GB
- **Storage**: 5 GB free space
- **Internet**: Required for initial installation (downloads dependencies)

### Recommended Requirements
- **OS**: Windows 11 (64-bit)
- **CPU**: 4 cores (2.5 GHz or higher)
- **RAM**: 8 GB
- **Storage**: 10 GB free space (SSD preferred)
- **Internet**: Broadband connection

---

## Troubleshooting

### Installation Issues

**Problem: "Python not found"**
- **Solution**: Install Python 3.11+ and make sure to check "Add Python to PATH" during installation
- Verify: Open Command Prompt, type `python --version`

**Problem: "Node.js not found"**
- **Solution**: Install Node.js 18+ from nodejs.org
- Verify: Open Command Prompt, type `node --version`

**Problem: "PostgreSQL connection failed"**
- **Solution**: 
  - Make sure PostgreSQL service is running (Services → PostgreSQL)
  - Check if password is correct
  - Verify PostgreSQL is listening on port 5432

**Problem: "Port already in use"**
- **Solution**: 
  - Close other applications using ports 8000 or 3000
  - Or change ports in configuration files

**Problem: "npm install fails"**
- **Solution**:
  - Check internet connection
  - Try: `npm cache clean --force`
  - Try: `npm install --legacy-peer-deps`

**Problem: "pip install fails"**
- **Solution**:
  - Check internet connection
  - Try: `pip install --upgrade pip`
  - Try: `pip install -r requirements.txt --no-cache-dir`

### Runtime Issues

**Problem: "Backend won't start"**
- **Solution**:
  - Check if database is running
  - Verify .env file has correct database URL
  - Check backend logs for errors

**Problem: "Frontend won't start"**
- **Solution**:
  - Check if backend is running on port 8000
  - Verify node_modules folder exists
  - Check frontend console for errors

**Problem: "Can't connect to database"**
- **Solution**:
  - Verify PostgreSQL service is running
  - Check database password in .env file
  - Verify database 'temple_db' exists

---

## Post-Installation

### First Login

1. Open the application (desktop shortcut or browser: http://localhost:3000)
2. Default credentials:
   - **Email**: admin@temple.com
   - **Password**: (provided separately or set during first run)
3. Change password immediately after first login

### Creating Desktop Shortcut

If desktop shortcut wasn't created automatically:

1. Right-click on `launcher.py` (or the executable)
2. Select "Create shortcut"
3. Drag shortcut to Desktop
4. Rename to "MandirSync"

### Starting the Application

**Option 1: Desktop Shortcut**
- Double-click the MandirSync shortcut on desktop

**Option 2: Command Line**
```powershell
cd C:\MandirSync\installer
python launcher.py
```

**Option 3: Manual Start**
```powershell
# Terminal 1
cd C:\MandirSync\backend
venv\Scripts\activate
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000

# Terminal 2
cd C:\MandirSync\frontend
npm start
```

---

## Uninstallation

### Using Installer (if available)
1. Go to Control Panel → Programs and Features
2. Find "MandirSync"
3. Click "Uninstall"

### Manual Uninstallation
1. Stop all running servers (Ctrl+C in terminals)
2. Delete the installation folder (e.g., `C:\MandirSync`)
3. Delete desktop shortcut
4. (Optional) Delete PostgreSQL database:
   ```powershell
   psql -U postgres
   DROP DATABASE temple_db;
   \q
   ```

---

## Support

### Getting Help

- **Documentation**: See `V1.0_USER_GUIDE.md` for user manual
- **Overview**: See `V1.0_OVERVIEW.md` for system overview
- **Issues**: Contact support team

### Important Notes

- **Data Backup**: Always backup your database before updates
- **Updates**: Do not update manually. Wait for official updates.
- **Security**: Change default passwords immediately
- **Internet**: Required only for initial installation and updates

---

## FAQ

**Q: Do I need internet after installation?**
A: No, the application works offline. Internet is only needed for initial installation and future updates.

**Q: Can I install on multiple computers?**
A: Yes, but each installation will have its own database. For shared data, use a network database setup.

**Q: How do I backup my data?**
A: Backup the PostgreSQL database using pg_dump or use the backup feature in the application.

**Q: Can I change the installation location?**
A: Yes, during installation you can choose a custom location.

**Q: What if I forget my PostgreSQL password?**
A: You'll need to reset it in PostgreSQL or reinstall PostgreSQL (data will be lost).

---

**Version:** 1.0  
**Last Updated:** 28th November 2025

---

**Thank you for using MandirSync!** 🙏


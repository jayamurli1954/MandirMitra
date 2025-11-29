"""
MandirSync Launcher
One-click launcher that checks dependencies and starts the application
"""

import os
import sys
import subprocess
import json
import webbrowser
import time
import shutil
from pathlib import Path
from typing import Optional, Tuple

# Configuration
APP_NAME = "MandirSync"
APP_VERSION = "1.0.0"
INSTALL_DIR = Path(os.path.expanduser("~")) / "MandirSync"
BACKEND_DIR = INSTALL_DIR / "backend"
FRONTEND_DIR = INSTALL_DIR / "frontend"
CONFIG_FILE = INSTALL_DIR / "config.json"
BACKEND_PORT = 8000
FRONTEND_PORT = 3000
FRONTEND_URL = f"http://localhost:{FRONTEND_PORT}"


def check_python() -> Tuple[bool, Optional[str]]:
    """Check if Python is installed"""
    try:
        result = subprocess.run(
            [sys.executable, "--version"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            version = result.stdout.strip()
            # Check if Python 3.11+
            version_num = version.split()[1]
            major, minor = map(int, version_num.split('.')[:2])
            if major >= 3 and minor >= 11:
                return True, version
        return False, None
    except Exception:
        return False, None


def check_nodejs() -> Tuple[bool, Optional[str]]:
    """Check if Node.js is installed"""
    try:
        result = subprocess.run(
            ["node", "--version"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            return True, result.stdout.strip()
        return False, None
    except FileNotFoundError:
        return False, None
    except Exception:
        return False, None


def check_postgresql() -> Tuple[bool, Optional[str]]:
    """Check if PostgreSQL is installed"""
    try:
        result = subprocess.run(
            ["psql", "--version"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            return True, result.stdout.strip()
        return False, None
    except FileNotFoundError:
        return False, None
    except Exception:
        return False, None


def check_postgresql_running() -> bool:
    """Check if PostgreSQL service is running"""
    try:
        result = subprocess.run(
            ["pg_isready", "-U", "postgres"],
            capture_output=True,
            text=True,
            timeout=5
        )
        return result.returncode == 0
    except Exception:
        return False


def install_dependencies():
    """Install all required dependencies"""
    print("\n" + "="*60)
    print(f"Installing {APP_NAME} Dependencies")
    print("="*60 + "\n")
    
    # Check Python
    python_ok, python_version = check_python()
    if not python_ok:
        print("❌ Python 3.11+ not found!")
        print("Please install Python 3.11+ from https://www.python.org/downloads/")
        print("Make sure to check 'Add Python to PATH' during installation.")
        input("\nPress Enter after installing Python to continue...")
        return False
    
    print(f"✅ Python found: {python_version}")
    
    # Check Node.js
    node_ok, node_version = check_nodejs()
    if not node_ok:
        print("❌ Node.js 18+ not found!")
        print("Please install Node.js 18+ from https://nodejs.org/")
        input("\nPress Enter after installing Node.js to continue...")
        return False
    
    print(f"✅ Node.js found: {node_version}")
    
    # Check PostgreSQL
    postgres_ok, postgres_version = check_postgresql()
    if not postgres_ok:
        print("❌ PostgreSQL not found!")
        print("Please install PostgreSQL 14+ from https://www.postgresql.org/download/windows/")
        print("During installation, remember the password you set for 'postgres' user.")
        input("\nPress Enter after installing PostgreSQL to continue...")
        return False
    
    print(f"✅ PostgreSQL found: {postgres_version}")
    
    # Check if PostgreSQL is running
    if not check_postgresql_running():
        print("\n⚠️  PostgreSQL service is not running!")
        print("Starting PostgreSQL service...")
        try:
            subprocess.run(
                ["net", "start", "postgresql-x64-14"],
                check=True,
                timeout=30
            )
            time.sleep(5)
        except Exception as e:
            print(f"❌ Could not start PostgreSQL: {e}")
            print("Please start PostgreSQL service manually from Services.")
            input("\nPress Enter after starting PostgreSQL to continue...")
    
    return True


def setup_database():
    """Setup PostgreSQL database"""
    print("\n" + "="*60)
    print("Setting up Database")
    print("="*60 + "\n")
    
    # Get PostgreSQL password
    print("Enter PostgreSQL password for 'postgres' user:")
    postgres_password = input("Password: ").strip()
    
    if not postgres_password:
        print("❌ Password cannot be empty!")
        return False
    
    # Create database
    try:
        env = os.environ.copy()
        env['PGPASSWORD'] = postgres_password
        
        # Check if database exists
        result = subprocess.run(
            ["psql", "-U", "postgres", "-lqt"],
            env=env,
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if "temple_db" not in result.stdout:
            print("Creating database 'temple_db'...")
            subprocess.run(
                ["psql", "-U", "postgres", "-c", "CREATE DATABASE temple_db;"],
                env=env,
                check=True,
                timeout=10
            )
            print("✅ Database created successfully!")
        else:
            print("✅ Database already exists!")
        
        # Save password to config (encrypted in production)
        config = load_config()
        config['database'] = {
            'host': 'localhost',
            'port': 5432,
            'database': 'temple_db',
            'user': 'postgres',
            'password': postgres_password
        }
        save_config(config)
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Database setup failed: {e}")
        print("Please check your PostgreSQL password and try again.")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def setup_backend():
    """Setup backend environment"""
    print("\n" + "="*60)
    print("Setting up Backend")
    print("="*60 + "\n")
    
    backend_dir = BACKEND_DIR
    
    # Check if backend directory exists
    if not backend_dir.exists():
        print(f"❌ Backend directory not found: {backend_dir}")
        print("Please ensure backend files are in the installation directory.")
        return False
    
    # Check if backend already set up
    venv_dir = backend_dir / "venv"
    if venv_dir.exists():
        print("✅ Backend virtual environment already exists!")
        return True
    
    # Create virtual environment
    print("Creating Python virtual environment...")
    try:
        subprocess.run(
            [sys.executable, "-m", "venv", str(venv_dir)],
            check=True,
            timeout=60
        )
        print("✅ Virtual environment created!")
    except Exception as e:
        print(f"❌ Failed to create virtual environment: {e}")
        return False
    
    # Install dependencies
    print("Installing Python dependencies...")
    pip_exe = venv_dir / "Scripts" / "pip.exe"
    requirements_file = backend_dir / "requirements.txt"
    
    if not requirements_file.exists():
        print("❌ requirements.txt not found!")
        return False
    
    try:
        subprocess.run(
            [str(pip_exe), "install", "-r", str(requirements_file)],
            check=True,
            timeout=600
        )
        print("✅ Python dependencies installed!")
    except Exception as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False
    
    # Create .env file
    config = load_config()
    env_file = backend_dir / ".env"
    if not env_file.exists():
        db_config = config.get('database', {})
        env_content = f"""# MandirSync Backend Configuration
DATABASE_URL=postgresql://{db_config.get('user', 'postgres')}:{db_config.get('password', '')}@{db_config.get('host', 'localhost')}:{db_config.get('port', 5432)}/{db_config.get('database', 'temple_db')}
SECRET_KEY=mandirsync-secret-key-change-in-production
JWT_SECRET_KEY=mandirsync-jwt-secret-key-change-in-production
DEBUG=True
HOST=0.0.0.0
PORT={BACKEND_PORT}
ALLOWED_ORIGINS=http://localhost:{FRONTEND_PORT},http://127.0.0.1:{FRONTEND_PORT}
"""
        env_file.write_text(env_content)
        print("✅ Environment file created!")
    
    return True


def setup_frontend():
    """Setup frontend environment"""
    print("\n" + "="*60)
    print("Setting up Frontend")
    print("="*60 + "\n")
    
    frontend_dir = FRONTEND_DIR
    
    # Check if frontend directory exists
    if not frontend_dir.exists():
        print(f"❌ Frontend directory not found: {frontend_dir}")
        print("Please ensure frontend files are in the installation directory.")
        return False
    
    # Check if node_modules exists
    node_modules = frontend_dir / "node_modules"
    if node_modules.exists():
        print("✅ Frontend dependencies already installed!")
        return True
    
    # Check if package.json exists
    package_json = frontend_dir / "package.json"
    if not package_json.exists():
        print("❌ package.json not found!")
        return False
    
    # Install dependencies
    print("Installing Node.js dependencies...")
    try:
        subprocess.run(
            ["npm", "install"],
            cwd=str(frontend_dir),
            check=True,
            timeout=600
        )
        print("✅ Node.js dependencies installed!")
    except Exception as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False
    
    return True


def load_config() -> dict:
    """Load configuration from file"""
    if CONFIG_FILE.exists():
        try:
            return json.loads(CONFIG_FILE.read_text())
        except Exception:
            return {}
    return {}


def save_config(config: dict):
    """Save configuration to file"""
    CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
    CONFIG_FILE.write_text(json.dumps(config, indent=2))


def create_desktop_shortcut():
    """Create desktop shortcut"""
    try:
        desktop = Path.home() / "Desktop"
        shortcut_path = desktop / f"{APP_NAME}.lnk"
        
        # Get the launcher script path
        launcher_script = Path(__file__).resolve()
        
        # Use PowerShell to create shortcut
        ps_script = f"""
$WshShell = New-Object -ComObject WScript.Shell
$Shortcut = $WshShell.CreateShortcut("{shortcut_path}")
$Shortcut.TargetPath = "{sys.executable}"
$Shortcut.Arguments = '"{launcher_script}"'
$Shortcut.WorkingDirectory = "{INSTALL_DIR}"
$Shortcut.IconLocation = "{sys.executable},0"
$Shortcut.Description = "{APP_NAME} - Temple Management System"
$Shortcut.Save()
"""
        subprocess.run(
            ["powershell", "-Command", ps_script],
            check=True,
            timeout=10
        )
        print(f"✅ Desktop shortcut created: {shortcut_path}")
        return True
    except Exception as e:
        print(f"⚠️  Could not create desktop shortcut: {e}")
        return False


def start_backend():
    """Start backend server"""
    backend_dir = BACKEND_DIR
    venv_python = backend_dir / "venv" / "Scripts" / "python.exe"
    
    if not venv_python.exists():
        print("❌ Backend not set up! Please run setup first.")
        return None
    
    try:
        process = subprocess.Popen(
            [str(venv_python), "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", str(BACKEND_PORT)],
            cwd=str(backend_dir),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        # Wait a bit for server to start
        time.sleep(3)
        
        # Check if process is still running
        if process.poll() is None:
            print(f"✅ Backend server started on port {BACKEND_PORT}")
            return process
        else:
            stdout, stderr = process.communicate()
            print(f"❌ Backend failed to start: {stderr.decode()}")
            return None
    except Exception as e:
        print(f"❌ Error starting backend: {e}")
        return None


def start_frontend():
    """Start frontend server"""
    frontend_dir = FRONTEND_DIR
    
    if not (frontend_dir / "node_modules").exists():
        print("❌ Frontend not set up! Please run setup first.")
        return None
    
    try:
        process = subprocess.Popen(
            ["npm", "start"],
            cwd=str(frontend_dir),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env={**os.environ, "BROWSER": "none"}  # Don't auto-open browser
        )
        
        # Wait for server to start
        time.sleep(10)
        
        # Check if process is still running
        if process.poll() is None:
            print(f"✅ Frontend server started on port {FRONTEND_PORT}")
            return process
        else:
            stdout, stderr = process.communicate()
            print(f"❌ Frontend failed to start: {stderr.decode()}")
            return None
    except Exception as e:
        print(f"❌ Error starting frontend: {e}")
        return None


def open_browser():
    """Open browser to dashboard"""
    time.sleep(2)  # Wait a bit more for servers to be ready
    try:
        webbrowser.open(FRONTEND_URL)
        print(f"✅ Opening {APP_NAME} in browser...")
    except Exception as e:
        print(f"⚠️  Could not open browser automatically: {e}")
        print(f"Please open: {FRONTEND_URL}")


def main():
    """Main launcher function"""
    print("\n" + "="*60)
    print(f"  {APP_NAME} v{APP_VERSION} - Launcher")
    print("="*60 + "\n")
    
    # Check if first-time setup needed
    config = load_config()
    is_setup = config.get('setup_complete', False)
    
    if not is_setup:
        print("🔧 First-time setup detected!")
        print("This will install all dependencies and configure the system.\n")
        
        # Install dependencies
        if not install_dependencies():
            print("\n❌ Dependency installation failed!")
            input("Press Enter to exit...")
            return
        
        # Setup database
        if not setup_database():
            print("\n❌ Database setup failed!")
            input("Press Enter to exit...")
            return
        
        # Setup backend
        if not setup_backend():
            print("\n❌ Backend setup failed!")
            input("Press Enter to exit...")
            return
        
        # Setup frontend
        if not setup_frontend():
            print("\n❌ Frontend setup failed!")
            input("Press Enter to exit...")
            return
        
        # Create desktop shortcut
        create_desktop_shortcut()
        
        # Mark setup as complete
        config['setup_complete'] = True
        save_config(config)
        
        print("\n" + "="*60)
        print("✅ Setup Complete!")
        print("="*60 + "\n")
        print(f"{APP_NAME} is now ready to use!")
        print("A desktop shortcut has been created for easy access.\n")
    
    # Start servers
    print("Starting servers...\n")
    
    backend_process = start_backend()
    if not backend_process:
        print("❌ Failed to start backend!")
        input("Press Enter to exit...")
        return
    
    frontend_process = start_frontend()
    if not frontend_process:
        print("❌ Failed to start frontend!")
        backend_process.terminate()
        input("Press Enter to exit...")
        return
    
    # Open browser
    open_browser()
    
    print("\n" + "="*60)
    print(f"{APP_NAME} is running!")
    print("="*60)
    print(f"Backend: http://localhost:{BACKEND_PORT}")
    print(f"Frontend: {FRONTEND_URL}")
    print("\nPress Ctrl+C to stop the servers...\n")
    
    try:
        # Keep processes running
        backend_process.wait()
        frontend_process.wait()
    except KeyboardInterrupt:
        print("\n\nStopping servers...")
        backend_process.terminate()
        frontend_process.terminate()
        print("✅ Servers stopped. Goodbye!")


if __name__ == "__main__":
    main()


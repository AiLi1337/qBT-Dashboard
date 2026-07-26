#!/usr/bin/env python3
"""
Cross-platform startup script for qBittorrent Management Panel.
Works on both Windows and Linux.
"""

from __future__ import annotations

import os
import sys
import subprocess
import webbrowser
from pathlib import Path


def get_python_command() -> str:
    """Get the appropriate Python command for this platform."""
    # Try common Python commands
    for cmd in ["python3", "python", "py"]:
        try:
            result = subprocess.run(
                [cmd, "--version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0 and "Python" in result.stdout:
                return cmd
        except (FileNotFoundError, subprocess.TimeoutExpired):
            continue
    
    # On Windows, py launcher is often available
    if sys.platform == "win32":
        return "py"
    
    raise RuntimeError("Python not found. Please install Python 3.13 or later.")


def ensure_dependencies():
    """Install required dependencies if not already installed."""
    python = get_python_command()
    required_packages = [
        "fastapi",
        "uvicorn[standard]",
        "jinja2",
        "httpx",
        "APScheduler",
        "bcrypt",
        "cryptography",
        "python-multipart",
    ]
    
    print("Checking dependencies...")
    for package in required_packages:
        try:
            __import__(package.split("[")[0].replace("-", "_"))
        except ImportError:
            print(f"Installing {package}...")
            subprocess.run(
                [python, "-m", "pip", "install", package],
                check=True
            )


def generate_encryption_key():
    """Generate a new Fernet encryption key."""
    from cryptography.fernet import Fernet
    return Fernet.generate_key().decode()


def setup_environment():
    """Set up the environment and configuration."""
    # Get the project root directory
    if getattr(sys, 'frozen', False):
        # Running as compiled executable
        project_root = Path(sys.executable).parent
    else:
        # Running as script
        project_root = Path(__file__).parent.resolve()
    
    # Change to project root
    os.chdir(project_root)
    
    # Check for .env file
    env_file = project_root / ".env"
    if not env_file.exists():
        # Copy from .env.example
        env_example = project_root / ".env.example"
        if env_example.exists():
            print("Creating .env file from template...")
            content = env_example.read_text(encoding="utf-8")
            
            # Generate new encryption key if not present
            if "APP_ENCRYPTION_KEY=replace-with-generated-fernet-key" in content:
                new_key = generate_encryption_key()
                content = content.replace(
                    "APP_ENCRYPTION_KEY=replace-with-generated-fernet-key",
                    f"APP_ENCRYPTION_KEY={new_key}"
                )
            
            env_file.write_text(content, encoding="utf-8")
            print(f"Created .env file at {env_file}")
            print("Please edit the .env file to set secure passwords!")
        else:
            print("Warning: .env.example not found!")
    
    return project_root


def start_server(host: str = "127.0.0.1", port: int = 8000, open_browser: bool = True):
    """Start the uvicorn server."""
    python = get_python_command()
    
    cmd = [python, "-m", "uvicorn", "app.main:app", "--host", host, "--port", str(port), "--reload"]
    
    print(f"\nStarting qBittorrent Management Panel...")
    print(f"Server will be available at: http://{host}:{port}")
    print(f"Press Ctrl+C to stop the server.\n")
    
    if open_browser:
        import threading
        def open_browser_delayed():
            import time
            time.sleep(2)
            webbrowser.open(f"http://{host}:{port}")
        threading.Thread(target=open_browser_delayed, daemon=True).start()
    
    try:
        subprocess.run(cmd, check=True)
    except KeyboardInterrupt:
        print("\n\nServer stopped.")
    except subprocess.CalledProcessError as e:
        print(f"Error starting server: {e}")
        sys.exit(1)


def main():
    """Main entry point."""
    print("=" * 50)
    print("  qBittorrent Management Panel")
    print("  Cross-platform Startup Script")
    print("=" * 50)
    
    # Parse command line arguments
    host = "127.0.0.1"
    port = 8000
    no_browser = False
    
    args = sys.argv[1:]
    i = 0
    while i < len(args):
        if args[i] == "--host" and i + 1 < len(args):
            host = args[i + 1]
            i += 2
        elif args[i] == "--port" and i + 1 < len(args):
            port = int(args[i + 1])
            i += 2
        elif args[i] == "--no-browser":
            no_browser = True
            i += 1
        elif args[i] == "--help":
            print("Usage: python run.py [options]")
            print("Options:")
            print("  --host HOST     Host to bind to (default: 127.0.0.1)")
            print("  --port PORT     Port to bind to (default: 8000)")
            print("  --no-browser    Don't open browser automatically")
            print("  --help          Show this help message")
            sys.exit(0)
        else:
            i += 1
    
    try:
        # Setup environment
        setup_environment()
        
        # Ensure dependencies
        ensure_dependencies()
        
        # Start server
        start_server(host, port, not no_browser)
        
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
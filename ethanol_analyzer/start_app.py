#!/usr/bin/env python3
"""
Start script for Ethanol Analyzer - Alternative to systemd
"""

import subprocess
import sys
import os
from pathlib import Path

def main():
    # Ensure we're in the right directory
    script_dir = Path(__file__).parent
    os.chdir(script_dir)
    
    print("🚀 Starting Ethanol Analyzer...")
    print(f"📁 Working directory: {script_dir}")
    print("🌐 Application will be available at: http://13.233.90.90:8001")
    print("🔗 API Health Check: http://13.233.90.90:8001/api/health")
    
    # Check if virtual environment exists
    venv_path = script_dir / "ethanol_env"
    if not venv_path.exists():
        print("❌ Virtual environment not found. Please run deploy_to_ec2.sh first")
        sys.exit(1)
    
    # Start the server
    python_path = venv_path / "bin" / "python"
    
    try:
        cmd = [
            str(python_path), "-m", "uvicorn",
            "backend.main_gemini:app",
            "--host", "0.0.0.0",
            "--port", "8001",
            "--reload" if "--dev" in sys.argv else "--no-reload"
        ]
        
        print(f"🔄 Running command: {' '.join(cmd)}")
        subprocess.run(cmd, check=True)
        
    except KeyboardInterrupt:
        print("\n👋 Shutting down server...")
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        print("💡 Try running: python3 -m uvicorn backend.main_gemini:app --host 0.0.0.0 --port 8001")
        sys.exit(1)

if __name__ == "__main__":
    main()
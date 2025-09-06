#!/usr/bin/env python3
"""
Start script for Gemini Ethanol Analyzer
For EC2 deployment - serves both API and static files
"""

import subprocess
import sys
import os
from pathlib import Path

def main():
    # Change to the directory containing this script
    script_dir = Path(__file__).parent
    os.chdir(script_dir)
    
    print("🚀 Starting Gemini Ethanol Analyzer...")
    print(f"📁 Working directory: {script_dir}")
    print("🌐 Frontend will be available at: http://your-ec2-ip:8001")
    print("🔗 API endpoints available at: http://your-ec2-ip:8001/api/")
    print("💡 Users need Gemini API key from: https://aistudio.google.com/")
    
    # Start the backend server with static file serving
    try:
        subprocess.run([
            sys.executable, "-m", "uvicorn", 
            "backend.main_gemini:app", 
            "--host", "0.0.0.0", 
            "--port", "8001",
            "--reload" if "--dev" in sys.argv else "--no-reload"
        ], check=True)
    except KeyboardInterrupt:
        print("\n👋 Shutting down server...")
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        print("💡 Make sure you have installed dependencies: pip install -r requirements.txt")
        sys.exit(1)

if __name__ == "__main__":
    main()
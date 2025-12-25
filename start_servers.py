import subprocess
import os
import time
import sys
from pathlib import Path

def run_command(cmd, cwd=None, shell=True):
    """Запуск команды с выводом"""
    process = subprocess.Popen(cmd, cwd=cwd, shell=shell, 
                             stdout=subprocess.PIPE, 
                             stderr=subprocess.PIPE,
                             text=True, bufsize=1,
                             universal_newlines=True)
    return process

print("🚀 Starting Document Builder servers...")
print("=" * 50)

# Backend
print("1. Starting Django backend...")
backend_dir = Path("backend")
os.chdir(backend_dir)
backend = run_command("venv\\Scripts\\python.exe manage.py runserver 0.0.0.0:8000")
print("✅ Backend: http://localhost:8000")

# Frontend  
print("2. Starting Quasar frontend...")
frontend_dir = backend_dir / "frontend"
os.chdir(frontend_dir)
frontend = run_command("npm run dev")
print("✅ Frontend: http://localhost:9000")

print("\n🎉 Servers started successfully!")
print("Backend: http://localhost:8000")
print("Frontend: http://localhost:9000")
print("Press Ctrl+C to stop")

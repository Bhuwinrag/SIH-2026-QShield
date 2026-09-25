import subprocess
import sys
import threading
import time
import os
import signal
import socket

def prefix_output(process, prefix):
    for line in iter(process.stdout.readline, b''):
        sys.stdout.write(f"[{prefix}] {line.decode('utf-8', errors='replace')}")
        sys.stdout.flush()

def check_port(host, port, name):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(1)
    try:
        s.connect((host, port))
        print(f"[{name.upper()}] {name}: ONLINE")
        return True
    except (socket.timeout, ConnectionRefusedError):
        print(f"[{name.upper()}] {name}: OFFLINE - Please ensure native {name} service is running on port {port}.")
        return False
    finally:
        s.close()

def main():
    print("==================================================")
    print("Q-SHIELD BACKEND")
    print("==================================================")

    env = os.environ.copy()
    env["PYTHONPATH"] = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend"))

    # Determine python and celery executables based on venv
    venv_python = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "venv", "Scripts", "python.exe"))
    venv_celery = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "venv", "Scripts", "celery.exe"))
    
    if not os.path.exists(venv_python):
        venv_python = "python"
        venv_celery = "celery"

    backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend"))

    print("[FASTAPI] Starting...")
    fastapi_proc = subprocess.Popen(
        [venv_python, "-m", "uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", "8000"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        cwd=backend_dir,
        env=env
    )

    print("[CELERY] Starting worker...")
    celery_proc = subprocess.Popen(
        [venv_celery, "-A", "app.workers.celery_app", "worker", "--loglevel=info", "-P", "solo"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        cwd=backend_dir,
        env=env
    )

    t1 = threading.Thread(target=prefix_output, args=(fastapi_proc, "FASTAPI"), daemon=True)
    t2 = threading.Thread(target=prefix_output, args=(celery_proc, "CELERY"), daemon=True)
    t1.start()
    t2.start()

    time.sleep(2) # Give them a moment to start before checking DBs
    print("")
    check_port("127.0.0.1", 5432, "Database")
    check_port("127.0.0.1", 6379, "Redis")
    print("\nQ-SHIELD BACKEND READY")
    print("Press Ctrl+C to stop.\n")

    try:
        while True:
            if fastapi_proc.poll() is not None:
                print(f"[SUPERVISOR] FastAPI exited with code {fastapi_proc.returncode}")
                break
            if celery_proc.poll() is not None:
                print(f"[SUPERVISOR] Celery exited with code {celery_proc.returncode}")
                break
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n[SUPERVISOR] Shutting down Q-SHIELD backend services...")
    finally:
        fastapi_proc.terminate()
        celery_proc.terminate()
        fastapi_proc.wait()
        celery_proc.wait()
        print("[SUPERVISOR] All backend processes stopped cleanly.")
        sys.exit(1 if fastapi_proc.returncode or celery_proc.returncode else 0)

if __name__ == "__main__":
    main()

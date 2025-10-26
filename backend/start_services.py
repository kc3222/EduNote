# backend/start_services.py
import os
import sys
import subprocess
from pathlib import Path
import signal
import time

# Keep child PIDs here so the signal handler can terminate them
processes = []

def signal_handler(sig, frame):
    print("\nShutting down services...")
    for p in processes:
        if p.poll() is None:
            try:
                p.terminate()
            except Exception:
                pass
    # give them a moment to exit gracefully
    for p in processes:
        try:
            p.wait(timeout=5)
        except Exception:
            try:
                p.kill()
            except Exception:
                pass
    sys.exit(0)

def start_service(label: str, module_name: str, port: int, cwd: Path, env: dict):
    """
    Start a service via 'python -m <module_name> --port <port>' so that
    absolute imports like 'from auth_service...' work reliably.
    """
    print(f"Starting {label} on port {port}...")
    # Inherit stdout/stderr so you see logs in this terminal
    proc = subprocess.Popen(
        [sys.executable, "-m", module_name, "--port", str(port)],
        cwd=str(cwd),
        env=env,
    )
    return proc

if __name__ == "__main__":
    # Graceful shutdown (Ctrl+C / SIGTERM)
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # Backend directory (this file lives inside it)
    backend_path = Path(__file__).resolve().parent

    # Ensure our packages (auth_service, note_service, document_service) are importable
    env = os.environ.copy()
    env["PYTHONPATH"] = f"{backend_path}{os.pathsep}{env.get('PYTHONPATH','')}"

    # Service definitions: module must match the package folder name + '.main'
    services = [
        {"label": "Auth Service",     "module": "auth_service.main",     "port": int(os.getenv("AUTH_PORT", 8000))},
        {"label": "Notes Service",    "module": "note_service.main",     "port": int(os.getenv("NOTES_PORT", 8001))},
        {"label": "Document Service", "module": "document_service.main", "port": int(os.getenv("DOC_PORT", 8002))},
    ]

    try:
        for svc in services:
            # Optional: skip if the package folder doesn't exist (prevents crashes if doc svc isn't present yet)
            pkg_folder = backend_path / svc["module"].split(".")[0]
            if not pkg_folder.exists():
                print(f"Skipping {svc['label']} — package folder not found: {pkg_folder}")
                continue

            proc = start_service(
                label=svc["label"],
                module_name=svc["module"],
                port=svc["port"],
                cwd=backend_path,
                env=env,
            )
            processes.append(proc)
            time.sleep(0.3)  # small delay to keep logs readable

        if not processes:
            print("No services started. Make sure your service packages exist (e.g., auth_service/, note_service/).")
            sys.exit(1)

        print("\nAll requested services launched!")
        for svc in services:
            pkg_folder = backend_path / svc["module"].split(".")[0]
            if pkg_folder.exists():
                print(f"- {svc['label']}: http://localhost:{svc['port']}")

        print("\nPress Ctrl+C to stop.")

        # Keep parent alive while children run; exit if any child exits
        while True:
            for p in list(processes):
                rc = p.poll()
                if rc is not None:
                    print(f"\n{p.args} exited with code {rc}. Shutting down the rest...")
                    signal_handler(None, None)
            time.sleep(0.5)

    except KeyboardInterrupt:
        signal_handler(None, None)
    except Exception as e:
        print(f"Error: {e}")
        signal_handler(None, None)
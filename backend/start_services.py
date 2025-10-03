#!/usr/bin/env python3
import subprocess
import sys
import time
import signal
import os
from pathlib import Path

def signal_handler(sig, frame):
    print('\nShutting down services...')
    for process in processes:
        if process.poll() is None:  # Process is still running
            process.terminate()
    sys.exit(0)

def start_service(service_name, service_path, port):
    """Start a service in a subprocess"""
    print(f"Starting {service_name} on port {port}...")
    process = subprocess.Popen([
        sys.executable, "main.py", "--port", str(port)
    ], cwd=service_path)
    return process

if __name__ == "__main__":
    # Set up signal handler for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Get the directory where this script is located (backend directory)
    backend_path = Path(__file__).parent
    
    # Service configurations
    services = [
        {
            "name": "Auth Service",
            "path": backend_path / "auth_service",
            "port": 8000
        },
        {
            "name": "Notes Service", 
            "path": backend_path / "note_service",
            "port": 8001
        }
    ]
    
    processes = []
    
    try:
        # Start all services
        for service in services:
            if not service["path"].exists():
                print(f"Error: Service path {service['path']} does not exist")
                sys.exit(1)
            
            process = start_service(service["name"], service["path"], service["port"])
            processes.append(process)
            time.sleep(1)  # Small delay between starting services
        
        print("\nAll services started successfully!")
        print("Auth Service: http://localhost:8000")
        print("Notes Service: http://localhost:8001")
        print("\nPress Ctrl+C to stop all services")
        
        # Wait for all processes
        for process in processes:
            process.wait()
            
    except KeyboardInterrupt:
        signal_handler(None, None)
    except Exception as e:
        print(f"Error: {e}")
        signal_handler(None, None)

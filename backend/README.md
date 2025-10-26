# EduNote Backend Services

## Quick Start

Start all services:
```bash
python start_services.py
```

Start individual services:
```bash
# Auth Service (port 8000)
cd auth_service && python main.py

# Notes Service (port 8001) 
cd note_service && python main.py

# Custom port
python main.py --port 8002
```

## Adding a New Service

1. Create service directory: `mkdir new_service`
2. Add `main.py` with FastAPI app and port argument parsing
3. Add `requirements.txt` with dependencies
4. Update `start_services.py` to include your service
5. Assign next available port (8003, 8004, etc.)

## Service Template

```python
from fastapi import FastAPI
import uvicorn
import argparse

app = FastAPI(title="Service Name")

@app.get("/health")
async def health():
    return {"status": "healthy"}

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=8003)
    args = parser.parse_args()
    uvicorn.run(app, host="0.0.0.0", port=args.port)
```

## Ports
- 8000: Auth Service
- 8001: Notes Service
- 8002: Document Service  

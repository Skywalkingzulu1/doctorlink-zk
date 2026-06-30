"""DoctorLink Health Services — Main Entry Point."""

from pathlib import Path
from config import settings
from models import init_db
from frontend import app

# Initialize DB on startup
init_db()

from fastapi.responses import FileResponse

@app.get("/health")
def health_check():
    return {"status": "healthy", "app": settings.APP_NAME, "version": settings.APP_VERSION}

if __name__ == "__main__":
    import os
    import uvicorn
    port = int(os.getenv("PORT", 8001))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)

"""
FastAPI Server Entry Point.
Mounts REST API routers and static web dashboard files.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.config import FRONTEND_DIR
from backend.api import patients, doctors, appointments, beds, emergency, analytics
from database.init_db import init_database

app = FastAPI(
    title="AI-Driven Medical Appointment & Hospital Bed Allocation System",
    description="DSA-3 Advanced Algorithms Implementation Project (Review 2, Review 3, Review 4)",
    version="3.0.0"
)

# Enable CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API routers
app.include_router(patients.router)
app.include_router(doctors.router)
app.include_router(appointments.router)
app.include_router(beds.router)
app.include_router(emergency.router)
app.include_router(analytics.router)

# Mount frontend static directory
if os.path.exists(FRONTEND_DIR):
    app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")

@app.on_event("startup")
def startup_event():
    # Ensure database is initialised
    db_file = os.path.join(os.path.dirname(__file__), "..", "database", "hospital.db")
    if not os.path.exists(db_file):
        init_database(reset=False)

@app.get("/")
def serve_index():
    index_path = os.path.join(FRONTEND_DIR, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {"message": "Backend API is running cleanly. Frontend files present in /frontend."}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="127.0.0.1", port=8000, reload=True)

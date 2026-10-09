"""
Emergency Triage REST API Endpoints.
"""

from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional, Dict, Any
from database.db import execute_query
from services.emergency_service import EmergencyService

router = APIRouter(prefix="/api/emergency", tags=["Emergency Triage"])
emergency_service = EmergencyService()

class EmergencyAddRequest(BaseModel):
    name: str
    age: Optional[int] = 35
    gender: Optional[str] = "Other"
    urgency_level: int      # 1 (Critical) to 5 (Non-urgent)
    required_specialty: str
    required_ward_type: Optional[str] = "Emergency"
    arrival_time_min: Optional[int] = 540
    vital_signs_severity: Optional[float] = 2.0

@router.get("")
def get_emergency_cases():
    cases = execute_query("SELECT * FROM emergency_cases ORDER BY created_at DESC")
    return {"total": len(cases), "cases": cases}

@router.post("/triage/greedy-approximation")
def trigger_greedy_triage():
    """
    Executes fast priority-based greedy emergency triage under strict latency constraints.
    """
    return emergency_service.process_emergency_queue()

@router.post("/add")
def add_emergency_patient(req: EmergencyAddRequest):
    """
    Registers a new emergency patient and runs immediate triage allocation pass.
    """
    return emergency_service.add_emergency_patient(req.dict())

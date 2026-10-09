"""
Appointment Scheduling REST API Endpoints.
"""

from fastapi import APIRouter
from typing import Dict, Any
from database.db import execute_query
from services.allocation_service import AllocationService

router = APIRouter(prefix="/api/appointments", tags=["Appointments"])
alloc_service = AllocationService()

@router.get("")
def get_appointments():
    apps = execute_query("""
        SELECT a.appointment_id, a.patient_id, p.name as patient_name,
               a.doctor_id, d.name as doctor_name, d.specialty,
               s.start_time, s.end_time, d.room_no, a.status, a.matched_at
        FROM appointments a
        JOIN patients p ON a.patient_id = p.patient_id
        JOIN doctors d ON a.doctor_id = d.doctor_id
        JOIN doctor_slots s ON a.slot_id = s.slot_id
        ORDER BY a.matched_at DESC
    """)
    return {"total": len(apps), "appointments": apps}

@router.post("/match/bipartite-max-flow")
def trigger_bipartite_max_flow():
    """
    Executes Bipartite Maximum Flow algorithm to maximize feasible patient-doctor-slot matches.
    """
    return alloc_service.run_appointment_matching()

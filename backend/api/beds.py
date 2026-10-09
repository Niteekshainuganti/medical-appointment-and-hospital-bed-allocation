"""
Ward & Bed Management REST API Endpoints.
Includes Dinic Max-Flow bed allocation, Min-Cut capacity bottleneck reporting, and Admissions/Discharges.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any
from database.db import execute_query
from services.allocation_service import AllocationService

router = APIRouter(prefix="/api/beds", tags=["Beds & Wards"])
alloc_service = AllocationService()

class DischargeRequest(BaseModel):
    patient_id: str
    bed_id: str

@router.get("/wards")
def get_wards():
    wards = execute_query("""
        SELECT w.*, 
               (w.total_beds - w.occupied_beds) as available_beds
        FROM wards w
    """)
    return {"wards": wards}

@router.get("")
def get_beds(ward_id: str = None):
    if ward_id:
        beds = execute_query("SELECT b.*, p.name as patient_name FROM beds b LEFT JOIN patients p ON b.patient_id = p.patient_id WHERE b.ward_id = ?", (ward_id,))
    else:
        beds = execute_query("SELECT b.*, p.name as patient_name FROM beds b LEFT JOIN patients p ON b.patient_id = p.patient_id")
    return {"total": len(beds), "beds": beds}

@router.post("/allocate/dinic-max-flow")
def trigger_dinic_bed_allocation():
    """
    Executes Dinic Maximum Flow algorithm for bed allocation and returns Min-Cut bottleneck diagnosis.
    """
    return alloc_service.run_bed_allocation()

@router.post("/discharge")
def discharge_patient_and_reoptimise(req: DischargeRequest):
    """
    Records a discharge, updates bed state, and runs live re-optimisation pass.
    """
    return alloc_service.discharge_patient(req.patient_id, req.bed_id)

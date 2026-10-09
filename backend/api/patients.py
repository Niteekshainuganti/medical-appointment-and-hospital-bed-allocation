"""
Patient Management REST API Endpoints.
"""

from fastapi import APIRouter, Query, HTTPException, Response
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from database.db import execute_query, execute_statement, log_system_event
from services.search_service import SearchService

router = APIRouter(prefix="/api/patients", tags=["Patients"])
search_service = SearchService()

class PatientCreateRequest(BaseModel):
    name: str
    age: int
    gender: str
    phone: Optional[str] = None
    required_specialty: str
    required_ward_type: str
    urgency_level: int = 3
    preferred_doctor_id: Optional[str] = None

@router.get("")
def get_patients(limit: int = 100, offset: int = 0):
    patients = execute_query("SELECT * FROM patients ORDER BY created_at DESC LIMIT ? OFFSET ?", (limit, offset))
    total = execute_query("SELECT COUNT(*) as cnt FROM patients")[0]["cnt"]
    return {"total": total, "patients": patients}

@router.get("/search/exact")
def search_patients_exact(q: str = Query(..., min_length=1), algorithm: str = Query("KMP")):
    return search_service.exact_search_records(query=q, algorithm=algorithm)

@router.get("/search/fuzzy")
def search_patients_fuzzy(q: str = Query(..., min_length=1), max_distance: int = Query(3, ge=1, le=6)):
    return search_service.fuzzy_search_patients(query=q, max_distance=max_distance)

@router.get("/lookup/{patient_id}")
def lookup_patient_by_id(patient_id: str):
    res = search_service.search_by_id_universal_hash(patient_id)
    if not res["found"]:
        raise HTTPException(status_code=404, detail=f"Patient ID '{patient_id}' not found.")
    return res

@router.post("")
def add_patient(req: PatientCreateRequest):
    # Generate unique patient ID
    max_id_res = execute_query("SELECT MAX(CAST(SUBSTR(patient_id, 5) AS INTEGER)) as max_num FROM patients WHERE patient_id LIKE 'PAT-%'")
    next_num = (max_id_res[0]["max_num"] or 1000) + 1
    new_pid = f"PAT-{next_num:05d}"

    query = """
        INSERT INTO patients (patient_id, name, age, gender, phone, required_specialty, required_ward_type, urgency_level, preferred_doctor_id, status)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'Pending Allocation')
    """
    execute_statement(query, (
        new_pid, req.name, req.age, req.gender, req.phone or "+91-9000000000",
        req.required_specialty, req.required_ward_type, req.urgency_level, req.preferred_doctor_id
    ))

    # Index in Universal Hash Table
    new_p_record = execute_query("SELECT * FROM patients WHERE patient_id = ?", (new_pid,))[0]
    search_service.hash_table.insert(new_pid, new_p_record)

    log_system_event("PATIENT_REGISTERED", f"Registered new patient {new_pid} ({req.name}).")
    return {"status": "Success", "patient": new_p_record}

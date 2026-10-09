"""
Doctor Management REST API Endpoints.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from database.db import execute_query, execute_statement, log_system_event

router = APIRouter(prefix="/api/doctors", tags=["Doctors"])

class DoctorCreateRequest(BaseModel):
    name: str
    specialty: str
    room_no: str
    availability: str = "Available"

@router.get("")
def get_doctors():
    docs = execute_query("SELECT * FROM doctors")
    slots = execute_query("SELECT * FROM doctor_slots WHERE is_booked = 0")

    slot_counts = {}
    for s in slots:
        doc_id = s["doctor_id"]
        slot_counts[doc_id] = slot_counts.get(doc_id, 0) + 1

    results = []
    for d in docs:
        d_dict = dict(d)
        d_dict["free_slots_count"] = slot_counts.get(d["doctor_id"], 0)
        results.append(d_dict)

    return {"total": len(results), "doctors": results}

@router.post("")
def add_doctor(req: DoctorCreateRequest):
    max_id_res = execute_query("SELECT MAX(CAST(SUBSTR(doctor_id, 5) AS INTEGER)) as max_num FROM doctors WHERE doctor_id LIKE 'DOC-%'")
    next_num = (max_id_res[0]["max_num"] or 100) + 1
    new_doc_id = f"DOC-{next_num:03d}"

    query = "INSERT INTO doctors (doctor_id, name, specialty, room_no, availability) VALUES (?, ?, ?, ?, ?)"
    execute_statement(query, (new_doc_id, req.name, req.specialty, req.room_no, req.availability))

    # Generate 8 standard hourly time slots for the new doctor
    slot_rows = []
    for h in range(9, 17):
        slot_id = f"SLOT-{new_doc_id}-{h:02d}00"
        slot_rows.append((slot_id, new_doc_id, "2026-10-10", f"{h:02d}:00", f"{h:02d}:30", 0, None))

    execute_statement("INSERT INTO doctor_slots VALUES (?, ?, ?, ?, ?, ?, ?)", slot_rows[0])

    log_system_event("DOCTOR_ADDED", f"Added doctor {new_doc_id} ({req.name} - {req.specialty}).")
    return {"status": "Success", "doctor_id": new_doc_id}

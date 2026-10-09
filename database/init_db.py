"""
Database Initialization Script.
Creates tables and seeds SQLite database with synthetic hospital data.
"""

import json
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from database.db import get_db_connection, execute_statement, execute_many, log_system_event
from database.models import CREATE_TABLES_SQL
from data.generator import export_sample_data

DATA_JSON_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "sample_hospital_data.json")

def init_database(reset: bool = True):
    """
    Initializes database schema and populates sample synthetic records.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    if reset:
        cursor.executescript("""
            DROP TABLE IF EXISTS system_logs;
            DROP TABLE IF EXISTS emergency_cases;
            DROP TABLE IF EXISTS bed_allocations;
            DROP TABLE IF EXISTS appointments;
            DROP TABLE IF EXISTS patients;
            DROP TABLE IF EXISTS doctor_slots;
            DROP TABLE IF EXISTS doctors;
            DROP TABLE IF EXISTS beds;
            DROP TABLE IF EXISTS wards;
        """)
        conn.commit()

    # Create tables
    cursor.executescript(CREATE_TABLES_SQL)
    conn.commit()
    conn.close()

    # Check if sample JSON exists, if not generate it
    if not os.path.exists(DATA_JSON_PATH):
        export_sample_data(DATA_JSON_PATH, num_patients=1000, seed=42)

    with open(DATA_JSON_PATH, "r") as f:
        data = json.load(f)

    # Populate Wards
    ward_rows = [
        (w["ward_id"], w["ward_name"], w["ward_type"], w["specialty"], w["total_beds"], w["occupied_beds"])
        for w in data["wards"]
    ]
    execute_many("INSERT OR REPLACE INTO wards VALUES (?, ?, ?, ?, ?, ?)", ward_rows)

    # Populate Beds
    bed_rows = [
        (b["bed_id"], b["bed_number"], b["ward_id"], b["status"], b["patient_id"])
        for b in data["beds"]
    ]
    execute_many("INSERT OR REPLACE INTO beds VALUES (?, ?, ?, ?, ?)", bed_rows)

    # Update ward occupied counts
    execute_statement("""
        UPDATE wards SET occupied_beds = (
            SELECT COUNT(*) FROM beds WHERE beds.ward_id = wards.ward_id AND status = 'Occupied'
        )
    """)

    # Populate Doctors
    doc_rows = [
        (d["doctor_id"], d["name"], d["specialty"], d["room_no"], d["availability"])
        for d in data["doctors"]
    ]
    execute_many("INSERT OR REPLACE INTO doctors VALUES (?, ?, ?, ?, ?)", doc_rows)

    # Populate Slots
    slot_rows = [
        (s["slot_id"], s["doctor_id"], s["date"], s["start_time"], s["end_time"], 1 if s.get("is_booked") else 0, s.get("patient_id"))
        for s in data["slots"]
    ]
    execute_many("INSERT OR REPLACE INTO doctor_slots VALUES (?, ?, ?, ?, ?, ?, ?)", slot_rows)

    # Populate Patients
    patient_rows = [
        (
            p["patient_id"], p["name"], p.get("original_clean_name"), p["age"], p["gender"], p["phone"],
            p["required_specialty"], p["required_ward_type"], p["urgency_level"], p.get("preferred_doctor_id"),
            p.get("status", "Pending Allocation")
        )
        for p in data["patients"]
    ]
    execute_many("INSERT OR REPLACE INTO patients (patient_id, name, original_clean_name, age, gender, phone, required_specialty, required_ward_type, urgency_level, preferred_doctor_id, status) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", patient_rows)

    # Populate Emergency Cases
    emg_rows = [
        (
            e["emergency_id"], e["patient_id"], e["name"], e["urgency_level"], e["required_specialty"],
            e["required_ward_type"], e["arrival_time_min"], e["vital_signs_severity"], e["status"], None, None
        )
        for e in data["emergencies"]
    ]
    execute_many("INSERT OR REPLACE INTO emergency_cases (emergency_id, patient_id, name, urgency_level, required_specialty, required_ward_type, arrival_time_min, vital_signs_severity, status, assigned_bed_id, latency_ms) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", emg_rows)

    log_system_event("INIT", f"Database initialized with {len(patient_rows)} synthetic patient records.")
    print("Database initialization complete.")


if __name__ == "__main__":
    init_database(reset=True)

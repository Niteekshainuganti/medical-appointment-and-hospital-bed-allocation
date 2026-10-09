"""
Database Schema Definitions for SQLite.
Provides SQL DDL for patients, doctors, slots, wards, beds, appointments, allocations, emergency cases, and system logs.
"""

CREATE_TABLES_SQL = """
CREATE TABLE IF NOT EXISTS wards (
    ward_id TEXT PRIMARY KEY,
    ward_name TEXT NOT NULL,
    ward_type TEXT NOT NULL,
    specialty TEXT NOT NULL,
    total_beds INTEGER NOT NULL,
    occupied_beds INTEGER DEFAULT 0
);

CREATE TABLE IF NOT EXISTS beds (
    bed_id TEXT PRIMARY KEY,
    bed_number TEXT NOT NULL,
    ward_id TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'Available',
    patient_id TEXT,
    FOREIGN KEY(ward_id) REFERENCES wards(ward_id)
);

CREATE TABLE IF NOT EXISTS doctors (
    doctor_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    specialty TEXT NOT NULL,
    room_no TEXT NOT NULL,
    availability TEXT DEFAULT 'Available'
);

CREATE TABLE IF NOT EXISTS doctor_slots (
    slot_id TEXT PRIMARY KEY,
    doctor_id TEXT NOT NULL,
    date TEXT NOT NULL,
    start_time TEXT NOT NULL,
    end_time TEXT NOT NULL,
    is_booked INTEGER DEFAULT 0,
    patient_id TEXT,
    FOREIGN KEY(doctor_id) REFERENCES doctors(doctor_id)
);

CREATE TABLE IF NOT EXISTS patients (
    patient_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    original_clean_name TEXT,
    age INTEGER NOT NULL,
    gender TEXT NOT NULL,
    phone TEXT,
    required_specialty TEXT NOT NULL,
    required_ward_type TEXT NOT NULL,
    urgency_level INTEGER DEFAULT 3,
    preferred_doctor_id TEXT,
    status TEXT DEFAULT 'Pending Allocation',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS appointments (
    appointment_id TEXT PRIMARY KEY,
    patient_id TEXT NOT NULL,
    doctor_id TEXT NOT NULL,
    slot_id TEXT NOT NULL,
    matched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status TEXT DEFAULT 'Scheduled',
    FOREIGN KEY(patient_id) REFERENCES patients(patient_id),
    FOREIGN KEY(doctor_id) REFERENCES doctors(doctor_id),
    FOREIGN KEY(slot_id) REFERENCES doctor_slots(slot_id)
);

CREATE TABLE IF NOT EXISTS bed_allocations (
    allocation_id INTEGER PRIMARY KEY AUTOINCREMENT,
    patient_id TEXT NOT NULL,
    ward_id TEXT NOT NULL,
    bed_id TEXT NOT NULL,
    allocation_method TEXT DEFAULT 'Dinic Max-Flow',
    allocated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status TEXT DEFAULT 'Active',
    FOREIGN KEY(patient_id) REFERENCES patients(patient_id),
    FOREIGN KEY(ward_id) REFERENCES wards(ward_id),
    FOREIGN KEY(bed_id) REFERENCES beds(bed_id)
);

CREATE TABLE IF NOT EXISTS emergency_cases (
    emergency_id TEXT PRIMARY KEY,
    patient_id TEXT NOT NULL,
    name TEXT NOT NULL,
    urgency_level INTEGER NOT NULL,
    required_specialty TEXT NOT NULL,
    required_ward_type TEXT NOT NULL,
    arrival_time_min INTEGER NOT NULL,
    vital_signs_severity REAL DEFAULT 1.0,
    status TEXT DEFAULT 'Queued',
    assigned_bed_id TEXT,
    latency_ms REAL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS system_logs (
    log_id INTEGER PRIMARY KEY AUTOINCREMENT,
    event_type TEXT NOT NULL,
    message TEXT NOT NULL,
    execution_time_ms REAL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""

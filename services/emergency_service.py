"""
Emergency Triage Service Layer.
Manages emergency queue, greedy triage execution, latency tracking, and bed assignments.
"""

import time
from typing import List, Dict, Any
from database.db import execute_query, execute_statement, execute_many, log_system_event
from algorithms.emergency_greedy import greedy_emergency_triage, EmergencyPatient

class EmergencyService:

    def get_queued_emergencies(self) -> List[Dict[str, Any]]:
        return execute_query("SELECT * FROM emergency_cases WHERE status = 'Queued' ORDER BY urgency_level ASC, arrival_time_min ASC")

    def process_emergency_queue(self) -> Dict[str, Any]:
        """
        Executes priority-based greedy emergency triage under strict latency constraints.
        """
        start = time.perf_counter_ns()
        
        queued = self.get_queued_emergencies()
        if not queued:
            return {
                "status": "No Queued Emergencies",
                "assigned_count": 0,
                "latency_ms": 0.0,
                "results": []
            }

        # Convert DB rows to EmergencyPatient instances
        em_objects = []
        for q in queued:
            em_objects.append(EmergencyPatient(
                patient_id=q["patient_id"],
                name=q["name"],
                urgency_level=q["urgency_level"],
                required_specialty=q["required_specialty"],
                arrival_time_min=q["arrival_time_min"],
                required_ward_type=q["required_ward_type"],
                vital_signs_severity=q.get("vital_signs_severity", 1.5)
            ))

        # Fetch available beds and wards
        available_beds = execute_query("SELECT * FROM beds WHERE status = 'Available'")
        wards = execute_query("SELECT * FROM wards")

        triage_res = greedy_emergency_triage(em_objects, available_beds, wards)

        # Update database with emergency assignments
        assigned = triage_res.get("assigned_cases", [])
        if assigned:
            em_updates = []
            bed_updates = []
            patient_updates = []

            for c in assigned:
                em_updates.append((c["assigned_bed_id"], "Admitted", triage_res["latency_ms"], c["patient_id"]))
                bed_updates.append((c["patient_id"], c["assigned_bed_id"]))
                patient_updates.append(("Admitted (Emergency)", c["patient_id"]))

            execute_many("UPDATE emergency_cases SET assigned_bed_id = ?, status = ?, latency_ms = ? WHERE patient_id = ?", em_updates)
            execute_many("UPDATE beds SET status = 'Occupied', patient_id = ? WHERE bed_id = ?", bed_updates)
            execute_many("UPDATE patients SET status = ? WHERE patient_id = ?", patient_updates)

            # Update ward occupied counts
            execute_statement("""
                UPDATE wards SET occupied_beds = (
                    SELECT COUNT(*) FROM beds WHERE beds.ward_id = wards.ward_id AND status = 'Occupied'
                )
            """)

        elapsed_ms = (time.perf_counter_ns() - start) / 1e6
        log_system_event("EMERGENCY_TRIAGE_GREEDY", f"Processed {len(queued)} emergency cases in {triage_res['latency_ms']}ms. Assigned: {triage_res['total_assigned']}", elapsed_ms)

        triage_res["service_execution_time_ms"] = round(elapsed_ms, 3)
        return triage_res

    def add_emergency_patient(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Registers a new incoming emergency patient and triggers immediate triage pass.
        """
        em_id = f"EMG-{int(time.time()):04d}"
        p_id = data.get("patient_id") or f"PAT-E{int(time.time()):04d}"

        # Insert patient record if new
        execute_statement(
            "INSERT OR REPLACE INTO patients (patient_id, name, age, gender, phone, required_specialty, required_ward_type, urgency_level, status) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (p_id, data["name"], data.get("age", 30), data.get("gender", "Other"), "+91-9999999999", data["required_specialty"], data.get("required_ward_type", "Emergency"), data.get("urgency_level", 1), "Queued Emergency")
        )

        # Insert emergency record
        execute_statement(
            "INSERT INTO emergency_cases (emergency_id, patient_id, name, urgency_level, required_specialty, required_ward_type, arrival_time_min, vital_signs_severity, status) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (em_id, p_id, data["name"], data.get("urgency_level", 1), data["required_specialty"], data.get("required_ward_type", "Emergency"), data.get("arrival_time_min", 600), data.get("vital_signs_severity", 2.0), "Queued")
        )

        # Trigger immediate triage pass
        triage_out = self.process_emergency_queue()
        triage_out["registered_emergency_id"] = em_id
        triage_out["registered_patient_id"] = p_id
        return triage_out

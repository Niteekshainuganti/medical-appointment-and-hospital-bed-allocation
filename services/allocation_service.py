"""
Allocation Service Layer.
Manages Bipartite Max-Flow appointment matching, Dinic Max-Flow bed allocation, Min-Cut diagnosis,
admissions, discharges, and incremental re-optimisation.
"""

import time
from typing import List, Dict, Any
from database.db import execute_query, execute_statement, execute_many, log_system_event
from algorithms.max_flow import match_appointments
from algorithms.dinic import allocate_beds_dinic
from algorithms.min_cut import find_min_cut_bottlenecks

class AllocationService:

    def run_appointment_matching(self) -> Dict[str, Any]:
        """
        Runs Bipartite Max-Flow to match pending patients with doctor slots.
        """
        start = time.perf_counter_ns()
        patients = execute_query("SELECT * FROM patients WHERE status = 'Pending Allocation' OR status = 'Pending Appointment'")
        doctors = execute_query("SELECT * FROM doctors WHERE availability = 'Available'")
        slots = execute_query("SELECT * FROM doctor_slots WHERE is_booked = 0")

        match_res = match_appointments(patients, doctors, slots)

        # Save matches to database
        matched_records = match_res.get("matched", [])
        if matched_records:
            app_rows = []
            slot_updates = []
            patient_updates = []

            for m in matched_records:
                app_id = f"APP-{m['patient_id']}-{m['slot_id']}"
                app_rows.append((app_id, m["patient_id"], m["doctor_id"], m["slot_id"], "Scheduled"))
                slot_updates.append((m["patient_id"], m["slot_id"]))
                patient_updates.append(("Appointment Scheduled", m["patient_id"]))

            execute_many("INSERT OR REPLACE INTO appointments (appointment_id, patient_id, doctor_id, slot_id, status) VALUES (?, ?, ?, ?, ?)", app_rows)
            execute_many("UPDATE doctor_slots SET is_booked = 1, patient_id = ? WHERE slot_id = ?", slot_updates)
            execute_many("UPDATE patients SET status = ? WHERE patient_id = ?", patient_updates)

        elapsed_ms = (time.perf_counter_ns() - start) / 1e6
        log_system_event("APPOINTMENT_MATCHING", f"Matched {match_res['total_matched']}/{match_res['total_requested']} appointments.", elapsed_ms)

        match_res["execution_time_ms"] = round(elapsed_ms, 3)
        return match_res

    def run_bed_allocation(self) -> Dict[str, Any]:
        """
        Runs Dinic Max-Flow for batch bed allocation and computes Min-Cut capacity bottlenecks.
        """
        start = time.perf_counter_ns()
        patients = execute_query("SELECT * FROM patients WHERE status IN ('Pending Allocation', 'Appointment Scheduled')")
        wards = execute_query("SELECT * FROM wards")
        beds = execute_query("SELECT * FROM beds")

        alloc_res = allocate_beds_dinic(patients, wards, beds)

        # Process allocations
        allocations = alloc_res.get("allocations", [])
        if allocations:
            alloc_rows = []
            bed_updates = []
            patient_updates = []

            for a in allocations:
                alloc_rows.append((a["patient_id"], a["ward_id"], a["bed_id"], a["allocation_method"], "Active"))
                bed_updates.append((a["patient_id"], a["bed_id"]))
                patient_updates.append(("Admitted", a["patient_id"]))

            execute_many("INSERT INTO bed_allocations (patient_id, ward_id, bed_id, allocation_method, status) VALUES (?, ?, ?, ?, ?)", alloc_rows)
            execute_many("UPDATE beds SET status = 'Occupied', patient_id = ? WHERE bed_id = ?", bed_updates)
            execute_many("UPDATE patients SET status = ? WHERE patient_id = ?", patient_updates)

            # Update ward occupied beds counter
            execute_statement("""
                UPDATE wards SET occupied_beds = (
                    SELECT COUNT(*) FROM beds WHERE beds.ward_id = wards.ward_id AND status = 'Occupied'
                )
            """)

        # Compute Min-Cut bottlenecks on residual graph
        dinic_solver = alloc_res.get("dinic_solver")
        graph_meta = alloc_res.get("graph_metadata", {})
        min_cut_res = find_min_cut_bottlenecks(
            dinic_solver,
            s=graph_meta.get("source", 0),
            t=graph_meta.get("sink", 0),
            wards=wards,
            beds=beds,
            patients=patients
        )

        elapsed_ms = (time.perf_counter_ns() - start) / 1e6
        log_system_event("BED_ALLOCATION_DINIC", f"Allocated {alloc_res['total_allocated']} beds. Min-cut value: {min_cut_res.min_cut_value}", elapsed_ms)

        # Remove un-serializable dinic_solver object before returning JSON response
        alloc_res.pop("dinic_solver", None)
        alloc_res["execution_time_ms"] = round(elapsed_ms, 3)
        alloc_res["min_cut_bottleneck"] = {
            "min_cut_value": min_cut_res.min_cut_value,
            "bottleneck_wards": min_cut_res.bottleneck_wards,
            "summary_explanation": min_cut_res.summary_explanation
        }

        return alloc_res

    def discharge_patient(self, patient_id: str, bed_id: str) -> Dict[str, Any]:
        """
        Discharges a patient, frees the bed, and re-optimises bed allocations live.
        """
        start = time.perf_counter_ns()

        # Capture pre-state allocations
        pre_allocations = execute_query("SELECT patient_id, bed_id FROM beds WHERE status = 'Occupied'")

        # Free bed and mark patient discharged
        execute_statement("UPDATE beds SET status = 'Available', patient_id = NULL WHERE bed_id = ?", (bed_id,))
        execute_statement("UPDATE patients SET status = 'Discharged' WHERE patient_id = ?", (patient_id,))
        execute_statement("UPDATE bed_allocations SET status = 'Discharged' WHERE patient_id = ? AND bed_id = ?", (patient_id, bed_id))

        # Recalculate ward occupied count
        execute_statement("""
            UPDATE wards SET occupied_beds = (
                SELECT COUNT(*) FROM beds WHERE beds.ward_id = wards.ward_id AND status = 'Occupied'
            )
        """)

        # Re-run Dinic max flow allocation for remaining pending patients
        reopt_res = self.run_bed_allocation()

        # Capture post-state allocations
        post_allocations = execute_query("SELECT patient_id, bed_id FROM beds WHERE status = 'Occupied'")

        pre_set = {(r["patient_id"], r["bed_id"]) for r in pre_allocations}
        post_set = {(r["patient_id"], r["bed_id"]) for r in post_allocations}

        changed_assignments = list(post_set - pre_set)

        elapsed_ms = (time.perf_counter_ns() - start) / 1e6
        log_system_event("DISCHARGE_REOPTIMISE", f"Discharged {patient_id} from {bed_id}. Live re-optimisation completed in {elapsed_ms:.2f}ms.", elapsed_ms)

        return {
            "status": "Success",
            "discharged_patient_id": patient_id,
            "freed_bed_id": bed_id,
            "reoptimisation_execution_time_ms": round(elapsed_ms, 3),
            "newly_allocated_count": len(reopt_res.get("allocations", [])),
            "assignment_changes": changed_assignments,
            "reopt_summary": reopt_res
        }

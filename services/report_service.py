"""
Report and Analytics Service Layer.
Calculates dashboard metrics, algorithm utilization stats, and exports downloadable CSV reports.
"""

import csv
import io
import time
from typing import Dict, List, Any
from database.db import execute_query

class ReportService:

    def get_dashboard_summary(self) -> Dict[str, Any]:
        """
        Calculates real-time dashboard statistics from database.
        """
        patients = execute_query("SELECT COUNT(*) as cnt FROM patients")[0]["cnt"]
        doctors = execute_query("SELECT COUNT(*) as cnt FROM doctors")[0]["cnt"]
        appointments = execute_query("SELECT COUNT(*) as cnt FROM appointments")[0]["cnt"]
        wards = execute_query("SELECT COUNT(*) as cnt FROM wards")[0]["cnt"]
        beds_total = execute_query("SELECT COUNT(*) as cnt FROM beds")[0]["cnt"]
        beds_occupied = execute_query("SELECT COUNT(*) as cnt FROM beds WHERE status = 'Occupied'")[0]["cnt"]
        beds_available = execute_query("SELECT COUNT(*) as cnt FROM beds WHERE status = 'Available'")[0]["cnt"]

        emergencies_total = execute_query("SELECT COUNT(*) as cnt FROM emergency_cases")[0]["cnt"]
        emergencies_queued = execute_query("SELECT COUNT(*) as cnt FROM emergency_cases WHERE status = 'Queued'")[0]["cnt"]
        pending_patients = execute_query("SELECT COUNT(*) as cnt FROM patients WHERE status = 'Pending Allocation'")[0]["cnt"]

        # Calculate Utilization Rates
        bed_utilization = round((beds_occupied / max(1, beds_total)) * 100, 1)

        # Average Emergency Latency
        lat_res = execute_query("SELECT AVG(latency_ms) as avg_lat FROM emergency_cases WHERE latency_ms IS NOT NULL")
        avg_latency = round(lat_res[0]["avg_lat"] or 0.0, 2)

        # Recent Activity Logs
        recent_logs = execute_query("SELECT * FROM system_logs ORDER BY timestamp DESC LIMIT 8")

        # Bottleneck ward count
        ward_utilization = execute_query("""
            SELECT ward_name, total_beds, occupied_beds, 
            ROUND((CAST(occupied_beds AS REAL) / total_beds) * 100, 1) as util_pct
            FROM wards ORDER BY util_pct DESC
        """)

        return {
            "totals": {
                "patients": patients,
                "doctors": doctors,
                "appointments": appointments,
                "wards": wards,
                "beds_total": beds_total,
                "beds_occupied": beds_occupied,
                "beds_available": beds_available,
                "emergencies_total": emergencies_total,
                "emergencies_queued": emergencies_queued,
                "pending_patients": pending_patients
            },
            "performance": {
                "bed_utilization_pct": bed_utilization,
                "avg_emergency_latency_ms": avg_latency
            },
            "ward_status": ward_utilization,
            "recent_activity": recent_logs
        }

    def export_patients_csv(self) -> str:
        """
        Generates CSV text for patients list.
        """
        patients = execute_query("SELECT * FROM patients")
        output = io.StringIO()
        if not patients:
            return ""

        writer = csv.DictWriter(output, fieldnames=patients[0].keys())
        writer.writeheader()
        writer.writerows(patients)
        return output.getvalue()

    def export_bed_allocations_csv(self) -> str:
        """
        Generates CSV text for active bed allocations.
        """
        allocations = execute_query("""
            SELECT a.allocation_id, a.patient_id, p.name as patient_name, 
                   w.ward_name, b.bed_number, a.allocation_method, a.status, a.allocated_at
            FROM bed_allocations a
            JOIN patients p ON a.patient_id = p.patient_id
            JOIN wards w ON a.ward_id = w.ward_id
            JOIN beds b ON a.bed_id = b.bed_id
            ORDER BY a.allocated_at DESC
        """)
        output = io.StringIO()
        if not allocations:
            return ""

        writer = csv.DictWriter(output, fieldnames=allocations[0].keys())
        writer.writeheader()
        writer.writerows(allocations)
        return output.getvalue()

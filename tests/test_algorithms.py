"""
Unit Tests for All 9 Required Core Algorithms.
Verifies correctness, boundary cases, constraint satisfaction, and expected output structures.
"""

import unittest
import sys
import os

# Ensure parent directory is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from algorithms.kmp import kmp_search, compute_lps
from algorithms.z_function import z_search, compute_z_array
from algorithms.edit_distance import edit_distance, edit_distance_matrix, fuzzy_search_records
from algorithms.interval_dp import interval_scheduling_dp, IntervalRequest
from algorithms.max_flow import match_appointments
from algorithms.dinic import allocate_beds_dinic
from algorithms.min_cut import find_min_cut_bottlenecks
from algorithms.emergency_greedy import greedy_emergency_triage, EmergencyPatient
from algorithms.universal_hash import UniversalHashTable


class TestHospitalAlgorithms(unittest.TestCase):

    def test_kmp_search(self):
        text = "Patient John Smith registered at Cardiology Ward"
        pattern = "John Smith"
        matches = kmp_search(text, pattern, case_sensitive=True)
        self.assertEqual(matches, [8])

        # Case insensitive test
        matches_ci = kmp_search(text, "cardiology", case_sensitive=False)
        self.assertEqual(matches_ci, [33])

        # Non-matching pattern
        self.assertEqual(kmp_search(text, "Oncology"), [])

    def test_z_function_search(self):
        text = "Patient John Smith registered at Cardiology Ward"
        pattern = "John Smith"
        matches_z = z_search(text, pattern, case_sensitive=True)
        matches_kmp = kmp_search(text, pattern, case_sensitive=True)
        self.assertEqual(matches_z, matches_kmp)
        self.assertEqual(matches_z, [8])

    def test_edit_distance(self):
        dist1 = edit_distance("John", "Jon")
        self.assertEqual(dist1, 1)

        dist2, matrix = edit_distance_matrix("Kitten", "Sitting")
        self.assertEqual(dist2, 3)
        self.assertEqual(len(matrix), 7)  # 6+1
        self.assertEqual(len(matrix[0]), 8)  # 7+1

        # Fuzzy search test
        records = [
            {"patient_id": "PAT-101", "name": "John Smith"},
            {"patient_id": "PAT-102", "name": "Jane Doe"},
            {"patient_id": "PAT-103", "name": "Jonathan Smith"}
        ]
        results = fuzzy_search_records("Jon Smith", records, max_distance=3)
        self.assertTrue(len(results) > 0)
        self.assertEqual(results[0]["patient_id"], "PAT-101")

    def test_interval_dp(self):
        reqs = [
            IntervalRequest("R1", "P1", "D1", 540, 600, 10.0), # 9:00 - 10:00
            IntervalRequest("R2", "P2", "D1", 570, 630, 15.0), # 9:30 - 10:30 (overlaps R1)
            IntervalRequest("R3", "P3", "D1", 600, 660, 20.0), # 10:00 - 11:00 (overlaps R2, compatible with R1)
        ]
        res = interval_scheduling_dp(reqs)
        self.assertEqual(res["max_weight"], 30.0) # R1 + R3 = 10 + 20 = 30
        self.assertEqual(res["total_scheduled"], 2)

    def test_bipartite_max_flow_matching(self):
        patients = [
            {"patient_id": "P1", "name": "Alice", "required_specialty": "Cardiology"},
            {"patient_id": "P2", "name": "Bob", "required_specialty": "Cardiology"},
            {"patient_id": "P3", "name": "Charlie", "required_specialty": "Neurology"}
        ]
        doctors = [
            {"doctor_id": "D1", "name": "Dr. Adams", "specialty": "Cardiology"},
            {"doctor_id": "D2", "name": "Dr. Baker", "specialty": "Neurology"}
        ]
        slots = [
            {"slot_id": "S1", "doctor_id": "D1", "start_time": "09:00", "end_time": "09:30"},
            {"slot_id": "S2", "doctor_id": "D1", "start_time": "09:30", "end_time": "10:00"},
            {"slot_id": "S3", "doctor_id": "D2", "start_time": "09:00", "end_time": "09:30"}
        ]

        res = match_appointments(patients, doctors, slots)
        self.assertEqual(res["total_matched"], 3)
        self.assertEqual(res["match_rate"], 100.0)

    def test_dinic_bed_allocation_and_min_cut(self):
        patients = [
            {"patient_id": "P1", "name": "Pat1", "required_ward_type": "ICU", "urgency_level": 1},
            {"patient_id": "P2", "name": "Pat2", "required_ward_type": "ICU", "urgency_level": 1},
            {"patient_id": "P3", "name": "Pat3", "required_ward_type": "ICU", "urgency_level": 1}
        ]
        wards = [
            {"ward_id": "W1", "ward_name": "Cardiology ICU", "ward_type": "ICU", "total_beds": 2}
        ]
        beds = [
            {"bed_id": "B1", "bed_number": "ICU-101", "ward_id": "W1", "status": "Available"},
            {"bed_id": "B2", "bed_number": "ICU-102", "ward_id": "W1", "status": "Available"}
        ]

        res = allocate_beds_dinic(patients, wards, beds)
        self.assertEqual(res["total_allocated"], 2) # Only 2 available beds for 3 patients
        self.assertEqual(len(res["unallocated"]), 1)

        # Verify Min-Cut diagnosis
        dinic_solver = res["dinic_solver"]
        min_cut = find_min_cut_bottlenecks(dinic_solver, 0, res["graph_metadata"]["sink"], wards, beds, patients)
        self.assertTrue(len(min_cut.bottleneck_wards) > 0)
        self.assertIn("Cardiology ICU", min_cut.summary_explanation)

    def test_greedy_emergency_triage(self):
        emergencies = [
            EmergencyPatient("EM-1", "Severe Trauma", 1, "Surgery", 540, "Emergency", 2.8),
            EmergencyPatient("EM-2", "Minor Fracture", 4, "Orthopedics", 550, "General", 1.1),
            EmergencyPatient("EM-3", "Cardiac Arrest", 1, "Cardiology", 545, "ICU", 3.0)
        ]
        wards = [
            {"ward_id": "W1", "ward_name": "Emergency ICU", "ward_type": "ICU"}
        ]
        beds = [
            {"bed_id": "B1", "ward_id": "W1", "status": "Available"},
            {"bed_id": "B2", "ward_id": "W1", "status": "Available"}
        ]

        triage_res = greedy_emergency_triage(emergencies, beds, wards)
        self.assertEqual(triage_res["total_assigned"], 2)
        # EM-3 and EM-1 (Urgency 1) should be assigned over EM-2 (Urgency 4)
        assigned_ids = [c["patient_id"] for c in triage_res["assigned_cases"]]
        self.assertIn("EM-3", assigned_ids)
        self.assertIn("EM-1", assigned_ids)
        self.assertNotIn("EM-2", assigned_ids)

    def test_universal_hash_table(self):
        hash_table = UniversalHashTable(capacity=100, seed=42)
        
        # Insert records
        hash_table.insert("PAT-1001", {"name": "Alice"})
        hash_table.insert("PAT-1002", {"name": "Bob"})
        
        # Lookups
        val1 = hash_table.get("PAT-1001")
        self.assertIsNotNone(val1)
        self.assertEqual(val1["name"], "Alice")
        
        self.assertIsNone(hash_table.get("PAT-9999"))
        
        # Collision stats check
        stats = hash_table.get_collision_stats()
        self.assertEqual(stats["total_elements"], 2)
        self.assertIn("O(1)", stats["theoretical_complexity"])


if __name__ == "__main__":
    unittest.main()

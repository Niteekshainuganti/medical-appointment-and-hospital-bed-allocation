"""
Integration Tests for Hospital System Backend API & Database Services.
Tests end-to-end patient registration, searching, appointment matching, bed allocation, emergency triage, and report generation.
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from database.init_db import init_database
from backend.api.patients import search_patients_exact, search_patients_fuzzy, lookup_patient_by_id
from backend.api.appointments import trigger_bipartite_max_flow
from backend.api.beds import trigger_dinic_bed_allocation
from backend.api.emergency import trigger_greedy_triage
from backend.api.analytics import get_dashboard_summary, get_ai_demand_forecast, export_patients_csv

class TestHospitalIntegration(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        init_database(reset=True)

    def test_01_dashboard_summary_api(self):
        data = get_dashboard_summary()
        self.assertIn("totals", data)
        self.assertGreater(data["totals"]["patients"], 0)
        self.assertGreater(data["totals"]["doctors"], 0)

    def test_02_patient_exact_search_kmp(self):
        data = search_patients_exact(q="Sharma", algorithm="KMP")
        self.assertIn("total_matches", data)

    def test_03_patient_fuzzy_search_edit_distance(self):
        data = search_patients_fuzzy(q="Jon", max_distance=2)
        self.assertIn("results", data)

    def test_04_universal_hash_lookup(self):
        data = lookup_patient_by_id("PAT-00001")
        self.assertTrue(data["found"])
        self.assertEqual(data["patient"]["patient_id"], "PAT-00001")

    def test_05_bipartite_max_flow_matching(self):
        data = trigger_bipartite_max_flow()
        self.assertIn("total_matched", data)

    def test_06_dinic_bed_allocation_and_min_cut(self):
        data = trigger_dinic_bed_allocation()
        self.assertIn("total_allocated", data)
        self.assertIn("min_cut_bottleneck", data)

    def test_07_emergency_triage_greedy(self):
        data = trigger_greedy_triage()
        self.assertIn("total_assigned", data)
        self.assertLess(data["latency_ms"], 100.0)

    def test_08_ai_demand_forecast(self):
        data = get_ai_demand_forecast()
        self.assertEqual(data["module_status"], "EXPERIMENTAL_EXTENSION_MODULE")
        self.assertIn("ward_forecasts", data)

    def test_09_csv_reports(self):
        res_pat = export_patients_csv()
        self.assertIn("patient_id,name", res_pat.body.decode('utf-8'))


if __name__ == "__main__":
    unittest.main()

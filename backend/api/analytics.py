"""
Analytics, AI Forecast, Benchmarks & Algorithm Lab REST API Endpoints.
"""

from fastapi import APIRouter, Response
import json
import os
from typing import Dict, Any
from services.report_service import ReportService
from services.ai_forecaster import AIDemandForecaster
from algorithms.kmp import kmp_search, compute_lps
from algorithms.z_function import z_search, compute_z_array
from algorithms.edit_distance import edit_distance_matrix
from algorithms.interval_dp import interval_scheduling_dp, IntervalRequest

router = APIRouter(prefix="/api/analytics", tags=["Analytics & AI"])
report_service = ReportService()
ai_forecaster = AIDemandForecaster()

BENCHMARK_JSON_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "data", "benchmark_results.json")

@router.get("/dashboard-summary")
def get_dashboard_summary():
    return report_service.get_dashboard_summary()

@router.get("/ai-demand-forecast")
def get_ai_demand_forecast():
    """
    Returns 7-day predicted bed demand per ward using synthetic seasonal trend regression.
    """
    return ai_forecaster.forecast_7day_bed_demand()

@router.get("/benchmark-results")
def get_benchmark_results():
    if os.path.exists(BENCHMARK_JSON_PATH):
        with open(BENCHMARK_JSON_PATH, "r") as f:
            return json.load(f)
    return {"error": "Benchmark data not generated yet. Run tests/benchmark.py."}

@router.get("/export/patients.csv")
def export_patients_csv():
    csv_text = report_service.export_patients_csv()
    return Response(content=csv_text, media_type="text/csv", headers={"Content-Disposition": "attachment; filename=patients_report.csv"})

@router.get("/export/allocations.csv")
def export_allocations_csv():
    csv_text = report_service.export_bed_allocations_csv()
    return Response(content=csv_text, media_type="text/csv", headers={"Content-Disposition": "attachment; filename=bed_allocations_report.csv"})

@router.post("/algorithm-lab/kmp")
def lab_run_kmp(text: str, pattern: str):
    lps = compute_lps(pattern)
    matches = kmp_search(text, pattern, case_sensitive=True)
    return {"text": text, "pattern": pattern, "lps_array": lps, "matches_0indexed": matches}

@router.post("/algorithm-lab/z-function")
def lab_run_z(text: str, pattern: str):
    concat_s = pattern + "$" + text
    z_arr = compute_z_array(concat_s)
    matches = z_search(text, pattern, case_sensitive=True)
    return {"concat_string": concat_s, "z_array": z_arr, "matches_0indexed": matches}

@router.post("/algorithm-lab/edit-distance")
def lab_run_edit_distance(str1: str, str2: str):
    dist, matrix = edit_distance_matrix(str1, str2)
    return {"str1": str1, "str2": str2, "edit_distance": dist, "dp_table": matrix}

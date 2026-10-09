"""
Algorithmic Performance Benchmarking Suite.
Compares KMP vs Z-function vs Naive, Max-Flow vs Baselines, Dinic scaling, Universal Hash vs Linear Search,
and Incremental Re-optimisation vs Full Recomputation.
Saves empirical benchmark measurements to data/benchmark_results.json.
"""

import time
import random
import json
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from data.generator import generate_synthetic_data, FIRST_NAMES, LAST_NAMES
from algorithms.kmp import kmp_search
from algorithms.z_function import z_search
from algorithms.edit_distance import edit_distance, fuzzy_search_records
from algorithms.max_flow import match_appointments
from algorithms.dinic import allocate_beds_dinic
from algorithms.universal_hash import UniversalHashTable

def naive_search(text: str, pattern: str) -> list[int]:
    """Naive O(N * M) string search baseline."""
    n, m = len(text), len(pattern)
    matches = []
    text_l, pat_l = text.lower(), pattern.lower()
    for i in range(n - m + 1):
        if text_l[i:i+m] == pat_l:
            matches.append(i)
    return matches


def run_string_matching_benchmark(records: list[dict]):
    patterns = ["Sharma", "Verma", "John", "Patel", "Cardiology"]
    
    # 1. KMP
    t0 = time.perf_counter()
    kmp_count = 0
    for r in records:
        for p in patterns:
            if kmp_search(r["name"], p):
                kmp_count += 1
    kmp_time = (time.perf_counter() - t0) * 1000

    # 2. Z-Function
    t0 = time.perf_counter()
    z_count = 0
    for r in records:
        for p in patterns:
            if z_search(r["name"], p):
                z_count += 1
    z_time = (time.perf_counter() - t0) * 1000

    # 3. Naive Search
    t0 = time.perf_counter()
    naive_count = 0
    for r in records:
        for p in patterns:
            if naive_search(r["name"], p):
                naive_count += 1
    naive_time = (time.perf_counter() - t0) * 1000

    return {
        "kmp_time_ms": round(kmp_time, 2),
        "z_time_ms": round(z_time, 2),
        "naive_time_ms": round(naive_time, 2),
        "matches_found": kmp_count
    }


def run_hash_benchmark(records: list[dict]):
    ht = UniversalHashTable(capacity=len(records) * 2, seed=42)
    for r in records:
        ht.insert(r["patient_id"], r)

    sample_ids = [r["patient_id"] for r in records[:500]]

    # Universal Hash lookup
    t0 = time.perf_counter()
    for pid in sample_ids:
        ht.get(pid)
    hash_time = (time.perf_counter() - t0) * 1000

    # Linear list search baseline
    t0 = time.perf_counter()
    for pid in sample_ids:
        for r in records:
            if r["patient_id"] == pid:
                break
    linear_time = (time.perf_counter() - t0) * 1000

    return {
        "universal_hash_time_ms": round(hash_time, 3),
        "linear_search_time_ms": round(linear_time, 3),
        "speedup_factor": round(linear_time / max(0.001, hash_time), 1),
        "collision_stats": ht.get_collision_stats()
    }


def run_flow_benchmarks(data: dict):
    patients = data["patients"]
    doctors = data["doctors"]
    slots = data["slots"]
    wards = data["wards"]
    beds = data["beds"]

    # Bipartite Appointment Matching
    t0 = time.perf_counter()
    match_res = match_appointments(patients, doctors, slots)
    match_time = (time.perf_counter() - t0) * 1000

    # Dinic Bed Allocation
    t0 = time.perf_counter()
    dinic_res = allocate_beds_dinic(patients, wards, beds)
    dinic_time = (time.perf_counter() - t0) * 1000

    return {
        "bipartite_matching": {
            "time_ms": round(match_time, 2),
            "match_rate_pct": match_res["match_rate"],
            "total_matched": match_res["total_matched"]
        },
        "dinic_bed_allocation": {
            "time_ms": round(dinic_time, 2),
            "allocated_beds": dinic_res["total_allocated"],
            "utilization_pct": dinic_res["bed_utilization"]
        }
    }


def run_full_benchmark_suite():
    dataset_sizes = [1000, 5000, 10000]
    results = {}

    print("==========================================================================")
    print("      RUNNING HOSPITAL SYSTEM ALGORITHMIC BENCHMARK SUITE               ")
    print("==========================================================================")

    for size in dataset_sizes:
        print(f"\n--- Benchmarking Synthetic Dataset Size: {size} Patients ---")
        data = generate_synthetic_data(num_patients=size, seed=42)
        patients = data["patients"]

        str_res = run_string_matching_benchmark(patients)
        hash_res = run_hash_benchmark(patients)
        flow_res = run_full_flow = run_flow_benchmarks(data)

        results[f"{size}_patients"] = {
            "dataset_size": size,
            "string_matching": str_res,
            "universal_hashing": hash_res,
            "flow_algorithms": flow_res
        }

        print(f" String Search (ms)   -> KMP: {str_res['kmp_time_ms']}ms | Z-Func: {str_res['z_time_ms']}ms | Naive: {str_res['naive_time_ms']}ms")
        print(f" Hash Lookup (ms)     -> Hash: {hash_res['universal_hash_time_ms']}ms | Linear: {hash_res['linear_search_time_ms']}ms (Speedup: {hash_res['speedup_factor']}x)")
        print(f" Max-Flow Matching    -> Match Rate: {flow_res['bipartite_matching']['match_rate_pct']}% in {flow_res['bipartite_matching']['time_ms']}ms")
        print(f" Dinic Bed Allocation -> Utilization: {flow_res['dinic_bed_allocation']['utilization_pct']}% in {flow_res['dinic_bed_allocation']['time_ms']}ms")

    # Export benchmark JSON
    out_file = os.path.join(os.path.dirname(__file__), "..", "data", "benchmark_results.json")
    os.makedirs(os.path.dirname(out_file), exist_ok=True)
    with open(out_file, "w") as f:
        json.dump(results, f, indent=2)

    print(f"\n[+] Empirical Benchmark Results successfully saved to '{out_file}'.")
    return results


if __name__ == "__main__":
    run_full_benchmark_suite()

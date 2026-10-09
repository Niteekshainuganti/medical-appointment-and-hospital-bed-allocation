"""
Search Service Layer.
Integrates KMP, Z-Function, Edit-Distance DP, and Universal Hashing for patient & record searches.
"""

from typing import List, Dict, Any
import time
from database.db import execute_query, log_system_event
from algorithms.kmp import kmp_search
from algorithms.z_function import z_search
from algorithms.edit_distance import edit_distance, fuzzy_search_records
from algorithms.universal_hash import UniversalHashTable

class SearchService:
    def __init__(self):
        self.hash_table = UniversalHashTable(capacity=20011, seed=42)
        self._build_hash_index()

    def _build_hash_index(self):
        """
        Indexes all patient records in the Universal Hash Table.
        """
        patients = execute_query("SELECT * FROM patients")
        for p in patients:
            self.hash_table.insert(p["patient_id"], p)

    def search_by_id_universal_hash(self, patient_id: str) -> Dict[str, Any]:
        """
        O(1) expected lookup using Universal Hash Table.
        """
        start = time.perf_counter_ns()
        result = self.hash_table.get(patient_id)
        elapsed_ms = (time.perf_counter_ns() - start) / 1e6

        stats = self.hash_table.get_collision_stats()

        return {
            "query": patient_id,
            "found": result is not None,
            "patient": result,
            "execution_time_ms": round(elapsed_ms, 4),
            "algorithm": "Universal Hashing (h_{a,b}(k) = ((a*k+b) mod p) mod m)",
            "hash_stats": stats
        }

    def exact_search_records(self, query: str, algorithm: str = "KMP") -> Dict[str, Any]:
        """
        Performs exact string search across patient records using KMP or Z-Function.
        """
        start = time.perf_counter_ns()
        patients = execute_query("SELECT * FROM patients")

        matches = []
        pattern = query.strip().lower()

        for p in patients:
            name_text = p["name"].lower()
            pid_text = p["patient_id"].lower()
            spec_text = p["required_specialty"].lower()

            if algorithm.upper() == "Z-FUNCTION":
                match_indices = z_search(name_text, pattern) or z_search(pid_text, pattern) or z_search(spec_text, pattern)
            else:
                match_indices = kmp_search(name_text, pattern) or kmp_search(pid_text, pattern) or kmp_search(spec_text, pattern)

            if match_indices:
                p_copy = dict(p)
                p_copy["matched_indices"] = match_indices
                matches.append(p_copy)

        elapsed_ms = (time.perf_counter_ns() - start) / 1e6
        log_system_event(f"SEARCH_{algorithm.upper()}", f"Exact search for '{query}' returned {len(matches)} matches.", elapsed_ms)

        return {
            "query": query,
            "algorithm": f"Exact Pattern Matching ({algorithm.upper()})",
            "total_matches": len(matches),
            "execution_time_ms": round(elapsed_ms, 4),
            "results": matches
        }

    def fuzzy_search_patients(self, query: str, max_distance: int = 3) -> Dict[str, Any]:
        """
        Performs typo-tolerant fuzzy patient search using Edit-Distance DP.
        """
        start = time.perf_counter_ns()
        patients = execute_query("SELECT * FROM patients")

        results = fuzzy_search_records(
            query=query,
            records=patients,
            search_keys=["name", "patient_id", "original_clean_name"],
            max_distance=max_distance,
            top_k=20
        )

        elapsed_ms = (time.perf_counter_ns() - start) / 1e6
        log_system_event("SEARCH_FUZZY", f"Fuzzy search for '{query}' returned {len(results)} matches.", elapsed_ms)

        return {
            "query": query,
            "algorithm": "Edit-Distance Dynamic Programming (Levenshtein)",
            "max_distance_threshold": max_distance,
            "total_matches": len(results),
            "execution_time_ms": round(elapsed_ms, 4),
            "results": results
        }

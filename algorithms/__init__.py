"""
Hospital Resource Allocation System - Core Algorithms Package.
Includes String Matching, Dynamic Programming, Network Flow, Greedy Approximation, and Universal Hashing.
"""

from .kmp import kmp_search, compute_lps
from .z_function import z_search, compute_z_array
from .edit_distance import edit_distance, edit_distance_matrix, fuzzy_search_records
from .interval_dp import interval_scheduling_dp, IntervalRequest
from .max_flow import BipartiteMaxFlow, match_appointments
from .dinic import DinicMaxFlow, allocate_beds_dinic
from .min_cut import find_min_cut_bottlenecks, MinCutResult
from .emergency_greedy import greedy_emergency_triage, EmergencyPatient
from .universal_hash import UniversalHashTable

__all__ = [
    'kmp_search', 'compute_lps',
    'z_search', 'compute_z_array',
    'edit_distance', 'edit_distance_matrix', 'fuzzy_search_records',
    'interval_scheduling_dp', 'IntervalRequest',
    'BipartiteMaxFlow', 'match_appointments',
    'DinicMaxFlow', 'allocate_beds_dinic',
    'find_min_cut_bottlenecks', 'MinCutResult',
    'greedy_emergency_triage', 'EmergencyPatient',
    'UniversalHashTable'
]

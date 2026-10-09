"""
Interval Dynamic Programming for Compatible Appointment Slot Scheduling.
Weighted Interval Scheduling Problem solved via DP + Binary Search.
Time Complexity: O(N log N) for sorting and binary search predecessor lookups.
Space Complexity: O(N) for DP state memoization.
Used to compute non-overlapping compatible appointment schedules for doctors and operating rooms.
"""

from typing import List, Dict, Any
from dataclasses import dataclass
import bisect

@dataclass
class IntervalRequest:
    request_id: str
    patient_id: str
    doctor_id: str
    start_time: int  # minutes from midnight (e.g. 9:00 AM = 540)
    end_time: int    # minutes from midnight (e.g. 9:30 AM = 570)
    weight: float    # priority score or preference weight

def interval_scheduling_dp(requests: List[IntervalRequest]) -> Dict[str, Any]:
    """
    Computes the maximum weight subset of non-overlapping interval requests.
    Returns optimal value and selected non-overlapping interval list.
    """
    if not requests:
        return {"max_weight": 0.0, "selected_requests": [], "total_scheduled": 0}

    # Sort intervals by finish time
    sorted_reqs = sorted(requests, key=lambda r: r.end_time)
    n = len(sorted_reqs)

    # Extract finish times for binary search
    finish_times = [r.end_time for r in sorted_reqs]

    # p[i] = largest index j < i such that interval j does not overlap with interval i
    p = [-1] * n
    for i in range(n):
        # find rightmost interval j with end_time <= sorted_reqs[i].start_time
        idx = bisect.bisect_right(finish_times, sorted_reqs[i].start_time) - 1
        if idx >= 0 and idx < i:
            p[i] = idx
        else:
            p[i] = -1

    # DP table: dp[i] = max weight achievable using a subset of intervals from 0..i
    dp = [0.0] * n
    dp[0] = sorted_reqs[0].weight

    for i in range(1, n):
        incl_weight = sorted_reqs[i].weight + (dp[p[i]] if p[i] != -1 else 0.0)
        excl_weight = dp[i - 1]
        dp[i] = max(incl_weight, excl_weight)

    # Reconstruct optimal solution subset by backtracing
    selected = []
    curr = n - 1
    while curr >= 0:
        incl_weight = sorted_reqs[curr].weight + (dp[p[curr]] if p[curr] != -1 else 0.0)
        excl_weight = dp[curr - 1] if curr > 0 else 0.0

        if incl_weight >= excl_weight and (curr == 0 or incl_weight > dp[curr - 1]):
            selected.append(sorted_reqs[curr])
            curr = p[curr]
        else:
            curr -= 1

    selected.reverse()

    return {
        "max_weight": round(dp[n - 1], 2),
        "selected_requests": selected,
        "total_scheduled": len(selected),
        "total_requested": len(requests)
    }

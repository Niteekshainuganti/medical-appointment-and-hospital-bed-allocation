"""
Minimum Cut Bottleneck Diagnosis Module.
Uses Max-Flow Min-Cut Theorem (Ford-Fulkerson / Dinic residual graph reachable set).
Time Complexity: O(V + E) post-flow graph traversal.
Space Complexity: O(V) for reachable set.
Identifies capacity bottlenecks and reports exact limiting wards/resources to hospital administrators.
"""

from collections import deque
from typing import List, Dict, Any
from dataclasses import dataclass
from .dinic import DinicMaxFlow

@dataclass
class MinCutResult:
    min_cut_value: int
    reachable_nodes: List[int]
    unreachable_nodes: List[int]
    cut_edges: List[Dict[str, Any]]
    bottleneck_wards: List[Dict[str, Any]]
    summary_explanation: str

def find_min_cut_bottlenecks(
    dinic: DinicMaxFlow,
    s: int,
    t: int,
    wards: List[Dict[str, Any]],
    beds: List[Dict[str, Any]],
    patients: List[Dict[str, Any]]
) -> MinCutResult:
    """
    Performs BFS on the residual graph to partition nodes into S_reachable and T_unreachable.
    Identifies saturated edges across the cut boundary as capacity bottlenecks.
    """
    if dinic is None:
        return MinCutResult(
            min_cut_value=0,
            reachable_nodes=[],
            unreachable_nodes=[],
            cut_edges=[],
            bottleneck_wards=[],
            summary_explanation="No network flow instance available for min-cut analysis."
        )

    # BFS from Source s in residual graph (edges with residual capacity cap - flow > 0)
    visited = [False] * dinic.n
    queue = deque([s])
    visited[s] = True

    while queue:
        curr = queue.popleft()
        for edge_idx in dinic.adj[curr]:
            edge = dinic.edges[edge_idx]
            if edge.cap - edge.flow > 0 and not visited[edge.v]:
                visited[edge.v] = True
                queue.append(edge.v)

    s_reachable = [i for i in range(dinic.n) if visited[i]]
    t_unreachable = [i for i in range(dinic.n) if not visited[i]]

    # Identify cut edges (u in S_reachable, v in T_unreachable with cap > 0)
    cut_edges = []
    min_cut_val = 0

    ward_lookup = {w["ward_id"]: w for w in wards}
    bed_lookup = {b["bed_id"]: b for b in beds}

    bottleneck_counts = {}

    for u in s_reachable:
        for edge_idx in dinic.adj[u]:
            edge = dinic.edges[edge_idx]
            if not visited[edge.v] and edge.cap > 0:
                min_cut_val += edge.cap
                cut_info = {
                    "from_node": edge.u,
                    "to_node": edge.v,
                    "capacity": edge.cap,
                    "flow": edge.flow,
                    "edge_id": edge.edge_id
                }
                cut_edges.append(cut_info)

                # Parse edge_id for ward bottleneck diagnosis
                if "W_" in edge.edge_id:
                    # Ward to Bed edge or Patient to Ward edge
                    parts = edge.edge_id.split("->")
                    for p in parts:
                        if p.startswith("W_"):
                            w_id = p.replace("W_", "")
                            bottleneck_counts[w_id] = bottleneck_counts.get(w_id, 0) + 1

    # Format bottleneck wards list
    bottleneck_wards = []
    for w_id, count in bottleneck_counts.items():
        w_info = ward_lookup.get(w_id, {"ward_name": f"Ward {w_id}", "ward_type": "Specialized"})
        bottleneck_wards.append({
            "ward_id": w_id,
            "ward_name": w_info.get("ward_name"),
            "ward_type": w_info.get("ward_type"),
            "capacity": w_info.get("total_beds", 0),
            "saturated_cut_count": count,
            "bottleneck_severity": "HIGH" if count >= 3 else "MEDIUM"
        })

    # Summary explanation
    if bottleneck_wards:
        ward_names = ", ".join([f"'{bw['ward_name']}' ({bw['ward_type']})" for bw in bottleneck_wards])
        explanation = (
            f"Min-Cut Bottleneck Identified (Cut Value = {min_cut_val}): "
            f"The capacity bottleneck is strictly located at ward(s): {ward_names}. "
            f"All outgoing residual edges for these wards are saturated (flow = capacity). "
            f"To increase overall hospital admission flow, bed expansion or patient discharge in these specific wards is required."
        )
    else:
        explanation = (
            f"Min-Cut Analysis Complete (Cut Value = {min_cut_val}): "
            f"No specific ward capacity bottleneck detected. Unallocated patients were restricted by specialty eligibility constraints or total bed saturation."
        )

    return MinCutResult(
        min_cut_value=min_cut_val,
        reachable_nodes=s_reachable,
        unreachable_nodes=t_unreachable,
        cut_edges=cut_edges,
        bottleneck_wards=bottleneck_wards,
        summary_explanation=explanation
    )

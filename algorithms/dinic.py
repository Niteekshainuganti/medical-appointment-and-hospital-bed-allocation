"""
Dinic's Maximum Flow Algorithm for Capacity-Aware Hospital Bed Allocation.
Time Complexity: O(V^2 * E) general, O(E * sqrt(V)) for unit network graphs.
Space Complexity: O(V + E) for residual graph.
Constructs level graphs via BFS and finds blocking flows via DFS.
"""

from collections import deque
from typing import List, Dict, Any, Tuple

class DinicEdge:
    def __init__(self, u: int, v: int, cap: int, flow: int = 0, edge_id: str = ""):
        self.u = u
        self.v = v
        self.cap = cap
        self.flow = flow
        self.rev_idx = -1
        self.edge_id = edge_id

class DinicMaxFlow:
    """
    Dinic's algorithm implementation using level graph and blocking flow search.
    """
    def __init__(self, num_nodes: int):
        self.n = num_nodes
        self.adj = [[] for _ in range(num_nodes)]
        self.edges = []
        self.level = [-1] * num_nodes
        self.ptr = [0] * num_nodes

    def add_edge(self, u: int, v: int, cap: int, edge_id: str = "") -> int:
        forward_edge = DinicEdge(u, v, cap, 0, edge_id)
        backward_edge = DinicEdge(v, u, 0, 0, f"rev_{edge_id}")

        self.adj[u].append(len(self.edges))
        forward_edge.rev_idx = len(self.edges) + 1
        self.edges.append(forward_edge)

        self.adj[v].append(len(self.edges))
        backward_edge.rev_idx = len(self.edges) - 1
        self.edges.append(backward_edge)

        return len(self.edges) - 2

    def _bfs(self, s: int, t: int) -> bool:
        self.level = [-1] * self.n
        self.level[s] = 0
        queue = deque([s])

        while queue:
            curr = queue.popleft()
            for edge_idx in self.adj[curr]:
                edge = self.edges[edge_idx]
                if edge.cap - edge.flow > 0 and self.level[edge.v] == -1:
                    self.level[edge.v] = self.level[curr] + 1
                    queue.append(edge.v)

        return self.level[t] != -1

    def _dfs(self, curr: int, t: int, pushed: int) -> int:
        if pushed == 0 or curr == t:
            return pushed

        for i in range(self.ptr[curr], len(self.adj[curr])):
            self.ptr[curr] = i
            edge_idx = self.adj[curr][i]
            edge = self.edges[edge_idx]
            tr = edge.v

            if self.level[curr] + 1 != self.level[tr] or edge.cap - edge.flow == 0:
                continue

            tr_pushed = self._dfs(tr, t, min(pushed, edge.cap - edge.flow))
            if tr_pushed == 0:
                continue

            edge.flow += tr_pushed
            self.edges[edge.rev_idx].flow -= tr_pushed
            return tr_pushed

        return 0

    def max_flow(self, s: int, t: int) -> int:
        flow = 0
        while self._bfs(s, t):
            self.ptr = [0] * self.n
            while True:
                pushed = self._dfs(s, t, float('inf'))
                if pushed == 0:
                    break
                flow += pushed
        return flow


def allocate_beds_dinic(
    patients: List[Dict[str, Any]],
    wards: List[Dict[str, Any]],
    beds: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Allocates hospital beds to eligible patients using Dinic Max-Flow.
    
    Graph Topology:
    0: Source S
    1..P: Patient Nodes
    P+1..P+W: Ward Capacity Nodes
    P+W+1..P+W+B: Available Bed Nodes
    P+W+B+1: Sink T
    """
    num_patients = len(patients)
    num_wards = len(wards)
    
    # Filter available beds only
    available_beds = [b for b in beds if b.get("status") == "Available"]
    num_beds = len(available_beds)

    if num_patients == 0 or num_beds == 0:
        return {
            "allocations": [],
            "unallocated": [p["patient_id"] for p in patients],
            "total_allocated": 0,
            "utilization_rate": 0.0,
            "dinic_solver": None,
            "reason": "No patients or available beds"
        }

    s = 0
    patient_offset = 0
    ward_offset = num_patients
    bed_offset = num_patients + num_wards
    t = num_patients + num_wards + num_beds + 1

    dinic = DinicMaxFlow(t + 1)

    # Patient indexing
    patient_map = {}
    for i, p in enumerate(patients):
        p_node = patient_offset + 1 + i
        patient_map[p_node] = p
        # Source -> Patient capacity 1
        dinic.add_edge(s, p_node, cap=1, edge_id=f"S->P_{p['patient_id']}")

    # Ward indexing & Ward -> Bed connections
    ward_map = {}
    ward_node_map = {}
    for i, w in enumerate(wards):
        w_node = ward_offset + 1 + i
        ward_map[w_node] = w
        ward_node_map[w["ward_id"]] = w_node

    # Bed indexing & Bed -> Sink connections
    bed_map = {}
    for i, b in enumerate(available_beds):
        b_node = bed_offset + 1 + i
        bed_map[b_node] = b
        # Bed -> Sink capacity 1
        dinic.add_edge(b_node, t, cap=1, edge_id=f"B_{b['bed_id']}->T")

        # Ward -> Bed capacity 1
        w_node = ward_node_map.get(b["ward_id"])
        if w_node:
            dinic.add_edge(w_node, b_node, cap=1, edge_id=f"W_{b['ward_id']}->B_{b['bed_id']}")

    # Patient -> Ward edges based on eligibility (required_ward_type / specialty)
    edges_added = 0
    for i, p in enumerate(patients):
        p_node = patient_offset + 1 + i
        req_ward_type = p.get("required_ward_type", "General").strip().lower()
        urgency = p.get("urgency_level", 3)

        for w_node, w in ward_map.items():
            w_type = w.get("ward_type", "").strip().lower()
            w_specialty = w.get("specialty", "").strip().lower()

            # Ward type matching or specialty match or ICU override for emergency urgency 1-2
            is_eligible = False
            if req_ward_type == w_type or req_ward_type == w_specialty:
                is_eligible = True
            elif urgency <= 2 and "icu" in w_type:
                is_eligible = True
            elif req_ward_type == "general":
                is_eligible = True

            if is_eligible:
                dinic.add_edge(p_node, w_node, cap=1, edge_id=f"P_{p['patient_id']}->W_{w['ward_id']}")
                edges_added += 1

    # Solve Max Flow via Dinic
    max_flow_val = dinic.max_flow(s, t)

    # Extract allocations from residual graph
    allocations = []
    allocated_patient_ids = set()

    for edge in dinic.edges:
        if edge.flow == 1 and edge.u > patient_offset and edge.u <= ward_offset:
            p_node = edge.u
            w_node = edge.v
            p = patient_map.get(p_node)
            w = ward_map.get(w_node)

            if p and w:
                # Find which bed was assigned from this ward
                assigned_bed = None
                for b_edge_idx in dinic.adj[w_node]:
                    b_edge = dinic.edges[b_edge_idx]
                    if b_edge.flow == 1 and b_edge.v > bed_offset and b_edge.v < t:
                        assigned_bed = bed_map.get(b_edge.v)
                        break

                if assigned_bed:
                    allocations.append({
                        "patient_id": p["patient_id"],
                        "patient_name": p.get("name"),
                        "urgency_level": p.get("urgency_level", 3),
                        "ward_id": w["ward_id"],
                        "ward_name": w["ward_name"],
                        "ward_type": w["ward_type"],
                        "bed_id": assigned_bed["bed_id"],
                        "bed_number": assigned_bed.get("bed_number"),
                        "allocation_method": "Dinic Max-Flow"
                    })
                    allocated_patient_ids.add(p["patient_id"])

    # Unallocated patients
    unallocated = []
    for p in patients:
        if p["patient_id"] not in allocated_patient_ids:
            unallocated.append({
                "patient_id": p["patient_id"],
                "patient_name": p.get("name"),
                "urgency_level": p.get("urgency_level", 3),
                "required_ward_type": p.get("required_ward_type", "General"),
                "reason": f"Insufficient bed capacity or no available bed in eligible ward type '{p.get('required_ward_type', 'General')}'"
            })

    total_beds_all = len(beds)
    bed_utilization = round(((total_beds_all - len(available_beds) + max_flow_val) / max(1, total_beds_all)) * 100, 1)

    return {
        "allocations": allocations,
        "unallocated": unallocated,
        "total_allocated": max_flow_val,
        "total_requested": num_patients,
        "available_beds_count": num_beds,
        "total_beds_count": total_beds_all,
        "bed_utilization": bed_utilization,
        "dinic_solver": dinic,
        "graph_metadata": {
            "source": s,
            "sink": t,
            "nodes": t + 1,
            "edges": edges_added
        }
    }

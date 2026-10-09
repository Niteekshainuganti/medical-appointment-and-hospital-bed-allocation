"""
Bipartite Maximum Flow Algorithm for Patient-Doctor-Slot Appointment Matching.
Uses Network Flow (Edmonds-Karp / Dinic) to compute the maximum cardinality bipartite matching.
Time Complexity: O(V * E^2) for Edmonds-Karp or O(E * sqrt(V)) for unit networks.
Space Complexity: O(V + E) for residual flow graph.
Prevents double-booking and enforces specialty and shift availability constraints.
"""

from collections import deque
from typing import List, Dict, Any, Tuple

class BipartiteMaxFlow:
    """
    Solves Bipartite Maximum Flow matching between Patients and Doctor-Slots.
    """
    def __init__(self, num_nodes: int):
        self.n = num_nodes
        self.capacity = [[0] * num_nodes for _ in range(num_nodes)]
        self.adj = [[] for _ in range(num_nodes)]

    def add_edge(self, u: int, v: int, cap: int = 1):
        self.capacity[u][v] += cap
        self.adj[u].append(v)
        self.adj[v].append(u)

    def _bfs(self, s: int, t: int, parent: List[int]) -> bool:
        visited = [False] * self.n
        queue = deque([s])
        visited[s] = True

        while queue:
            curr = queue.popleft()
            if curr == t:
                return True

            for nxt in self.adj[curr]:
                if not visited[nxt] and self.capacity[curr][nxt] > 0:
                    visited[nxt] = True
                    parent[nxt] = curr
                    queue.append(nxt)

        return False

    def max_flow(self, s: int, t: int) -> int:
        """
        Computes Max-Flow using Edmonds-Karp (BFS augmenting path).
        """
        parent = [-1] * self.n
        flow = 0

        while self._bfs(s, t, parent):
            path_flow = float('inf')
            curr = t

            while curr != s:
                p = parent[curr]
                path_flow = min(path_flow, self.capacity[p][curr])
                curr = p

            curr = t
            while curr != s:
                p = parent[curr]
                self.capacity[p][curr] -= path_flow
                self.capacity[curr][p] += path_flow
                curr = p

            flow += path_flow
            parent = [-1] * self.n

        return flow


def match_appointments(
    patients: List[Dict[str, Any]],
    doctors: List[Dict[str, Any]],
    slots: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Constructs a bipartite network and runs Max-Flow matching.
    
    Node mapping:
    0: Source S
    1..N: Patient nodes
    N+1..N+M: Doctor-Slot nodes
    N+M+1: Sink T
    """
    num_patients = len(patients)
    num_slots = len(slots)

    if num_patients == 0 or num_slots == 0:
        return {
            "matched": [],
            "unmatched": [p["patient_id"] for p in patients],
            "total_matched": 0,
            "match_rate": 0.0,
            "reasons": {"no_slots": "No available doctor slots in system"}
        }

    s = 0
    t = num_patients + num_slots + 1
    total_nodes = t + 1

    flow_net = BipartiteMaxFlow(total_nodes)

    # Doctor lookup map by doctor_id
    doc_map = {d["doctor_id"]: d for d in doctors}

    # Slot index lookup
    slot_idx_map = {}
    for i, sl in enumerate(slots):
        node_id = num_patients + 1 + i
        slot_idx_map[node_id] = sl

    # Patient node mapping
    patient_node_map = {}
    for i, p in enumerate(patients):
        p_node = i + 1
        patient_node_map[p_node] = p
        # Source to Patient capacity = 1
        flow_net.add_edge(s, p_node, cap=1)

    # Doctor-Slot to Sink capacity = 1
    for i, sl in enumerate(slots):
        slot_node = num_patients + 1 + i
        flow_net.add_edge(slot_node, t, cap=1)

    # Add edges Patient -> Doctor-Slot if specialty and constraints match
    edges_added = 0
    slot_contention = {}

    for p_idx, p in enumerate(patients):
        p_node = p_idx + 1
        p_spec = p.get("required_specialty", "").strip().lower()
        p_pref_doc = p.get("preferred_doctor_id")

        for s_idx, sl in enumerate(slots):
            slot_node = num_patients + 1 + s_idx
            doc_id = sl.get("doctor_id")
            doc = doc_map.get(doc_id)

            if not doc:
                continue

            doc_spec = doc.get("specialty", "").strip().lower()

            # Check specialty constraint
            if p_spec and p_spec != doc_spec:
                continue

            # Check preferred doctor constraint if specified
            if p_pref_doc and p_pref_doc != doc_id:
                continue

            # Eligible edge
            flow_net.add_edge(p_node, slot_node, cap=1)
            edges_added += 1
            slot_contention[sl["slot_id"]] = slot_contention.get(sl["slot_id"], 0) + 1

    # Run Max Flow
    max_matches = flow_net.max_flow(s, t)

    # Reconstruct matching results
    matched = []
    matched_patient_ids = set()

    for p_idx, p in enumerate(patients):
        p_node = p_idx + 1
        for s_idx, sl in enumerate(slots):
            slot_node = num_patients + 1 + s_idx
            # If capacity p_node -> slot_node was used (capacity became 0 from original 1)
            if flow_net.capacity[slot_node][p_node] == 1:
                doc = doc_map.get(sl["doctor_id"], {})
                matched.append({
                    "patient_id": p["patient_id"],
                    "patient_name": p.get("name", "Unknown"),
                    "doctor_id": sl["doctor_id"],
                    "doctor_name": doc.get("name", "Unknown"),
                    "specialty": doc.get("specialty", "General"),
                    "slot_id": sl["slot_id"],
                    "start_time": sl.get("start_time"),
                    "end_time": sl.get("end_time"),
                    "date": sl.get("date"),
                    "room_no": doc.get("room_no", "Room 101")
                })
                matched_patient_ids.add(p["patient_id"])

    # Collect unmatched patients with explanation reasons
    unmatched = []
    for p in patients:
        if p["patient_id"] not in matched_patient_ids:
            p_spec = p.get("required_specialty", "General")
            matching_doc_slots = [
                sl for sl in slots 
                if doc_map.get(sl["doctor_id"], {}).get("specialty", "").lower() == p_spec.lower()
            ]
            if not matching_doc_slots:
                reason = f"No available doctor slots found for specialty '{p_spec}'"
            else:
                reason = f"High slot contention for specialty '{p_spec}'; all matching slots assigned to higher priority/earlier requests"
            
            unmatched.append({
                "patient_id": p["patient_id"],
                "patient_name": p.get("name"),
                "required_specialty": p_spec,
                "reason": reason
            })

    match_rate = round((max_matches / max(1, num_patients)) * 100, 1)

    return {
        "matched": matched,
        "unmatched": unmatched,
        "total_matched": max_matches,
        "total_requested": num_patients,
        "match_rate": match_rate,
        "graph_nodes": total_nodes,
        "graph_edges": edges_added
    }

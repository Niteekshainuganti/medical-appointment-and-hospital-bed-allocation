# System Architecture & Technical Specification

## AI-Driven Medical Appointment and Hospital Bed Allocation System
**DSA-3 Advanced Algorithms Project**

---

## 1. Architectural Overview

The system is designed around a single connected graph and hospital state model. The decisions across searching, appointment matching, ward/bed allocation, emergency triage, and live re-optimisation are interconnected so that the output of one algorithm becomes a constraint for the next.

```
                                  [ Patient / Hospital Data ]
                                               │
                                               ▼
                         ┌──────────────────────────────────────────┐
                         │ 1. Record Search & Identification        │
                         │    • Universal Hash Table O(1) Lookup   │
                         │    • KMP & Z-Function Exact Search       │
                         │    • Edit-Distance DP Fuzzy Search       │
                         └────────────────────┬─────────────────────┘
                                              │ Candidate Edges
                                              ▼
                         ┌──────────────────────────────────────────┐
                         │ 2. Doctor Appointment Scheduling        │
                         │    • Bipartite Max-Flow Matching         │
                         │    • Interval DP Slot Compatibility      │
                         └────────────────────┬─────────────────────┘
                                              │ Valid Appointments
                                              ▼
                         ┌──────────────────────────────────────────┐
                         │ 3. Hospital Ward & Bed Allocation        │
                         │    • Dinic's Algorithm (Level/Residual) │
                         │    • Min-Cut Capacity Bottleneck Diagnosis│
                         └────────────────────┬─────────────────────┘
                                              │ Allocation State
                                              ▼
                         ┌──────────────────────────────────────────┐
                         │ 4. Emergency Triage & Re-optimisation    │
                         │    • Priority-Based Greedy Approximation │
                         │    • Live Residual Graph Augmentation    │
                         └──────────────────────────────────────────┘
```

---

## 2. Component Breakdown

### A. Frontend Layer (`frontend/`)
- Single Page Dashboard with responsive CSS Grid/Flexbox design.
- Tab views: Dashboard, Patient Directory, Doctor Scheduling, Bed Allocation Map, Emergency Triage Queue, AI Forecast & Analytics, Algorithm Viva Lab.
- Built using native HTML5, modern CSS, JavaScript (ES6+), and Chart.js.

### B. Backend API Layer (`backend/`)
- **Framework**: FastAPI (Asynchronous Python REST API).
- **Routers**: `patients`, `doctors`, `appointments`, `beds`, `emergency`, `analytics`.
- Serves static assets and provides OpenAPI documentation at `/docs`.

### C. Algorithm Engine (`algorithms/`)
Pure, modular algorithm implementations:
1. `kmp.py`: Knuth-Morris-Pratt string matcher ($O(N+M)$).
2. `z_function.py`: Z-algorithm linear pattern matcher ($O(N+M)$).
3. `edit_distance.py`: Levenshtein distance dynamic programming matrix & candidate ranker ($O(NM)$).
4. `interval_dp.py`: Weighted interval scheduling dynamic programming ($O(N \log N)$).
5. `max_flow.py`: Bipartite maximum flow network graph for patient-doctor-slot matching ($O(VE^2)$).
6. `dinic.py`: Dinic's maximum flow algorithm with level graphs and blocking flows ($O(V^2E)$ worst case, $O(E \sqrt{V})$ for unit networks).
7. `min_cut.py`: Min-cut capacity bottleneck diagnosis via BFS on residual graph ($O(V+E)$).
8. `emergency_greedy.py`: Priority-based greedy emergency triage under strict latency bounds ($O(N \log N)$).
9. `universal_hash.py`: Universal hash table ($h_{a,b}(k) = ((a \cdot k + b) \pmod p) \pmod m$) with separate chaining ($O(1)$ expected).

### D. Data & Storage Layer (`database/` & `data/`)
- **SQLite Database** (`hospital.db`): Stores persistent records for patients, doctors, slots, wards, beds, allocations, emergency cases, and execution logs.
- **Reproducible Data Generator** (`generator.py`): Synthetic data generator with fixed seed `42` for benchmarking datasets of size 1k, 5k, 10k, 50k, 100k.

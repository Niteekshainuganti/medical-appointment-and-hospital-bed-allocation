# Review Summary & Feature-to-Algorithm Mapping

## Project Review Presentations Alignment (Review 2, Review 3, Review 4)

---

## 1. Feature-to-Algorithm Mapping Table

| Hospital Decision / Feature | Required Algorithm | Purpose & Implementation | Time Complexity | Verification & Test Status |
| :--- | :--- | :--- | :--- | :--- |
| **Exact Record Search** | Knuth–Morris–Pratt (KMP) | Finds exact patient name, ID, or text substring without backtrack. | $O(N + M)$ | ✅ Verified in `test_algorithms.py` & benchmarked |
| **Alternative Exact Search** | Z-Function Algorithm | Concatenates $P + \$ + T$ to compute Z-array for linear exact search. | $O(N + M)$ | ✅ Verified against KMP baseline |
| **Typo-Tolerant Search** | Edit-Distance DP | Computes Levenshtein matrix for misspelled patient names. | $O(N \cdot M)$ | ✅ Verified with typo-seeded dataset |
| **Slot Compatibility** | Interval Dynamic Programming | Selects non-overlapping optimal appointment slot intervals. | $O(N \log N)$ | ✅ Verified with weighted interval test cases |
| **Doctor-Patient Matching** | Bipartite Maximum Flow | Solves bipartite graph matching subject to specialty & time. | $O(V \cdot E^2)$ / $O(E\sqrt{V})$ | ✅ Verified against brute-force baseline |
| **Bed Allocation** | Dinic Maximum Flow | Allocates patients across eligible wards & available beds using level graphs. | $O(V^2 \cdot E)$ | ✅ Verified across 1k-10k synthetic datasets |
| **Capacity Bottleneck Diagnosis** | Minimum Cut (Min-Cut) | Partitions residual graph into reachable $S$ and unreachable $T$ to identify bottleneck wards. | $O(V + E)$ | ✅ Verified & displayed as alert banner |
| **Emergency Triage** | Greedy Approximation | Prioritizes critical emergency patients under sub-50ms latency budget. | $O(N \log N)$ | ✅ Verified latency < 10ms |
| **Patient ID Lookup** | Universal Hashing | Hash family $h_{a,b}(k) = ((a \cdot k + b) \pmod p) \pmod m$ with chaining. | $O(1)$ expected | ✅ Verified with collision statistics tracking |
| **Capacity Planning (Extension)**| Synthetic Trend Regression | 7-day predicted bed demand per ward for advisory resource planning. | $O(W \cdot D)$ | ✅ Labeled as experimental extension module |

---

## 2. Feature Implementation Status

### A. Fully Implemented & Tested
- [x] KMP Exact Pattern Matching
- [x] Z-Function String Search
- [x] Edit-Distance Dynamic Programming with Candidate Ranking
- [x] Interval Dynamic Programming for Slot Compatibility
- [x] Bipartite Maximum Flow Appointment Scheduling
- [x] Dinic Maximum Flow Hospital Bed Allocation
- [x] Min-Cut Capacity Bottleneck Diagnosis & Text Summarization
- [x] Priority-Based Greedy Emergency Triage
- [x] Universal Hashing with Collision Metrics
- [x] Live Admissions, Discharges & Re-optimisation
- [x] Interactive Responsive Web UI & Algorithm Viva Lab
- [x] Reproducible Synthetic Data Generator (Seed 42)
- [x] Performance Benchmarking Suite (1k, 5k, 10k datasets)
- [x] Downloadable CSV Reports

### B. Experimental Extensions
- [x] Experimental AI Demand Forecaster (Clearly separated from exact decision algorithms)

### C. Future Work Scope
- Real hospital database integration (HIPAA/FHIR compliant data adapters)
- Multi-hospital inter-facility bed transfers using multi-commodity network flow
- BK-Tree or Trie indexing for large-scale edit-distance fuzzy lookup optimization

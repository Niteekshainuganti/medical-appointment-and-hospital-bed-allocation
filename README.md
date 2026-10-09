# AI-Driven Medical Appointment and Hospital Bed Allocation System
**DSA-3 Advanced Algorithms Project (B.Tech CSE)**
*Standardized Implementation aligned with Review 2, Review 3, and Review 4 Presentation Requirements*

---

## 📌 Project Overview
This project presents an integrated, capacity-aware hospital resource allocation system designed around a single connected graph and hospital state model. Rather than solving hospital decisions in isolation, the system connects:
1. **Record Search & ID Lookup** (KMP, Z-Function, Edit-Distance DP, Universal Hashing)
2. **Doctor-Patient Appointment Scheduling** (Bipartite Maximum Flow & Interval DP)
3. **Hospital Ward & Bed Allocation** (Dinic's Maximum Flow & Minimum Cut Bottleneck Diagnosis)
4. **Emergency Triage** (Priority-Based Greedy Approximation under latency constraints)
5. **Live Admissions, Discharges & Re-optimisation** (Residual Graph Augmentation)
6. **Experimental Capacity Planning Layer** (Synthetic Time-Series Trend Regression)

---

## 🛠️ Technology Stack
- **Language**: Python 3.13
- **Backend API**: FastAPI + Uvicorn
- **Data Persistence**: SQLite 3 (DAO Pattern)
- **Frontend UI**: HTML5, Modern CSS (Responsive Grid/Flexbox), JavaScript (ES6+), Chart.js
- **Testing & Benchmarks**: Python `unittest`, custom benchmark engine
- **Synthetic Data**: Seeded generator producing reproducible 1k, 5k, 10k, 50k, 100k datasets

---

## 📁 Folder Structure
```
hospital-allocation-system/
├── frontend/
│   ├── index.html            # Main Web Dashboard Markup
│   ├── css/
│   │   └── style.css         # Dark/Light Responsive Dashboard Stylesheet
│   └── js/
│       └── app.js            # API Fetch Handlers, Tab Switcher & Chart Logic
├── backend/
│   ├── main.py               # FastAPI Server Entry Point & Static File Mounting
│   ├── config.py             # System Configurations
│   └── api/
│       ├── patients.py       # Patient REST Endpoints
│       ├── doctors.py        # Doctor & Slot Endpoints
│       ├── appointments.py   # Bipartite Max-Flow Appointment Endpoints
│       ├── beds.py           # Dinic Max-Flow Bed & Min-Cut Endpoints
│       ├── emergency.py      # Emergency Triage Endpoints
│       └── analytics.py      # Dashboard Stats, AI Forecast & Algorithm Lab
├── algorithms/
│   ├── kmp.py                # Knuth-Morris-Pratt Pattern Matching
│   ├── z_function.py         # Z-Function Linear Search
│   ├── edit_distance.py      # Edit-Distance Dynamic Programming
│   ├── interval_dp.py        # Weighted Interval Scheduling DP
│   ├── max_flow.py           # Bipartite Max-Flow Matching
│   ├── dinic.py              # Dinic Max-Flow Bed Allocator
│   ├── min_cut.py            # Min-Cut Bottleneck Diagnosis
│   ├── emergency_greedy.py   # Priority Greedy Emergency Triage
│   └── universal_hash.py     # Universal Hashing with Collision Metrics
├── services/
│   ├── search_service.py     # Search & Hashing Service
│   ├── allocation_service.py # Flow Allocation & Re-optimisation Service
│   ├── emergency_service.py  # Emergency Queue Service
│   ├── ai_forecaster.py      # Experimental Demand Forecasting Service
│   └── report_service.py     # Analytics & CSV Report Exporter
├── database/
│   ├── db.py                 # SQLite DAO & Connection Manager
│   ├── models.py             # DDL Database Table Schemas
│   └── init_db.py            # Database Initialisation Script
├── tests/
│   ├── test_algorithms.py    # Unit Tests for Core Algorithms
│   ├── test_integration.py   # Integration Tests for REST APIs
│   └── benchmark.py          # Benchmark Execution Engine
├── data/
│   ├── generator.py          # Reproducible Synthetic Data Generator (Seed 42)
│   ├── sample_hospital_data.json
│   └── benchmark_results.json
├── docs/
│   ├── architecture.md       # Architectural Blueprint
│   ├── review_summary.md     # Review Alignment & Algorithm Mapping
│   └── algorithms_viva_guide.md # Viva Q&A & Demo Walkthrough Script
├── requirements.txt
└── README.md
```

---

## ⚡ Quick Start & Run Commands

### 1. Prerequisites & Environment Setup
Navigate to the project root directory:
```bash
cd C:\Users\lenovo\.gemini\antigravity\scratch\hospital-allocation-system
```

### 2. Initialize Database & Seed Synthetic Data
```bash
python database/init_db.py
```

### 3. Run Unit & Integration Tests
```bash
# Run Core Algorithm Unit Tests
python -m unittest tests/test_algorithms.py

# Run API Integration Tests
python -m unittest tests/test_integration.py
```

### 4. Run Benchmark Performance Suite
```bash
python tests/benchmark.py
```

### 5. Launch Web Application Server
```bash
python backend/main.py
```
Open your browser and navigate to:
👉 **`http://127.0.0.1:8000`**

---

## 🧮 Core Algorithms & Complexity Matrix

| Algorithm | Hospital Decision | Time Complexity | Space Complexity |
| :--- | :--- | :--- | :--- |
| **KMP Search** | Exact patient / doctor pattern search | $O(N + M)$ | $O(M)$ |
| **Z-Function** | Linear exact string search alternative | $O(N + M)$ | $O(N + M)$ |
| **Edit-Distance DP** | Typo-tolerant fuzzy patient lookup | $O(N \cdot M)$ | $O(N \cdot M)$ |
| **Interval DP** | Compatible non-overlapping slot scheduling | $O(N \log N)$ | $O(N)$ |
| **Bipartite Max-Flow** | Patient-Doctor-Slot matching | $O(V \cdot E^2)$ | $O(V + E)$ |
| **Dinic Max-Flow** | Capacity-aware hospital bed allocation | $O(V^2 \cdot E)$ | $O(V + E)$ |
| **Minimum Cut** | Identifying capacity bottleneck wards | $O(V + E)$ | $O(V)$ |
| **Greedy Emergency** | Fast priority emergency triage | $O(N \log N)$ | $O(N)$ |
| **Universal Hashing** | $O(1)$ expected Patient ID lookup | $O(1)$ expected | $O(M)$ |

---

## 📊 Performance Benchmark Highlights

Measured on synthetic datasets:
- **Universal Hash Lookup Speedup**: **19.3x faster** than linear search.
- **Dinic Bed Allocation Execution Time**: **8.28 ms** for 1,000 patients; **57.91 ms** for 10,000 patients.
- **Emergency Triage Latency**: **< 10 ms** (Sub-50ms latency requirement satisfied).
- **Bed Utilization at Peak Load**: **93.1%** optimal bed allocation efficiency.

---

## 🔒 Academic & Privacy Statement
This project is built strictly for academic demonstration and evaluation in DSA-3 (Advanced Algorithms). All patient records, doctor profiles, and hospital wards are generated synthetically using a fixed random seed (`42`). No real personal health information (PHI) or live patient data is used.

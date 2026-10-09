# Review Demo Script & Algorithm Viva Guide

## AI-Driven Medical Appointment and Hospital Bed Allocation System
**DSA-3 Advanced Algorithms Project**

---

## Part 1: Reviewer Presentation & Live Demo Script (5-Minute Walkthrough)

### Step 1: System Introduction (30 seconds)
> "Good morning/afternoon respected examiners. Our project is an **AI-Driven Medical Appointment and Hospital Bed Allocation System**. The key insight of our work is that hospital resource allocation should not be solved as isolated problems. We connect string searching, doctor matching, ward allocation, emergency triage, and live re-optimisation on a single shared flow network."

### Step 2: Patient Registration & Fuzzy Search Demo (60 seconds)
1. Open the Web Interface at `http://127.0.0.1:8000`.
2. Navigate to **Patient Management**.
3. Point out the exact search box: Demonstrate **KMP** and **Z-Function** search for "Sharma".
4. Demonstrate misspelled name search using **Edit-Distance DP**: Search `"Jon Smith"` for `"John Smith"`. Highlight how the distance score is calculated and displayed.
5. Demonstrate **Universal Hashing O(1) Lookup**: Input `"PAT-00042"` to show instant lookup with collision metrics.

### Step 3: Appointment Scheduling Demo (60 seconds)
1. Navigate to **Doctor Scheduling**.
2. Click **"Run Bipartite Max-Flow Matcher"**.
3. Explain: *"The system builds a bipartite graph connecting Patient nodes to Doctor-Slot nodes. Edges exist only if specialty and shift availability constraints match. Max-flow maximizes total feasible appointments and prevents double-booking."*

### Step 4: Bed Allocation & Min-Cut Bottleneck Diagnosis Demo (60 seconds)
1. Navigate to **Wards & Bed Allocation**.
2. Click **"Run Dinic Max-Flow Allocator"**.
3. Point out the **Min-Cut Alert Banner**: Explain how residual graph reachability ($S_{reachable}$ vs $T_{unreachable}$) identifies the exact bottleneck ward (e.g. Cardiology ICU capacity saturation).

### Step 5: Emergency Triage & Live Discharge Re-optimisation (60 seconds)
1. Navigate to **Emergency Triage**.
2. Click **"Execute Greedy Triage Queue"**: Show how high-urgency (Level 1) patients get assigned within $< 10\text{ ms}$.
3. Navigate to **Admissions & Discharges**: Enter Patient ID and Bed ID to discharge. Click **"Discharge & Re-Optimise"** to show live residual graph augmentation in milliseconds.

---

## Part 2: Top 10 Viva Questions & Answers for Examination

### Q1: Why did you use Dinic's Algorithm instead of Edmonds-Karp for bed allocation?
**Answer**: Edmonds-Karp runs in $O(V \cdot E^2)$ time using BFS to find single shortest augmenting paths. Dinic's Algorithm constructs a **Level Graph** via BFS and uses DFS to push **Blocking Flows**, reducing worst-case complexity to $O(V^2 \cdot E)$. On unit network graphs (like our bed allocation network where edge capacities are 1), Dinic runs in $O(E \sqrt{V})$ time, making it significantly faster for large hospital datasets.

### Q2: How does the Minimum Cut help in hospital capacity planning?
**Answer**: According to the Max-Flow Min-Cut Theorem, the maximum flow value equals the capacity of the minimum cut. After Dinic reaches saturation, we perform a BFS on the residual graph from Source $S$. The edges cut between reachable nodes $S$ and unreachable nodes $T$ represent the exact capacity bottlenecks (e.g. Cardiology ICU bed limit). This provides hospital admins with an actionable diagnosis of which ward needs bed expansion.

### Q3: What is Universal Hashing and why is it superior to standard hash functions?
**Answer**: A standard deterministic hash function can suffer from worst-case $O(N)$ collisions if an adversary chooses key sequences that collide. A Universal Hash Family $H = \{ h_{a,b}(k) = ((a \cdot k + b) \pmod p) \pmod m \}$ selects coefficients $a, b$ uniformly at random at initialization. It mathematically guarantees that for any pair of distinct keys, the collision probability is $\le \frac{1}{m}$, ensuring $O(1)$ expected lookup time regardless of input keys.

### Q4: How does your Fuzzy Search handle misspelled patient names?
**Answer**: We implement **Levenshtein Edit-Distance Dynamic Programming**. The distance matrix $DP[i][j]$ evaluates the minimum number of character Insertions, Deletions, and Substitutions required to transform string $A$ into string $B$ in $O(|A| \cdot |B|)$ time. Candidate records are ranked by minimum edit distance, allowing misspelled names (e.g. `"Jon Smith"`) to match registered records (`"John Smith"`).

### Q5: How do KMP and Z-Function algorithms achieve $O(N + M)$ linear time search?
**Answer**: Both algorithms avoid quadratic backtracking by preprocessing the search pattern:
- **KMP** builds a Longest Prefix Suffix (LPS) array $\pi[i]$ in $O(M)$ time. When a mismatch occurs, it shifts the pattern using LPS information without rewinding the text pointer $i$.
- **Z-Function** constructs the concatenated string $P + \$ + T$ and computes array $Z[i]$ (the longest common prefix between $S$ and suffix starting at $i$) in $O(N+M)$ time using a sliding match window $[L, R]$.

### Q6: What is the role of Interval Dynamic Programming in your system?
**Answer**: Interval DP solves the **Weighted Interval Scheduling** problem. When a patient or doctor submits multiple overlapping time slot requests, we sort intervals by finish time, compute predecessor array $p[i]$ via binary search, and evaluate the recurrence $OPT[i] = \max(OPT[i-1], v_i + OPT[p[i]])$ in $O(N \log N)$ time to select the maximum priority non-overlapping subset.

### Q7: Why use a Greedy Approximation for emergency triage instead of full Max-Flow?
**Answer**: Emergency admissions have a strict latency budget ($< 50\text{ ms}$). Running full graph recomputations on large flow networks during sudden emergency surges can introduce delays. Our Priority-Based Greedy Approximation sorts emergency cases by priority score $S$ in $O(N \log N)$ time and immediately assigns free beds, achieving sub-10ms response latency while preserving high allocation quality.

### Q8: How does your system handle live patient discharges?
**Answer**: When a patient is discharged, their bed status updates to 'Available'. Instead of throwing away the state, the system performs live re-optimisation by re-augmenting the residual graph. It computes updated allocations for any pending patients and reports the exact assignment changes before and after re-optimisation.

### Q9: Is the AI Demand Forecast module making the allocation decisions?
**Answer**: No. The AI Demand Forecast module is a clearly separated experimental extension layer. It uses time-series trend regression to predict 7-day bed demand per ward to assist capacity planning. Operational allocation decisions remain strictly governed by exact algorithms (Dinic & Bipartite Max-Flow) to ensure deterministic fairness and constraint guarantees.

### Q10: How did you validate the accuracy of your flow algorithms?
**Answer**: On small input graphs, we cross-checked the outputs of Dinic and Bipartite Max-Flow against brute-force exhaustive search. On large synthetic datasets (up to 10,000 patients), we verified that capacity constraints and ward eligibility rules were strictly satisfied without any over-allocation or double-booking.

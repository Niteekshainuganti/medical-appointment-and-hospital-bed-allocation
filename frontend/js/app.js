/**
 * Hospital Resource Allocation System - Frontend JavaScript Application.
 * Handles API calls, tab switching, form submissions, live data updates, and Chart.js graphs.
 */

const API_BASE = "";

// Global State Cache
let state = {
  dashboard: null,
  patients: [],
  doctors: [],
  wards: [],
  beds: [],
  emergencies: [],
  benchmarks: null,
  aiForecast: null
};

document.addEventListener("DOMContentLoaded", () => {
  initNavigation();
  loadDashboardData();
});

/* Navigation & Tab Switcher */
function initNavigation() {
  const navItems = document.querySelectorAll(".nav-item");
  const tabViews = document.querySelectorAll(".tab-view");

  navItems.forEach(item => {
    item.addEventListener("click", () => {
      const targetTab = item.getAttribute("data-tab");

      navItems.forEach(n => n.classList.remove("active"));
      tabViews.forEach(v => v.classList.remove("active"));

      item.classList.add("active");
      const activeView = document.getElementById(targetTab);
      if (activeView) {
        activeView.classList.add("active");
        document.getElementById("page-title-text").innerText = item.innerText.trim();
        
        // Trigger tab-specific refresh
        switch (targetTab) {
          case "dashboard-view": loadDashboardData(); break;
          case "patients-view": loadPatientsData(); break;
          case "doctors-view": loadDoctorsData(); break;
          case "beds-view": loadBedsData(); break;
          case "emergency-view": loadEmergencyData(); break;
          case "analytics-view": loadAnalyticsData(); break;
          case "algo-lab-view": break;
        }
      }
    });
  });
}

/* Helper Fetch wrapper */
async function fetchAPI(endpoint, options = {}) {
  try {
    const res = await fetch(`${API_BASE}${endpoint}`, options);
    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || "API Request Failed");
    }
    return await res.json();
  } catch (err) {
    showToast(`Error: ${err.message}`, "danger");
    console.error("API Error:", err);
    return null;
  }
}

function showToast(msg, type = "success") {
  alert(`${type.toUpperCase()}: ${msg}`);
}

/* Dashboard Tab */
async function loadDashboardData() {
  const data = await fetchAPI("/api/analytics/dashboard-summary");
  if (!data) return;
  state.dashboard = data;

  document.getElementById("metric-patients").innerText = data.totals.patients;
  document.getElementById("metric-doctors").innerText = data.totals.doctors;
  document.getElementById("metric-appointments").innerText = data.totals.appointments;
  document.getElementById("metric-beds-occupied").innerText = `${data.totals.beds_occupied} / ${data.totals.beds_total}`;
  document.getElementById("metric-bed-utilization").innerText = `${data.performance.bed_utilization_pct}%`;
  document.getElementById("metric-emergencies").innerText = `${data.totals.emergencies_queued} Queued`;
  document.getElementById("metric-emergency-latency").innerText = `${data.performance.avg_emergency_latency_ms} ms`;

  // Render recent logs
  const logTable = document.getElementById("dashboard-logs-tbody");
  if (logTable) {
    logTable.innerHTML = data.recent_activity.map(l => `
      <tr>
        <td><span class="status-pill available">${l.event_type}</span></td>
        <td>${l.message}</td>
        <td>${l.execution_time_ms ? l.execution_time_ms + ' ms' : '-'}</td>
        <td>${l.timestamp}</td>
      </tr>
    `).join("");
  }
}

/* Patient Management Tab */
async function loadPatientsData() {
  const data = await fetchAPI("/api/patients?limit=100");
  if (!data) return;
  state.patients = data.patients;
  renderPatientsTable(data.patients);
}

function renderPatientsTable(patients) {
  const tbody = document.getElementById("patients-tbody");
  if (!tbody) return;

  tbody.innerHTML = patients.map(p => `
    <tr>
      <td><strong>${p.patient_id}</strong></td>
      <td>${p.name} ${p.edit_distance !== undefined ? `<span class="status-pill pending">Dist: ${p.edit_distance}</span>` : ''}</td>
      <td>${p.age} / ${p.gender}</td>
      <td>${p.phone || '-'}</td>
      <td><span class="badge-tag">${p.required_specialty}</span></td>
      <td>Urgency ${p.urgency_level}</td>
      <td><span class="status-pill ${p.status.includes('Admitted') ? 'admitted' : (p.status.includes('Scheduled') ? 'available' : 'pending')}">${p.status}</span></td>
    </tr>
  `).join("");
}

async function triggerExactSearch() {
  const query = document.getElementById("search-exact-input").value.trim();
  const algo = document.getElementById("search-algo-select").value;
  if (!query) return loadPatientsData();

  const res = await fetchAPI(`/api/patients/search/exact?q=${encodeURIComponent(query)}&algorithm=${algo}`);
  if (res) renderPatientsTable(res.results);
}

async function triggerFuzzySearch() {
  const query = document.getElementById("search-fuzzy-input").value.trim();
  const maxDist = document.getElementById("fuzzy-dist-slider").value;
  if (!query) return loadPatientsData();

  const res = await fetchAPI(`/api/patients/search/fuzzy?q=${encodeURIComponent(query)}&max_distance=${maxDist}`);
  if (res) renderPatientsTable(res.results);
}

async function triggerUniversalHashLookup() {
  const pid = document.getElementById("search-hash-input").value.trim();
  if (!pid) return;

  const res = await fetchAPI(`/api/patients/lookup/${encodeURIComponent(pid)}`);
  if (res && res.found) {
    renderPatientsTable([res.patient]);
    document.getElementById("hash-stats-box").innerHTML = `
      <div style="font-size:0.8rem; color:#94a3b8; margin-top:0.5rem;">
        ⚡ <strong>Universal Hash Lookup Result:</strong> Found in ${res.execution_time_ms}ms | Load Factor: ${res.hash_stats.load_factor} | Total Collisions: ${res.hash_stats.total_collisions}
      </div>
    `;
  }
}

async function handleAddPatientForm(e) {
  e.preventDefault();
  const body = {
    name: document.getElementById("p-name").value,
    age: parseInt(document.getElementById("p-age").value),
    gender: document.getElementById("p-gender").value,
    phone: document.getElementById("p-phone").value,
    required_specialty: document.getElementById("p-specialty").value,
    required_ward_type: document.getElementById("p-ward-type").value,
    urgency_level: parseInt(document.getElementById("p-urgency").value)
  };

  const res = await fetchAPI("/api/patients", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body)
  });

  if (res && res.status === "Success") {
    showToast(`Patient ${res.patient.patient_id} registered successfully!`);
    loadPatientsData();
  }
}

/* Doctor & Appointments Tab */
async function loadDoctorsData() {
  const docs = await fetchAPI("/api/doctors");
  const apps = await fetchAPI("/api/appointments");

  if (docs) {
    document.getElementById("doctors-tbody").innerHTML = docs.doctors.map(d => `
      <tr>
        <td><strong>${d.doctor_id}</strong></td>
        <td>${d.name}</td>
        <td><span class="badge-tag">${d.specialty}</span></td>
        <td>${d.room_no}</td>
        <td>${d.free_slots_count} Available</td>
      </tr>
    `).join("");
  }

  if (apps) {
    document.getElementById("appointments-tbody").innerHTML = apps.appointments.map(a => `
      <tr>
        <td><strong>${a.appointment_id}</strong></td>
        <td>${a.patient_name} (${a.patient_id})</td>
        <td>${a.doctor_name} (${a.specialty})</td>
        <td>${a.start_time} - ${a.end_time}</td>
        <td>${a.room_no}</td>
        <td><span class="status-pill available">${a.status}</span></td>
      </tr>
    `).join("");
  }
}

async function triggerBipartiteMatching() {
  const res = await fetchAPI("/api/appointments/match/bipartite-max-flow", { method: "POST" });
  if (res) {
    showToast(`Bipartite Max-Flow Matched ${res.total_matched} / ${res.total_requested} requests (${res.match_rate}%) in ${res.execution_time_ms}ms.`);
    loadDoctorsData();
  }
}

/* Wards & Bed Allocation Tab */
async function loadBedsData() {
  const wardsRes = await fetchAPI("/api/beds/wards");
  const bedsRes = await fetchAPI("/api/beds");

  if (wardsRes) {
    document.getElementById("wards-summary-grid").innerHTML = wardsRes.wards.map(w => `
      <div class="panel" style="margin-bottom:0;">
        <div style="font-weight:700;">${w.ward_name} (${w.ward_type})</div>
        <div style="font-size:0.8rem; color:#94a3b8; margin-top:0.25rem;">Capacity: ${w.total_beds} Beds | Occupied: ${w.occupied_beds}</div>
        <div style="margin-top:0.5rem; background:#0f172a; height:6px; border-radius:3px; overflow:hidden;">
          <div style="width:${Math.round((w.occupied_beds/w.total_beds)*100)}%; background:var(--primary); height:100%;"></div>
        </div>
      </div>
    `).join("");
  }

  if (bedsRes) {
    document.getElementById("beds-map-grid").innerHTML = bedsRes.beds.map(b => `
      <div class="bed-box ${b.status.toLowerCase()}">
        <div class="bed-num">${b.bed_number}</div>
        <div style="font-size:0.75rem; margin-top:0.25rem;">
          <span class="status-pill ${b.status === 'Available' ? 'available' : 'occupied'}">${b.status}</span>
        </div>
        <div class="bed-patient">${b.patient_name || 'Free Bed'}</div>
      </div>
    `).join("");
  }
}

async function triggerDinicBedAllocation() {
  const res = await fetchAPI("/api/beds/allocate/dinic-max-flow", { method: "POST" });
  if (res) {
    showToast(`Dinic Max-Flow Allocated ${res.total_allocated} beds in ${res.execution_time_ms}ms.`);
    
    // Display Min-Cut Bottleneck diagnosis
    const bc = res.min_cut_bottleneck;
    if (bc) {
      document.getElementById("min-cut-alert-box").style.display = "block";
      document.getElementById("min-cut-explanation-text").innerText = bc.summary_explanation;
    }

    loadBedsData();
  }
}

async function handleDischargePatient() {
  const pid = document.getElementById("discharge-patient-id").value.trim();
  const bid = document.getElementById("discharge-bed-id").value.trim();
  if (!pid || !bid) return alert("Please specify Patient ID and Bed ID to discharge.");

  const res = await fetchAPI("/api/beds/discharge", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ patient_id: pid, bed_id: bid })
  });

  if (res) {
    showToast(`Discharged ${pid}. Re-optimisation pass ran in ${res.reoptimisation_execution_time_ms}ms!`);
    loadBedsData();
  }
}

/* Emergency Triage Tab */
async function loadEmergencyData() {
  const res = await fetchAPI("/api/emergency");
  if (!res) return;

  document.getElementById("emergency-tbody").innerHTML = res.cases.map(e => `
    <tr>
      <td><strong>${e.emergency_id}</strong></td>
      <td>${e.name} (${e.patient_id})</td>
      <td><span class="status-pill ${e.urgency_level <= 2 ? 'occupied' : 'pending'}">Urgency ${e.urgency_level}</span></td>
      <td><span class="badge-tag">${e.required_specialty}</span></td>
      <td>${e.vital_signs_severity}</td>
      <td><span class="status-pill ${e.status === 'Admitted' ? 'admitted' : 'pending'}">${e.status}</span></td>
      <td>${e.latency_ms ? e.latency_ms + ' ms' : 'In Queue'}</td>
    </tr>
  `).join("");
}

async function triggerGreedyTriage() {
  const res = await fetchAPI("/api/emergency/triage/greedy-approximation", { method: "POST" });
  if (res) {
    showToast(`Greedy Triage Processed Queue in ${res.latency_ms}ms! Assigned ${res.total_assigned} emergency beds.`);
    loadEmergencyData();
  }
}

async function handleAddEmergencyForm(e) {
  e.preventDefault();
  const body = {
    name: document.getElementById("em-name").value,
    urgency_level: parseInt(document.getElementById("em-urgency").value),
    required_specialty: document.getElementById("em-specialty").value,
    vital_signs_severity: parseFloat(document.getElementById("em-vitals").value)
  };

  const res = await fetchAPI("/api/emergency/add", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body)
  });

  if (res) {
    showToast(`Emergency patient registered! Triage latency: ${res.latency_ms}ms.`);
    loadEmergencyData();
  }
}

/* Analytics & AI Forecast Tab */
async function loadAnalyticsData() {
  const forecast = await fetchAPI("/api/analytics/ai-demand-forecast");
  const benchmarks = await fetchAPI("/api/analytics/benchmark-results");

  if (forecast) {
    document.getElementById("ai-forecast-container").innerHTML = `
      <div style="font-size:0.85rem; color:#94a3b8; margin-bottom:1rem;">
        🤖 <em>${forecast.disclaimer}</em>
      </div>
      <div class="metrics-grid">
        ${forecast.ward_forecasts.map(w => `
          <div class="metric-card ${w.shortage_risk === 'HIGH' ? 'danger' : 'accent'}">
            <div class="metric-label">${w.ward_name}</div>
            <div class="metric-value">${w.predicted_7day_demand} Demand</div>
            <div class="metric-sub">Current: ${w.current_occupancy_pct}% | Risk: <strong>${w.shortage_risk}</strong></div>
          </div>
        `).join("")}
      </div>
    `;
  }

  if (benchmarks) {
    document.getElementById("benchmark-json-view").innerText = JSON.stringify(benchmarks, null, 2);
  }
}

/* Algorithm Lab Interactive Runner */
async function runLabKMP() {
  const text = document.getElementById("lab-kmp-text").value;
  const pat = document.getElementById("lab-kmp-pattern").value;

  const res = await fetchAPI(`/api/analytics/algorithm-lab/kmp?text=${encodeURIComponent(text)}&pattern=${encodeURIComponent(pat)}`, { method: "POST" });
  if (res) {
    document.getElementById("lab-kmp-output").innerHTML = `
      <div style="font-size:0.85rem;">
        <strong>LPS Array:</strong> [${res.lps_array.join(", ")}]<br>
        <strong>Match Positions (0-indexed):</strong> [${res.matches_0indexed.join(", ")}]
      </div>
    `;
  }
}

async function runLabEditDistance() {
  const str1 = document.getElementById("lab-ed-str1").value;
  const str2 = document.getElementById("lab-ed-str2").value;

  const res = await fetchAPI(`/api/analytics/algorithm-lab/edit-distance?str1=${encodeURIComponent(str1)}&str2=${encodeURIComponent(str2)}`, { method: "POST" });
  if (res) {
    let tableHtml = `<table style="font-size:0.75rem; text-align:center;"><tr><th></th><th>""</th>`;
    for (let c of str2) tableHtml += `<th>${c}</th>`;
    tableHtml += `</tr>`;

    for (let i = 0; i < res.dp_table.length; i++) {
      tableHtml += `<tr><th>${i === 0 ? '""' : str1[i-1]}</th>`;
      for (let j = 0; j < res.dp_table[i].length; j++) {
        tableHtml += `<td><strong>${res.dp_table[i][j]}</strong></td>`;
      }
      tableHtml += `</tr>`;
    }
    tableHtml += `</table>`;

    document.getElementById("lab-ed-output").innerHTML = `
      <div style="font-size:0.85rem; margin-bottom:0.5rem;">
        <strong>Levenshtein Edit Distance:</strong> ${res.edit_distance}
      </div>
      ${tableHtml}
    `;
  }
}

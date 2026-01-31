let currentTab = "raw-data",
    autoRefreshInterval = null,
    dataTimerSeconds = 0,
    mlTimerSeconds = 0;
function switchTab(e) {
    ((currentTab = e),
        document.querySelectorAll(".tab-btn").forEach((e) => {
            e.classList.remove("active");
        }),
        event.target.closest(".tab-btn").classList.add("active"),
        document.querySelectorAll(".tab-content").forEach((e) => {
            e.classList.remove("active");
        }),
        document.getElementById(e).classList.add("active"),
        autoRefreshInterval && clearInterval(autoRefreshInterval),
        "raw-data" === e
            ? (fetchData(),
                fetchStats(),
                startDataTimer(),
                (autoRefreshInterval = setInterval(() => {
                    (fetchData(), fetchStats());
                }, 5e3)))
            : "ml-insights" === e &&
            (fetchMLInsights(),
                startMLTimer(),
                (autoRefreshInterval = setInterval(() => {
                    fetchMLInsights();
                }, 1e4))));
}
async function fetchData() {
    const e = document.getElementById("dataTableBody"),
        t = document.getElementById("dataStatus");
    ((t.innerHTML = "<span>●</span><span>Loading...</span>"),
        (t.className = "status-badge warning"));
    try {
        const a = await fetch("/data"),
            s = await a.json();
        s.success && s.data && s.data.length > 0
            ? (displayDataTable(s.data),
                displayLatestReading(s.data[0]),
                (t.innerHTML = "<span>●</span><span>Live</span>"),
                (t.className = "status-badge success"),
                (dataTimerSeconds = 0))
            : ((e.innerHTML =
                '<tr><td colspan="10" class="no-data"><div class="no-data-icon">📭</div><p>No data available</p></td></tr>'),
                (t.innerHTML = "<span>●</span><span>No Data</span>"),
                (t.className = "status-badge warning"));
    } catch (a) {
        (console.error("Error fetching data:", a),
            (e.innerHTML = `<tr><td colspan="10" class="no-data"><div class="no-data-icon">⚠️</div><p>Error: ${a.message}</p></td></tr>`),
            (t.innerHTML = "<span>●</span><span>Error</span>"),
            (t.className = "status-badge error"));
    }
}
function displayDataTable(e) {
    document.getElementById("dataTableBody").innerHTML = e
        .map(
            (e) =>
                `<tr><td>${formatTimestamp(e.timestamp)}</td><td><strong>${e.sensor_id || "N/A"}</strong></td><td>${formatNumber(e.voltage)} V</td><td>${formatNumber(e.current)} A</td><td>${formatNumber(e.temperature)} °C</td><td>${formatNumber(e.core_temp)} °C</td><td>${formatNumber(e.surface_temp)} °C</td><td>${formatNumber(e.soc)}%</td><td>${formatNumber(e.humidity)}%</td><td>${e.battery_location || "N/A"}</td></tr>`,
        )
        .join("");
}
function displayLatestReading(e) {
    document.getElementById("latestReading").innerHTML =
        `<div class="info-grid"><div class="info-item"><div class="info-label">Sensor ID</div><div class="info-value">${e.sensor_id || "N/A"}</div></div><div class="info-item"><div class="info-label">Voltage</div><div class="info-value">${formatNumber(e.voltage)} V</div></div><div class="info-item"><div class="info-label">Current</div><div class="info-value">${formatNumber(e.current)} A</div></div><div class="info-item"><div class="info-label">Temperature</div><div class="info-value">${formatNumber(e.temperature)} °C</div></div><div class="info-item"><div class="info-label">Core Temp</div><div class="info-value">${formatNumber(e.core_temp)} °C</div></div><div class="info-item"><div class="info-label">Surface Temp</div><div class="info-value">${formatNumber(e.surface_temp)} °C</div></div><div class="info-item"><div class="info-label">SOC</div><div class="info-value">${formatNumber(e.soc)}%</div></div><div class="info-item"><div class="info-label">Humidity</div><div class="info-value">${formatNumber(e.humidity)}%</div></div><div class="info-item"><div class="info-label">Heat Index</div><div class="info-value">${formatNumber(e.heat_index)} °C</div></div><div class="info-item"><div class="info-label">Location</div><div class="info-value" style="font-size:.9rem">${e.battery_location || "N/A"}</div></div><div class="info-item"><div class="info-label">Ambient Temp</div><div class="info-value">${formatNumber(e.ambient_temp)} °C</div></div><div class="info-item"><div class="info-label">Timestamp</div><div class="info-value" style="font-size:.85rem">${formatTimestamp(e.timestamp)}</div></div></div>`;
}
async function fetchStats() {
    try {
        const e = await fetch("/data/stats"),
            t = await e.json();
        if (t.success && t.stats) {
            const e = t.stats;
            ((document.getElementById("totalRecords").textContent =
                e.total_records || 0),
                (document.getElementById("avgVoltage").innerHTML =
                    `${formatNumber(e.avg_voltage)}<span class="stat-unit">V</span>`),
                (document.getElementById("avgCurrent").innerHTML =
                    `${formatNumber(e.avg_current)}<span class="stat-unit">A</span>`),
                (document.getElementById("avgTemp").innerHTML =
                    `${formatNumber(e.avg_temperature)}<span class="stat-unit">°C</span>`));
        }
    } catch (e) {
        console.error("Error fetching stats:", e);
    }
}
async function fetchMLInsights() {
    const e = document.getElementById("mlInsightContainer"),
        t = document.getElementById("mlStatus");
    ((e.innerHTML = '<div class="spinner"></div>'),
        (t.innerHTML = "<span>●</span><span>Analyzing...</span>"),
        (t.className = "status-badge warning"));
    try {
        const a = await fetch("/ml/predict"),
            s = await a.json();
        
        // Handle empty database
        if (s.empty_database) {
            (e.innerHTML = `<div class="no-data"><div class="no-data-icon">📭</div><h4>Database is Empty</h4><p>${s.message}</p></div>`),
            (t.innerHTML = "<span>●</span><span>No Data</span>"),
            (t.className = "status-badge warning");
            return;
        }
        
        // Handle ML server error
        if (s.ml_server_error) {
            (e.innerHTML = `<div class="no-data"><div class="no-data-icon">🔌</div><h4>ML Server Offline</h4><p>${s.message}</p><p style="font-size:.9rem;margin-top:1rem;color:#6c757d">Run: <code>python ml_server/app.py</code></p></div>`),
            (t.innerHTML = "<span>●</span><span>Offline</span>"),
            (t.className = "status-badge error");
            return;
        }
        
        // Handle general errors
        if (s.error) {
            (e.innerHTML = `<div class="no-data"><div class="no-data-icon">⚠️</div><h4>Error</h4><p>${s.message}</p></div>`),
            (t.innerHTML = "<span>●</span><span>Error</span>"),
            (t.className = "status-badge error");
            return;
        }
        
        // Success - display ML insights
        if (!s.success || !s.ml_prediction)
            throw new Error(s.message || "Failed to get ML prediction");
        (displayMLInsights(s),
            (t.innerHTML = "<span>●</span><span>Live</span>"),
            (t.className = "status-badge success"),
            (mlTimerSeconds = 0));
    } catch (a) {
        (console.error("Error fetching ML insights:", a),
            (e.innerHTML = `<div class="no-data"><div class="no-data-icon">⚠️</div><h4>Error Loading ML Insights</h4><p>${a.message}</p></div>`),
            (t.innerHTML = "<span>●</span><span>Error</span>"),
            (t.className = "status-badge error"));
    }
}
function displayMLInsights(e) {
    const t = document.getElementById("mlInsightContainer"),
        a = e.ml_prediction,
        s = e.sensor_data,
        n =
            "object" == typeof a.solution
                ? a.solution
                : {
                    action: a.solution || "No recommendation available",
                    severity: "MEDIUM",
                    emoji: "❓",
                },
        r = { HIGH: "LOW", MEDIUM: "MEDIUM", LOW: "HIGH" },
        o = n.severity || r[a.reliability] || "MEDIUM",
        i =
            n.emoji ||
            ("CRITICAL" === o
                ? "🚨"
                : "HIGH" === o
                    ? "⚠️"
                    : "MEDIUM" === o
                        ? "🔶"
                        : "✅");
    let d = `<div class="ml-header"><div class="prediction-emoji">${i}</div><div class="prediction-info"><div class="prediction-title">BATTERY STATUS: ${a.prediction || "UNKNOWN"}</div><span class="severity-badge severity-${o}">${o} PRIORITY</span></div></div><div class="confidence-section"><div class="section-title">📈 Prediction Confidence</div><div class="confidence-bar"><div class="confidence-fill" style="width:${a.confidence || 0}%">${formatNumber(a.confidence)}%</div></div><div style="display:flex;justify-content:space-between;margin-top:.5rem;font-size:.9rem;color:#6c757d"><span>Model Reliability: <strong>${a.reliability || "N/A"}</strong></span><span>Model Accuracy: <strong>${formatNumber(100 * a.model_accuracy)}%</strong></span></div></div><div class="action-box"><h4>💡 Recommended Action</h4><p>${n.action}</p></div><div class="section-title">🔍 Sensor Context</div><div class="info-grid"><div class="info-item"><div class="info-label">Sensor ID</div><div class="info-value">${s.sensor_id || "N/A"}</div></div><div class="info-item"><div class="info-label">Voltage</div><div class="info-value">${formatNumber(s.voltage)} V</div></div><div class="info-item"><div class="info-label">Current</div><div class="info-value">${formatNumber(s.current)} A</div></div><div class="info-item"><div class="info-label">Temperature</div><div class="info-value">${formatNumber(s.temperature)} °C</div></div><div class="info-item"><div class="info-label">Core Temp</div><div class="info-value">${formatNumber(s.core_temp)} °C</div></div><div class="info-item"><div class="info-label">SOC</div><div class="info-value">${formatNumber(s.soc)}%</div></div><div class="info-item"><div class="info-label">Humidity</div><div class="info-value">${formatNumber(s.humidity)}%</div></div></div>`;
    (a.probabilities &&
        Object.keys(a.probabilities).length > 0 &&
        (d += `<div class="probabilities-section"><div class="section-title">📊 Class Probabilities</div>${Object.entries(
            a.probabilities,
        )
            .map(
                ([e, t]) =>
                    `<div class="prob-item"><div class="prob-header"><span class="prob-label">${e}</span><span class="prob-value">${formatNumber(t)}%</span></div><div class="prob-bar"><div class="prob-bar-fill" style="width:${t}%"></div></div></div>`,
            )
            .join("")}</div>`),
        (t.innerHTML = d));
}
function exportData() {
    fetch("/data")
        .then((e) => e.json())
        .then((e) => {
            if (e.success && e.data) {
                const t = convertToCSV(e.data);
                downloadCSV(t, "battery_data.csv");
            }
        })
        .catch((e) => {
            (console.error("Error exporting data:", e),
                alert("Failed to export data"));
        });
}
function convertToCSV(e) {
    if (0 === e.length) return "";
    const t = Object.keys(e[0]),
        a = e.map((e) =>
            t
                .map((t) => {
                    const a = e[t];
                    return "string" == typeof a ? `"${a}"` : a;
                })
                .join(","),
        );
    return [t.join(","), ...a].join("\n");
}
function downloadCSV(e, t) {
    const a = new Blob([e], { type: "text/csv" }),
        s = window.URL.createObjectURL(a),
        n = document.createElement("a");
    ((n.href = s),
        (n.download = t),
        document.body.appendChild(n),
        n.click(),
        document.body.removeChild(n),
        window.URL.revokeObjectURL(s));
}
function startDataTimer() {
    ((dataTimerSeconds = 0),
        setInterval(() => {
            if ("raw-data" === currentTab) {
                dataTimerSeconds++;
                const e = document.getElementById("dataTimer");
                e && (e.textContent = `Updated ${dataTimerSeconds}s ago`);
            }
        }, 1e3));
}
function startMLTimer() {
    ((mlTimerSeconds = 0),
        setInterval(() => {
            if ("ml-insights" === currentTab) {
                mlTimerSeconds++;
                const e = document.getElementById("mlTimer");
                e && (e.textContent = `Updated ${mlTimerSeconds}s ago`);
            }
        }, 1e3));
}
function formatNumber(e) {
    return null == e ? "N/A" : "number" == typeof e ? e.toFixed(2) : e;
}
function formatTimestamp(e) {
    return e
        ? new Date(e).toLocaleString("en-US", {
            month: "short",
            day: "2-digit",
            year: "numeric",
            hour: "2-digit",
            minute: "2-digit",
            second: "2-digit",
        })
        : "N/A";
}
function getSeverity(e) {
    return (
        {
            Alarm: "CRITICAL",
            Warning: "HIGH",
            Watch: "MEDIUM",
            Normal: "LOW",
        }[e] || "MEDIUM"
    );
}
document.addEventListener("DOMContentLoaded", () => {
    (fetchData(),
        fetchStats(),
        startDataTimer(),
        (autoRefreshInterval = setInterval(() => {
            "raw-data" === currentTab && (fetchData(), fetchStats());
        }, 5e3)));
});

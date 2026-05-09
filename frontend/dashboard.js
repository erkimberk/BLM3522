/**
 * Smart City Dashboard JavaScript
 * Real-time sensör verisi görselleştirmesi
 */

// Configuration
const API_BASE = "http://localhost:5000/api";
const DEFAULT_INTERVAL = 10000; // 10 saniye

// Chart instances
let charts = {
    traffic: null,
    air: null,
    trash: null,
};

// Data storage
let sensorData = {
    traffic: [],
    air: [],
    trash: [],
};

// Auto-refresh state
let autoRefreshEnabled = false;
let autoRefreshInterval = null;

// Initialize on page load
document.addEventListener("DOMContentLoaded", () => {
    console.log("🚀 Dashboard initialized");
    initializeCharts();
    loadData();
    setupEventListeners();
    checkAPIHealth();
});

/**
 * Initialize Chart.js charts
 */
function initializeCharts() {
    const chartConfig = {
        type: "line",
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false },
            },
            scales: {
                y: {
                    beginAtZero: true,
                    max: 100,
                    ticks: { stepSize: 20 },
                },
                x: { display: false },
            },
        },
    };

    // Traffic Light Chart
    charts.traffic = new Chart(document.getElementById("traffic-chart"), {
        ...chartConfig,
        data: {
            labels: [],
            datasets: [
                {
                    label: "Yoğunluk %",
                    data: [],
                    borderColor: "#ff6b6b",
                    backgroundColor: "rgba(255, 107, 107, 0.1)",
                    borderWidth: 2,
                    tension: 0.4,
                },
            ],
        },
    });

    // Air Quality Chart
    charts.air = new Chart(document.getElementById("air-chart"), {
        ...chartConfig,
        data: {
            labels: [],
            datasets: [
                {
                    label: "PM2.5 µg/m³",
                    data: [],
                    borderColor: "#4ecdc4",
                    backgroundColor: "rgba(78, 205, 196, 0.1)",
                    borderWidth: 2,
                    tension: 0.4,
                },
            ],
        },
    });

    // Trash Bin Chart
    charts.trash = new Chart(document.getElementById("trash-chart"), {
        ...chartConfig,
        data: {
            labels: [],
            datasets: [
                {
                    label: "Doluluk %",
                    data: [],
                    borderColor: "#ffa502",
                    backgroundColor: "rgba(255, 165, 2, 0.1)",
                    borderWidth: 2,
                    tension: 0.4,
                },
            ],
        },
    });
}

/**
 * Setup event listeners
 */
function setupEventListeners() {
    // Refresh button
    document.getElementById("refresh-btn").addEventListener("click", loadData);

    // Auto-refresh button
    document
        .getElementById("auto-refresh-btn")
        .addEventListener("click", toggleAutoRefresh);

    // Update interval select
    document
        .getElementById("update-interval")
        .addEventListener("change", (e) => {
            if (autoRefreshEnabled) {
                toggleAutoRefresh(); // Stop
                const interval = parseInt(e.target.value) * 1000;
                setTimeout(toggleAutoRefresh, 100); // Restart with new interval
            }
        });
}

/**
 * Toggle auto-refresh
 */
function toggleAutoRefresh() {
    autoRefreshEnabled = !autoRefreshEnabled;
    const btn = document.getElementById("auto-refresh-btn");

    if (autoRefreshEnabled) {
        btn.textContent = "⏸ Otomatik Güncelle Durdur";
        btn.classList.add("active");

        const interval = parseInt(document.getElementById("update-interval").value) * 1000;
        autoRefreshInterval = setInterval(loadData, interval);
        console.log(`✅ Auto-refresh başladı (${interval / 1000}s)`);
    } else {
        btn.textContent = "▶ Otomatik Güncelle Başlat";
        btn.classList.remove("active");
        clearInterval(autoRefreshInterval);
        console.log("⏹ Auto-refresh durduruldu");
    }
}

/**
 * Check API health
 */
function checkAPIHealth() {
    fetch(`${API_BASE}/health`)
        .then((response) => response.json())
        .then((data) => {
            document.getElementById("api-status").textContent = "✅ Bağlı";
            document.getElementById("api-version").textContent = data.version || "1.0";
            document.getElementById("db-status").textContent =
                data.database === "connected" ? "✅ Bağlı" : "❌ Kesildi";
        })
        .catch((error) => {
            console.error("❌ Health check failed:", error);
            document.getElementById("api-status").textContent = "❌ Bağlı Değil";
        });
}

/**
 * Load all data from API
 */
async function loadData() {
    console.log("📡 Verileri yükle...");

    try {
        // Load alerts
        loadAlerts();

        // Load sensor data (parallel)
        await Promise.all([
            loadSensorData("traffic_light"),
            loadSensorData("air_quality"),
            loadSensorData("trash_bin"),
        ]);

        // Load statistics
        await Promise.all([
            loadStatistics("traffic_light", "traffic-light-001"),
            loadStatistics("air_quality", "air-quality-001"),
            loadStatistics("trash_bin", "trash-bin-001"),
        ]);

        updateLastRefreshTime();
    } catch (error) {
        console.error("❌ Veri yükleme hatası:", error);
    }
}

/**
 * Load sensor data for a specific type
 */
async function loadSensorData(sensorType) {
    try {
        const response = await fetch(`${API_BASE}/sensors/${sensorType}?limit=20`);
        const data = await response.json();

        if (data.data && data.data.length > 0) {
            sensorData[sensorType] = data.data;
            updateSensorCard(sensorType);
            updateChart(sensorType);
        }
    } catch (error) {
        console.error(`❌ Error loading ${sensorType}:`, error);
    }
}

/**
 * Load statistics for a device
 */
async function loadStatistics(sensorType, deviceId) {
    try {
        const response = await fetch(`${API_BASE}/stats/${sensorType}/${deviceId}`);
        const data = await response.json();

        if (data.statistics) {
            updateStatistics(sensorType, data.statistics);
        }
    } catch (error) {
        console.error(`❌ Error loading stats for ${deviceId}:`, error);
    }
}

/**
 * Load and display alerts
 */
async function loadAlerts() {
    try {
        const response = await fetch(`${API_BASE}/alerts`);
        const data = await response.json();

        const container = document.getElementById("alerts-container");

        if (data.alerts && data.alerts.length > 0) {
            container.innerHTML = data.alerts
                .map(
                    (alert) => `
                <div class="alert alert-${alert.severity}">
                    <div class="alert-header">
                        <span class="severity-badge severity-${alert.severity}">
                            ${alert.severity.toUpperCase()}
                        </span>
                        <span class="timestamp">${formatTime(alert.timestamp)}</span>
                    </div>
                    <p class="alert-message">${alert.message}</p>
                    <div class="alert-details">
                        <span>Cihaz: ${alert.device_id}</span>
                        <span>Değer: ${alert.value.toFixed(2)}</span>
                        <span>Eşik: ${alert.threshold}</span>
                    </div>
                </div>
            `
                )
                .join("");
        } else {
            container.innerHTML = '<div class="no-alerts">✅ Aktif uyarı yok</div>';
        }
    } catch (error) {
        console.error("❌ Error loading alerts:", error);
    }
}

/**
 * Update sensor card UI
 */
function updateSensorCard(sensorType) {
    const latest = sensorData[sensorType][0];

    if (!latest) return;

    if (sensorType === "traffic_light") {
        document.getElementById("traffic-value").textContent = latest.value.toFixed(1);
        document.getElementById("traffic-location").textContent =
            latest.metadata.location || "Unknown";

        const status = latest.metadata.status || "unknown";
        document.getElementById("traffic-status").textContent =
            status === "green"
                ? "🟢 Düşük"
                : status === "yellow"
                  ? "🟡 Orta"
                  : "🔴 Yüksek";
    } else if (sensorType === "air_quality") {
        document.getElementById("air-value").textContent = latest.value.toFixed(2);
        document.getElementById("air-aqi").textContent =
            latest.metadata.aqi || "N/A";
        document.getElementById("air-category").textContent =
            latest.metadata.category || "Unknown";
    } else if (sensorType === "trash_bin") {
        document.getElementById("trash-value").textContent = latest.value.toFixed(1);
        document.getElementById("trash-weight").textContent =
            (latest.metadata.weight_kg || 0).toFixed(2);

        const urgency = latest.metadata.urgency || "unknown";
        const urgencyEmoji = {
            low: "🟢 Düşük",
            medium: "🟡 Orta",
            high: "🟠 Yüksek",
            critical: "🔴 Acil",
        };
        document.getElementById("trash-urgency").textContent =
            urgencyEmoji[urgency] || urgency;
    }
}

/**
 * Update chart with new data
 */
function updateChart(sensorType) {
    const data = sensorData[sensorType];
    if (!data || data.length === 0) return;

    const values = data.map((d) => d.value).reverse();
    const labels = data.map((d) => formatTime(d.timestamp)).reverse();

    const chart = charts[sensorType];
    chart.data.labels = labels;
    chart.data.datasets[0].data = values;
    chart.update();
}

/**
 * Update statistics display
 */
function updateStatistics(sensorType, stats) {
    const prefix =
        sensorType === "traffic_light"
            ? "traffic"
            : sensorType === "air_quality"
              ? "air"
              : "trash";

    if (stats.min !== null) document.getElementById(`${prefix}-min`).textContent =
        stats.min.toFixed(2);
    if (stats.max !== null) document.getElementById(`${prefix}-max`).textContent =
        stats.max.toFixed(2);
    if (stats.avg !== null) document.getElementById(`${prefix}-avg`).textContent =
        stats.avg.toFixed(2);
    if (stats.count !== null) document.getElementById(`${prefix}-count`).textContent =
        stats.count;
}

/**
 * Update last refresh time
 */
function updateLastRefreshTime() {
    const now = new Date();
    const timeStr = now.toLocaleTimeString("tr-TR");
    document.getElementById("last-update").textContent =
        `Son güncelleme: ${timeStr}`;
    document.getElementById("last-refresh").textContent = timeStr;
}

/**
 * Format timestamp to HH:MM:SS
 */
function formatTime(timestamp) {
    if (!timestamp) return "--:--";
    const date = new Date(timestamp);
    return date.toLocaleTimeString("tr-TR").substring(0, 8);
}

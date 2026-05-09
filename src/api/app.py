"""
Flask REST API for Smart City IoT Application
DynamoDB'deki verileri REST endpoint'ler aracılığıyla sunma

Endpoints:
- GET /api/sensors/{sensor_type} - Son ölçümleri al
- GET /api/sensors/{sensor_type}/{device_id} - Belirtilen cihazın verisi
- GET /api/alerts - Aktif uyarılar
- GET /api/stats/{sensor_type}/{device_id} - İstatistikler
- GET /api/health - Health check
"""

from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import sys
from pathlib import Path
import logging
from datetime import datetime, timedelta
import json

# src/utils'ı path'e ekle
sys.path.insert(0, str(Path(__file__).parent.parent / "utils"))

# Import our modules
try:
    from dynamodb_query import SensorDataQuery
except ImportError:
    print("⚠️  Warning: DynamoDB Query module not found")
    SensorDataQuery = None

# Flask app oluştur
app = Flask(__name__, static_folder="../../frontend", static_url_path="/static")
CORS(app)  # Cross-Origin Resource Sharing aktif

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# DynamoDB Query instance
db_query = None

try:
    db_query = SensorDataQuery(region="eu-central-1")
    logger.info("✅ DynamoDB Query initialized")
except Exception as e:
    logger.warning(f"⚠️  DynamoDB connection failed: {e}")


# ============================================================
# HEALTH CHECK
# ============================================================


@app.route("/api/health", methods=["GET"])
def health_check():
    """API sağlık kontrolü"""
    db_status = "connected" if db_query else "disconnected"

    return jsonify(
        {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "database": db_status,
            "version": "1.0.0",
        }
    )


# ============================================================
# SENSÖR VERİSİ ENDPOİNT'LERİ
# ============================================================


@app.route("/api/sensors/<sensor_type>", methods=["GET"])
def get_sensor_latest(sensor_type):
    """
    Belirtilen sensor type'ın en son ölçümlerini al
    
    Query Parameters:
    - limit: Kaç adet (default: 10)
    
    Example: GET /api/sensors/traffic_light?limit=20
    """
    if not db_query:
        return jsonify({"error": "Database not connected"}), 503

    try:
        limit = request.args.get("limit", 10, type=int)
        limit = min(limit, 100)  # Max 100

        readings = db_query.get_latest_readings(sensor_type, limit=limit)

        # Verileri format et
        formatted = []
        for r in readings:
            formatted.append(
                {
                    "device_id": r.get("device_id"),
                    "value": r.get("value"),
                    "timestamp": r.get("timestamp"),
                    "location": r.get("location"),
                    "metadata": r.get("metadata", {}),
                }
            )

        return jsonify(
            {
                "sensor_type": sensor_type,
                "count": len(formatted),
                "data": formatted,
            }
        )

    except Exception as e:
        logger.error(f"❌ Error: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/sensors/<sensor_type>/<device_id>", methods=["GET"])
def get_sensor_by_device(sensor_type, device_id):
    """
    Belirtilen cihazın son ölçümlerini al
    
    Query Parameters:
    - hours: Kaç saat geriye (default: 24)
    
    Example: GET /api/sensors/traffic_light/traffic-light-001?hours=48
    """
    if not db_query:
        return jsonify({"error": "Database not connected"}), 503

    try:
        hours = request.args.get("hours", 24, type=int)
        hours = min(hours, 168)  # Max 1 hafta

        readings = db_query.get_readings_by_device(device_id, sensor_type, hours=hours)

        # Verileri format et
        formatted = []
        for r in readings:
            formatted.append(
                {
                    "value": r.get("value"),
                    "timestamp": r.get("timestamp"),
                    "metadata": r.get("metadata", {}),
                }
            )

        # İstatistikler hesapla
        values = [r["value"] for r in formatted]
        stats = {
            "count": len(values),
            "min": min(values) if values else None,
            "max": max(values) if values else None,
            "avg": sum(values) / len(values) if values else None,
        }

        return jsonify(
            {
                "device_id": device_id,
                "sensor_type": sensor_type,
                "hours": hours,
                "statistics": stats,
                "data": formatted,
            }
        )

    except Exception as e:
        logger.error(f"❌ Error: {e}")
        return jsonify({"error": str(e)}), 500


# ============================================================
# UYARI ENDPOİNT'LERİ
# ============================================================


@app.route("/api/alerts", methods=["GET"])
def get_alerts():
    """
    Aktif uyarıları al
    
    Query Parameters:
    - severity: "low", "medium", "high", "critical" (isteğe bağlı)
    
    Example: GET /api/alerts?severity=critical
    """
    if not db_query:
        return jsonify({"error": "Database not connected"}), 503

    try:
        alerts = db_query.get_active_alerts()

        # Severity'ye göre filtrele (isteğe bağlı)
        severity_filter = request.args.get("severity")
        if severity_filter:
            alerts = [a for a in alerts if a.get("severity") == severity_filter]

        # Alert'leri format et
        formatted = []
        for a in alerts:
            formatted.append(
                {
                    "alert_id": a.get("alert_id"),
                    "device_id": a.get("device_id"),
                    "severity": a.get("severity"),
                    "message": a.get("message"),
                    "timestamp": a.get("timestamp"),
                    "value": a.get("current_value"),
                    "threshold": a.get("threshold"),
                }
            )

        # Severity'ye göre sırala (critical → high → medium → low)
        severity_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
        formatted.sort(key=lambda x: severity_order.get(x["severity"], 99))

        return jsonify(
            {
                "total": len(formatted),
                "alerts": formatted,
            }
        )

    except Exception as e:
        logger.error(f"❌ Error: {e}")
        return jsonify({"error": str(e)}), 500


# ============================================================
# İSTATİSTİK ENDPOİNT'LERİ
# ============================================================


@app.route("/api/stats/<sensor_type>/<device_id>", methods=["GET"])
def get_statistics(sensor_type, device_id):
    """
    Belirtilen cihaz için istatistikleri al (son 24 saat)
    
    Returns: min, max, avg, count, latest
    
    Example: GET /api/stats/traffic_light/traffic-light-001
    """
    if not db_query:
        return jsonify({"error": "Database not connected"}), 503

    try:
        stats = db_query.get_statistics(sensor_type, device_id)

        return jsonify(
            {
                "device_id": device_id,
                "sensor_type": sensor_type,
                "period": "24h",
                "statistics": stats,
            }
        )

    except Exception as e:
        logger.error(f"❌ Error: {e}")
        return jsonify({"error": str(e)}), 500


# ============================================================
# FRONTEND SERVING
# ============================================================


@app.route("/", methods=["GET"])
def serve_dashboard():
    """Dashboard HTML'i serve et"""
    return send_from_directory("../../frontend", "index.html")


@app.route("/static/<path:filename>", methods=["GET"])
def serve_static(filename):
    """Static dosyaları (CSS, JS) serve et"""
    return send_from_directory("../../frontend", filename)


# ============================================================
# ERROR HANDLING
# ============================================================


@app.errorhandler(404)
def not_found(error):
    """404 hatası"""
    return jsonify({"error": "Not found"}), 404


@app.errorhandler(500)
def internal_error(error):
    """500 hatası"""
    logger.error(f"Internal error: {error}")
    return jsonify({"error": "Internal server error"}), 500


# ============================================================
# MAIN
# ============================================================


def main():
    """Flask uygulamasını başlat"""
    logger.info("=" * 60)
    logger.info("🚀 Smart City REST API Server Başlıyor...")
    logger.info("=" * 60)
    logger.info("📡 Endpoints:")
    logger.info("  GET  /api/health                                    - Health check")
    logger.info("  GET  /api/sensors/<type>?limit=10                   - Latest readings")
    logger.info("  GET  /api/sensors/<type>/<device>?hours=24          - Device history")
    logger.info("  GET  /api/alerts?severity=critical                  - Active alerts")
    logger.info("  GET  /api/stats/<type>/<device>                     - Statistics")
    logger.info("  GET  /                                              - Dashboard")
    logger.info("=" * 60)
    logger.info("🌐 Server: http://localhost:5000")
    logger.info("📊 Dashboard: http://localhost:5000/")
    logger.info("🔗 API Docs: http://localhost:5000/api/health")
    logger.info("=" * 60)

    app.run(host="0.0.0.0", port=5000, debug=False)


if __name__ == "__main__":
    main()

# app/routes.py

from flask import Blueprint, request, jsonify
from app import db
from app.models import Measure, Metric
from app.stats import compute_stats
from datetime import datetime, timezone

"""
Un Blueprint è un modo per raggruppare routes correlate.
Lo registriamo sull'app in __init__.py
"""
bp = Blueprint("api", __name__)


@bp.route("/measures", methods=["POST"])
def ingest_measure():
    """
    Riceve una misurazione da un sensore e la salva nel database.
    """
    data = request.get_json()

    # --- Validazione ---
    # Se il body non è JSON o mancano i campi obbligatori, rispondiamo con errore 400
    if not data:
        return jsonify({"error": "Il body deve essere JSON"}), 400

    sensor_id = data.get("sensor_id")
    timestamp_str = data.get("timestamp")
    metrics_data = data.get("metrics")

    if not sensor_id or not isinstance(sensor_id, str):
        return jsonify({"error": "Campo 'sensor_id' obbligatorio (stringa)"}), 400

    if not timestamp_str:
        return jsonify({"error": "Campo 'timestamp' obbligatorio"}), 400

    if not metrics_data or not isinstance(metrics_data, dict) or len(metrics_data) == 0:
        return jsonify({"error": "Campo 'metrics' obbligatorio (oggetto non vuoto)"}), 400

    # Verifichiamo che tutti i valori delle metriche siano numerici
    for key, val in metrics_data.items():
        if not isinstance(val, (int, float)):
            return jsonify({"error": f"Il valore di '{key}' deve essere numerico"}), 400

    # --- Analisi del timestamp ---
    try:
        # Python 3.11+ supporta il formato ISO 8601 con 'Z' finale
        timestamp = datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))
    except ValueError:
        return jsonify({"error": "Formato timestamp non valido. Usa ISO 8601"}), 400

    # --- Salvataggio nel DB ---
    measure = Measure(sensor_id=sensor_id, timestamp=timestamp)
    db.session.add(measure)

    for name, value in metrics_data.items():
        metric = Metric(name=name, value=float(value), measure=measure)
        db.session.add(metric)

    db.session.commit()

    return jsonify({"message": "Misura salvata", "id": measure.id}), 201


@bp.route("/measures", methods=["GET"])
def get_measures():
    """
    Restituisce lo storico delle misure.
    Supporta filtro opzionale per sensore: GET /measures?sensor_id=sensor-123
    """
    sensor_id = request.args.get("sensor_id")

    query = Measure.query.order_by(Measure.timestamp.desc())
    if sensor_id:
        query = query.filter(Measure.sensor_id == sensor_id)

    measures = query.all()
    return jsonify([m.to_dict() for m in measures]), 200


@bp.route("/stats", methods=["GET"])
def get_stats():
    """
    Restituisce statistiche (min, max, avg, count) sulle metriche.
    Filtri opzionali: ?sensor_id=... e/o ?metric=...
    """
    sensor_id = request.args.get("sensor_id")
    metric_name = request.args.get("metric")

    stats = compute_stats(sensor_id=sensor_id, metric_name=metric_name)
    return jsonify(stats), 200
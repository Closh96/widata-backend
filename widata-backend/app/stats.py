# app/stats.py

from app.models import Metric
from sqlalchemy import func

def compute_stats(sensor_id=None, metric_name=None):
    """
    Calcola min, max, media e conteggio per le metriche.
    Può essere filtrata per sensore e/o per nome metrica.
    
    'func' è un modulo di SQLAlchemy che mappa le funzioni SQL
    come MIN(), MAX(), AVG(), COUNT() in Python.
    """
    # Costruiamo la query di base
    query = Metric.query.join(Metric.measure)

    # Filtri opzionali
    if sensor_id:
        from app.models import Measure
        query = query.filter(Measure.sensor_id == sensor_id)
    if metric_name:
        query = query.filter(Metric.name == metric_name)

    # Raggruppiamo per nome metrica e calcoliamo le statistiche
    results = (
        query
        .with_entities(
            Metric.name,
            func.count(Metric.value).label("count"),
            func.min(Metric.value).label("min"),
            func.max(Metric.value).label("max"),
            func.avg(Metric.value).label("avg"),
        )
        .group_by(Metric.name)
        .all()
    )

    # Costruiamo la risposta come dizionario
    stats = {}
    for row in results:
        stats[row.name] = {
            "count": row.count,
            "min": round(row.min, 4),
            "max": round(row.max, 4),
            "avg": round(row.avg, 4),
        }

    return stats
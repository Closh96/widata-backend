# app/models.py

from app import db
from datetime import datetime, timezone

class Measure(db.Model):
    """
    Rappresenta una singola misurazione inviata da un sensore.
    Nel database questa diventa la tabella 'measure'.
    """
    __tablename__ = "measure"

    # Ogni riga ha un ID unico, generato automaticamente dal DB
    id = db.Column(db.Integer, primary_key=True)

    # L'identificativo del sensore, es: "sensor-123"
    sensor_id = db.Column(db.String(64), nullable=False, index=True)

    # Il timestamp della misurazione, es: "2026-02-06T10:15:30Z"
    timestamp = db.Column(db.DateTime, nullable=False)

    """
    Relazione: una misura può avere molte metriche
    'cascade="all, delete-orphan"' significa: se cancello una misura,
    cancella automaticamente anche tutte le sue metriche
    """

    metrics = db.relationship("Metric", backref="measure", cascade="all, delete-orphan")

    def to_dict(self):
        """
        Converte l'oggetto in un dizionario Python,
        così possiamo trasformarlo facilmente in JSON per la risposta API.
        """
        return {
            "id": self.id,
            "sensor_id": self.sensor_id,
            "timestamp": self.timestamp.isoformat(),
            "metrics": {m.name: m.value for m in self.metrics}
        }


class Metric(db.Model):
    """
    Rappresenta una singola metrica all'interno di una misurazione.
    Es: {"temperature": 22.4} → name="temperature", value=22.4
    Ogni misura può avere N metriche diverse.
    """
    __tablename__ = "metric"

    id = db.Column(db.Integer, primary_key=True)

    # Chiave esterna: collega questa metrica alla sua misura
    measure_id = db.Column(db.Integer, db.ForeignKey("measure.id"), nullable=False)

    # Il nome della metrica, es: "temperature", "humidity"
    name = db.Column(db.String(64), nullable=False)

    # Il valore numerico, es: 22.4
    value = db.Column(db.Float, nullable=False)
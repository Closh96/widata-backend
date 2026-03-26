# app/__init__.py

from flask import Flask
from flask_sqlalchemy import SQLAlchemy

# Creiamo l'oggetto db qui, a livello di modulo.
# Lo importeremo da altri file quando serve.
db = SQLAlchemy()

def create_app(testing=False):
    """
    Questa funzione crea e configura l'app Flask.
    Usiamo una 'factory function' invece di creare l'app globalmente,
    perché così possiamo creare versioni diverse dell'app
    (una normale, una per i test con un database separato).
    """
    app = Flask(__name__, instance_relative_config=True)

    if testing:
        """
        Durante i test, usiamo un database in memoria RAM.
        Questo è velocissimo e si cancella da solo alla fine del test.
        """
        app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
        app.config["TESTING"] = True
    else:
        # In produzione normale, il file .db viene salvato nella cartella /instance
        app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///widata.db"

    # Colleghiamo SQLAlchemy all'app Flask
    db.init_app(app)

    # Importiamo e registriamo le API
    from app.routes import bp
    app.register_blueprint(bp)

    # Creiamo le tabelle nel database se non esistono ancora
    with app.app_context():
        db.create_all()

    return app
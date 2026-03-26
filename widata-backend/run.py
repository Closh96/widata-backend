# run.py
from app import create_app

app = create_app()

if __name__ == "__main__":
    # debug=False in produzione/Docker, ma True durante lo sviluppo locale
    app.run(host="0.0.0.0", port=8000, debug=False)
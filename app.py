# app.py (wrapper de la app principal en src/app.py)

from src.app import app, server

if __name__ == "__main__":
    # Para ejecución local
    app.run(debug=False)

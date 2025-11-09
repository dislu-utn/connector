from flask import Flask, request, jsonify
import os
from dotenv import load_dotenv

from src.shared.integrate_dto import IntegrateDTO
from src.connector import Connector

load_dotenv()

app = Flask(__name__)

@app.route("/sync", methods=["POST"])
def integrate():
    """
    Endpoint para integración entre dislu y connector.
    Valida el DISLU_SECRET desde el header Authorization cuando el origin es "dislu"
    """
    
    try:
        # Parse el mensaje
        data = request.get_json()
        message = IntegrateDTO(**data)
        
        # Validar el secret si el origen es dislu
        if message.origin == "dislu":
            expected_secret = os.getenv("DISLU_SECRET")
            
            if not expected_secret:
                return jsonify({"error": "DISLU_SECRET no configurado en el servidor"}), 500
            
            # Obtener el secret del header Authorization
            auth_header = request.headers.get("Authorization")
            
            if not auth_header:
                return jsonify({"error": "Header Authorization no proporcionado"}), 401
            
            # Soportar formato "Bearer <secret>" o directamente el secret
            provided_secret = auth_header
            if auth_header.startswith("Bearer "):
                provided_secret = auth_header[7:]  # Remover "Bearer "
            
            if provided_secret != expected_secret:
                return jsonify({"error": "Secret inválido"}), 403
        
        connector = Connector(message.origin)

        if message.method == "sync":
            response = connector.initial_sync(message)
        else:
            response = connector.integrate(message)

        if not response:
            return ("", 500)

        return ("", 204)
    
    except Exception as e:
        print(f"Error in /sync endpoint: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 400

if __name__ == "__main__":
    app.run(host="localhost", port=6000, debug=True)

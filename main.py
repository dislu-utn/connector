from flask import Flask

from shared.integrate_dto import IntegrateDTO
from src.connector import Connector


app = Flask(__name__)

@app.route("/", methods=["POST"])
def integrate(message: IntegrateDTO):
    """
    - Capaz podría chequear en la db si hay que dejar pasar la request o talvez crear una condición en PubSub para bocharlos antes

    """
    if not Connector(message.origin).integrate(message):
        return ("", 500)

    return ("", 204)

# Debería hacer después otro cloud run para actualizar los registros de las instituciones en Firebase, pero que este separado de esto así queda desacoplada esa lógica.

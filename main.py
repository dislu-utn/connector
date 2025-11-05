from flask import Flask

from src.shared.integrate_dto import IntegrateDTO
from src.connector import Connector


app = Flask(__name__)

@app.route("/", methods=["POST"])
def integrate(message: IntegrateDTO):
    """
    - Capaz podría chequear en la db si hay que dejar pasar la request o talvez crear una condición en PubSub para bocharlos antes

    """

    connector = Connector(message.origin)

    if message.method == "sync":
        response = connector.initial_sync(message)
    else:
        response = connector.integrate(message)

    if not response:
        return ("", 500)

    return ("", 204)

if __name__ == "__main__":
    app.run(host="localhost", port=5000, debug=True)

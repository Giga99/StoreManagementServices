import csv
import io
import http

from flask import Flask, request, jsonify
from flask_jwt_extended import JWTManager

from configuration import Configuration
from commons.decorators import roleCheck
from commons.exceptions import BadRequestException
from worker_controller import WorkerController

application = Flask(__name__)
application.config.from_object(Configuration)
jwt = JWTManager(application)

worker_controller = WorkerController()


@application.route("/update", methods=["POST"])
@roleCheck(role="manager")
def update_products():
    if "file" not in request.files.keys():
        return jsonify(message="Field file is missing."), http.HTTPStatus.BAD_REQUEST

    content = request.files["file"].stream.read().decode("utf-8")
    stream = io.StringIO(content)
    reader = csv.reader(stream)

    num_of_products = 0
    try:
        num_of_products = worker_controller.update_products(reader)
    except BadRequestException as ex:
        return jsonify(message=str(ex)), http.HTTPStatus.BAD_REQUEST

    return jsonify(message="Successfully pushed {} on redis".format("products" if num_of_products > 1 else "product")), http.HTTPStatus.OK


if __name__ == "__main__":
    application.run(debug=True, host="0.0.0.0", port=5004)

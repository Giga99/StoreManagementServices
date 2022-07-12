import csv
import io

from flask import Flask, request, jsonify
from flask_jwt_extended import JWTManager
from redis import Redis

from configuration import Configuration
from applications.decorators import roleCheck

application = Flask(__name__)
application.config.from_object(Configuration)
jwt = JWTManager(application)


@application.route("/update", methods=["POST"])
@roleCheck(role="manager")
def updateProducts():
    if "file" not in request.files.keys():
        return jsonify(message="Field file is missing."), 400

    content = request.files["file"].stream.read().decode("utf-8")
    stream = io.StringIO(content)
    reader = csv.reader(stream)

    index = 0
    products = []
    for row in reader:
        if len(row) != 4:
            return jsonify(message="Incorrect number of values on line {}.".format(index)), 400

        try:
            if int(row[2]) <= 0:
                return jsonify(message="Incorrect quantity on line {}.".format(index)), 400
        except ValueError:
            return jsonify(message="Incorrect quantity on line {}.".format(index)), 400

        try:
            if float(row[3]) <= 0:
                return jsonify(message="Incorrect price on line {}.".format(index)), 400
        except ValueError:
            return jsonify(message="Incorrect price on line {}.".format(index)), 400

        products.append(row)
        index = index + 1

    for row in products:
        with Redis(host=Configuration.REDIS_HOST) as redis:
            redis.rpush(Configuration.REDIS_PRODUCTS_LIST, ",".join(row))

    return jsonify(message="Successfully pushed {} on redis".format("products" if index > 1 else "product"))


if __name__ == "__main__":
    application.run(debug=True, host="0.0.0.0", port=5004)

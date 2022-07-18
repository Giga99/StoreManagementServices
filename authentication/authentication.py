import http
from time import sleep

from flask import Flask, request, jsonify
from flask_jwt_extended import JWTManager, jwt_required, get_jwt_identity
from sqlalchemy_utils import database_exists, create_database

from authentication_controller import AuthenticationController
from configuration import Configuration
from models import database
from commons.decorators import roleCheck
from commons.exceptions import BadRequestException

application = Flask(__name__)
application.config.from_object(Configuration)
jwt = JWTManager(application)

authentication_controller = AuthenticationController()


@application.route("/register", methods=["POST"])
def register_user():
    forename = request.json.get("forename", "")
    surname = request.json.get("surname", "")
    email = request.json.get("email", "")
    password = request.json.get("password", "")
    is_customer: bool = request.json.get("isCustomer", None)

    try:
        authentication_controller.register_user(forename, surname, email, password, is_customer)
    except BadRequestException as ex:
        return jsonify(message=str(ex)), http.HTTPStatus.BAD_REQUEST

    return jsonify(message="Registration successful!"), http.HTTPStatus.OK


@application.route("/login", methods=["POST"])
def login_user():
    email = request.json.get("email", "")
    password = request.json.get("password", "")

    access_token = None
    refresh_token = None
    try:
        access_token, refresh_token = authentication_controller.login_user(email, password)
    except BadRequestException as ex:
        return jsonify(message=str(ex)), http.HTTPStatus.BAD_REQUEST

    return jsonify(accessToken=access_token, refreshToken=refresh_token), http.HTTPStatus.OK


@application.route("/refresh", methods=["POST"])
@jwt_required(refresh=True)
def refresh_token():
    identity = get_jwt_identity()

    access_token = authentication_controller.refresh_token(identity)

    return jsonify(accessToken=access_token), http.HTTPStatus.OK


@application.route("/delete", methods=["POST"])
@roleCheck(role="admin")
def deleteUser():
    email = request.json.get("email", "")

    try:
        authentication_controller.delete_user(email)
    except BadRequestException as ex:
        return jsonify(message=str(ex)), http.HTTPStatus.BAD_REQUEST

    return jsonify(message="Successfully deleted the user!"), http.HTTPStatus.OK


@application.route("/", methods=["GET"])
def index():
    return "Hello world!"


if __name__ == "__main__":
    done = False
    init_required = True
    while not done:
        try:
            if not database_exists(application.config["SQLALCHEMY_DATABASE_URI"]):
                create_database(application.config["SQLALCHEMY_DATABASE_URI"])
            else:
                init_required = False

            done = True
        except Exception as ex:
            print("Database didn't respond. Try again in 1 sec.")
            sleep(1)

    database.init_app(application)

    if init_required:
        authentication_controller.init_database(application)

    application.run(debug=True, host="0.0.0.0", port=5002)

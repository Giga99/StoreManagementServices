from flask import Flask, request, jsonify
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, create_refresh_token, get_jwt, \
    get_jwt_identity
from sqlalchemy import and_
from sqlalchemy_utils import database_exists, create_database
from time import sleep

from decorators import roleCheck
from configuration import Configuration
from models import database, User, UserRole, Role
from utils import passwordFormatIsGood, emailFormatIsGood

application = Flask(__name__)
application.config.from_object(Configuration)

jwt = JWTManager(application)


@application.route("/register", methods=["POST"])
def registerUser():
    forename = request.json.get("forename", "")
    surname = request.json.get("surname", "")
    email = request.json.get("email", "")
    password = request.json.get("password", "")
    is_customer: bool = request.json.get("isCustomer", None)

    forename_empty = len(forename) == 0
    surname_empty = len(surname) == 0
    email_empty = len(email) == 0
    password_empty = len(password) == 0
    is_customer_empty = is_customer is None

    if forename_empty:
        return jsonify(message="Field forename is missing."), 400
    elif surname_empty:
        return jsonify(message="Field surname is missing."), 400
    elif email_empty:
        return jsonify(message="Field email is missing."), 400
    elif password_empty:
        return jsonify(message="Field password is missing."), 400
    elif is_customer_empty:
        return jsonify(message="Field isCustomer is missing."), 400

    if not emailFormatIsGood(email):
        return jsonify(message="Invalid email."), 400

    if not passwordFormatIsGood(password):
        return jsonify(message="Invalid password."), 400

    if User.query.filter(User.email == email).first():
        return jsonify(message="Email already exists."), 400

    user = User(email=email, password=password, forename=forename, surname=surname)
    database.session.add(user)
    database.session.commit()

    role_id = Role.ROLE_CUSTOMER if is_customer else Role.ROLE_MANAGER
    user_role = UserRole(userId=user.id, roleId=role_id)
    database.session.add(user_role)
    database.session.commit()

    return jsonify(message="Registration successful!")


@application.route("/login", methods=["POST"])
def loginUser():
    email = request.json.get("email", "")
    password = request.json.get("password", "")

    email_empty = len(email) == 0
    password_empty = len(password) == 0

    if email_empty:
        return jsonify(message="Field email is missing."), 400
    elif password_empty:
        return jsonify(message="Field password is missing."), 400

    if not emailFormatIsGood(email):
        return jsonify(message="Invalid email."), 400

    user = User.query.filter(and_(User.email == email, User.password == password)).first()

    if not user:
        return jsonify(message="Invalid credentials."), 400

    additional_claims = {
        "forename": user.forename,
        "surname": user.surname,
        "roles": [str(role) for role in user.roles]
    }

    access_token = create_access_token(identity=user.email, additional_claims=additional_claims)
    refresh_token = create_refresh_token(identity=user.email, additional_claims=additional_claims)

    return jsonify(accessToken=access_token, refreshToken=refresh_token)


@application.route("/refresh", methods=["POST"])
@jwt_required(refresh=True)
def refreshToken():
    identity = get_jwt_identity()
    refresh_claims = get_jwt()

    additional_claims = {
        "forename": refresh_claims["forename"],
        "surname": refresh_claims["surname"],
        "roles": refresh_claims["roles"]
    }

    access_token = create_access_token(identity=identity, additional_claims=additional_claims)
    return jsonify(accessToken=access_token)


@application.route("/delete", methods=["POST"])
@roleCheck(role="admin")
def deleteUser():
    email = request.json.get("email", "")

    email_empty = len(email) == 0

    if email_empty:
        return jsonify(message="Field email is missing."), 400

    if not emailFormatIsGood(email):
        return jsonify(message="Invalid email."), 400

    user = User.query.filter(User.email == email).first()

    if not user:
        return jsonify(message="Unknown user."), 400

    database.session.delete(user)
    database.session.commit()

    return jsonify(message="Successfully deleted the user!")


@application.route("/", methods=["GET"])
def index():
    return "Hello world!"


def init_database(application):
    with application.app_context() as context:
        database.create_all()
        database.session.commit()

        adminRole = Role(name="admin")
        customerRole = Role(name="customer")
        managerRole = Role(name="manager")

        database.session.add(adminRole)
        database.session.add(customerRole)
        database.session.add(managerRole)
        database.session.commit()

        admin = User(
            email="admin@admin.com",
            password="1",
            forename="admin",
            surname="admin"
        )

        database.session.add(admin)
        database.session.commit()

        userRole = UserRole(
            userId=admin.id,
            roleId=adminRole.id
        )

        database.session.add(userRole)
        database.session.commit()


if __name__ == "__main__":
    done = False
    initRequired = True
    while not done:
        try:
            if not database_exists(application.config["SQLALCHEMY_DATABASE_URI"]):
                create_database(application.config["SQLALCHEMY_DATABASE_URI"])
            else:
                initRequired = False

            done = True
        except Exception as ex:
            print("Database didn't respond. Try again in 1 sec.")
            sleep(1)

    database.init_app(application)

    if initRequired:
        init_database(application)

    application.run(debug=True, host="0.0.0.0", port=5002)

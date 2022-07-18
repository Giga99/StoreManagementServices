from flask_jwt_extended import create_access_token, create_refresh_token, get_jwt
from sqlalchemy import and_

from models import database, User, UserRole, Role
from utils import passwordFormatIsGood, emailFormatIsGood
from commons.exceptions import BadRequestException


class AuthenticationController:

    def register_user(self, forename, surname, email, password, is_customer):
        forename_empty = len(forename) == 0
        surname_empty = len(surname) == 0
        email_empty = len(email) == 0
        password_empty = len(password) == 0
        is_customer_empty = is_customer is None

        if forename_empty:
            raise BadRequestException("Field forename is missing.")
        elif surname_empty:
            raise BadRequestException("Field surname is missing.")
        elif email_empty:
            raise BadRequestException("Field email is missing.")
        elif password_empty:
            raise BadRequestException("Field password is missing.")
        elif is_customer_empty:
            raise BadRequestException("Field isCustomer is missing.")

        if not emailFormatIsGood(email):
            raise BadRequestException("Invalid email.")

        if not passwordFormatIsGood(password):
            raise BadRequestException("Invalid password.")

        if User.query.filter(User.email == email).first():
            raise BadRequestException("Email already exists.")

        user = User(email=email, password=password, forename=forename, surname=surname)
        database.session.add(user)
        database.session.commit()

        role_id = Role.ROLE_CUSTOMER if is_customer else Role.ROLE_MANAGER
        user_role = UserRole(userId=user.id, roleId=role_id)
        database.session.add(user_role)
        database.session.commit()

    def login_user(self, email, password):
        email_empty = len(email) == 0
        password_empty = len(password) == 0

        if email_empty:
            raise BadRequestException("Field email is missing.")
        elif password_empty:
            raise BadRequestException("Field password is missing.")

        if not emailFormatIsGood(email):
            raise BadRequestException("Invalid email.")

        user = User.query.filter(and_(User.email == email, User.password == password)).first()

        if not user:
            raise BadRequestException("Invalid credentials.")

        additional_claims = {
            "forename": user.forename,
            "surname": user.surname,
            "roles": [str(role) for role in user.roles]
        }

        access_token = create_access_token(identity=user.email, additional_claims=additional_claims)
        refresh_token = create_refresh_token(identity=user.email, additional_claims=additional_claims)
        return access_token, refresh_token

    def refresh_token(self, identity):
        refresh_claims = get_jwt()

        additional_claims = {
            "forename": refresh_claims["forename"],
            "surname": refresh_claims["surname"],
            "roles": refresh_claims["roles"]
        }

        access_token = create_access_token(identity=identity, additional_claims=additional_claims)
        return access_token

    def delete_user(self, email):
        email_empty = len(email) == 0
        if email_empty:
            raise BadRequestException("Field email is missing.")

        if not emailFormatIsGood(email):
            raise BadRequestException("Invalid email.")

        user = User.query.filter(User.email == email).first()

        if not user:
            raise BadRequestException("Unknown user.")

        database.session.delete(user)
        database.session.commit()

    def init_database(self, application):
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

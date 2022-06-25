from functools import wraps

from flask import jsonify
from flask_jwt_extended import verify_jwt_in_request, get_jwt


def roleCheck(role):
    def innerRole(function):
        @wraps(function)
        def decorator(*arguments, **keyword_arguments):
            verify_jwt_in_request()
            claims = get_jwt()
            if ("roles" in claims) and (role in claims["roles"]):
                return function(*arguments, **keyword_arguments)
            else:
                return jsonify(message="Permission denied!"), 403

        return decorator

    return innerRole
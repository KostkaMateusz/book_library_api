from book_library_app import db
from flask import Response, jsonify
from book_library_app.errors import errors_bp

err_code = {
    "BadRequest": 400,
    "Unauthorized": 401,
    "NotFound": 404,
    "Conflict": 409,
    "UnsupportedMediaType": 415,
    "InternalServerError": 500,
}


class ErrorResponse:
    """Custom class that takes useful information from error handling function
    and converts it to json and sends it as response for a call"""

    def __init__(self, message: str, http_status: int):
        self.payload = {"success": False, "message": message}
        self.http_status = http_status

    def to_response(self) -> Response:
        response = jsonify(self.payload)
        response.status_code = self.http_status
        return response


@errors_bp.app_errorhandler(err_code["BadRequest"])
def bad_request_error(err):
    messages = err.data.get("messages", {}).get("json", {})
    return ErrorResponse(messages, err_code["BadRequest"]).to_response()


# Flask generic exception handlers


@errors_bp.app_errorhandler(err_code["NotFound"])
def not_found_error(err):
    return ErrorResponse(err.description, err_code["NotFound"]).to_response()


@errors_bp.app_errorhandler(err_code["Unauthorized"])
def unanthorized_error(err):
    return ErrorResponse(err.description, err_code["Unauthorized"]).to_response()


@errors_bp.app_errorhandler(err_code["Conflict"])
def conflict_error(err):
    return ErrorResponse(err.description, err_code["Conflict"]).to_response()


@errors_bp.app_errorhandler(err_code["UnsupportedMediaType"])
def unsupported_media_type_error(err):
    return ErrorResponse(
        err.description, err_code["UnsupportedMediaType"]
    ).to_response()


@errors_bp.app_errorhandler(err_code["InternalServerError"])
def internal_server_error(err):
    # in case of error 500 internal server error we reset connection with database
    db.session.rollback()
    return ErrorResponse(err.description, err_code["InternalServerError"]).to_response()

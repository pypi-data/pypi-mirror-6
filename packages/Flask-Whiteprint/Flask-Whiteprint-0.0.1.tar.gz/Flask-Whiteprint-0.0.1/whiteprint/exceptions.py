from werkzeug.exceptions import HTTPException


def abort(exception, *args, **kwargs):
    raise exception(*args, **kwargs)


class HTTPExceptionBase(HTTPException):

    response = None
    status = 500
    code = 1000
    message = "Internal server error."

    def __init__(self, **kwargs):
        if kwargs:
            self.message = self.message % kwargs


class NotAuthorizedError(HTTPExceptionBase):

    status = 401
    code = 1001
    message = "Not authorized."


class PageNotFoundError(HTTPExceptionBase):

    status = 404
    code = 1002
    message = "Page not found."


class ResourceNotFoundError(HTTPExceptionBase):

    status = 404
    code = 1003
    message = "%(resource)s not found."


class NoPermissionError(HTTPExceptionBase):

    status = 403
    code = 1004
    message = "No permission."


class MissingParamError(HTTPExceptionBase):

    status = 400
    code = 0
    message = "A required parameter '%(param)s' is missing."


class InvalidParamError(HTTPExceptionBase):

    status = 400
    code = 0
    message = "A value of parameter '%(param)s' is invalid."


class AlreadySignedupError(HTTPExceptionBase):

    status = 401
    code = 0
    message = "Already signed up."


class WrongPasswordError(HTTPExceptionBase):

    status = 401
    code = 0
    message = "Wrong password."


class FacebookAuthError(HTTPExceptionBase):

    status = 401
    code = 0
    message = "Facebook auth failed: %(description)s"


class TwitterAuthError(HTTPExceptionBase):

    status = 401
    code = 0
    message = "Twitter auth failed: %(description)s"


class FriendMyselfError(HTTPExceptionBase):

    status = 400
    code = 0
    message = "Cannot add myself as a friend."


class AlreadyFriendError(HTTPExceptionBase):

    status = 400
    code = 0
    message = "Already a friend."


class NotFriendError(HTTPExceptionBase):

    status = 400
    code = 0
    message = "Not a friend."


class AlreadyExistingVenueError(HTTPExceptionBase):

    status = 400
    code = 0
    message = "Venue already exists."

""" Cheddargetter exceptions."""


class CheddargetterException(Exception):

    """ Base class for Cheddargetter exceptions."""

    CODE = None

    def __init__(self, message, id_, code, aux_code):
        self.message = message
        self.id_ = id_
        self.code = self.CODE or code
        self.aux_code = aux_code

    def __str__(self):
        return "[{}] {} ()".format(self.code, self.message, self.aux_code)


class CheddargetterBadRequest(CheddargetterException):
    CODE = 400


class CheddargetterNotAuthorized(CheddargetterException):
    CODE = 401


class CheddargetterNotFound(CheddargetterException):
    CODE = 404


class CheddargetterPreconditionFailed(CheddargetterException):
    CODE = 412


class CheddargetterUnprocessableEntity(CheddargetterException):
    CODE = 422


class CheddargetterInternalServerError(CheddargetterException):
    CODE = 500


class CheddargetterBadGateway(CheddargetterException):
    CODE = 502


class CheddargetterServiceUnavailable(CheddargetterException):
    CODE = 503

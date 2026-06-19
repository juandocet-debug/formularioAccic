class DomainError(Exception):
    status_code = 400
    message = "Solicitud invalida"


class DuplicateDocumentError(DomainError):
    status_code = 409
    message = "Usuario ya registrado."


class GroupNotFoundError(DomainError):
    status_code = 404
    message = "El grupo seleccionado no existe."


class GroupFullError(DomainError):
    status_code = 409
    message = "El grupo seleccionado ya no tiene cupos disponibles."


class RegistrationNotFoundError(DomainError):
    status_code = 404
    message = "La respuesta no existe."


class InvalidCredentialsError(DomainError):
    status_code = 401
    message = "Credenciales invalidas."

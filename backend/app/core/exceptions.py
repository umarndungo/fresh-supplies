class AppError(Exception):
    status_code = 400

    def __init__(self, message: str, *, field: str | None = None):
        self.message = message
        self.field = field
        super().__init__(message)


class NotFoundError(AppError):
    status_code = 404


class ConflictError(AppError):
    status_code = 409


class UnauthorizedError(AppError):
    status_code = 401


class ForbiddenError(AppError):
    status_code = 403

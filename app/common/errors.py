from starlette import status


class AppError(Exception):
    def __init__(
        self,
        message: str,
        status_code: int = status.HTTP_400_BAD_REQUEST,
        details: dict = None,
    ):
        self.message = message
        self.status_code = status_code
        self.details = details
        super().__init__(self.message)


class UserAlreadyExistsError(AppError):
    def __init__(self, message="User with provided email address already exists."):
        self.message = message
        self.status_code = status.HTTP_409_CONFLICT  # Conflict
        super().__init__(self.message, self.status_code)


class RecordAlreadyExistsError(AppError):
    def __init__(self, message="Record with provided details already exists."):
        self.message = message
        self.status_code = status.HTTP_409_CONFLICT  # Conflict
        super().__init__(self.message, self.status_code)


class OrganisationAlreadyExistsError(AppError):
    def __init__(self, message="Organisation with provided details already exists."):
        self.message = message
        self.status_code = status.HTTP_409_CONFLICT  # Conflict
        super().__init__(self.message, self.status_code)


class AuthenticationFailedError(AppError):
    def __init__(self, message="User or password do not match"):
        self.message = message
        self.status_code = status.HTTP_401_UNAUTHORIZED  # Unauthorized
        super().__init__(self.message, self.status_code)


class RecordNotExistsError(AppError):
    def __init__(self, message="Record not found."):
        self.message = message
        self.status_code = status.HTTP_404_NOT_FOUND  # Not Found
        super().__init__(self.message, self.status_code)


class UserNotFoundError(AppError):
    def __init__(self, message="User not found."):
        self.message = message
        self.status_code = status.HTTP_404_NOT_FOUND  # Not Found
        super().__init__(self.message, self.status_code)


class OrganisationNotFoundError(AppError):
    def __init__(self, message="Organisation not found."):
        self.message = message
        self.status_code = status.HTTP_404_NOT_FOUND  # Not Found
        super().__init__(self.message, self.status_code)


class InvalidTokenError(AppError):
    def __init__(self, message="Invalid token provided."):
        self.message = message
        self.status_code = status.HTTP_401_UNAUTHORIZED  # Unauthorized
        super().__init__(self.message, self.status_code)


class InvalidOTPError(AppError):
    def __init__(self, message="Invalid OTP provided."):
        self.message = message
        self.status_code = status.HTTP_401_UNAUTHORIZED  # Unauthorized
        super().__init__(self.message, self.status_code)


class InvalidAuthorizationHeaderError(AppError):
    def __init__(self, message="Invalid authorization header error."):
        self.message = message
        self.status_code = status.HTTP_401_UNAUTHORIZED  # Unauthorized
        super().__init__(self.message, self.status_code)


class RoleAssignedToUserError(AppError):
    def __init__(self, message="Role is currently assigned to one or more users."):
        self.message = message
        self.status_code = status.HTTP_401_UNAUTHORIZED  # Unauthorized
        super().__init__(self.message, self.status_code)


class RoleAssignedToPermissionError(AppError):
    def __init__(self, message="Role is currently assigned to one or more permissions."):
        self.message = message
        self.status_code = status.HTTP_401_UNAUTHORIZED  # Unauthorized
        super().__init__(self.message, self.status_code)





class InvalidProviderError(Exception):
    pass


# class InvalidRoleToInviteError(Exception):
#     pass
#
#
# class InvalidAuthorizationHeaderError(Exception):
#     pass
#
#
# class OTPAlreadyVerifiedError(Exception):
#     pass
#
#
# class OTPInvalidCodeError(Exception):
#     pass
#
#
# class OTPNotGeneratedError(Exception):
#     pass
#
#
# class OTPNotVerifiedError(Exception):
#     pass
#
#
# class OTPNotValidatedError(Exception):
#     pass
#
#
# class RecordNotExistsError(Exception):
#     pass
#
#
# class FileExtensionNotSupportedError(Exception):
#     pass
#
#
# class DatasetTemplateNotFoundError(Exception):
#     pass
#
#
# class InvitationAlreadySentError(Exception):
#     pass
#
#
# class LinkNotValidError(Exception):
#     pass
#
#
# class LinkNotVerifiedError(Exception):
#     pass
#
#
# class IncompletePasswordChangeError(Exception):
#     pass
#
#
# class NewPasswordsNotMatchError(Exception):
#     pass
#
#
# class NewPasswordNotDifferentError(Exception):
#     pass
#
#
# class InsufficientPermissionError(Exception):
#     pass
#
#
# class ReportAlreadyUploadedError(Exception):
#     pass

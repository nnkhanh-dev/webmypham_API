from app.core.exceptions.base import BusinessException

class UserNotFoundException(BusinessException):
    def __init__ (self, user_id = str):
         super().__init__(
            message=f"User {user_id} not found",
            error_code="USER_NOT_FOUND",
            status_code=404,
            extra={"user_id": user_id},
        )
        
class UserEmailAlreadyExistsException(BusinessException):
    def __init__(self, email: str):
        super().__init__(
            message="Email already exists",
            error_code="EMAIL_ALREADY_EXISTS",
            status_code=409,
            extra={"email": email},
        )

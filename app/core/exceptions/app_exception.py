from app.core.exceptions.user_exception import BusinessException


class NotFoundException(BusinessException):
    """
    Dùng khi không tìm thấy resource (404)
    """

    def __init__(
        self,
        *,
        message: str = "Không tìm thấy dữ liệu",
        error_code: str = "NOT_FOUND",
        extra: dict | None = None
    ):
        super().__init__(
            message=message,
            error_code=error_code,
            status_code=404,
            extra=extra
        )

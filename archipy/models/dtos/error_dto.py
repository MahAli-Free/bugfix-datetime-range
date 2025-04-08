from typing import Self

from archipy.models.dtos.base_dtos import BaseDTO

try:
    from http import HTTPStatus

    HTTP_AVAILABLE = True
except ImportError:
    HTTP_AVAILABLE = False
    HTTPStatus = None  # type: ignore[misc, name-defined, assignment]

try:
    from grpc import StatusCode

    GRPC_AVAILABLE = True
except ImportError:
    GRPC_AVAILABLE = False
    StatusCode = None  # type: ignore[misc, name-defined, assignment]


class ErrorDetailDTO(BaseDTO):
    """Standardized error detail model."""

    code: str
    message_en: str
    message_fa: str
    http_status: int | None = None
    grpc_status: int | None = None

    @classmethod
    def create_error_detail(
        cls,
        code: str,
        message_en: str,
        message_fa: str,
        http_status: int | HTTPStatus | None = None,
        grpc_status: int | StatusCode | None = None,
    ) -> Self:
        """Creates an `ErrorDetailDTO` with appropriate status codes.

        Args:
            code (str): A unique error code.
            message_en (str): The error message in English.
            message_fa (str): The error message in Persian.
            http_status (int | HTTPStatus | None): The HTTP status code associated with the error.
            grpc_status (int | StatusCode | None): The gRPC status code associated with the error.

        Returns:
            ErrorDetailDTO: The created exception detail object.
        """
        status_kwargs = {}

        if HTTP_AVAILABLE and http_status is not None:
            status_kwargs["http_status"] = http_status.value if isinstance(http_status, HTTPStatus) else http_status

        if GRPC_AVAILABLE and grpc_status is not None:
            status_kwargs["grpc_status"] = grpc_status.value if isinstance(grpc_status, StatusCode) else grpc_status

        # We need to use cls() for proper typing with Self return type
        return cls(code=code, message_en=message_en, message_fa=message_fa, **status_kwargs)

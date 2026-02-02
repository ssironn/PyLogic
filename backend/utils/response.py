"""
Centralized API response creation.

Provides a consistent response format across all API endpoints using
modern Python patterns: dataclasses, type hints, and the Result pattern.

Usage:
    from utils.response import ApiResponse, ApiError

    # Success responses
    return ApiResponse.ok(data={"user": user_data})
    return ApiResponse.created(data={"id": new_id}, message="Recurso criado com sucesso")
    return ApiResponse.paginated(items=users, total=100, page=1, per_page=20)

    # Error responses
    return ApiResponse.bad_request(message="Dados invalidos", errors=validation_errors)
    return ApiResponse.not_found(message="Usuario nao encontrado")
    return ApiResponse.unauthorized(message="Credenciais invalidas")

    # Using the Result pattern for service layer
    result = UserService.create(data)
    return result.to_response()
"""
from __future__ import annotations

from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Generic, TypeVar, Optional
from http import HTTPStatus


T = TypeVar('T')


class ResponseStatus(str, Enum):
    """Response status indicators."""
    SUCCESS = "success"
    ERROR = "error"


@dataclass(frozen=True, slots=True)
class PaginationMeta:
    """Pagination metadata for list responses."""
    page: int
    per_page: int
    total: int
    total_pages: int
    has_next: bool
    has_prev: bool

    @classmethod
    def create(cls, page: int, per_page: int, total: int) -> PaginationMeta:
        """Factory method to create pagination metadata."""
        total_pages = (total + per_page - 1) // per_page if per_page > 0 else 0
        return cls(
            page=page,
            per_page=per_page,
            total=total,
            total_pages=total_pages,
            has_next=page < total_pages,
            has_prev=page > 1
        )


@dataclass(frozen=True, slots=True)
class ApiError:
    """Represents a single API error."""
    code: str
    message: str
    field: Optional[str] = None
    details: Optional[dict[str, Any]] = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary, excluding None values."""
        result = {"code": self.code, "message": self.message}
        if self.field is not None:
            result["field"] = self.field
        if self.details is not None:
            result["details"] = self.details
        return result


@dataclass(slots=True)
class ApiResponse(Generic[T]):
    """
    Standardized API response wrapper.

    Provides consistent structure for all API responses:
    - status: "success" or "error"
    - data: The response payload (for success)
    - message: Human-readable message
    - errors: List of error details (for errors)
    - meta: Additional metadata (pagination, timestamps, etc.)
    """
    status: ResponseStatus
    data: Optional[T] = None
    message: Optional[str] = None
    errors: list[ApiError] = field(default_factory=list)
    meta: dict[str, Any] = field(default_factory=dict)
    http_status: HTTPStatus = HTTPStatus.OK

    def to_dict(self) -> dict[str, Any]:
        """Convert response to dictionary for JSON serialization."""
        result: dict[str, Any] = {"status": self.status.value}

        if self.data is not None:
            result["data"] = self.data

        if self.message is not None:
            result["message"] = self.message

        if self.errors:
            result["errors"] = [e.to_dict() for e in self.errors]

        if self.meta:
            result["meta"] = self.meta

        return result

    def to_tuple(self) -> tuple[dict[str, Any], int]:
        """Convert to Flask response tuple (body, status_code)."""
        return self.to_dict(), self.http_status.value

    # ==================== Success Responses ====================

    @classmethod
    def ok(
        cls,
        data: Optional[T] = None,
        message: Optional[str] = None,
        meta: Optional[dict[str, Any]] = None
    ) -> ApiResponse[T]:
        """200 OK - Standard success response."""
        return cls(
            status=ResponseStatus.SUCCESS,
            data=data,
            message=message,
            meta=meta or {},
            http_status=HTTPStatus.OK
        )

    @classmethod
    def created(
        cls,
        data: Optional[T] = None,
        message: str = "Recurso criado com sucesso"
    ) -> ApiResponse[T]:
        """201 Created - Resource successfully created."""
        return cls(
            status=ResponseStatus.SUCCESS,
            data=data,
            message=message,
            http_status=HTTPStatus.CREATED
        )

    @classmethod
    def accepted(
        cls,
        data: Optional[T] = None,
        message: str = "Requisicao aceita para processamento"
    ) -> ApiResponse[T]:
        """202 Accepted - Request accepted for async processing."""
        return cls(
            status=ResponseStatus.SUCCESS,
            data=data,
            message=message,
            http_status=HTTPStatus.ACCEPTED
        )

    @classmethod
    def no_content(cls) -> ApiResponse[None]:
        """204 No Content - Success with no response body."""
        return cls(
            status=ResponseStatus.SUCCESS,
            http_status=HTTPStatus.NO_CONTENT
        )

    @classmethod
    def paginated(
        cls,
        items: list[T],
        total: int,
        page: int = 1,
        per_page: int = 20,
        message: Optional[str] = None
    ) -> ApiResponse[list[T]]:
        """Success response with pagination metadata."""
        pagination = PaginationMeta.create(page=page, per_page=per_page, total=total)
        return cls(
            status=ResponseStatus.SUCCESS,
            data=items,
            message=message,
            meta={"pagination": asdict(pagination)},
            http_status=HTTPStatus.OK
        )

    # ==================== Error Responses ====================

    @classmethod
    def error(
        cls,
        message: str,
        http_status: HTTPStatus = HTTPStatus.BAD_REQUEST,
        errors: Optional[list[ApiError]] = None,
        code: str = "ERROR"
    ) -> ApiResponse[None]:
        """Generic error response."""
        error_list = errors or [ApiError(code=code, message=message)]
        return cls(
            status=ResponseStatus.ERROR,
            message=message,
            errors=error_list,
            http_status=http_status
        )

    @classmethod
    def bad_request(
        cls,
        message: str = "Requisicao invalida",
        errors: Optional[list[ApiError]] = None
    ) -> ApiResponse[None]:
        """400 Bad Request - Invalid request data."""
        return cls.error(
            message=message,
            http_status=HTTPStatus.BAD_REQUEST,
            errors=errors,
            code="BAD_REQUEST"
        )

    @classmethod
    def validation_error(
        cls,
        errors: list[ApiError],
        message: str = "Erro de validacao"
    ) -> ApiResponse[None]:
        """400 Bad Request - Validation errors."""
        return cls(
            status=ResponseStatus.ERROR,
            message=message,
            errors=errors,
            http_status=HTTPStatus.BAD_REQUEST
        )

    @classmethod
    def unauthorized(
        cls,
        message: str = "Nao autorizado"
    ) -> ApiResponse[None]:
        """401 Unauthorized - Authentication required."""
        return cls.error(
            message=message,
            http_status=HTTPStatus.UNAUTHORIZED,
            code="UNAUTHORIZED"
        )

    @classmethod
    def forbidden(
        cls,
        message: str = "Acesso negado"
    ) -> ApiResponse[None]:
        """403 Forbidden - Insufficient permissions."""
        return cls.error(
            message=message,
            http_status=HTTPStatus.FORBIDDEN,
            code="FORBIDDEN"
        )

    @classmethod
    def not_found(
        cls,
        message: str = "Recurso nao encontrado",
        resource: Optional[str] = None
    ) -> ApiResponse[None]:
        """404 Not Found - Resource not found."""
        details = {"resource": resource} if resource else None
        return cls(
            status=ResponseStatus.ERROR,
            message=message,
            errors=[ApiError(code="NOT_FOUND", message=message, details=details)],
            http_status=HTTPStatus.NOT_FOUND
        )

    @classmethod
    def conflict(
        cls,
        message: str = "Conflito de recursos"
    ) -> ApiResponse[None]:
        """409 Conflict - Resource conflict."""
        return cls.error(
            message=message,
            http_status=HTTPStatus.CONFLICT,
            code="CONFLICT"
        )

    @classmethod
    def unprocessable(
        cls,
        message: str = "Entidade nao processavel",
        errors: Optional[list[ApiError]] = None
    ) -> ApiResponse[None]:
        """422 Unprocessable Entity - Semantic errors."""
        return cls.error(
            message=message,
            http_status=HTTPStatus.UNPROCESSABLE_ENTITY,
            errors=errors,
            code="UNPROCESSABLE_ENTITY"
        )

    @classmethod
    def internal_error(
        cls,
        message: str = "Erro interno do servidor"
    ) -> ApiResponse[None]:
        """500 Internal Server Error."""
        return cls.error(
            message=message,
            http_status=HTTPStatus.INTERNAL_SERVER_ERROR,
            code="INTERNAL_ERROR"
        )

    @classmethod
    def service_unavailable(
        cls,
        message: str = "Servico indisponivel"
    ) -> ApiResponse[None]:
        """503 Service Unavailable."""
        return cls.error(
            message=message,
            http_status=HTTPStatus.SERVICE_UNAVAILABLE,
            code="SERVICE_UNAVAILABLE"
        )


@dataclass(slots=True)
class Result(Generic[T]):
    """
    Result pattern for service layer operations.

    Encapsulates either a success value or an error, enabling
    explicit error handling without exceptions.

    Usage:
        def create_user(data: dict) -> Result[User]:
            if not data.get('email'):
                return Result.fail("Email e obrigatorio", field="email")

            user = User(**data)
            return Result.success(user, message="Usuario criado")

        # In controller
        result = UserService.create_user(data)
        if result.is_failure:
            return result.to_response()
        return ApiResponse.created(data=result.value)
    """
    value: Optional[T] = None
    error: Optional[ApiError] = None
    message: Optional[str] = None
    _is_success: bool = True

    @property
    def is_success(self) -> bool:
        """Check if result is successful."""
        return self._is_success

    @property
    def is_failure(self) -> bool:
        """Check if result is a failure."""
        return not self._is_success

    @classmethod
    def success(cls, value: T, message: Optional[str] = None) -> Result[T]:
        """Create a successful result."""
        return cls(value=value, message=message, _is_success=True)

    @classmethod
    def fail(
        cls,
        message: str,
        code: str = "ERROR",
        field: Optional[str] = None,
        details: Optional[dict[str, Any]] = None
    ) -> Result[T]:
        """Create a failed result."""
        error = ApiError(code=code, message=message, field=field, details=details)
        return cls(error=error, message=message, _is_success=False)

    def to_response(
        self,
        http_status_on_success: HTTPStatus = HTTPStatus.OK,
        http_status_on_failure: HTTPStatus = HTTPStatus.BAD_REQUEST
    ) -> ApiResponse[T]:
        """Convert result to API response."""
        if self.is_success:
            return ApiResponse(
                status=ResponseStatus.SUCCESS,
                data=self.value,
                message=self.message,
                http_status=http_status_on_success
            )
        return ApiResponse(
            status=ResponseStatus.ERROR,
            message=self.message,
            errors=[self.error] if self.error else [],
            http_status=http_status_on_failure
        )

    def map(self, fn) -> Result:
        """Transform the success value."""
        if self.is_failure:
            return self
        return Result.success(fn(self.value), self.message)

    def flat_map(self, fn) -> Result:
        """Chain operations that return Results."""
        if self.is_failure:
            return self
        return fn(self.value)


def validation_errors_from_dict(errors: dict[str, list[str]]) -> list[ApiError]:
    """
    Convert validation error dict to list of ApiError.

    Args:
        errors: Dict mapping field names to list of error messages
                e.g., {"email": ["Invalid format", "Already exists"]}

    Returns:
        List of ApiError objects
    """
    result = []
    for field_name, messages in errors.items():
        for message in messages:
            result.append(ApiError(
                code="VALIDATION_ERROR",
                message=message,
                field=field_name
            ))
    return result


def with_timestamp(response: ApiResponse[T]) -> ApiResponse[T]:
    """Add timestamp to response metadata."""
    response.meta["timestamp"] = datetime.now(timezone.utc).isoformat()
    return response

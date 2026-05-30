from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.core.exceptions import AppException
from app.schemas.response import ApiResponse, ErrorItem
from app.utils.responses import error_response


def _to_json_response(body: ApiResponse, status_code: int) -> JSONResponse:
    return JSONResponse(status_code=status_code, content=body.model_dump())


async def app_exception_handler(_: Request, exc: AppException) -> JSONResponse:
    body = error_response(message=exc.message, errors=exc.errors or None)
    return _to_json_response(body, exc.status_code)


async def http_exception_handler(_: Request, exc: HTTPException) -> JSONResponse:
    detail = exc.detail
    if isinstance(detail, list):
        errors = [
            ErrorItem(
                field=str(item.get("loc", [""])[-1]) if isinstance(item, dict) else None,
                message=str(item.get("msg", item)) if isinstance(item, dict) else str(item),
            )
            for item in detail
        ]
        message = "Request failed"
    elif isinstance(detail, dict):
        message = str(detail.get("message", "Request failed"))
        errors = None
    else:
        message = str(detail)
        errors = None

    body = error_response(message=message, errors=errors)
    return _to_json_response(body, exc.status_code)


async def validation_exception_handler(
    _: Request, exc: RequestValidationError
) -> JSONResponse:
    errors = [
        ErrorItem(
            field=".".join(str(part) for part in err["loc"] if part != "body"),
            message=err["msg"],
        )
        for err in exc.errors()
    ]
    body = error_response(message="Validation failed", errors=errors)
    return _to_json_response(body, 422)


async def unhandled_exception_handler(_: Request, __: Exception) -> JSONResponse:
    body = error_response(message="Internal server error")
    return _to_json_response(body, 500)


def register_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(AppException, app_exception_handler)
    app.add_exception_handler(HTTPException, http_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(Exception, unhandled_exception_handler)

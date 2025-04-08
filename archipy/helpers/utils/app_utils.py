from __future__ import annotations

import logging
from collections.abc import Awaitable, Callable
from http import HTTPStatus
from typing import Any, cast

from fastapi import FastAPI, Request, Response
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.routing import APIRoute
from pydantic import ValidationError
from starlette.middleware.cors import CORSMiddleware

from archipy.configs.base_config import BaseConfig
from archipy.helpers.utils.base_utils import BaseUtils
from archipy.models.errors import (
    BaseError,
    InvalidArgumentError,
    UnavailableError,
    UnknownError,
)


class FastAPIExceptionHandler:
    """Handles various types of errors and converts them to appropriate JSON responses."""

    @staticmethod
    def create_error_response(exception: BaseError) -> JSONResponse:
        """Creates a standardized error response.

        Args:
            exception (BaseError): The exception to be converted into a response.

        Returns:
            JSONResponse: A JSON response containing the exception details.
        """
        BaseUtils.capture_exception(exception)
        # Default to internal server error if status code is not set
        status_code = exception.http_status_code if exception.http_status_code else HTTPStatus.INTERNAL_SERVER_ERROR
        return JSONResponse(status_code=status_code, content=exception.to_dict())

    @staticmethod
    async def custom_exception_handler(request: Request, exception: BaseError) -> JSONResponse:  # noqa: ARG004
        """Handles custom errors.

        Args:
            request (Request): The incoming request.
            exception (BaseError): The custom exception to handle.

        Returns:
            JSONResponse: A JSON response containing the exception details.
        """
        return FastAPIExceptionHandler.create_error_response(exception)

    @staticmethod
    async def generic_exception_handler(request: Request, exception: Exception) -> JSONResponse:  # noqa: ARG004
        """Handles generic errors.

        Args:
            request (Request): The incoming request.
            exception (Exception): The generic exception to handle.

        Returns:
            JSONResponse: A JSON response containing the exception details.
        """
        return FastAPIExceptionHandler.create_error_response(UnknownError())

    @staticmethod
    async def validation_exception_handler(
        request: Request,  # noqa: ARG004
        exception: ValidationError,
    ) -> JSONResponse:
        """Handles validation errors.

        Args:
            request (Request): The incoming request.
            exception (ValidationError): The validation exception to handle.

        Returns:
            JSONResponse: A JSON response containing the validation error details.
        """
        # Using list comprehension instead of append for better performance
        errors: list[dict[str, str]] = [
            {
                "field": ".".join(str(x) for x in error["loc"]),
                "message": error["msg"],
                "value": str(error.get("input", "")),
            }
            for error in exception.errors()
        ]

        return JSONResponse(
            status_code=HTTPStatus.UNPROCESSABLE_ENTITY,
            content={"error": "VALIDATION_ERROR", "detail": errors},
        )


class FastAPIUtils:
    """Utility class for FastAPI configuration and setup."""

    @staticmethod
    def custom_generate_unique_id(route: APIRoute) -> str:
        """Generates a unique ID for API routes.

        Args:
            route (APIRoute): The route for which to generate a unique ID.

        Returns:
            str: A unique ID for the route.
        """
        return f"{route.tags[0]}-{route.name}" if route.tags else route.name

    @staticmethod
    def setup_sentry(config: BaseConfig) -> None:
        """Initializes Sentry configuration if enabled.

        Args:
            config (BaseConfig): The configuration object containing Sentry settings.
        """
        if not config.SENTRY.IS_ENABLED:
            return

        try:
            import sentry_sdk

            sentry_sdk.init(
                dsn=config.SENTRY.DSN,
                debug=config.SENTRY.DEBUG,
                release=config.SENTRY.RELEASE,
                sample_rate=config.SENTRY.SAMPLE_RATE,
                traces_sample_rate=config.SENTRY.TRACES_SAMPLE_RATE,
                environment=config.ENVIRONMENT,
            )
        except Exception:
            logging.exception("Failed to initialize Sentry")

    @staticmethod
    def setup_cors(app: FastAPI, config: BaseConfig) -> None:
        """Configures CORS middleware.

        Args:
            app (FastAPI): The FastAPI application instance.
            config (BaseConfig): The configuration object containing CORS settings.
        """
        origins = [str(origin).strip("/") for origin in config.FASTAPI.CORS_MIDDLEWARE_ALLOW_ORIGINS]
        app.add_middleware(
            CORSMiddleware,
            allow_origins=origins,
            allow_credentials=config.FASTAPI.CORS_MIDDLEWARE_ALLOW_CREDENTIALS,
            allow_methods=config.FASTAPI.CORS_MIDDLEWARE_ALLOW_METHODS,
            allow_headers=config.FASTAPI.CORS_MIDDLEWARE_ALLOW_HEADERS,
        )

    @staticmethod
    def setup_elastic_apm(app: FastAPI, config: BaseConfig) -> None:
        """Configures Elastic APM if enabled.

        Args:
            app (FastAPI): The FastAPI application instance.
            config (BaseConfig): The configuration object containing Elastic APM settings.
        """
        if not config.ELASTIC_APM.IS_ENABLED:
            return

        try:
            from elasticapm.contrib.starlette import ElasticAPM, make_apm_client

            apm_client = make_apm_client(
                {
                    "API_REQUEST_SIZE": config.ELASTIC_APM.API_REQUEST_SIZE,
                    "API_REQUEST_TIME": config.ELASTIC_APM.API_REQUEST_TIME,
                    "AUTO_LOG_STACKS": config.ELASTIC_APM.AUTO_LOG_STACKS,
                    "CAPTURE_BODY": config.ELASTIC_APM.CAPTURE_BODY,
                    "CAPTURE_HEADERS": config.ELASTIC_APM.CAPTURE_HEADERS,
                    "COLLECT_LOCAL_VARIABLES": config.ELASTIC_APM.COLLECT_LOCAL_VARIABLES,
                    "ENVIRONMENT": config.ENVIRONMENT,
                    "LOG_FILE": config.ELASTIC_APM.LOG_FILE,
                    "LOG_FILE_SIZE": config.ELASTIC_APM.LOG_FILE_SIZE,
                    "RECORDING": config.ELASTIC_APM.RECORDING,
                    "SECRET_TOKEN": config.ELASTIC_APM.SECRET_TOKEN,
                    "SERVER_TIMEOUT": config.ELASTIC_APM.SERVER_TIMEOUT,
                    "SERVER_URL": config.ELASTIC_APM.SERVER_URL,
                    "SERVICE_NAME": config.ELASTIC_APM.SERVICE_NAME,
                    "SERVICE_VERSION": config.ELASTIC_APM.SERVICE_VERSION,
                    "TRANSACTION_SAMPLE_RATE": config.ELASTIC_APM.TRANSACTION_SAMPLE_RATE,
                    "API_KEY": config.ELASTIC_APM.API_KEY,
                },
            )
            app.add_middleware(ElasticAPM, client=apm_client)
        except Exception:
            logging.exception("Failed to initialize Elastic APM")

    @staticmethod
    def setup_exception_handlers(app: FastAPI) -> None:
        """Configures exception handlers for the FastAPI application.

        Args:
            app (FastAPI): The FastAPI application instance.
        """
        # While these handlers don't match the exact type signatures expected by FastAPI,
        # they are compatible in practice as they return JSONResponse objects.
        # We need to use a more general type cast to bypass the strict type checking.
        validation_handler = cast(
            Callable[[Request, Exception], Awaitable[Response]],
            FastAPIExceptionHandler.validation_exception_handler,
        )
        custom_handler = cast(
            Callable[[Request, Exception], Awaitable[Response]],
            FastAPIExceptionHandler.custom_exception_handler,
        )
        generic_handler = cast(
            Callable[[Request, Exception], Awaitable[Response]],
            FastAPIExceptionHandler.generic_exception_handler,
        )

        app.add_exception_handler(RequestValidationError, validation_handler)
        app.add_exception_handler(ValidationError, validation_handler)
        app.add_exception_handler(BaseError, custom_handler)
        app.add_exception_handler(Exception, generic_handler)


class AppUtils:
    """Utility class for creating and configuring FastAPI applications."""

    @classmethod
    def create_fastapi_app(
        cls,
        config: BaseConfig | None = None,
        *,
        configure_exception_handlers: bool = True,
    ) -> FastAPI:
        """Creates and configures a FastAPI application.

        Args:
            config (BaseConfig | None): Optional custom configuration. If not provided, uses global config.
            configure_exception_handlers (bool): Whether to configure exception handlers.

        Returns:
            FastAPI: The configured FastAPI application instance.
        """
        config = config or BaseConfig.global_config()

        # Define common responses for all endpoints
        common_responses = BaseUtils.get_fastapi_exception_responses(
            [UnknownError, UnavailableError, InvalidArgumentError],
        )
        app = FastAPI(
            title=config.FASTAPI.PROJECT_NAME,
            openapi_url=config.FASTAPI.OPENAPI_URL,
            generate_unique_id_function=FastAPIUtils.custom_generate_unique_id,
            swagger_ui_parameters=config.FASTAPI.SWAGGER_UI_PARAMS,
            docs_url=config.FASTAPI.DOCS_URL,
            redocs_url=config.FASTAPI.RE_DOCS_URL,
            responses=cast(dict[int | str, Any], common_responses),
        )

        FastAPIUtils.setup_sentry(config)
        FastAPIUtils.setup_cors(app, config)
        FastAPIUtils.setup_elastic_apm(app, config)

        if configure_exception_handlers:
            FastAPIUtils.setup_exception_handlers(app)

        return app

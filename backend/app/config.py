"""Configuraciones de aplicación de FastAPI."""
import os

from fastapi import FastAPI, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.requests import Request

from app.exceptions import ExceptionBase
from app.routers import permissions, roles, token, users


def create_app() -> FastAPI:
    """Crear aplicación de FastAPI.

    Returns:
        aplicación de FastAPI
    """
    root_path = os.environ.get("API_PATH", "")

    app = FastAPI(root_path=root_path)

    attach_app_cors(app)
    attach_app_routers(app)
    attach_app_exception_handlers(app)

    return app


def attach_app_cors(app: FastAPI) -> None:
    """Conectar el middleware de CORS a aplicación de FastAPI.

    Arguments:
        app -- aplicación de FastAPI
    """
    origins = os.environ.get("CORS_ORIGINS", "").split(",")

    if origins:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=origins,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )


def attach_app_routers(app: FastAPI) -> None:
    """Conectar ruteadores a aplicación de FastAPI.

    Arguments:
        app -- aplicación de FastAPI
    """
    app.include_router(permissions.router)
    app.include_router(roles.router)
    app.include_router(token.router)
    app.include_router(users.router)


def attach_app_exception_handlers(app: FastAPI) -> None:
    """Conectar excepciones a aplicación de FastAPI.

    Arguments:
        app -- aplicación de FastAPI
    """

    @app.exception_handler(ExceptionBase)
    async def service_exception_handler(_: Request, e: ExceptionBase) -> JSONResponse:
        """Controlador de excepción de servicio.

            e -- excepción de servicio

        Returns:
            JSONResponse
        """
        status_code = {
            ExceptionBase.Type.UNAUTHORIZED: status.HTTP_401_UNAUTHORIZED,
            ExceptionBase.Type.FORBIDDEN: status.HTTP_403_FORBIDDEN,
            ExceptionBase.Type.INVALID_INPUT: status.HTTP_400_BAD_REQUEST,
            ExceptionBase.Type.NOT_FOUND: status.HTTP_404_NOT_FOUND,
            ExceptionBase.Type.ALREADY_EXIST: status.HTTP_409_CONFLICT,
        }.get(e.error_type, status.HTTP_400_BAD_REQUEST)

        return JSONResponse(
            status_code=status_code,
            content={"detail": e.message, "status": status_code},
            headers={"Content-Type": "application/problem+json"},
        )

    @app.exception_handler(RequestValidationError)
    async def request_validation_exception_handler(
        _: Request, e: RequestValidationError
    ) -> JSONResponse:
        """Controlador de excepción de servicio.

            e -- excepción de servicio

        Returns:
            JSONResponse
        """
        status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
        detail = [x["msg"] for x in e.errors()]
        return JSONResponse(
            status_code=status_code,
            content={"detail": detail, "status": status_code},
            headers={"Content-Type": "application/problem+json"},
        )

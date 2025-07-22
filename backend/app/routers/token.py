"""Router para endpoints de token."""

from fastapi import APIRouter, Depends

from app.dependencies import get_credentials, get_user_service
from app.schemas.token import Credentials, Token
from app.services.user import UserService

router = APIRouter(
    prefix="/token",
    tags=["token"],
)


@router.post("/")
async def post_token(
    credentials: Credentials = Depends(get_credentials),
    token_service: UserService = Depends(get_user_service),
) -> Token:
    """Obtener token de autenticación.

    Las credenciales se toman de Form Data en el request, son extraidas y .

    Returns:
        JWT (JSON web token) con el acceso codificado.
    """
    return token_service.token(credentials)

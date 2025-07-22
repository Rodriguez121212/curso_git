"""Servicio de usuarios."""
import itertools
import os
import re
import uuid
from datetime import datetime, timedelta
from typing import Any, Dict, List

from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from email_validator import EmailNotValidError, validate_email
from jose import JWTError, jwt
from multimethod import multimethod
from redbird.oper import in_, not_equal

from app.schemas.token import Credentials, Token, TokenData
from app.schemas.user import (
    UpdatePassword,
    UserCreate,
    UserNewPassword,
    UserPublic,
    UserUpdate,
)
from app.services import BaseService, ServiceException


class UserService(BaseService):
    """Servicio de usuarios."""

    __ACCESS_TOKEN_EXPIRE_MINUTES = 30
    __JWT_ALGORITHM = "HS256"  # to get a string like this run: openssl rand -hex 32
    __JWT_SECRET_KEY = os.environ.get("SECRET", "")

    __password_hasher = PasswordHasher()

    @classmethod
    def encode_access_token(cls, data: Dict[str, Any]) -> str:
        """Codificar datos dentro de token de acceso.

        Arguments:
            data -- datos a codificar en el access token

        Returns:
            Token de acceso
        """
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(
            minutes=cls.__ACCESS_TOKEN_EXPIRE_MINUTES
        )
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(
            to_encode, cls.__JWT_SECRET_KEY, algorithm=cls.__JWT_ALGORITHM
        )
        return encoded_jwt

    def token(self, credentials: Credentials) -> Token:
        """Autenticar usuario.

        Arguments:
            credentials -- credenciales de usuario

        Returns:
            Token de autorización
        """
        credentials_exception = ServiceException(
            error_type=ServiceException.Type.UNAUTHORIZED,
            message="incorrect username or password",
        )
        user = self.repository.filter_by(username=credentials.username).first()
        if not user:
            raise credentials_exception
        if user:
            try:
                self.__password_hasher.verify(
                    hash=user["hashed_password"], password=credentials.password
                )
            except VerifyMismatchError:
                raise credentials_exception

        access_token = UserService.encode_access_token(
            data={"sub": credentials.username}
        )
        return Token(access_token=access_token, token_type=Token.Type.BEARER)

    def insert(self, user_create: UserCreate) -> uuid.UUID:
        """Crear usuario.

        Arguments:
            user_create -- informacion de usuario a crear

        Raises:
            ServiceException: ALREADY_EXIST si nombre de usuario o email están en uso
            ServiceException: INVALID_INPUT si el email es incorrecto

        Returns:
            identificador de usuario creado
        """
        exiting_user = self.repository.filter_by(username=user_create.username).first()
        if exiting_user:
            raise ServiceException(
                error_type=ServiceException.Type.ALREADY_EXIST,
                message="actually username exist",
            )
        exiting_user = self.repository.filter_by(username=user_create.username).first()
        try:
            validate_email(user_create.email, check_deliverability=True)
        except EmailNotValidError as email_not_valid_error:
            raise ServiceException(
                error_type=ServiceException.Type.INVALID_INPUT,
                message=str(email_not_valid_error),
            )
        exiting_user = self.repository.filter_by(email=user_create.email).first()
        if exiting_user:
            raise ServiceException(
                error_type=ServiceException.Type.ALREADY_EXIST,
                message="actually email exist",
            )

        id = uuid.uuid4()
        user_data = {
            "id": id,
            "username": user_create.username,
            "first_name": user_create.first_name,
            "last_name": user_create.last_name,
            "email": user_create.email,
            "hashed_password": self.__password_hasher.hash(user_create.password),
        }

        self.repository.insert(user_data)
        return id

    def list(self, skip: int, limit: int) -> List[UserPublic]:
        """Listar usuarios disponibles.

        Arguments:
        skip -- numero de registros omitidos
        limit -- límite de registros entregados

        Returns:
            Lista de roles
        """
        user_iter = iter(self.repository)
        return list(itertools.islice(user_iter, skip, skip + limit))

    @multimethod
    def get_by(self, token: str) -> UserPublic:
        """Obtener usuario.

        Arguments:
            token -- token con información de usuario codificada

        Raises:
            ServiceException: UNAUTHORIZED si usuario no puede ser obtenido de token

        Returns:
            Usuario
        """
        credentials_exception = ServiceException(
            error_type=ServiceException.Type.UNAUTHORIZED,
            message="Could not validate credentials",
        )
        try:
            payload = jwt.decode(
                token, self.__JWT_SECRET_KEY, algorithms=[self.__JWT_ALGORITHM]
            )
            username = payload.get("sub")
            if not username:
                raise credentials_exception
            token_data = TokenData(username=username)
        except JWTError:
            raise credentials_exception
        if token_data and token_data.username:
            user = self.repository.filter_by(username=username).first()
        if user:
            return UserPublic(**user)
        raise credentials_exception

    @get_by.register
    def _(self, user_id: uuid.UUID) -> UserPublic:
        """Obtener usuario.

        Arguments:
            user_id -- identificador de usuario

        Raises:
            ServiceException: NOT FOUND si el usuario no existe

        Returns:
            Usuario
        """
        user = self.repository.get_by(user_id).first()
        if user:
            return UserPublic(**user)
        raise ServiceException(
            error_type=ServiceException.Type.NOT_FOUND,
            message=f"user {user_id} not found",
        )

    @multimethod
    def filter_by(self, user_ids: List[uuid.UUID]) -> List[UserPublic]:
        """Filtrar usuarios.

        Arguments:
            user_ids -- identificadores de usuarios

        Returns:
            Lista de usuarios
        """
        users = [
            UserPublic(**user)
            for user in list(self.repository.filter_by(user_id=in_(user_ids)).all())
        ]
        return users

    @multimethod
    def update(self, user_id: uuid.UUID, update_new_password: UserNewPassword) -> None:
        """Actualizar usuario con nueva contraseña.

        Arguments:
            user_id -- identificador de usuario a actualizar
            update_new_password -- información de contraseña a actualizar.

        Raises:
            ServiceException: INVALID_INPUT si el formato incorrecto de contraseña
        """
        password_regex = re.compile(r"^[a-zA-Z0-9@$!%*?&#]{8,24}$")
        if not password_regex.fullmatch(str(update_new_password.new_password)):
            raise ServiceException(
                error_type=ServiceException.Type.INVALID_INPUT,
                message="incorrect password format, please check and try again",
            )
        hashed_password = self.__password_hasher.hash(update_new_password.new_password)
        self.repository.get_by(user_id).update(hashed_password=hashed_password)

    @update.register
    def _(self, user_id: uuid.UUID, update_password: UpdatePassword) -> None:
        """Actualizar usuario con nueva contraseña.

        Arguments:
            user_id -- identificador de usuario a actualizar
            update_password -- información de contraseña actual y nueva contraseña

        Raises:
            ServiceException: FORBIDDEN si la contraseña actual no coincide
        """
        current_user = self.repository.get_by(user_id).first()
        try:
            self.__password_hasher.verify(
                hash=current_user["hashed_password"],
                password=update_password.current_password,
            )
        except VerifyMismatchError:
            raise ServiceException(
                error_type=ServiceException.Type.FORBIDDEN,
                message="Incorrect password, please check and try again",
            )
        self.update(user_id, UserNewPassword(new_password=update_password.new_password))

    @update.register
    def _(self, user_id: uuid.UUID, user_update: UserUpdate) -> None:
        """Actualizar usuario.

        Arguments:
            user_id -- identificador de usuario
            user_update -- información a actualizar de usuario

        Raises:
            ServiceException: NOT_FOUND si el usuario no existe
            ServiceException: INVALID_INPUT si el email es incorrecto
            ServiceException: ALREADY_EXIST si el email pertenece a otro usuario
        """
        user = self.repository.get_by(user_id).first()
        if not user:
            raise ServiceException(
                error_type=ServiceException.Type.NOT_FOUND,
                message=f"user {user_id} not found",
            )
        if user_update.email:
            try:
                validate_email(user_update.email, check_deliverability=True)
            except EmailNotValidError as email_not_valid_error:
                raise ServiceException(
                    error_type=ServiceException.Type.INVALID_INPUT,
                    message=str(email_not_valid_error),
                )
            other_user = self.repository.filter_by(
                id=not_equal(user_id), email=user_update.email
            ).first()
            if other_user:
                raise ServiceException(
                    error_type=ServiceException.Type.ALREADY_EXIST,
                    message="actually email exist",
                )
        user_update_data = user_update.model_dump(exclude_unset=True, exclude_none=True)
        keys_with_same_value = [
            key for key, value in user_update_data.items() if user[key] == value
        ]
        for key in keys_with_same_value:
            del user_update_data[key]

        if user_update_data:
            self.repository.get_by(id=user_id).update(**user_update_data)

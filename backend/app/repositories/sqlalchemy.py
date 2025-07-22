"""Configuraciones de repositorio de SQLAlchemy."""
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

# TODO: Crear stubs para redbird for typing


def get_url_connection(db_name: str = "DB") -> str:
    """Obtener la URL para conectarse a base de datos.

    Keyword Arguments:
        db_name -- nombre de base de datos (default: {"DB"})

    Returns:
        URL
    """
    names = ["TYPE", "USER", "PASSWORD", "HOST", "PORT", "NAME"]
    vars = [os.environ.get(f"{db_name}_{name}") for name in names]
    return f"{vars[0]}://{vars[1]}:{vars[2]}@{vars[3]}:{vars[4]}/{vars[5]}"


def get_session(db_name: str = "DB") -> sessionmaker[Session]:
    """Obtener clase para generar sesiones de base de datos.

    Variables de entorno requeridas:
    - {db_name}_TYPE
    - {db_name}_USER
    - {db_name}_PASSWORD
    - {db_name}_HOST
    - {db_name}_PORT
    - {db_name}_NAME

    Arguments:
        db_name -- nombre de base de datos

    Returns:
        Generador de sessiones para la base de datos proporcionada.
    """
    url = get_url_connection(db_name)
    engine = create_engine(url)
    return sessionmaker(bind=engine)

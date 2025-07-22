"""Esquemas de permiso."""
from pydantic import BaseModel, ConfigDict


class Permission(BaseModel):
    """Esquema para permiso de rol."""

    id: str
    module: str
    description: str
    model_config = ConfigDict(from_attributes=True)

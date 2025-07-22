"""Relación roles y permisos iniciales."""
from app.data.permissions import initial_permissions
from app.data.roles import initial_roles

# Rol de Administrador tiene todos los permisos
initial_role_permissions = [
    {"role_id": initial_roles[0]["id"], "permission_id": permission["id"]}
    for permission in initial_permissions
]


# Rol Usuario tiene permiso de actualizar datos de perfil

initial_role_permissions += [
    {"role_id": initial_roles[1]["id"], "permission_id": initial_permissions[8]["id"]}
]

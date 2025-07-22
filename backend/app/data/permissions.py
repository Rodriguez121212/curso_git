"""Permisos iniciales."""
initial_permissions = [
    {
        "id": "get_current_user_info",
        "module": "usuarios",
        "description": "Obtiene información de usuario actual",
    },
    {
        "id": "get_user_info",
        "module": "usuarios",
        "description": "Obtiene información de usuario",
    },
    {
        "id": "get_user_info_with_roles_and_permissions",
        "module": "usuarios",
        "description": "Obtiene información de usuario en incluyendo roles y permisos",
    },
    {
        "id": "assign_user_roles",
        "module": "usuarios",
        "description": "Asigna uno o varios roles a usuario",
    },
    {
        "id": "unassign_user_roles",
        "module": "usuarios",
        "description": "Desasigna uno o varios roles a usuario",
    },
    {
        "id": "create_new_user",
        "module": "usuarios",
        "description": "Crea nuevo usuario",
    },
    {
        "id": "update_current_user_password",
        "module": "usuarios",
        "description": "Actualiza contraseña de usuario actual",
    },
    {
        "id": "get_all_users",
        "module": "usuarios",
        "description": "Obtiene lista de usuarios",
    },
    {
        "id": "update_user_info",
        "module": "usuarios",
        "description": "Actualiza información de usuario",
    },
    {"id": "get_role", "module": "roles", "description": "Obtiene rol de usuario"},
    {
        "id": "create_new_role",
        "module": "roles",
        "description": "Crea nuevo rol de usuario",
    },
    {
        "id": "delete_role",
        "module": "roles",
        "description": "Elimina rol de usuario",
    },
    {
        "id": "update_role",
        "module": "roles",
        "description": "Edita información de rol",
    },
    {
        "id": "get_all_roles",
        "module": "roles",
        "description": "Obtiene lista de roles",
    },
    {
        "id": "assign_role_permissions",
        "module": "roles",
        "description": "Asigna uno o varios permisos a rol",
    },
    {
        "id": "unassign_role_permissions",
        "module": "roles",
        "description": "Desasigna uno o varios permisos a rol",
    },
    {
        "id": "get_all_permissions",
        "module": "permisos",
        "description": "Obtiene lista de permisos de sistema",
    },
    {
        "id": "get_roles",
        "module": "roles",
        "description": "Obtiene lista de permisos asignados a rol",
    },
    {
        "id": "update_user_password",
        "module": "usuarios",
        "description": "Actualiza contraseña de usuario",
    },
]

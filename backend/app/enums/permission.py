"""Permission Enum."""
from enum import Enum


class Permission(Enum):
    """Enumeración de tipo de permisos para router de usuario."""

    # Permissions router
    GET_ALL_PERMISSIONS = "get_all_permissions"
    GET_ROLES = "get_roles"

    # Role router
    GET_ROLE = "get_role"
    CREATE_NEW_ROLE = "create_new_role"
    UPDATE_ROLE = "update_role"
    GET_ALL_ROLES = "get_all_roles"
    ASSIGN_ROLE_PERMISSIONS = "assign_role_permissions"
    UNASSIGN_ROLE_PERMISSIONS = "unassign_role_permissions"
    DELETE_ROLE = "delete_role"

    # Users router
    GET_USER_INFO = "get_user_info"
    GET_USER_INFO_WITH_ACCESS_DATA = "get_user_info_with_roles_and_permissions"
    ASSIGN_USER_ROLES = "assign_user_roles"
    UNASSIGN_USER_ROLES = "unassign_user_roles"
    CREATE_NEW_USER = "create_new_user"
    GET_ALL_USERS = "get_all_users"
    UPDATE_USER_INFO = "update_user_info"
    UPDATE_USER_PRIVATE = "update_user_password"

"""Relación usuarios y roles iniciales."""
from app.data.roles import initial_roles
from app.data.users import initial_users

initial_users_roles = [
    {"user_id": initial_users[0]["id"], "role_id": initial_roles[0]["id"]}
]

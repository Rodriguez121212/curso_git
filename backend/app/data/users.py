"""Usuarios iniciales."""
from uuid import UUID

initial_users = [
    {
        "id": UUID("4f1aecbe-ccc4-4e55-987f-e1c28ab54f06"),
        "username": "Administrador",
        "hashed_password": "$argon2id$v=19$m=65536,t=3,p=4$n/mlqJoiT"
        "zHMjqYHUqIuxQ$ZSpyRzTputhjiE9xSCoEuMMaasy5hPWgOb1m0oUtyFs",
        "first_name": "test_firstname",
        "last_name": "test_lastname",
        "email": "Administrador@kadasoftware.com",
    },
]

#! /usr/bin/env bash

# Run migrations
alembic upgrade head

# Create initial data in DB
python3 /app/app/initial_data.py

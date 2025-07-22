FROM tiangolo/uvicorn-gunicorn-fastapi:python3.11 AS python_base

FROM python_base AS backend
LABEL name=btu-backend version=1.0.0
WORKDIR /app
COPY ./prestart.sh /app/prestart.sh
COPY ./requirements.txt /app/requirements.txt
COPY ./alembic.ini /app/alembic.ini
COPY ./app /app/app
COPY ./alembic /app/alembic
RUN python -m pip install --no-cache-dir -r /app/requirements.txt

FROM backend AS backend_debug
LABEL name=btu-backend_debug version=1.0.0
COPY ./tests /app/tests
COPY ./utils /app/utils
RUN python -m pip install --no-cache-dir -r /app/tests/requirements.txt
CMD ["/start-reload.sh"]

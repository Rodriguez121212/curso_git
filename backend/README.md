# Testing

Before commit run the tests and fix the problems.

## Run pytest on docker container

```
docker exec btu-api-dev pytest
```

## Run coverage test report

```
docker exec btu-api-dev pytest --cov-report term-missing:skip-covered --cov app
```

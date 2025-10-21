.PHONY: dev worker migrate initdb

initdb:
	alembic -c projects/tools/db/alembic.ini upgrade head

migrate:
	alembic -c projects/tools/db/alembic.ini revision --autogenerate -m "update"

dev:
	uvicorn projects.tools.api.main:app --reload --port 8000

worker:
	python -m projects.tools.worker.worker

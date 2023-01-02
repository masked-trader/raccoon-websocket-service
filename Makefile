SHELL := /bin/bash

.DEFAULT_GOAL := build

TOP_DIR = $(realpath .)

build:
	docker compose build --no-cache

clean:
	docker system prune --force
	docker volume prune --force
	docker network prune --force

debug_service:
	docker compose exec raccoon-websocket bash

debug_redis:
	docker compose exec redis redis-cli

test:
	poetry run python3 -m py.test tests/

venv: venv_clean
	poetry config virtualenvs.in-project true
	poetry install

venv_clean:
	poetry env remove --all


#!make
# Setup the shell and python version.
# It's necessary to set this because some environments don't link sh -> bash.
SHELL := /bin/bash
PYTHON := python3
ENVFILE := .env
SERVICES := schema_registry
DB_DATABASE:= schema_regestry
CONTAINER_NAME := schema_regestry
ISORT := isort -rc -m 3 -e -fgw -q
# -fass, --force-alphabetical-sort-within-sections
# -e, --balanced
# -m, --multi-line
# -q, --quiet
# -rc, --recursive
# -fgw, --force-grid-wrap
# -d, --stdout

VIRTUAL_ENV_CHECK := import sys;b=hasattr(sys, \"real_prefix\");r=hasattr(sys, \"base_prefix\");print(b or (r and sys.base_prefix != sys.prefix))
VIRTUAL_ENV := $(shell echo "$(VIRTUAL_ENV_CHECK)" | python3.5)

RUN_ARGS := $(wordlist 2,$(words $(MAKECMDGOALS)),$(MAKECMDGOALS))
$(eval $(RUN_ARGS):;@:)

.PHONY: help build install run test tox lint sort migrate migrations clean clean-build clean-pyc in_data_dump out_data_dump

help:
	@echo "Использование: make <command>"
	@echo
	@echo "Доступные команды (все операции через docker-compose):"
	@echo "  build              сбилдить сервисы"
	@echo "  run                запустить сервисы"
	@echo "  stop               остановить сервисы"
	@echo "  restart            перезапустить сервисы"
	@echo "  test               запуск тестов (pytest)"
	@echo "  lint               запуск линтеров"
	@echo "  tox                запуск тестов и линтеров"

build:
ifeq ($(VIRTUAL_ENV), True)
	@pip install -i http://nexus.centr.m:8081/repository/pypi/simple/  --trusted-host nexus.centr.m -r requirements.txt
	@pip install -i http://nexus.centr.m:8081/repository/pypi/simple/  --trusted-host nexus.centr.m -r requirements.dev.txt
else
	@docker-compose build
endif

install: build

run:
ifeq ($(VIRTUAL_ENV), True)
	@watchmedo auto-restart --pattern="*.py" --recursive --directory="." python app.py
else
	@docker-compose up -d
endif

stop:
ifeq ($(VIRTUAL_ENV), True)
	@echo "does not run"
else
	@docker-compose down
endif

restart:
ifeq ($(VIRTUAL_ENV), True)
	@echo "does not run"
else
	@docker-compose down && docker-compose up -d
endif

test:
ifeq ($(VIRTUAL_ENV), True)
	@pytest tests
else
	docker-compose run --rm -v $(PWD)/tests:/app/tests:ro $(CONTAINER_NAME) python -m pytest
endif

lint:
ifeq ($(VIRTUAL_ENV), True)
	@flake8 $(SERVICES)
else
	@docker-compose run --rm $(CONTAINER_NAME) flake8 $(SERVICES)
endif

sort:
ifeq ($(VIRTUAL_ENV), True)
	$(ISORT)
else
	@docker-compose run --rm -v $(PWD)/tests:/app/tests $(CONTAINER_NAME) $(ISORT)
endif

migrations:
	@alembic revision -m "auto" --autogenerate --head head
	@git add db/alembic/versions/.

migrate:
	@alembic upgrade head
	@eralchemy -i postgresql://postgres:postgres@localhost/$(DB_DATABASE) -o docs/erd.pdf

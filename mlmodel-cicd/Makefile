COMPOSE_FILE ?= docker/docker-compose.yml

run:
	docker compose -f $(COMPOSE_FILE) down -v && docker compose -f $(COMPOSE_FILE) up --build

install:
	pip install -r requirements.txt

ml:
	python mlmodel_cicd.py
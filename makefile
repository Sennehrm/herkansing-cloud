DC=docker compose

.PHONY: help deploy up down restart logs build clean

help:
	@echo "Beschikbare commando's:"
	@echo "  make deploy   - Voert de complete CI/CD pipeline uit"
	@echo "  make up       - Start alle containers in de achtergrond"
	@echo "  make down     - Stopt alle containers"
	@echo "  make restart  - Herstart de volledige stack"
	@echo "  make logs     - Toont live logging van alle services"
	@echo "  make build    - Bouwt alle custom images opnieuw"
	@echo "  make clean    - Stopt stack en verwijdert dangling images"

deploy:
	git pull origin main
	$(DC) build --no-cache
	$(DC) up -d --remove-orphans
	docker image prune -f
	$(DC) ps

up:
	$(DC) up -d

down:
	$(DC) down

restart: down up

logs:
	$(DC) logs -f

build:
	$(DC) build --no-cache

clean:
	$(DC) down -v
	docker image prune -f

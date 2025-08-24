.PHONY: build up run exec stop logs extract

DOCKER=docker-compose
SERVICE=nggasak-analyzer

build:
	$(DOCKER) build

up:
	$(DOCKER) up -d $(SERVICE)

run:
	$(DOCKER) run --rm $(SERVICE)

exec:
	$(DOCKER) exec $(SERVICE) bash

stop:
	$(DOCKER) down

logs:
	$(DOCKER) logs -f $(SERVICE)
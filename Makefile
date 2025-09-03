.PHONY: build up exec stop logs

DOCKER=docker-compose
SERVICE=nggasak-analyzer

build:
	$(DOCKER) build

up:
	$(DOCKER) up -d $(SERVICE)

exec:
	$(DOCKER) exec -it $(SERVICE) bash

stop:
	$(DOCKER) down

logs:
	$(DOCKER) logs -f $(SERVICE)
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

# Generate analysis/curl.txt from decompiled sources
extract:
	python3 scripts/extract_endpoints.py --root ./data/decompiled --out ./analysis/curl.txt

# Process any .apk/.xapk in ./data once (inside container)
process-once: up
	$(DOCKER) exec $(SERVICE) bash -lc "python3 /scripts/auto_queue.py --once"

# Watch ./data for new files and process automatically
watch: up
	$(DOCKER) exec -d $(SERVICE) bash -lc "python3 /scripts/auto_queue.py --watch"

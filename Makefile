.PHONY: all

local-run-dev:
	docker compose -p dev -f docker-compose.yml -f docker-compose.dev.yml up --build

local-run-prod:
	docker compose -p prod -f docker-compose.yml up --build
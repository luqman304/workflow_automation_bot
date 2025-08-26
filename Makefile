.PHONY: run test lint docker

run:
	uvicorn app.main:app --reload --port 8000

test:
	pytest -q

lint:
	flake8 app tests

docker:
	docker build -t workflow_automation_bot:latest .

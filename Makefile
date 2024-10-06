install:
	@curl -sSL https://install.python-poetry.org | python3 -
	@poetry install

run:
	@poetry run python main.py

test:
	@poetry run pytest

lint:
	@poetry run isort .
	@poetry run black .
	@poetry run flake8

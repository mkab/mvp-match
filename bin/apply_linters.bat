poetry run black --config=../pyproject.toml ../vending_machine/vending;
poetry run flake8 --config=../config.ini ../vending_machine/vending;
poetry run isort --sp=../pyproject.toml ../vending_machine/vending

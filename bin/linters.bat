poetry run flake8 --config=../config.ini ../vending_machine/vending
poetry run black --config=../pyproject.toml --check --diff ../vending_machine/vending
poetry run isort --sp=../pyproject.toml --check --diff ../vending_machine/vending
!#/bin/bash

curl -sSL https://install.python-poetry.org | python3 -

poetry config virtualenvs.in-project true

poetry self add poethepoet[plugin]

echo "Configuration complete. You can now use the 'poe' command to run tasks defined in pyproject.toml."
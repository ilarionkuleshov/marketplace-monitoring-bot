set -e

echo "Isort formatting..."
isort src/

echo "Autoflake formatting..."
autoflake src/

echo "Black formatting..."
black src/

echo "Flake8 checking..."
flake8 src/

echo "Pylint checking..."
pylint src/

echo "Mypy checking..."
mypy src/

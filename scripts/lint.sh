set -e

echo "Isort checking..."
isort src/ --check

echo "Autoflake checking..."
autoflake src/ --check

echo "Black checking..."
black src/ --check

echo "Flake8 checking..."
flake8 src/

echo "Pylint checking..."
pylint src/

echo "Mypy checking..."
mypy src/

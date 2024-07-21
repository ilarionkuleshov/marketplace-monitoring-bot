set -e

echo "isort checking..."
isort src --check

echo "autoflake checking..."
autoflake src --check

echo "black checking..."
black src --check

echo "flake8 checking..."
flake8 src

echo "pylint checking..."
pylint src

echo "mypy checking..."
mypy src

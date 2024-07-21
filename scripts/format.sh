set -e

echo "isort formatting..."
isort src

echo "autoflake formatting..."
autoflake src

echo "black formatting..."
black src

echo "flake8 checking..."
flake8 src

echo "pylint checking..."
pylint src

echo "mypy checking..."
mypy src

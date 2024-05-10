set -e

echo "isort checking"
isort src tests --check

echo "autoflake checking"
autoflake src tests --check

echo "black checking"
black src tests --check

echo "flake8 checking"
flake8 src tests

echo "pylint checking"
pylint src tests

echo "mypy checking"
mypy src
mypy tests

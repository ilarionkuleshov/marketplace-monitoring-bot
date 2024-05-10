set -e

echo "isort formatting"
isort src tests

echo "autoflake formatting"
autoflake src tests

echo "black formatting"
black src tests

echo "flake8 checking"
flake8 src tests

echo "pylint checking"
pylint src tests

echo "mypy checking"
mypy src
mypy tests

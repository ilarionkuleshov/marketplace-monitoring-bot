set -e

echo "isort formatting:"
isort src

echo "autoflake formatting:"
autoflake src

echo "black formatting:"
black src

echo "flake8 check:"
flake8 src

echo "pylint check:"
pylint src

echo "mypy check:"
mypy src

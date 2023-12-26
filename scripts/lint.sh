echo "isort check:"
isort src --check

echo "autoflake check:"
autoflake src --check

echo "black check:"
black src --check

echo "flake8 check:"
flake8 src

echo "pylint check:"
pylint src

echo "mypy check:"
mypy src

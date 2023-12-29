"""Script to generate postman collection for the API.

Command to run (in `src` directory):
    $ python -m api.utils.generate_postman_collection

To customize name of the postman collection (default is `Marketplace Monitoring Bot API`):
    $ python -m api.utils.generate_postman_collection --name=custom_name

"""

import inspect
import json
from argparse import ArgumentParser
from pathlib import Path
from string import Template
from typing import Any

from fastapi import FastAPI
from fastapi.routing import APIRoute

from api.schemas.base import SchemaWithExample
from api.utils import create_app

URL_TEMPLATE = Template("{{api_url}}$path")


def get_post_request_body(route: APIRoute) -> dict[str, Any] | None:
    """Returns example body for the POST `route`."""
    post_arg_type = next(iter(route.endpoint.__annotations__.values()))

    if issubclass(post_arg_type, SchemaWithExample):
        return {
            "mode": "raw",
            "raw": post_arg_type.example().model_dump_json(indent=4),
            "options": {"raw": {"language": "json"}},
        }

    return None


def get_query_parameters(route: APIRoute) -> list[dict[str, Any]]:
    """Returns query parameters for `route`."""
    query_parameters = []
    for parameter in inspect.signature(route.endpoint).parameters:
        if parameter not in ["db_provider"]:
            query_parameters.append(
                {
                    "key": parameter,
                    "value": None,
                    "disabled": True,
                }
            )
    return query_parameters


def get_route_items(app: FastAPI) -> list[dict[str, Any]]:
    """Returns items for routes to create postman collection.

    Args:
        app (FastAPI): FastAPI app to get routes.

    """
    items = []

    for route in app.routes:
        if not isinstance(route, APIRoute):
            continue

        method = route.methods.pop()
        path = route.path.replace("{", ":").replace("}", "")

        item: dict[str, Any] = {
            "name": route.name.replace("_", " ").title(),
            "request": {
                "method": method,
                "url": {
                    "raw": URL_TEMPLATE.substitute(path=path),
                    "host": ["{{api_url}}"],
                    "path": path,
                },
            },
        }

        if method in ["POST", "PATCH"] and (body := get_post_request_body(route)):
            item["request"]["body"] = body
        elif query_parameters := get_query_parameters(route):
            item["request"]["url"]["query"] = query_parameters

        items.append(item)

    return items


def main() -> None:
    """Creates API postman collection."""
    arg_parser = ArgumentParser()
    arg_parser.add_argument(
        "--name", type=str, help="Name of the postman collection.", default="Marketplace Monitoring Bot API"
    )
    args = arg_parser.parse_args()

    app = create_app()

    collection = {
        "info": {
            "name": args.name,
            "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json",
        },
        "item": get_route_items(app),
        "auth": {
            "type": "apikey",
            "apikey": [
                {"key": "value", "value": "{{x_api_key}}", "type": "string"},
                {"key": "key", "value": "x-api-key", "type": "string"},
            ],
        },
        "variable": [
            {"key": "api_url", "value": "", "type": "string"},
            {"key": "x_api_key", "value": "", "type": "string"},
        ],
    }

    path = Path.cwd().parent / "docs" / f"{args.name}.postman_collection.json"
    with open(path, "w", encoding="utf-8") as file:
        json.dump(collection, file, indent=4)


if __name__ == "__main__":
    main()

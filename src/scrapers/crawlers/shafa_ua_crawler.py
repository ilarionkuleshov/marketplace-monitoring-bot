from typing import Any, AsyncIterator

from fastcrawl import Request, Response
from httpx import URL

from database.schemas import AdvertCreate
from scrapers.crawlers.base_advert_crawler import BaseAdvertCrawler


class ShafaUaCrawler(BaseAdvertCrawler):
    """Crawler for scraping adverts from `shafa.ua`."""

    async def generate_requests(self) -> AsyncIterator[Request]:
        """Yields GraphQL request to start scraping."""
        yield self._build_graphql_request()

    async def parse_catalog(
        self, response: Response, metadata: dict[str, Any]
    ) -> AsyncIterator[AdvertCreate | Request]:
        """Parses GraphQL response with catalog data.

        Args:
            response (Response): GraphQL response.

        Yields:
            AdvertCreate: Extracted advert.
            Request: Next page request.

        """
        products = response.get_json_data()["data"]["products"]

        for product in products["edges"]:
            node = product["node"]
            yield AdvertCreate(
                monitoring_id=self.monitoring_id,
                monitoring_run_id=self.monitoring_run_id,
                url="https://shafa.ua" + node["url"],
                title=self.crop_advert_title(node["name"]),
                image=node["thumbnail"],
                price=node["price"],
                currency="UAH",
            )

        if products["pageInfo"]["hasNextPage"]:
            yield self._build_graphql_request(metadata["page"] + 1)

    def _build_graphql_request(self, page: int = 1) -> Request:
        """Returns GraphQL request.

        Args:
            page (int): Page number. Default is 1.

        """
        url = self._prepare_monitoring_url()
        return Request(
            url="https://shafa.ua/api/v3/graphiql",
            method="POST",
            json_data=self._build_graphql_payload(url, page),
            cookies={"language": "uk" if url.path.lstrip("/").split("/")[0] == "uk" else "ru"},
            callback=self.parse_catalog,
            callback_data={"page": page},
        )

    def _prepare_monitoring_url(self) -> URL:
        """Returns prepared monitoring URL."""
        url = URL(self.monitoring_url)
        path_segments = url.path.split("/")
        if path_segments[-2] == "if":
            broken_param = path_segments[-1].split("=")
            if len(broken_param) == 2:
                return URL(
                    scheme=url.scheme,
                    host=url.host,
                    path="/".join(path_segments[:-2]),
                    params={broken_param[0]: broken_param[1], **url.params},
                )
        return url

    def _build_graphql_payload(self, url: URL, page: int) -> dict[str, Any]:
        """Returns payload for GraphQL request.

        Args:
            url (URL): Monitoring URL.
            page (int): Page number.

        """
        return {
            "operationName": "WEB_CatalogProducts",
            "variables": {
                "catalogSlug": self._get_graphql_catalog_slug(url),
                "pageNum": page,
                "first": 100,
                **self._get_graphql_variables(url),
            },
            "query": "query WEB_CatalogProducts($first: Int!, $pageNum: Int!, $catalogSlug: String, $brands: [Int], $orderBy: String, $sizes: [Int], $conditions: [Int], $colors: [Int], $priceTo: Int, $priceFrom: Int, $priceId: [Int], $ukrainian: Boolean, $searchText: String, $freeShipping: Boolean, $isOnSale: Boolean, $characteristics: [Int!], $cities: [Int!], $lastViewedProductId: Int) {\n  products(\n    first: $first\n    pageNum: $pageNum\n    orderBy: $orderBy\n    sizes: $sizes\n    condition: $conditions\n    colors: $colors\n    priceTo: $priceTo\n    priceFrom: $priceFrom\n    catalogSlug: $catalogSlug\n    brands: $brands\n    priceId: $priceId\n    ukrainian: $ukrainian\n    searchText: $searchText\n    freeShipping: $freeShipping\n    isOnSale: $isOnSale\n    characteristics: $characteristics\n    cities: $cities\n    lastViewedProductId: $lastViewedProductId\n  ) {\n    mostFrequentCatalogSlug\n    topLevelCategories {\n      id\n      name\n      slug\n      countOfProducts\n      __typename\n    }\n    edges {\n      node {\n        id\n        ...productCardFeedData\n        __typename\n      }\n      __typename\n    }\n    pageInfo {\n      endCursor\n      hasNextPage\n      total\n      __typename\n    }\n    __typename\n  }\n}\n\nfragment productCardFeedData on Product {\n  id\n  url\n  thumbnail\n  name\n  price\n  oldPrice\n  statusTitle\n  discountPercent\n  ...productLikes\n  brand {\n    id\n    name\n    __typename\n  }\n  catalogSlug\n  isNew\n  sizes {\n    id\n    name\n    __typename\n  }\n  saleLabel {\n    status\n    date\n    price\n    __typename\n  }\n  freeDeliveryServices\n  isUkrainian\n  ownerHasRecentActivity\n  tags\n  rating\n  ratingAmount\n  seller {\n    id\n    isTopSeller\n    __typename\n  }\n  isViewed\n  createdAt\n  sellingCondition\n  __typename\n}\n\nfragment productLikes on Product {\n  likes\n  isLiked\n  __typename\n}",  # noqa: E501  # pylint: disable=C0301
        }

    def _get_graphql_catalog_slug(self, url: URL) -> str:
        """Returns catalog slug for GraphQL request.

        Args:
            url (URL): Monitoring URL.

        """
        path_segments = url.path.lstrip("/").split("/")
        if path_segments[0] == "uk":
            path_segments.pop(0)
        if len(path_segments) == 1:
            return path_segments[0]
        return "/".join(path_segments[1:])

    def _get_graphql_variables(self, url: URL) -> dict[str, Any]:
        """Returns variables for GraphQL request.

        Args:
            url (URL): Monitoring URL.

        """
        variables: dict[str, Any] = {}

        for name, value in url.params.multi_items():
            variable_name = self._snake_to_camel(name)

            if variable_name == "prices":
                variable_name = "priceId"

            if value == "true":
                variable_value: Any = True
            elif value == "false":
                variable_value = False
            elif value.isdigit():
                variable_value = int(value)
            else:
                variable_value = value

            if variable_name in variables:
                if not isinstance(variables[variable_name], list):
                    variables[variable_name] = [variables[variable_name]]
                variables[variable_name].append(variable_value)
            else:
                variables[variable_name] = variable_value

        return variables

    def _snake_to_camel(self, snake_str: str) -> str:
        """Returns camel case string from snake case string.

        Args:
            snake_str (str): Snake case string.

        """
        segments = snake_str.split("_")
        return segments[0] + "".join(word.capitalize() for word in segments[1:])

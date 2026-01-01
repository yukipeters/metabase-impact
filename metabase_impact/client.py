"""Metabase API client."""

from dataclasses import dataclass
import requests


class MetabaseAPIError(Exception):
    """Raised when a Metabase API request fails."""


@dataclass
class Card:
    """A Metabase card (question)."""

    id: int
    name: str
    query: str


class MetabaseClient:
    """Client for interacting with the Metabase API."""

    def __init__(self, base_url: str, api_key: str) -> None:
        """
        Initialize the client.

        Args:
            base_url: Metabase instance URL (e.g., http://localhost:3000)
            api_key: Metabase API key
        """
        self.base_url = base_url.rstrip("/")
        self.session = requests.Session()
        self.session.headers.update({"X-API-Key": api_key})

    def _request(self, endpoint: str) -> dict | list:
        """Make a GET request to the Metabase API."""
        url = f"{self.base_url}{endpoint}"
        try:
            response = self.session.get(url)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.ConnectionError:
            raise MetabaseAPIError(f"Could not connect to {self.base_url}")
        except requests.exceptions.HTTPError as e:
            if e.response.status_code in (401, 403):
                raise MetabaseAPIError("Authentication failed. Check your API key.")
            raise MetabaseAPIError(f"API error: {e.response.status_code}")

    def get_cards(self) -> list[Card]:
        """Fetch all native SQL cards from Metabase.

        Metabase has two formats for native SQL queries:

        New format (MBQL 5):
            "dataset_query": {
                "lib/type": "mbql/query",
                "database": 1,
                "stages": [
                    {
                        "lib/type": "mbql.stage/native",
                        "native": "SELECT ..."
                    }
                ]
            }

        Legacy format (MBQL 4):
            "dataset_query": {
                "database": 1,
                "type": "native",
                "native": {
                    "query": "SELECT ..."
                }
            }
        """
        cards = []
        for item in self._request("/api/card"):
            dataset_query = item.get("dataset_query", {})
            query = None

            # New format (MBQL 5): stages[0].native is a string
            stages = dataset_query.get("stages", [])
            if stages:
                query = stages[0].get("native")

            # Legacy format (MBQL 4): native.query is nested
            if not query and dataset_query.get("type") == "native":
                query = dataset_query.get("native", {}).get("query")

            if query:
                cards.append(Card(
                    id=item["id"],
                    name=item.get("name", f"Card {item['id']}"),
                    query=query,
                ))
        return cards

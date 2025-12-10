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
        """Fetch all native SQL cards from Metabase."""
        cards = []
        for item in self._request("/api/card"):
            dataset_query = item.get("dataset_query", {})
            stages = dataset_query.get("stages", [])
            query = stages[0].get("native") if stages else None
            if query:
                cards.append(Card(
                    id=item["id"],
                    name=item.get("name", f"Card {item['id']}"),
                    query=query,
                ))
        return cards

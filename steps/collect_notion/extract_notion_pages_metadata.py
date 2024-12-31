import json
from typing import Any

import requests
from loguru import logger
from typing_extensions import Annotated
from zenml import step

from second_brain import settings


@step
def extract_notion_pages_metadata(
    database_id: str,
) -> Annotated[list[str], "notion_pages_metadata"]:
    notion_datapage_results = _query_notion_database(database_id)

    ids = [page["id"] for page in notion_datapage_results]

    return ids


def _query_notion_database(
    database_id: str, query_json: str | None = None
) -> list[dict[str, Any]] | str:
    url = f"https://api.notion.com/v1/databases/{database_id}/query"
    headers = {
        "Authorization": f"Bearer {settings.NOTION_SECRET_KEY}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28",
    }

    query_payload = {}
    if query_json and query_json.strip():
        try:
            query_payload = json.loads(query_json)
        except json.JSONDecodeError as e:
            return f"Invalid JSON format for query: {e}"

    try:
        response = requests.post(url, headers=headers, json=query_payload, timeout=10)
        response.raise_for_status()
        results = response.json()
        return results["results"]
    except requests.exceptions.RequestException as e:
        return f"Error querying Notion database: {e}"
    except KeyError:
        return "Unexpected response format from Notion API"
    except Exception as e:  # noqa: BLE001
        logger.opt(exception=True).debug("Error querying Notion database")
        return f"An unexpected error occurred: {e}"

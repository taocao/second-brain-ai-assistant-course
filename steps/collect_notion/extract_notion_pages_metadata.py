import json
from typing import Any

import requests
from loguru import logger
from typing_extensions import Annotated
from zenml import step

from second_brain import settings
from second_brain.entities import PageMetadata


@step
def extract_notion_pages_metadata(
    database_id: str,
) -> Annotated[list[PageMetadata], "notion_pages_metadata"]:
    notion_datapage_results = _query_notion_database(database_id)

    pages_metadata = [_build_page_metadata(page) for page in notion_datapage_results]

    return pages_metadata


def _query_notion_database(
    database_id: str, query_json: str | None = None
) -> list[dict[str, Any]]:
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
        except json.JSONDecodeError:
            logger.opt(exception=True).debug("Invalid JSON format for query")
            return []

    try:
        response = requests.post(url, headers=headers, json=query_payload, timeout=10)
        response.raise_for_status()
        results = response.json()
        return results["results"]
    except requests.exceptions.RequestException:
        logger.opt(exception=True).debug("Error querying Notion database")
        return []
    except KeyError:
        logger.opt(exception=True).debug("Unexpected response format from Notion API")
        return []
    except Exception:  # noqa: BLE001
        logger.opt(exception=True).debug("Error querying Notion database")
        return []


def _build_page_metadata(page: dict[str, Any]) -> PageMetadata:
    properties = _flatten_properties(page.get("properties", {}))
    title = properties.pop("Name")

    return PageMetadata(
        id=page["id"], url=page["url"], title=title, properties=properties
    )


def _flatten_properties(properties: dict) -> dict:
    """Flatten Notion properties dictionary into a simpler key-value format.

    Example:
        Input: {
            'Type': {'type': 'select', 'select': {'name': 'Leaf'}},
            'Name': {'type': 'title', 'title': [{'plain_text': 'Merging'}]}
        }
        Output: {
            'Type': 'Leaf',
            'Name': 'Merging'
        }
    """

    flattened = {}

    for key, value in properties.items():
        prop_type = value.get("type")

        if prop_type == "select":
            flattened[key] = value.get("select", {}).get("name")
        elif prop_type == "multi_select":
            flattened[key] = [
                item.get("name") for item in value.get("multi_select", [])
            ]
        elif prop_type == "title":
            # Join all plain_text values from the title array
            flattened[key] = "\n".join(
                item.get("plain_text", "") for item in value.get("title", [])
            )
        elif prop_type == "rich_text":
            # Join all plain_text values from the rich_text array
            flattened[key] = " ".join(
                item.get("plain_text", "") for item in value.get("rich_text", [])
            )
        elif prop_type == "number":
            flattened[key] = value.get("number")
        elif prop_type == "checkbox":
            flattened[key] = value.get("checkbox")
        elif prop_type == "date":
            date_value = value.get("date", {})
            if date_value:
                flattened[key] = {
                    "start": date_value.get("start"),
                    "end": date_value.get("end"),
                }
        else:
            # For any unhandled property types, store as is
            flattened[key] = value

    return flattened

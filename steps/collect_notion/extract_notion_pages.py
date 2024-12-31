import requests
from loguru import logger
from typing_extensions import Annotated
from zenml import step

from second_brain import settings


@step
def extract_notion_pages(
    page_ids: list[str],
) -> Annotated[dict[str, str], "pages"]:
    page_contents = {}
    for page_id in page_ids:
        page_content = _retrieve_page_content(page_id)
        page_contents[page_id] = page_content

    return page_contents


def _retrieve_page_content(page_id: str, depth: int = 0) -> str:
    blocks_url = f"https://api.notion.com/v1/blocks/{page_id}/children?page_size=100"
    headers = {
        "Authorization": f"Bearer {settings.NOTION_SECRET_KEY}",
        "Notion-Version": "2022-06-28",
    }
    try:
        blocks_response = requests.get(blocks_url, headers=headers, timeout=10)
        blocks_response.raise_for_status()
        blocks_data = blocks_response.json()
        return parse_blocks(blocks_data.get("results", []), depth)
    except requests.exceptions.RequestException as e:
        error_message = f"Error: Failed to retrieve Notion page content. {e}"
        if hasattr(e, "response") and e.response is not None:
            error_message += (
                f" Status code: {e.response.status_code}, Response: {e.response.text}"
            )
        return error_message
    except Exception as e:  # noqa: BLE001
        logger.opt(exception=True).debug("Error retrieving Notion page content")
        return f"Error: An unexpected error occurred while retrieving Notion page content. {e}"


def parse_blocks(blocks: list, depth: int = 0) -> str:
    content = ""
    for block in blocks:
        block_type = block.get("type")
        block_id = block.get("id")

        if block_type == "toggle":
            toggle_text = parse_rich_text(block["toggle"].get("rich_text", []))
            content += f"▼ {toggle_text}\n\n"

            if "has_children" in block and block["has_children"]:
                children_blocks = _fetch_block_children(block_id)
                children_content = parse_blocks(children_blocks, depth + 1)
                content += (
                    "\n".join("    " + line for line in children_content.split("\n"))
                    + "\n\n"
                )
        elif block_type in {
            "paragraph",
            "heading_1",
            "heading_2",
            "heading_3",
            "quote",
        }:
            text_content = parse_rich_text(block[block_type].get("rich_text", []))
            content += text_content + "\n\n"
            urls = extract_urls(block[block_type].get("rich_text", []))

            if urls:
                content += "\n".join(f"- {url}" for url in urls) + "\n\n"
        elif block_type in {"bulleted_list_item", "numbered_list_item"}:
            content += parse_rich_text(block[block_type].get("rich_text", [])) + "\n"
        elif block_type == "to_do":
            content += parse_rich_text(block["to_do"].get("rich_text", [])) + "\n"
        elif block_type == "code":
            content += parse_rich_text(block["code"].get("rich_text", [])) + "\n\n"
        elif block_type == "image":
            content += f"[Image: {block['image'].get('external', {}).get('url', 'No URL')}]\n\n"
        elif block_type == "divider":
            content += "---\n\n"
        elif block_type == "child_page" and depth < 3:  # Limit recursion depth
            child_id = block.get("id")
            child_title = block.get("child_page", {}).get("title", "Untitled")
            content += f"\n### {child_title}\n\n"
            child_content = _retrieve_page_content(child_id, depth + 1)
            content += child_content + "\n\n"

        elif block_type == "child_database":
            db_id = block.get("id")
            db_title = block.get("child_database", {}).get("title", "Untitled Database")
            content += f"\n### Database: {db_title}\n\n"

    return content.strip()


def parse_rich_text(rich_text: list) -> str:
    return "".join(segment.get("plain_text", "") for segment in rich_text)


def extract_urls(rich_text: list) -> list:
    """Extract URLs from rich text blocks."""
    urls = []
    for text in rich_text:
        if text.get("href"):
            urls.append(text["href"])
        if "url" in text.get("annotations", {}):
            urls.append(text["annotations"]["url"])
    return urls


def _fetch_block_children(block_id: str) -> list:
    """Fetch children blocks for a given block ID."""
    children_url = f"https://api.notion.com/v1/blocks/{block_id}/children?page_size=100"
    headers = {
        "Authorization": f"Bearer {settings.NOTION_SECRET_KEY}",
        "Notion-Version": "2022-06-28",
    }
    try:
        children_response = requests.get(children_url, headers=headers, timeout=10)
        children_response.raise_for_status()
        children_data = children_response.json()
        return children_data.get("results", [])
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to fetch block children: {e}")
        return []

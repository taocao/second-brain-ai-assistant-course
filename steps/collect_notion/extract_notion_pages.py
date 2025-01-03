import requests
from loguru import logger
from typing_extensions import Annotated
from zenml import step

from second_brain import settings, utils
from second_brain.entities import Page


@step
def extract_notion_pages(
    page_ids: list[str],
) -> Annotated[dict[str, Page], "pages"]:
    page_contents = {}
    for page_id in page_ids:
        blocks = _retrieve_child_blocks(page_id)
        content, metadata = _parse_blocks(blocks)
        page_contents[page_id] = Page(content=content, metadata=metadata)

    return page_contents


def _retrieve_child_blocks(block_id: str, page_size: int = 100) -> list[dict]:
    blocks_url = (
        f"https://api.notion.com/v1/blocks/{block_id}/children?page_size={page_size}"
    )
    headers = {
        "Authorization": f"Bearer {settings.NOTION_SECRET_KEY}",
        "Notion-Version": "2022-06-28",
    }
    try:
        blocks_response = requests.get(blocks_url, headers=headers, timeout=10)
        blocks_response.raise_for_status()
        blocks_data = blocks_response.json()

        return blocks_data.get("results", [])
    except requests.exceptions.RequestException as e:
        error_message = f"Error: Failed to retrieve Notion page content. {e}"
        if hasattr(e, "response") and e.response is not None:
            error_message += (
                f" Status code: {e.response.status_code}, Response: {e.response.text}"
            )
        logger.exception(error_message)

        return []
    except Exception:
        error_message = "Error retrieving Notion page content"
        logger.exception(error_message)

        return []


def _parse_blocks(blocks: list, depth: int = 0) -> tuple[str, dict]:
    content = ""
    metadata = {
        "urls": [],
    }
    for block in blocks:
        block_type = block.get("type")
        block_id = block.get("id")

        if block_type in {
            "paragraph",
            "heading_1",
            "heading_2",
            "heading_3",
            "quote",
        }:
            text_content = _parse_rich_text(block[block_type].get("rich_text", []))
            content += text_content + "\n\n"
            urls = _extract_urls(block[block_type].get("rich_text", []))
            if urls:
                metadata["urls"].extend(urls)

            if "has_children" in block and block["has_children"]:
                child_blocks = _retrieve_child_blocks(block_id)
                child_content, child_metadata = _parse_blocks(child_blocks, depth + 1)
                content += (
                    "\n".join("    " + line for line in child_content.split("\n"))
                    + "\n\n"
                )
                metadata = utils.merge_dicts(metadata, child_metadata)

        elif block_type in {"bulleted_list_item", "numbered_list_item"}:
            content += _parse_rich_text(block[block_type].get("rich_text", [])) + "\n"
        elif block_type == "to_do":
            content += _parse_rich_text(block["to_do"].get("rich_text", [])) + "\n"
        elif block_type == "code":
            content += _parse_rich_text(block["code"].get("rich_text", [])) + "\n\n"
        elif block_type == "image":
            content += f"[Image: {block['image'].get('external', {}).get('url', 'No URL')}]\n\n"
        elif block_type == "divider":
            content += "---\n\n"
        elif block_type == "child_page" and depth < 3:
            child_id = block.get("id")
            child_title = block.get("child_page", {}).get("title", "Untitled")
            content += f"\n### {child_title}\n\n"

            child_blocks = _retrieve_child_blocks(child_id)
            child_content, child_metadata = _parse_blocks(child_blocks, depth + 1)
            content += child_content + "\n\n"
            metadata = utils.merge_dicts(metadata, child_metadata)

        elif block_type == "link_preview":
            url = block.get("link_preview", {}).get("url", "")
            content += f"[Link Preview: {url}]\n\n"

            metadata["urls"].append(url)
        else:
            logger.warning(f"Unknown block type: {block_type}")

    return content.strip("\n "), metadata


def _parse_rich_text(rich_text: list) -> str:
    return "".join(segment.get("plain_text", "") for segment in rich_text)


def _extract_urls(rich_text: list) -> list:
    """Extract URLs from rich text blocks."""
    urls = []
    for text in rich_text:
        if text.get("href"):
            urls.append(text["href"])
        if "url" in text.get("annotations", {}):
            urls.append(text["annotations"]["url"])
    return urls

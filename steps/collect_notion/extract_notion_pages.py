import requests
from loguru import logger
from typing_extensions import Annotated
from zenml import step

from second_brain import settings
from second_brain.entities import Page, PageMetadata


@step
def extract_notion_pages(
    pages_metadata: list[PageMetadata],
) -> Annotated[dict[str, Page], "pages"]:
    pages = {}
    for page_metadata in pages_metadata:
        blocks = _retrieve_child_blocks(page_metadata.id)
        content, urls = _parse_blocks(blocks)
        pages[page_metadata.id] = Page(
            page_metadata=page_metadata, content=content, urls=urls
        )

    return pages


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


def _parse_blocks(blocks: list, depth: int = 0) -> tuple[str, list[str]]:
    content = ""
    urls = []
    for block in blocks:
        block_type = block.get("type")
        block_id = block.get("id")

        if block_type in {
            "heading_1",
            "heading_2",
            "heading_3",
        }:
            content += (
                f"# {_parse_rich_text(block[block_type].get('rich_text', []))}\n\n"
            )
            urls.extend(_extract_urls(block[block_type].get("rich_text", [])))
        elif block_type in {
            "paragraph",
            "quote",
        }:
            content += f"{_parse_rich_text(block[block_type].get('rich_text', []))}\n"
            urls.extend(_extract_urls(block[block_type].get("rich_text", [])))
        elif block_type in {"bulleted_list_item", "numbered_list_item"}:
            content += f"- {_parse_rich_text(block[block_type].get('rich_text', []))}\n"
            urls.extend(_extract_urls(block[block_type].get("rich_text", [])))
        elif block_type == "to_do":
            content += f"[] {_parse_rich_text(block['to_do'].get('rich_text', []))}\n"
            urls.extend(_extract_urls(block[block_type].get("rich_text", [])))
        elif block_type == "code":
            content += (
                f"```\n{_parse_rich_text(block['code'].get('rich_text', []))}\n````\n"
            )
            urls.extend(_extract_urls(block[block_type].get("rich_text", [])))
        elif block_type == "image":
            content += (
                f"[Image]({block['image'].get('external', {}).get('url', 'No URL')})\n"
            )
        elif block_type == "divider":
            content += "---\n\n"
        elif block_type == "child_page" and depth < 3:
            child_id = block.get("id")
            child_title = block.get("child_page", {}).get("title", "Untitled")
            content += f"\n\n<child_page>\n# {child_title}\n\n"

            child_blocks = _retrieve_child_blocks(child_id)
            child_content, child_urls = _parse_blocks(child_blocks, depth + 1)
            content += child_content + "\n</child_page>\n\n"
            urls += child_urls

        elif block_type == "link_preview":
            url = block.get("link_preview", {}).get("url", "")
            content += f"[Link Preview]({url})\n"

            urls.append(_normalize_url(url))
        else:
            logger.warning(f"Unknown block type: {block_type}")

        # Parse child pages that are bullet points, toggles or similar structures.
        # Subpages (child_page) are parsed individually as a block.
        if (
            block_type != "child_page"
            and "has_children" in block
            and block["has_children"]
        ):
            child_blocks = _retrieve_child_blocks(block_id)
            child_content, child_urls = _parse_blocks(child_blocks, depth + 1)
            content += (
                "\n".join("\t" + line for line in child_content.split("\n")) + "\n\n"
            )
            urls += child_urls

    urls = list(set(urls))

    return content.strip("\n "), urls


def _parse_rich_text(rich_text: list) -> str:
    text = ""
    for segment in rich_text:
        if segment.get("href"):
            text += f"[{segment.get('plain_text', '')}]({segment.get('href', '')})"
        else:
            text += segment.get("plain_text", "")
    return text


def _extract_urls(rich_text: list) -> list:
    """Extract URLs from rich text blocks."""
    urls = []
    for text in rich_text:
        url = None
        if text.get("href"):
            url = text["href"]
        elif "url" in text.get("annotations", {}):
            url = text["annotations"]["url"]

        if url:
            urls.append(_normalize_url(url))

    return urls


def _normalize_url(url: str) -> str:
    if not url.endswith("/"):
        url += "/"
    return url

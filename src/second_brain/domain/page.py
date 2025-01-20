import json
import random
import string
from pathlib import Path

from pydantic import BaseModel


class PageMetadata(BaseModel):
    id: str
    url: str
    title: str
    properties: dict

    def __eq__(self, other: object) -> bool:
        """Compare two PageMetadata objects for equality.

        Args:
            other: Another object to compare with this PageMetadata.

        Returns:
            bool: True if the other object is a PageMetadata with the same ID.
        """
        if not isinstance(other, PageMetadata):
            return False
        return self.id == other.id

    def __hash__(self) -> int:
        """Generate a hash value for the PageMetadata.

        Returns:
            int: Hash value based on the page's ID.
        """
        return hash(self.id)


class Page(BaseModel):
    metadata: PageMetadata
    parent_metadata: PageMetadata | None = None
    content: str
    child_urls: list[str]

    @classmethod
    def from_file(cls, file_path: Path) -> "Page":
        """Read a Page object from a JSON file.

        Args:
            file_path: Path to the JSON file containing page data.

        Returns:
            Page: A new Page instance constructed from the file data.

        Raises:
            FileNotFoundError: If the specified file doesn't exist.
            ValidationError: If the JSON data doesn't match the expected model structure.
        """

        json_data = file_path.read_text(encoding="utf-8")

        return cls.model_validate_json(json_data)

    def write(
        self, file_path: Path, obfuscate: bool = False, also_save_as_txt: bool = False
    ) -> None:
        """Write page data to file, optionally obfuscating sensitive information."""

        json_page = self.model_dump()

        if obfuscate:
            json_page = self._obfuscate_data(json_page)

        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(
                json_page,
                f,
                indent=4,
                ensure_ascii=False,
            )

        if also_save_as_txt:
            txt_path = file_path.with_suffix(".txt")
            with open(txt_path, "w", encoding="utf-8") as f:
                f.write(self.content)

    def _obfuscate_data(self, data: dict) -> dict:
        """Obfuscate sensitive IDs in the page data."""

        original_id = data["metadata"]["id"]
        fake_id = self._generate_random_hex(32)

        obfuscated_data = data.copy()

        # Obfuscate the page ID (32-char hex)
        obfuscated_data["metadata"]["id"] = fake_id

        # Obfuscate UUID in URL if present
        url = data["metadata"]["url"]
        flattened_original_id = original_id.replace("-", "")
        obfuscated_data["metadata"]["url"] = url.replace(flattened_original_id, fake_id)

        return obfuscated_data

    def _generate_random_hex(self, length: int) -> str:
        """Generate a random hex string of specified length."""

        hex_chars = string.hexdigits.lower()
        return "".join(random.choice(hex_chars) for _ in range(length))

    def __eq__(self, other: object) -> bool:
        """Compare two Page objects for equality.

        Args:
            other: Another object to compare with this Page.

        Returns:
            bool: True if the other object is a Page with the same metadata.
        """
        if not isinstance(other, Page):
            return False
        return self.metadata == other.metadata

    def __hash__(self) -> int:
        """Generate a hash value for the Page.

        Returns:
            int: Hash value based on the page's metadata.
        """
        return hash(self.metadata)

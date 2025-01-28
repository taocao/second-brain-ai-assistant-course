import json
from pathlib import Path

from pydantic import BaseModel, Field

from second_brain_offline import utils


class DocumentMetadata(BaseModel):
    id: str
    url: str
    title: str
    properties: dict

    def obfuscate(self) -> "DocumentMetadata":
        """Create an obfuscated version of this metadata by modifying in place.

        Returns:
            DocumentMetadata: Self, with ID and URL obfuscated.
        """

        original_id = self.id.replace("-", "")
        fake_id = utils.generate_random_hex(len(original_id))

        self.id = fake_id
        self.url = self.url.replace(original_id, fake_id)

        return self


class Document(BaseModel):
    id: str = Field(default_factory=lambda: utils.generate_random_hex(length=32))
    metadata: DocumentMetadata
    parent_metadata: DocumentMetadata | None = None
    content: str
    content_quality_score: float | None = None
    summary: str | None = None
    child_urls: list[str] = Field(default_factory=list)

    @classmethod
    def from_file(cls, file_path: Path) -> "Document":
        """Read a Document object from a JSON file.

        Args:
            file_path: Path to the JSON file containing document data.

        Returns:
            Document: A new Document instance constructed from the file data.

        Raises:
            FileNotFoundError: If the specified file doesn't exist.
            ValidationError: If the JSON data doesn't match the expected model structure.
        """

        json_data = file_path.read_text(encoding="utf-8")

        return cls.model_validate_json(json_data)

    def add_summary(self, summary: str) -> "Document":
        self.summary = summary

        return self

    def add_quality_score(self, score: float) -> "Document":
        self.content_quality_score = score

        return self

    def write(
        self, output_dir: Path, obfuscate: bool = False, also_save_as_txt: bool = False
    ) -> None:
        """Write document data to file, optionally obfuscating sensitive information.

        Args:
            output_dir: Directory path where the files should be written.
            obfuscate: If True, sensitive information will be obfuscated.
            also_save_as_txt: If True, content will also be saved as a text file.
        """

        output_dir.mkdir(parents=True, exist_ok=True)

        if obfuscate:
            self.obfuscate()

        json_page = self.model_dump()

        output_file = output_dir / f"{self.id}.json"
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(
                json_page,
                f,
                indent=4,
                ensure_ascii=False,
            )

        if also_save_as_txt:
            txt_path = output_file.with_suffix(".txt")
            with open(txt_path, "w", encoding="utf-8") as f:
                f.write(self.content)

    def obfuscate(self) -> "Document":
        """Create an obfuscated version of this document by modifying in place.

        Returns:
            Document: Self, with obfuscated metadata and parent_metadata.
        """

        self.metadata = self.metadata.obfuscate()
        self.parent_metadata = (
            self.parent_metadata.obfuscate() if self.parent_metadata else None
        )
        self.id = self.metadata.id

        return self

    def __eq__(self, other: object) -> bool:
        """Compare two Document objects for equality.

        Args:
            other: Another object to compare with this Document.

        Returns:
            bool: True if the other object is a Document with the same ID.
        """
        if not isinstance(other, Document):
            return False
        return self.id == other.id

    def __hash__(self) -> int:
        """Generate a hash value for the Document.

        Returns:
            int: Hash value based on the document's ID.
        """
        return hash(self.id)

import json
from pathlib import Path

from pydantic import BaseModel


class Page(BaseModel):
    content: str
    metadata: dict

    def write(self, file_path: Path) -> None:
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(
                {"content": self.content, "metadata": self.metadata},
                f,
                indent=4,
                ensure_ascii=False,
            )

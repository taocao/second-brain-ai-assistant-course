import json
from pathlib import Path

import pytest


@pytest.mark.integration
class TestDownloadNotionDataset:
    """Tests to verify Notion dataset download structure and content."""

    @pytest.fixture
    def notion_dir(self) -> Path:
        """
        Fixture that provides the path to the Notion data directory.

        Returns:
            Path: Path object pointing to the Notion data directory
        """
        return Path("data/notion")

    def test_notion_data_directory_exists(self, notion_dir: Path) -> None:
        """
        Test that the Notion data directory exists.

        Returns:
            None
        """
        assert notion_dir.exists(), "Notion data directory does not exist"
        assert notion_dir.is_dir(), "Notion data path is not a directory"

    def test_database_directories_exist(self, notion_dir: Path) -> None:
        """
        Test that database subdirectories exist and follow the expected naming pattern.

        Returns:
            None
        """
        database_dirs = [d for d in notion_dir.iterdir() if d.is_dir()]

        assert len(database_dirs) > 0, "No database directories found"

        # Check directory naming pattern
        for dir_path in database_dirs:
            assert dir_path.name.startswith("database_"), (
                f"Invalid directory name format: {dir_path.name}"
            )

    def test_json_files_in_databases(self, notion_dir: Path) -> None:
        """
        Test that each database directory contains at least one non-empty JSON file.

        Returns:
            None
        """
        database_dirs = [d for d in notion_dir.iterdir() if d.is_dir()]

        for database_dir in database_dirs:
            non_empty_json_files = []
            json_files = list(database_dir.glob("*.json"))

            for json_file in json_files:
                if json_file.stat().st_size > 0:
                    # Verify JSON is valid
                    try:
                        with open(json_file, "r") as f:
                            json.load(f)
                            non_empty_json_files.append(json_file)
                    except json.JSONDecodeError:
                        pytest.fail(f"Invalid JSON file: {json_file}")

            assert len(non_empty_json_files) > 0, (
                f"No non-empty JSON files found in {database_dir}"
            )

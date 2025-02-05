import json
from pathlib import Path

import pytest


@pytest.mark.integration
class TestDownloadCrawledDataset:
    """Tests to verify Crawled dataset download structure and content."""

    @pytest.fixture
    def crawled_dir(self) -> Path:
        """
        Fixture that provides the path to the crawled data directory.

        Returns:
            Path: Path object pointing to the crawled data directory
        """
        return Path("data/crawled")

    def test_crawled_data_directory_exists(self, crawled_dir: Path) -> None:
        """
        Test that the crawled data directory exists.

        Args:
            crawled_dir: Path to the crawled data directory

        Returns:
            None
        """
        assert crawled_dir.exists(), "Crawled data directory does not exist"
        assert crawled_dir.is_dir(), "Crawled data path is not a directory"

    def test_json_files_in_crawled_dir(self, crawled_dir: Path) -> None:
        """
        Test that the crawled directory contains at least one non-empty JSON file.
        Each JSON file should:
        - Be non-empty
        - Contain valid JSON

        Args:
            crawled_dir: Path to the crawled data directory

        Returns:
            None
        """
        json_files = list(crawled_dir.glob("*.json"))
        non_empty_json_files = [f for f in json_files if f.stat().st_size > 0]

        assert len(non_empty_json_files) > 0, (
            "No non-empty JSON files found in crawled directory"
        )

        for json_file in json_files:
            # Verify JSON is valid
            try:
                with open(json_file, "r") as f:
                    json.load(f)
            except json.JSONDecodeError:
                pytest.fail(f"Invalid JSON file: {json_file}")

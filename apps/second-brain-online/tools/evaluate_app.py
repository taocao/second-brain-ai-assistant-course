from pathlib import Path
from typing import List

import click

from second_brain_online.application import evaluate

DEFAULT_PROMPTS: List[str] = [
    """
Write me a paragraph on the feature/training/inference (FTI) pipelines architecture following the next structure:

- introduction
- what are its main components
- why it's powerful

Retrieve the sources when compiling the answer. Also, return the sources you used as context.
""",
    "What is the feature/training/inference (FTI) pipelines architecture?",
    "What is the Tensorflow Recommenders Python package?",
    "Summarize 3 LLM frameworks",
    "List 5 ways or tools to process PDFs for LLMs and RAG",
    """How can I optimize my LLMs during inference?

Provide a list of top 3 best practices, while providing a short explanation for each, which contains why it's important.
""",
]


@click.command()
@click.option(
    "--retriever-config-path",
    type=click.Path(exists=True, path_type=Path),
    required=True,
    help="Path to the retriever configuration file",
)
def main(retriever_config_path: Path) -> None:
    """Evaluate agent with custom retriever configuration."""
    evaluate.evaluate_agent(
        DEFAULT_PROMPTS, retriever_config_path=retriever_config_path
    )


if __name__ == "__main__":
    main()

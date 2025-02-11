from pathlib import Path

import click
from smolagents import GradioUI

from second_brain_online.application.agents import get_agent


@click.command()
@click.option(
    "--retriever-config-path",
    type=click.Path(exists=True),
    required=True,
    help="Path to the retriever config file",
)
@click.option(
    "--ui",
    is_flag=True,
    default=False,
    help="Launch with Gradio UI instead of CLI mode",
)
@click.option(
    "--query",
    "-q",
    type=str,
    default="What is the feature/training/inference (FTI) pipelines architecture?",
    help="Query to run in CLI mode",
)
def main(retriever_config_path: Path, ui: bool, query: str) -> None:
    """Run the agent either in Gradio UI or CLI mode.

    Args:
        ui: If True, launches Gradio UI. If False, runs in CLI mode
        query: Query string to run in CLI mode
    """
    agent = get_agent(retriever_config_path=Path(retriever_config_path))
    if ui:
        GradioUI(agent).launch()
    else:
        assert query, "Query is required in CLI mode"

        result = agent.run(query)

        print(result)


if __name__ == "__main__":
    main()

import click
from smolagents import GradioUI

from second_brain_online.application.agents import get_agent


@click.command()
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
def main(ui: bool, query: str) -> None:
    """Run the agent either in Gradio UI or CLI mode.

    Args:
        ui: If True, launches Gradio UI. If False, runs in CLI mode
        query: Query string to run in CLI mode
    """
    agent = get_agent()
    if ui:
        GradioUI(agent).launch()
    else:
        assert query, "Query is required in CLI mode"

        result = agent.run(query)

        print(result)


if __name__ == "__main__":
    main()

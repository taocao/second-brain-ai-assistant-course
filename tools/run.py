from datetime import datetime as dt
from pathlib import Path
from typing import Any

import click

from pipelines import (
    collect_notion_data,
    etl
)


@click.command(
    help="""
Second Brain CLI v0.0.1. 

Main entry point for the pipeline execution. 
This entrypoint is where everything comes together.

Run the ZenML Second Brain project pipelines with various options.

Run a pipeline with the required parameters. This executes
all steps in the pipeline in the correct order using the orchestrator
stack component that is configured in your active ZenML stack.

Examples:

  \b
  # Run the pipeline with default options
  python run.py
               
  \b
  # Run the pipeline without cache
  python run.py --no-cache
  
  \b
  # Run only the Notion data collection pipeline
  python run.py --run-collect-notion-data

"""
)
@click.option(
    "--no-cache",
    is_flag=True,
    default=False,
    help="Disable caching for the pipeline run.",
)
@click.option(
    "--run-collect-notion-data",
    is_flag=True,
    default=False,
    help="Whether to run the collection data from Notion pipeline.",
)
@click.option(
    "--run-etl",
    is_flag=True,
    default=False,
    help="Whether to run the ETL pipeline.",
)
def main(
    no_cache: bool = False,
    run_collect_notion_data: bool = False,
    run_etl: bool = False,
) -> None:
    assert run_collect_notion_data or run_etl, "Please specify an action to run."

    pipeline_args: dict[str, Any] = {
        "enable_cache": not no_cache,
    }
    root_dir = Path(__file__).resolve().parent.parent

    if run_collect_notion_data:
        run_args = {}
        pipeline_args["config_path"] = root_dir / "configs" / "collect_notion_data.yaml"
        assert pipeline_args[
            "config_path"
        ].exists(), f"Config file not found: {pipeline_args['config_path']}"
        pipeline_args["run_name"] = (
            f"collect_notion_data_run_{dt.now().strftime('%Y_%m_%d_%H_%M_%S')}"
        )
        collect_notion_data.with_options(**pipeline_args)(**run_args)

    if run_etl:
        run_args = {}
        pipeline_args["config_path"] = root_dir / "configs" / "etl.yaml"
        assert pipeline_args[
            "config_path"
        ].exists(), f"Config file not found: {pipeline_args['config_path']}"
        pipeline_args["run_name"] = (
            f"etl_run_{dt.now().strftime('%Y_%m_%d_%H_%M_%S')}"
        )
        etl.with_options(**pipeline_args)(**run_args)

if __name__ == "__main__":
    main()

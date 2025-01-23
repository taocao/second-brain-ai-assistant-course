from loguru import logger
from opik.evaluation import evaluate
from opik.evaluation.metrics import AnswerRelevance, Hallucination, Moderation

from second_brain_online import opik_utils
from second_brain_online.application.agents import agents, extract_tool_responses
from second_brain_online.config import settings

opik_utils.configure()


def evaluate_agent(prompts: list[str]) -> None:
    assert settings.COMET_API_KEY, (
        "COMET_API_KEY is not set. We need it to track the experiment with Opik."
    )

    def evaluation_task(x: dict) -> dict:
        """Call agentic app logic to evaluate."""

        agent = agents.get_agent()
        response = agent.run(x["input"])
        context = extract_tool_responses(agent)

        return {
            "input": x["input"],
            "context": context,
            "output": response,
        }

    # Get or create dataset
    dataset_name = "app_eval_dataset"
    dataset = opik_utils.get_or_create_dataset(name=dataset_name, prompts=prompts)

    # Evaluate
    experiment_config = {
        "model_id": settings.OPENAI_MODEL_ID,
        "embedding_model": settings.TEXT_EMBEDDING_MODEL_ID,
        "agent_config": {"max_steps": 3},
    }
    # TODO: We could also write a custom metric that checks for references to the context.
    scoring_metrics = [Hallucination(), AnswerRelevance(), Moderation()]

    if dataset:
        logger.info("Evaluation details:")
        logger.info(f"Dataset: {dataset_name}")
        logger.info(f"Metrics: {[m.__class__.__name__ for m in scoring_metrics]}")

        evaluate(
            dataset=dataset,
            task=evaluation_task,
            scoring_metrics=scoring_metrics,
            experiment_config=experiment_config,
        )
    else:
        logger.error("Can't run the evaluation as the dataset items are empty.")

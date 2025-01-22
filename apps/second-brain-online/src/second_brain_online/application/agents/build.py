from smolagents import LiteLLMModel, MultiStepAgent, ToolCallingAgent

from second_brain_online.config import settings

from .tools import MongoDBRetrieverTool, SummarizerTool, what_can_i_do


def get_agent() -> MultiStepAgent:
    retriever_tool = MongoDBRetrieverTool()
    summarizer_tool = SummarizerTool()

    model = LiteLLMModel(
        model_id=settings.OPENAI_MODEL_ID,
        api_base="https://api.openai.com/v1",
        api_key=settings.OPENAI_API_KEY,
    )

    agent = ToolCallingAgent(
        # tools=[retriever_tool, what_can_i_do, summarizer_tool],
        tools=[retriever_tool, what_can_i_do],
        model=model,
        max_steps=3,
        verbosity_level=2,
    )

    return agent

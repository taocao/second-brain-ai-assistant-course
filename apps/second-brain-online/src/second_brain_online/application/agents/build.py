from smolagents import LiteLLMModel, ToolCallingAgent

from second_brain_online.config import settings

from .tools.mongodb_retriever_tool import MongoDBRetrieverTool

retriever_tool = MongoDBRetrieverTool()

# Define the LLM Model
model = LiteLLMModel(
    model_id="gpt-4o-mini",
    api_base="https://api.openai.com/v1",
    api_key=settings.OPENAI_API_KEY,
)

# Create the CodeAgent with tools and model

agent = ToolCallingAgent(
    tools=[retriever_tool], model=model, max_steps=2, verbosity_level=2
)

from smolagents import tool


@tool
def what_can_i_do(question: str) -> str:
    """
    A tool that returns a list of tasks that can be done within the Second Brain agentic system.
    This tool is useful when the user asks what can be done within the application.
    Use this tool only when the user wants to find out more about the application.

    Args:
        question: The question that the user asked.
    """

    return """"
You can ask questions about the content in your Second Brain, such as:
- What is the feature/training/inference (FTI) architecture?
- What are LLMs?
- How do agentic systems work?
- What is the difference between LLMs and other types of models?
"""

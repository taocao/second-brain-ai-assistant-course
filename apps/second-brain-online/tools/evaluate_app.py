from second_brain_online.application import evaluate

prompts = [
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
]

if __name__ == "__main__":
    evaluate.evaluate_agent(prompts)

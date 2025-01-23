from second_brain_online.application import agents, evaluate

prompts = [
    "What is the feature/training/inference (FTI) pipelines architecture?",
    "What is the Tensorflow Recommenders Python package?",
    "Summarize 3 LLM frameworks",
]

if __name__ == "__main__":
    evaluate.evaluate_agent(prompts)

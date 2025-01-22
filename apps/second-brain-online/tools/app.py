### IMPORTS: Core dependencies and type hints


from second_brain_online.application.agents import get_agent

# @track
# def process_query_with_agent(question: str) -> Tuple[str, str]:
#     """
#     Process user query with the SmolAgent framework, dynamically routing to RAG or LLM.

#     Args:
#         question (str): User's input question.

#     Returns:
#         Tuple[str, str]: (retrieved documents, AI-generated response).
#     """
#     try:
#         # Run the agent
#         response = agent.run(f"Answer the query: {question}")

#         # Extract retrieved documents from the response
#         retrieved_docs = retriever_tool.forward(question)

#         # Return both retrieved documents and AI response
#         return retrieved_docs, response
#     except Exception as e:
#         error_msg = f"Error processing query: {str(e)}"
#         logger.error(error_msg)
#         return error_msg, error_msg


# def create_gradio_interface() -> gr.Blocks:
#     """
#     Create and configure the Gradio web interface.

#     Returns:
#         gr.Blocks: Configured Gradio interface
#     """
#     with gr.Blocks(theme=Base(), title="Second Brain QA System") as demo:
#         gr.Markdown(
#             """
#             # Second Brain Question Answering System
#             Leveraging MongoDB, OpenAI, and SmolAgents.
#             """
#         )

#         textbox = gr.Textbox(
#             label="Enter your Question:",
#             placeholder="Ask me anything about the content in your Second Brain...",
#         )

#         with gr.Row():
#             button = gr.Button("Submit", variant="primary")

#         with gr.Column():
#             output1 = gr.Textbox(
#                 lines=10,
#                 max_lines=20,
#                 label="Retrieved Documents:",
#                 show_copy_button=True,
#             )

#             output2 = gr.Textbox(
#                 lines=8, max_lines=15, label="AI Response:", show_copy_button=True
#             )

#         button.click(process_query_with_agent, textbox, outputs=[output1, output2])

#     return demo


if __name__ == "__main__":
    # demo = create_gradio_interface()
    # demo.launch()
    from smolagents import GradioUI

    agent = get_agent()
    GradioUI(agent).launch()

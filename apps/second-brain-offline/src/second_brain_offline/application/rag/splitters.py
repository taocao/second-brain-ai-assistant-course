from langchain_text_splitters import RecursiveCharacterTextSplitter


def get_splitter(chunk_size: int) -> RecursiveCharacterTextSplitter:
    """Returns a token-based text splitter with overlap.

    Args:
        chunk_size: Number of tokens for each text chunk.

    Returns:
        A configured RecursiveCharacterTextSplitter instance.
    """

    return RecursiveCharacterTextSplitter.from_tiktoken_encoder(
        encoding_name="cl100k_base",
        chunk_size=chunk_size,
        chunk_overlap=0.15 * chunk_size,
    )

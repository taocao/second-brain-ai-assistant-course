from typing import Literal, Union

from langchain_huggingface import HuggingFaceEmbeddings
from langchain_openai import OpenAIEmbeddings

EmbeddingModelType = Literal["openai", "huggingface"]
EmbeddingsModel = Union[OpenAIEmbeddings, HuggingFaceEmbeddings]


def get_embedding_model(
    model_id: str,
    model_type: EmbeddingModelType = "huggingface",
    device: str = "cpu",
) -> EmbeddingsModel:
    """Gets an instance of the configured embedding model.

    Args:
        model_id: The ID of the embedding model to use
        model_type: The type of embedding model to use ("openai" or "huggingface")
        device: The device to use for the embedding model. Defaults to "cpu"

    Returns:
        EmbeddingsModel: An embedding model instance based on the configuration settings

    Raises:
        ValueError: If an invalid model_type is provided
    """

    if model_type == "openai":
        return get_openai_embedding_model(model_id)
    elif model_type == "huggingface":
        return get_huggingface_embedding_model(model_id, device)
    else:
        raise ValueError(f"Invalid embedding model type: {model_type}")


def get_openai_embedding_model(model_id: str) -> OpenAIEmbeddings:
    """Gets an OpenAI embedding model instance.

    Args:
        model_id: The ID of the OpenAI embedding model to use

    Returns:
        OpenAIEmbeddings: Configured OpenAI embeddings model instance
    """
    return OpenAIEmbeddings(
        model=model_id,
        allowed_special={"<|endoftext|>"},
    )


def get_huggingface_embedding_model(
    model_id: str, device: str
) -> HuggingFaceEmbeddings:
    """Gets a HuggingFace embedding model instance.

    Args:
        model_id: The ID of the HuggingFace embedding model to use
        device: The device to use for the embedding model

    Returns:
        HuggingFaceEmbeddings: Configured HuggingFace embeddings model instance
    """
    return HuggingFaceEmbeddings(
        model_name=model_id,
        model_kwargs={"device": device, "trust_remote_code": True},
        encode_kwargs={"normalize_embeddings": False},
    )

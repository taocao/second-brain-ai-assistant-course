from typing import Generator

from openai import OpenAI

from second_brain_offline.config import settings


def get_chat_completion(prompt: str) -> Generator[str, None, None]:
    """Gets chat completion from HuggingFace endpoint.

    Args:
        prompt: The user prompt to send to the model

    Yields:
        Generated text chunks from the model response
    """

    assert settings.HUGGINGFACE_DEDICATED_ENDPOINT is not None, (
        "HUGGINGFACE_DEDICATED_ENDPOINT is not set"
    )
    assert settings.HUGGINGFACE_ACCESS_TOKEN is not None, (
        "HUGGINGFACE_ACCESS_TOKEN is not set"
    )

    client = OpenAI(
        base_url=settings.HUGGINGFACE_DEDICATED_ENDPOINT,
        api_key=settings.HUGGINGFACE_ACCESS_TOKEN,
    )

    chat_completion = client.chat.completions.create(
        model="tgi",
        messages=[
            {
                "role": "system",
                "content": "You are a helpful assistant that provides accurate and concise information.",
            },
            {
                "role": "user",
                "content": prompt,
            },
        ],
        stream=True,
    )

    for message in chat_completion:
        if message.choices[0].delta.content is not None:
            yield message.choices[0].delta.content


if __name__ == "__main__":
    sample_prompt = """
The tower is 324 metres (1,063 ft) tall, about the same height as an 81-storey building, 
and the tallest structure in Paris. Its base is square, measuring 125 metres (410 ft) on each side. 
During its construction, the Eiffel Tower surpassed the Washington Monument to become the tallest 
man-made structure in the world, a title it held for 41 years until the Chrysler Building in
New York City was finished in 1930. It was the first structure to reach a height of 300 metres. 
Due to the addition of a broadcasting aerial at the top of the tower in 1957, 
it is now taller than the Chrysler Building by 5.2 metres (17 ft). 
Excluding transmitters, the Eiffel Tower is the second tallest free-standing structure in 
France after the Millau Viaduct."""

    for chunk in get_chat_completion(sample_prompt):
        print(chunk, end="")

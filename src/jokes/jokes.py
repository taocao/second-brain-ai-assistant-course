from typing import TypedDict


class Joke(TypedDict):
    preambula: str
    punchline: str


def get_joke() -> Joke:
    return Joke(preambula="fake", punchline="fake")

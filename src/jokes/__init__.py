from .jokes import get_joke


def make_me_laugh():
    joke = get_joke()
    print(f"{joke["preambula"]} ... {joke['punchline']}")
